"""LDF1 lossless frame receiver. Offline input or an explicit USB CDC port.

Only complete paired 16- or 64-chirp export windows are published. The original incoming
stream is retained separately, including rejected and truncated messages.
No UART update commands, automatic port selection, or device flashing.

Live radar register control (LDC1 commands, LDF1 type-5 REPLY messages) is
encoded/decoded here; see firmware/include/ld2450_radar_control.h.
"""
import argparse
from collections import deque
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct
import time
import zlib

HEADER = struct.Struct('<4sBBBBHHIIIII')
MAX_PAYLOAD = 2057
RECORD_BYTES = 2056


def crc(data):
    return zlib.crc32(data) & 0xffffffff


CONTROL_READ, CONTROL_WRITE, CONTROL_REINIT = 1, 2, 3
CONTROL_READ_MAX = 32
CONTROL_STATUS = {0: 'ok', 1: 'bus error', 2: 'bad command', 3: 'queue overflow', 4: 'reinit failed'}


def encode_command(op, register=0, count=0, value=0, tag=0):
    """20-byte LDC1 command for the device's live radar register control."""
    body = struct.pack('<4sBBBBHHI', b'LDC1', op, count, register, 0, value, 0, tag)
    return body + struct.pack('<I', crc(body))


def decode_reply(payload):
    if len(payload) < 12:
        raise ValueError('Short REPLY')
    tag, op, status, register, count, generation, error = struct.unpack('<IBBBBHh', payload[:12])
    if len(payload) != 12 + 2 * count:
        raise ValueError('REPLY length mismatch')
    return dict(tag=tag, op=op, status=status, register=register, generation=generation,
                driver_error=error, values=list(struct.unpack(f'<{count}H', payload[12:])))


