"""CTest runs these against the freshly built C producer, never a Python encoder."""
import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from frame_stream import Parser, Frames, HEADER, crc, decode_record

EXE = Path(sys.argv.pop(1)).resolve()


def raw_record(lane, chirp, values):
    iq = struct.pack('>1024h', *values)
    return (struct.pack('>I', 0xaa200201 | lane << 22 | chirp << 11) + iq +
            struct.pack('>HH', sum(struct.unpack('>1024H', iq)) & 65535,
                        lane << 14 | 0x2000 | (chirp & 15) << 8 | 0x55))


def message_bytes(m):
    header = HEADER.pack(b'LDF1', 1, m.kind, m.codec, m.lane, len(m.payload), m.chirp,
                         m.sequence, m.frame, m.timestamp_us, m.raw_crc, 0)
    return header[:28] + struct.pack('<I', crc(header[:28])) + m.payload + struct.pack('<I', crc(m.payload))


def receive(wire, chunk=37):
    parser, frames, completed = Parser(), Frames(), []
    for pos in range(0, len(wire), chunk):
        for m in parser.feed(wire[pos:pos + chunk]):
            frame = frames.accept(m)
            if frame is not None:
                completed.append(frame)
    parser.finish()
    frames.invalidate()
    return completed, frames, parser