def decode_record(payload, previous=None):
    if len(payload) < 9 or payload[0] not in (0, 1):
        raise ValueError('Invalid codec mode/length')
    if payload[0] == 0:
        if len(payload) != 2057:
            raise ValueError('Invalid raw record length')
        iq = payload[9:]
    else:
        if previous is None or len(previous) != 2048:
            raise ValueError('Residual without reference chirp')
        reference = struct.unpack('>1024h', previous)
        values, pos = [], 9
        for block in range(32):
            if pos >= len(payload):
                raise ValueError('Truncated block')
            width = payload[pos]
            pos += 1
            if width > 17 or pos + 4 * width > len(payload):
                raise ValueError('Invalid block width/length')
            packed = int.from_bytes(payload[pos:pos + 4 * width], 'big')
            pos += 4 * width
            for index in range(32):
                z = (packed >> (width * (31 - index))) & ((1 << width) - 1)
                value = reference[block * 32 + index] + (z // 2 if not z & 1 else -(z // 2) - 1)
                if not -32768 <= value <= 32767:
                    raise ValueError('Residual outside int16')
                values.append(value)
        if pos != len(payload):
            raise ValueError('Trailing codec data')
        iq = struct.pack('>1024h', *values)
    record = payload[1:5] + iq + payload[5:9]
    validate_record(record)
    return record


def validate_record(record):
    if len(record) != RECORD_BYTES:
        raise ValueError('Wrong raw length')
    header = int.from_bytes(record[:4], 'big')
    lane, chirp = (header >> 22) & 3, (header >> 11) & 511
    if header >> 24 != 0xaa or lane > 1 or (header >> 20) & 3 != 2 or header & 2047 != 513 or chirp >= 64:
        raise ValueError('Unexpected DS RAW header')
    checksum, trailer = struct.unpack('>HH', record[-4:])
    if trailer != (lane << 14) | 0x2000 | ((chirp & 15) << 8) | 0x55:
        raise ValueError('Invalid radar trailer')
    if sum(struct.unpack('>1024H', record[4:-4])) & 65535 != checksum:
        raise ValueError('Radar checksum mismatch')
    return lane, chirp


@dataclass
class Message:
    kind: int
    codec: int
    lane: int
    chirp: int
    sequence: int
    frame: int
    timestamp_us: int
    raw_crc: int
    payload: bytes


class Parser:
    """Bounded incremental parser; None events invalidate an in-progress frame."""
    def __init__(self):
        self.buffer = bytearray()
        self.errors = 0
        self.discarded_bytes = 0

    def feed(self, data):
        for start in range(0, len(data), 4096):
            self.buffer.extend(data[start:start + 4096])
            while len(self.buffer) >= 32:
                fields = HEADER.unpack_from(self.buffer)
                magic, version, kind, codec, lane, length, chirp, seq, frame, stamp, raw_crc, header_crc = fields
                if magic != b'LDF1' or version != 1 or length > MAX_PAYLOAD or header_crc != crc(self.buffer[:28]):
                    del self.buffer[0]
                    self.errors += 1
                    self.discarded_bytes += 1
                    yield None
                    continue
                size = 36 + length
                if len(self.buffer) < size:
                    break
                payload = bytes(self.buffer[32:32 + length])
                valid = crc(payload) == struct.unpack_from('<I', self.buffer, 32 + length)[0]
                if not valid:
                    # A corrupt but CRC-valid length may cover a subsequent BEGIN.
                    # Rescan rather than dropping that whole region blindly.
                    del self.buffer[0]
                    self.errors += 1
                    self.discarded_bytes += 1
                    yield None
                    continue
                del self.buffer[:size]
                yield Message(kind, codec, lane, chirp, seq, frame, stamp, raw_crc, payload)

    def finish(self):
        if self.buffer:
            self.errors += 1
            self.discarded_bytes += len(self.buffer)
            self.buffer.clear()
            return True
        return False


class Frames:
    def __init__(self):
        self.current = None
        self.rejected = 0
        self.completed = 0
        self.protocol_errors = 0
        self.aborted = 0
        self.abort_reasons = {}
        self.last_abort = None
        self.latest_device_stats = {}
        self.replies = deque(maxlen=1024)  # Control REPLY messages, oldest first.

    def invalidate(self):
        if self.current is not None:
            self.rejected += 1
        self.current = None

    def accept(self, msg):
        if msg is None:
            self.invalidate()
            return None
        try:
            return self._accept(msg)
        except (ValueError, struct.error):
            self.protocol_errors += 1
            self.invalidate()
            return None

    def _accept(self, m):
        if m.kind == 1:
            self.invalidate()
            if (m.codec, m.lane, m.chirp, m.raw_crc, len(m.payload)) != (0, 255, 65535, 0, 52):
                raise ValueError('Invalid BEGIN')
            skipped, rejected, peak, pairs, chirps, lanes, version, generation = struct.unpack('<IIIHHBBH', m.payload[32:])
            if (pairs, lanes, version) != (512, 2, 1) or chirps not in (16, 64):
                raise ValueError('Unsupported frame configuration')
            self.latest_device_stats = dict(device_skipped=skipped, device_rejected=rejected,
                                            device_queue_peak=peak)
            self.current = dict(frame_id=m.frame, config_sha256=m.payload[:32].hex(),
                                chirps=chirps, register_generation=generation,
                                started_us=m.timestamp_us, device_skipped=skipped,
                                device_rejected=rejected, device_queue_peak=peak,
                                lanes=[[], []], timestamps_us=[[], []], next_sequence=(m.sequence + 1) & 0xffffffff)
            return None
        if m.kind == 5:
            # Control replies are only valid between frames.
            if self.current is not None or (m.codec, m.lane, m.chirp, m.raw_crc) != (0, 255, 65535, 0):
                raise ValueError('Invalid REPLY')
            reply = decode_reply(m.payload)
            reply['timestamp_us'] = m.timestamp_us
            self.replies.append(reply)
            return None
        f = self.current
        if f is None:
            return None
        if m.frame != f['frame_id'] or m.sequence != f['next_sequence']:
            raise ValueError('Frame/message sequence discontinuity')
        f['next_sequence'] = (m.sequence + 1) & 0xffffffff
        if m.kind == 2:
            if m.codec != 1 or m.lane > 1 or m.chirp != len(f['lanes'][m.lane]) or m.chirp >= f['chirps']:
                raise ValueError('Record order mismatch')
            records = f['lanes'][m.lane]
            if not records and m.payload[:1] != b'\x00':
                raise ValueError('First chirp must be raw')
            raw = decode_record(m.payload, records[-1][4:-4] if records else None)
            if validate_record(raw) != (m.lane, m.chirp) or crc(raw) != m.raw_crc:
                raise ValueError('Record identity/integrity mismatch')
            records.append(raw)
            f['timestamps_us'][m.lane].append(m.timestamp_us)
        elif m.kind in (3, 4):
            if (m.codec, m.lane, m.chirp, m.raw_crc) != (0, 255, 65535, 0):
                raise ValueError('Invalid terminal message')
            if m.kind == 4:
                if len(m.payload) != 4:
                    raise ValueError('Invalid ABORT')
                reason, = struct.unpack('<I', m.payload)
                self.aborted += 1
                self.abort_reasons[reason] = self.abort_reasons.get(reason, 0) + 1
                self.last_abort = dict(reason=reason, frame_id=m.frame, timestamp_us=m.timestamp_us,
                                       received_records=sum(len(lane) for lane in f['lanes']),
                                       expected_records=2*f['chirps'])
                self.invalidate()
            else:
                if m.payload or [len(lane) for lane in f['lanes']] != [f['chirps'], f['chirps']]:
                    raise ValueError('Incomplete frame')
                self.current = None
                self.completed += 1
                f.pop('next_sequence')
                f['ended_us'] = m.timestamp_us
                f['lanes'] = [b''.join(lane) for lane in f['lanes']]
                return f
        else:
            raise ValueError('Unknown message kind')
        return None


def save_frame(frame, out, ordinal):
    dest = out / f'frame-{ordinal:06d}-id-{frame["frame_id"]:010d}'
    dest.mkdir()  # Never replace previously accepted evidence.
    lanes = frame.pop('lanes')
    frame['lane_sha256'] = [hashlib.sha256(lane).hexdigest() for lane in lanes]
    for lane, raw in enumerate(lanes):
        (dest / f'lane{lane}.bin').write_bytes(raw)
    (dest / 'frame.json').write_text(json.dumps(frame, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument('--input', type=Path, help='Saved LDF1 stream')
    source.add_argument('--port', help='Explicit USB CDC port; never an updater UART')
    ap.add_argument('--out', type=Path, required=True, help='New capture directory')
    ap.add_argument('--seconds', type=float, default=30, help='Live capture duration')
    args = ap.parse_args()
    if args.seconds <= 0:
        ap.error('--seconds must be positive')
    args.out.mkdir(parents=True, exist_ok=False)
    parser, frames = Parser(), Frames()
    if args.input:
        transport = args.input.open('rb')
    else:
        import serial  # Optional, offline decoding needs only the standard library.
        transport = serial.Serial(args.port, 115200, timeout=0.1, rtscts=False, dsrdtr=False)
    started = time.monotonic()
    stream_hash, received_bytes = hashlib.sha256(), 0
    with transport, (args.out / 'stream.ldf').open('xb') as evidence:
        try:
            while args.input or time.monotonic() - started < args.seconds:
                data = transport.read(4096)
                if args.input and not data:
                    break
                evidence.write(data)
                stream_hash.update(data)
                received_bytes += len(data)
                for msg in parser.feed(data):
                    frame = frames.accept(msg)
                    if frame is not None:
                        save_frame(frame, args.out, frames.completed)
        finally:
            parser.finish()
            frames.invalidate()
            report = dict(source=str(args.input or args.port), complete_frames=frames.completed,
                          rejected_frames=frames.rejected, protocol_errors=frames.protocol_errors,
                          parser_errors=parser.errors, discarded_bytes=parser.discarded_bytes,
                          received_bytes=received_bytes, stream_sha256=stream_hash.hexdigest())
            (args.out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if frames.completed else 1


if __name__ == '__main__':
    raise SystemExit(main())