class Interop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / 'build').mkdir(exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(dir=ROOT / 'build')
        cls.path = Path(cls.temp.name)
        rng = random.Random(314159)
        cls.lanes = []
        for lane in range(2):
            base = [rng.randrange(-3000, 3001) for _ in range(1024)]
            raw = b''.join(raw_record(lane, chirp, [v + chirp * 2 for v in base]) for chirp in range(64))
            cls.lanes.append(raw)
            (cls.path / f'lane{lane}.bin').write_bytes(raw)
        output = cls.path / 'full.ldf'
        subprocess.run([str(EXE), '--replay', str(cls.path / 'lane0.bin'), str(cls.path / 'lane1.bin'), str(output)], check=True)
        cls.wire = output.read_bytes()
        cls.messages = list(Parser().feed(cls.wire))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def codec(self, raw):
        source, encoded = self.path / 'source.bin', self.path / 'encoded.bin'
        source.write_bytes(raw)
        subprocess.run([str(EXE), '--codec', str(source), str(encoded)], check=True)
        blob = encoded.read_bytes()
        pos, previous, result, modes = 0, None, [], []
        while pos < len(blob):
            size = struct.unpack_from('<H', blob, pos)[0]
            pos += 2
            payload = blob[pos:pos + size]
            pos += size
            record = decode_record(payload, previous)
            previous = record[4:-4]
            result.append(record)
            modes.append(payload[0])
        self.assertEqual(b''.join(result), raw)
        return blob, modes

    def test_real_capture_exact_and_provenance(self):
        fixture = ROOT / 'tests/fixtures/dual_lane_startup'
        total = 0
        for entry in json.loads((fixture / 'manifest.json').read_text())['files']:
            raw = (fixture / entry['file']).read_bytes()
            self.assertEqual(len(raw), entry['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry['sha256'])
            blob, modes = self.codec(raw)
            total += len(blob) - 2 * len(modes)  # Exclude test harness length prefixes.
            self.assertEqual(modes[0], 0)
        self.assertEqual(total, 35332)  # Independent earlier block32 experiment.

    def test_zero_full_range_and_raw_fallback(self):
        rng = random.Random(123)
        arrays = [[0] * 1024, [0] * 1024, [-32768] * 1024, [32767] * 1024,
                  [rng.randrange(-32768, 32768) for _ in range(1024)]]
        blob, modes = self.codec(b''.join(raw_record(0, n, a) for n, a in enumerate(arrays)))
        self.assertEqual(modes, [0, 1, 0, 0, 0])
        self.assertLess(len(blob), 5 * 2057)

    def test_17bit_residual_in_compressed_packet(self):
        a = [-32768] + [0] * 1023
        b = [32767] + [0] * 1023
        _, modes = self.codec(raw_record(0, 0, a) + raw_record(0, 1, b) + raw_record(0, 2, a))
        self.assertEqual(modes, [0, 1, 1])

    def test_complete_frame_exact_arbitrary_usb_chunks(self):
        for chunk in [1, 63, 64, 511, 4096, len(self.wire)]:
            frames, state, parser = receive(self.wire, chunk)
            self.assertEqual(len(frames), 1)
            self.assertEqual(frames[0]['lanes'], self.lanes)
            self.assertEqual(frames[0]['frame_id'], 7)
            self.assertEqual((state.rejected, state.protocol_errors, parser.errors), (0, 0, 0))

    def test_missing_duplicated_reordered_record_rejects(self):
        original = [message_bytes(m) for m in self.messages]
        cases = [original[:4] + original[5:], original[:4] + original[3:],
                 original[:4] + [original[5], original[4]] + original[6:]]
        for case in cases:
            frames, state, _ = receive(b''.join(case))
            self.assertEqual(frames, [])
            self.assertEqual(state.rejected, 1)

    def test_corrupt_message_recovers_at_next_begin(self):
        rng = random.Random(731)
        for _ in range(20):
            damaged = bytearray(self.wire)
            at = rng.randrange(100, len(damaged) - 36)
            damaged[at] ^= 1 << rng.randrange(8)
            frames, state, parser = receive(bytes(damaged) + self.wire)
            self.assertEqual(len(frames), 1)
            self.assertEqual(frames[0]['lanes'], self.lanes)
            self.assertGreater(state.rejected + state.protocol_errors + parser.errors, 0)

    def test_truncation_never_publishes(self):
        for count in [1, 31, 88, 500, len(self.wire) - 1, len(self.wire) - 36]:
            frames, _, _ = receive(self.wire[:count])
            self.assertFalse(frames)

    def test_false_length_and_noise_bounded_resync(self):
        broken = bytearray(self.wire[:32])
        broken[8:10] = b'\xff\xff'
        broken[28:32] = struct.pack('<I', crc(broken[:28]))
        frames, _, parser = receive(b'noise' * 1000 + broken + self.wire)
        self.assertEqual(len(frames), 1)
        self.assertGreater(parser.discarded_bytes, 5000)

    def test_valid_transport_crc_cannot_hide_bad_radar_or_identity(self):
        from copy import deepcopy
        for alteration in ['checksum', 'lane', 'raw_crc', 'chirp', 'codec']:
            messages = deepcopy(self.messages)
            m = messages[1]
            if alteration == 'checksum':
                payload = bytearray(m.payload)
                payload[9] ^= 1
                m.payload = bytes(payload)
            else:
                setattr(m, alteration, getattr(m, alteration) ^ 1)
            frames, state, _ = receive(b''.join(message_bytes(m) for m in messages))
            self.assertEqual(frames, [])
            self.assertEqual(state.rejected, 1)

    def test_partial_capture_is_abort_not_complete_frame(self):
        fixture = ROOT / 'tests/fixtures/dual_lane_startup'
        out = self.path / 'partial.ldf'
        subprocess.run([str(EXE), '--replay', str(fixture / 'lane0.bin'), str(fixture / 'lane1.bin'), str(out)], check=True)
        frames, state, parser = receive(out.read_bytes())
        self.assertEqual(frames, [])
        self.assertEqual(state.rejected, 1)
        self.assertEqual(parser.errors, 0)

    def test_bad_codec_rejected(self):
        for payload, previous in [(b'\x02' + b'\x00'*2056, None), (b'\x00', None),
                                  (b'\x01' + b'\x00'*8, None),
                                  (b'\x01' + b'\x00'*8 + b'\x12', b'\x00'*2048)]:
            with self.assertRaises(ValueError):
                decode_record(payload, previous)

    def test_cli_preserves_stream_and_complete_frame(self):
        out = self.path / 'decoded'
        subprocess.run([sys.executable, str(ROOT / 'tools/frame_stream.py'), '--input',
                        str(self.path / 'full.ldf'), '--out', str(out)], check=True, capture_output=True)
        self.assertEqual((out / 'stream.ldf').read_bytes(), self.wire)
        self.assertEqual(json.loads((out / 'report.json').read_text())['complete_frames'], 1)
        for lane in range(2):
            path = next(out.glob(f'frame-*/lane{lane}.bin'))
            self.assertEqual(path.read_bytes(), self.lanes[lane])


if __name__ == '__main__':
    unittest.main()
