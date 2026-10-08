"""Signal invariants and the viewer's validated-frame / local-control boundary."""
import base64
import hashlib
import http.client
import json
from pathlib import Path
import queue
import struct
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import numpy as np

from .processing import Pipeline, DEFAULT_SETTINGS, unpack_iq
from . import server
from frame_stream import HEADER, crc, Parser, Frames, Message


def fixture(fast_bin=12, slow_bin=5, frame_id=7, config="ab" * 32, chirps=64):
    n = np.arange(512)[None, :]
    c = np.arange(chirps)[:, None]
    z = 1000 * np.exp(2j * np.pi * (n * fast_bin / 512 + c * slow_bin / chirps)) + (3000 - 1500j)
    lane_bytes = []
    for lane in range(2):
        records = []
        for chirp in range(chirps):
            iq = np.stack((z[chirp].real, z[chirp].imag), axis=-1).round().astype(">i2").tobytes()
            records.append(struct.pack(">I", 0xaa200201 | lane << 22 | chirp << 11) + iq +
                           struct.pack(">HH", sum(struct.unpack(">1024H", iq)) & 65535,
                                       lane << 14 | 0x2000 | (chirp & 15) << 8 | 0x55))
        lane_bytes.append(b"".join(records))
    stamps = [(0xffffff00 + 1200 * i) & 0xffffffff for i in range(chirps)]
    return dict(chirps=chirps, frame_id=frame_id, config_sha256=config, started_us=stamps[0],
                ended_us=stamps[-1], device_skipped=2, device_rejected=0,
                device_queue_peak=100, lanes=lane_bytes, timestamps_us=[stamps, stamps])


def bins_wire(frame, half=40, generation=0):
    """Codec-2 LDF1 stream for a raw fixture, encoded exactly as the firmware does."""
    sequence = 0
    def packet(kind, payload, codec=0, lane=255, chirp=65535, raw_crc=0):
        nonlocal sequence
        head = HEADER.pack(b"LDF1", 1, kind, codec, lane, len(payload), chirp, sequence, frame["frame_id"],
                           frame["started_us"] if chirp == 65535 else frame["timestamps_us"][lane][chirp], raw_crc, 0)
        sequence += 1
        return head[:28] + struct.pack("<I", crc(head[:28])) + payload + struct.pack("<I", crc(payload))
    begin = bytes.fromhex(frame["config_sha256"]) + struct.pack("<IIIHHBBH", 2, 0, 100, 512, frame["chirps"], 2, 2, generation)
    output = packet(1, begin + struct.pack("<HBB", 512, half, 1))
    ks = np.arange(-half, half + 1)
    for chirp in range(frame["chirps"]):
        for lane in range(2):
            record = frame["lanes"][lane][chirp * 2056:(chirp + 1) * 2056]
            v = np.frombuffer(record[4:-4], ">i2").astype(np.int64)
            X = np.fft.fft(v[0::2] + 1j * v[1::2])[ks % 512]
            re, im = np.round(X.real).astype(np.int64), np.round(X.imag).astype(np.int64)
            others = np.concatenate([np.delete(re, half), np.delete(im, half)])
            shift = 0
            while (int(np.max(np.abs(others))) >> shift) > 32767:
                shift += 1
            q = lambda a: np.clip((a + ((1 << shift) >> 1)) >> shift, -32768, 32767) if shift else a
            body = np.empty(4 * half, dtype="<i2")
            body[0::2], body[1::2] = q(np.delete(re, half)), q(np.delete(im, half))
            payload = (b"\x02" + record[:4] + record[-4:] + bytes([shift]) +
                       struct.pack("<ii", int(re[half]), int(im[half])) + body.tobytes())
            output += packet(2, payload, 2, lane, chirp, crc(record))
    return output + packet(3, b"")


def decode_one(stream):
    parser, frames, accepted = Parser(), Frames(), None
    for message in parser.feed(stream):
        result = frames.accept(message)
        if result:
            accepted = result
    return accepted


def wire(frame, generation=0):
    sequence = 0
    def packet(kind, payload, lane=255, chirp=65535, raw_crc=0):
        nonlocal sequence
        head = HEADER.pack(b"LDF1", 1, kind, int(kind == 2), lane, len(payload), chirp,
                           sequence, frame["frame_id"], frame["started_us"] if chirp == 65535 else frame["timestamps_us"][lane][chirp], raw_crc, 0)
        sequence += 1
        return head[:28] + struct.pack("<I", crc(head[:28])) + payload + struct.pack("<I", crc(payload))
    output = packet(1, bytes.fromhex(frame["config_sha256"]) + struct.pack("<IIIHHBBH", 2, 0, 100, 512, frame["chirps"], 2, 1, generation))
    for chirp in range(frame["chirps"]):
        for lane in range(2):
            record = frame["lanes"][lane][chirp * 2056:(chirp + 1) * 2056]
            output += packet(2, b"\0" + record[:4] + record[-4:] + record[4:-4], lane, chirp, crc(record))
    return output + packet(3, b"")


class ProcessingTests(unittest.TestCase):
    def test_raw16_decode_and_doppler_scale(self):
        frame = fixture(chirps=16, slow_bin=2)
        parser, frames = Parser(), Frames()
        accepted = None
        for message in parser.feed(wire(frame)):
            result = frames.accept(message)
            if result: accepted = result
        self.assertIsNotNone(accepted)
        self.assertEqual(accepted["chirps"],16)
        result = Pipeline().process(accepted,DEFAULT_SETTINGS)
        self.assertEqual((result["bins_shape"], result["bins_source"]), ([2,16,79,2], "host"))
        self.assertEqual(len(base64.b64decode(result["bins_base64"])),2*16*79*2*4)
        doppler = result["products"]["doppler"]
        row, col = np.unravel_index(np.argmax(doppler["db"][0]),(16,79))
        self.assertEqual((row-8,col-39),(2,12))
        self.assertAlmostEqual(doppler["hz"][row],2/(16*.0012),places=3)

    def test_complex_fft_sign_amplitude_and_doppler_frequency(self):
        result = Pipeline().process(fixture(), DEFAULT_SETTINGS)
        spectrum = np.asarray(result["products"]["spectrum"]["db"])
        self.assertEqual(result["bin_range"], [-39, 39])
        self.assertEqual(int(np.argmax(spectrum[0])) - 39, 12)
        self.assertAlmostEqual(spectrum[0, 39 + 12], 60, delta=.03)
        doppler = result["products"]["doppler"]
        row, col = np.unravel_index(np.argmax(doppler["db"][0]), (64, 79))
        self.assertEqual((row - 32, col - 39), (5, 12))
        self.assertAlmostEqual(doppler["hz"][row], 5 / (64 * .0012), places=3)
        self.assertEqual(result["products"]["quality"]["timing_outliers"], 0)  # Includes uint32 rollover.

    def test_wire_iq_endianness_and_published_bins(self):
        frame = fixture()
        self.assertEqual(tuple(unpack_iq(frame)[0, 0, 0]), (4000, -1500))
        result = Pipeline().process(frame, dict(DEFAULT_SETTINGS, window="rectangular"))
        bins = np.frombuffer(base64.b64decode(result["bins_base64"]), dtype="<f4").reshape(result["bins_shape"])
        z = bins[..., 0] + 1j * bins[..., 1]
        # Rectangular window: the tone at bin 12 reads its amplitude, chirp phase advances 5/64 cycle.
        self.assertAlmostEqual(abs(z[0, 0, 39 + 12]), 1000, delta=1)
        self.assertAlmostEqual(np.angle(z[0, 1, 39 + 12] / z[0, 0, 39 + 12]), 2 * np.pi * 5 / 64, places=3)

    def test_device_range_bins_match_host_conversion_of_raw(self):
        """Codec-2 frames (firmware encoding) process like the raw frame, within quantization."""
        for gain_db, phase_deg in ((0, 0), (-2.2, -18.2)):
            raw = self.imbalanced(gain_db, phase_deg, chirps=64)
            device = decode_one(bins_wire(raw))
            self.assertEqual((device["codec_version"], device["bins_half"], device["chirps"]), (2, 40, 64))
            for settings in (DEFAULT_SETTINGS, dict(DEFAULT_SETTINGS, window="rectangular", remove_dc=False)):
                results = []
                for frame in (raw, device):
                    pipeline = Pipeline()
                    pipeline.set_iq_calibration(frame)
                    pipeline.set_reference(frame)
                    pipeline.clear_reference()
                    results.append(pipeline.process(frame, settings))
                host, dev = results
                self.assertEqual((host["bins_source"], dev["bins_source"]), ("host", "device"))
                self.assertEqual(host["bin_range"], dev["bin_range"])
                for name in ("spectrum", "doppler", "change"):
                    a, b = np.array(host["products"][name]["db"]), np.array(dev["products"][name]["db"])
                    strong = a > np.max(a) - 60
                    self.assertLess(np.max(np.abs(a - b)[strong]), 0.05, (name, settings))
                self.assertAlmostEqual(dev["iq_calibration"]["phase_deg"][0], host["iq_calibration"]["phase_deg"][0], delta=0.05)
                self.assertEqual(host["stage_errors"], {})
                self.assertEqual(dev["stage_errors"], {})

    def test_reference_cancels_static_and_clears_on_config_change(self):
        frame = fixture(slow_bin=0)
        pipeline = Pipeline()
        pipeline.set_reference(frame)
        result = pipeline.process(frame, DEFAULT_SETTINGS)
        self.assertLess(np.max(result["products"]["spectrum"]["db"]), -100)
        self.assertEqual(result["reference_frame"], 7)
        changed = dict(frame, config_sha256="cd" * 32)
        self.assertIsNone(pipeline.process(changed, DEFAULT_SETTINGS)["reference_frame"])

    def test_static_rejection_only_affects_doppler(self):
        pipeline = Pipeline()
        frame = fixture(slow_bin=0)
        removed = pipeline.process(frame, DEFAULT_SETTINGS)
        kept = pipeline.process(frame, dict(DEFAULT_SETTINGS, remove_static=False))
        self.assertLess(np.max(removed["products"]["doppler"]["db"]), -100)
        self.assertGreater(np.max(kept["products"]["doppler"]["db"]), 59)
        self.assertEqual(kept["products"]["spectrum"], removed["products"]["spectrum"])

    def test_change_suppresses_static_and_reveals_motion(self):
        pipeline = Pipeline()
        static = fixture(slow_bin=0)
        pipeline.process(static, DEFAULT_SETTINGS)
        settled = pipeline.process(static, DEFAULT_SETTINGS)["products"]["change"]["db"]
        self.assertLess(np.max(settled), -100)
        moved = pipeline.process(fixture(fast_bin=20, slow_bin=0), DEFAULT_SETTINGS)
        self.assertGreater(moved["products"]["change"]["db"][0][39 + 20], 50)
        # A settings change restarts the average rather than mixing modes.
        restarted = pipeline.process(static, dict(DEFAULT_SETTINGS, window="rectangular"))
        self.assertLess(np.max(restarted["products"]["change"]["db"]), -100)

    @staticmethod
    def imbalanced(gain_db, phase_deg, config="ab" * 32, bins=(6, 9), chirps=16):
        """Static scene of tones on positive bins; Q = g*sin(t + phi) relative to I."""
        frame = fixture(chirps=chirps, config=config)
        n = np.arange(512)
        g, phi = 10 ** (gain_db / 20), np.radians(phase_deg)
        I = sum(900 / (i + 1) * np.cos(2 * np.pi * b * n / 512 + i) for i, b in enumerate(bins)) + 300
        Q = sum(900 / (i + 1) * g * np.sin(2 * np.pi * b * n / 512 + i + phi) for i, b in enumerate(bins)) - 200
        iq = np.stack((I, Q), axis=-1).round().astype(">i2").tobytes()
        trailer = lambda lane, c: struct.unpack(">HH", lane[(c + 1) * 2056 - 4:(c + 1) * 2056])[1]
        frame["lanes"] = [b"".join(lane[c * 2056:c * 2056 + 4] + iq +
                                   struct.pack(">HH", sum(struct.unpack(">1024H", iq)) & 65535, trailer(lane, c))
                                   for c in range(chirps)) for lane in frame["lanes"]]
        return frame

    def test_iq_calibration_recovers_mismatch_and_removes_mirror(self):
        frame = self.imbalanced(-2.2, -18.2)
        pipeline = Pipeline()
        uncorrected = pipeline.process(frame, DEFAULT_SETTINGS)
        before = uncorrected["products"]["iq_balance"]
        # Same model as the bench check: about -14 dB for this mismatch.
        self.assertAlmostEqual(before["image_db"][0], -13.8, delta=0.6)
        self.assertFalse(before["corrected"])
        summary = pipeline.set_iq_calibration(frame)
        self.assertAlmostEqual(summary["q_gain_db"][0], -2.2, delta=0.1)
        self.assertAlmostEqual(summary["phase_deg"][1], -18.2, delta=0.3)
        after = pipeline.process(frame, DEFAULT_SETTINGS)
        self.assertTrue(after["products"]["iq_balance"]["corrected"])
        self.assertLess(max(after["products"]["iq_balance"]["image_db"]), -45)
        spec = np.array(after["products"]["spectrum"]["db"])
        self.assertGreater(spec[0, 39 + 6] - spec[0, 39 - 6], 45)
        self.assertEqual(after["iq_calibration"]["frame"], frame["frame_id"])

    def test_iq_calibration_clears_on_settings_identity_change(self):
        pipeline = Pipeline()
        frame = self.imbalanced(-1, -10)
        pipeline.set_iq_calibration(dict(frame, config_id="cfg:0"))
        self.assertIsNotNone(pipeline.process(dict(frame, config_id="cfg:0"), DEFAULT_SETTINGS)["iq_calibration"])
        self.assertIsNone(pipeline.process(dict(frame, config_id="cfg:1"), DEFAULT_SETTINGS)["iq_calibration"])

    def test_stage_failure_is_visible_and_other_products_survive(self):
        pipeline = Pipeline()
        def fail(_):
            raise ValueError("deliberate test failure")
        pipeline.stages["experimental"] = fail
        result = pipeline.process(fixture(), DEFAULT_SETTINGS)
        self.assertIn("spectrum", result["products"])
        self.assertEqual(result["stage_errors"], {"experimental": "deliberate test failure"})

    def test_settings_reject_unexpected_or_wrong_types(self):
        # detrend was removed with the move to range bins; an old client sending it is refused.
        for settings in ({}, dict(DEFAULT_SETTINGS, remove_dc=1), dict(DEFAULT_SETTINGS, detrend=False), dict(DEFAULT_SETTINGS, window="bad")):
            with self.assertRaises(ValueError):
                Pipeline().process(fixture(), settings)


class AcquisitionTests(unittest.TestCase):
    def test_explicit_aborts_are_separate_from_invalid_frames(self):
        parser, frames = Parser(), Frames()
        messages = list(parser.feed(wire(fixture())))
        for reason in (3, 6, 5, 99):
            for message in messages[:3]:
                frames.accept(message)
            frames.accept(Message(4, 0, 255, 65535, 3, 7, 100, 0, struct.pack("<I", reason)))
        self.assertEqual(frames.rejected, 4)
        self.assertEqual(frames.aborted, 4)
        self.assertEqual(frames.protocol_errors, 0)
        self.assertEqual(frames.abort_reasons, {3: 1, 6: 1, 5: 1, 99: 1})
        self.assertEqual(frames.last_abort["received_records"], 2)
        viewer = server.Viewer()
        viewer._update_decode(parser, frames)
        self.assertEqual(viewer.stats["queue_aborts"], 1)
        self.assertEqual(viewer.stats["cpu_aborts"], 1)
        self.assertEqual(viewer.stats["other_aborts"], 2)
        self.assertEqual(viewer.stats["invalid_frames"], 0)
        self.assertEqual(viewer.stats["device_skipped"], 2)  # No completed frame required.
        self.assertEqual(viewer.stats["device_queue_peak"], 100)

    def test_malformed_abort_is_not_counted_as_firmware_protection(self):
        parser, frames = Parser(), Frames()
        for message in list(parser.feed(wire(fixture())))[:3]:
            frames.accept(message)
        frames.accept(Message(4, 0, 255, 65535, 3, 7, 100, 0, b"bad"))
        viewer = server.Viewer()
        viewer._update_decode(parser, frames)
        self.assertEqual(viewer.stats["invalid_frames"], 1)
        self.assertEqual(viewer.stats["device_aborts"], 0)
        self.assertEqual(viewer.stats["protocol_errors"], 1)

    def test_wire_rate_remains_visible_when_all_frames_abort(self):
        viewer = server.Viewer()
        viewer.last_frame_at = time.monotonic() - 10
        viewer.rate_at = time.monotonic()
        viewer.stats.update(wire_kbps=600, frames_per_second=5)
        self.assertEqual(viewer.state()["stats"]["wire_kbps"], 600)
        self.assertEqual(viewer.state()["stats"]["frames_per_second"], 0)
        viewer.rate_at -= 3
        self.assertEqual(viewer.state()["stats"]["wire_kbps"], 0)

    def test_corrupt_frame_never_reaches_processing_and_next_frame_recovers(self):
        viewer = server.Viewer()
        chunks, frames = queue.Queue(), queue.Queue(maxsize=1)
        original = wire(fixture())
        corrupt = bytearray(original)
        corrupt[200] ^= 0x80
        chunks.put(bytes(corrupt) + original)
        thread = threading.Thread(target=viewer._decode, args=(chunks, frames))
        thread.start()
        try:
            complete = frames.get(timeout=3)
            self.assertEqual(complete["lanes"], fixture()["lanes"])
        finally:
            viewer.stop_event.set()
            thread.join(2)
        self.assertEqual(viewer.stats["complete_frames"], 1)
        self.assertEqual(viewer.stats["rejected_frames"], 1)
        self.assertGreater(viewer.stats["parser_errors"], 0)

    def test_display_backlog_keeps_latest_without_discarding_raw_integrity(self):
        viewer = server.Viewer()
        frames = queue.Queue(maxsize=1)
        viewer._publish_raw(fixture(frame_id=1), frames)
        viewer._publish_raw(fixture(frame_id=2), frames)
        self.assertEqual(frames.get()["frame_id"], 2)
        self.assertEqual(viewer.stats["complete_frames"], 2)
        self.assertEqual(viewer.stats["processing_drops"], 1)

    def test_does_not_open_uart_or_nonmatching_device(self):
        viewer = server.Viewer()
        with patch.object(server, "usb_ports", return_value=["COM30"]), patch.object(server.serial, "Serial") as serial_open:
            with self.assertRaises(ValueError):
                viewer.connect(port="COM13")
            serial_open.assert_not_called()

    def test_replay_lifecycle_and_snapshot_preserve_raw_frame(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "test.ldf"
            path.write_bytes(wire(fixture()))
            viewer = server.Viewer()
            viewer.connect(replay=path)
            try:
                deadline = time.monotonic() + 3
                while viewer.latest is None and time.monotonic() < deadline:
                    time.sleep(.02)
                self.assertIsNotNone(viewer.latest)
                with patch.object(server, "OUTPUT", Path(temp) / "output"):
                    saved = Path(viewer.snapshot())
                    meta = json.loads(next(saved.glob("frame-*/frame.json")).read_text())
                    self.assertEqual(meta["lane_sha256"][0], hashlib.sha256(fixture()["lanes"][0]).hexdigest())
                    self.assertIn("lanes", viewer.raw_frame)
            finally:
                viewer.disconnect()
            self.assertFalse(viewer.threads)
            self.assertEqual(viewer.status, "disconnected")

    def test_recording_retains_exact_bytes_with_manifest(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(server, "OUTPUT", Path(temp)):
            viewer = server.Viewer()
            viewer.status = "live"
            viewer.source = "test"
            viewer.start_recording()
            data = wire(fixture())
            class FakeSerial:
                in_waiting = 0
                def __init__(self):
                    self.sent = False
                def read(self, _):
                    if self.sent:
                        viewer.stop_event.set()
                        return b""
                    self.sent = True
                    return data
                def close(self):
                    pass
            viewer.transport = FakeSerial()
            viewer._read_usb(queue.Queue())
            folder = Path(viewer.record_result)
            self.assertEqual((folder / "stream.ldf").read_bytes(), data)
            report = json.loads((folder / "report.json").read_text())
            self.assertEqual(report["stream_sha256"], hashlib.sha256(data).hexdigest())


def control_reply(tag, op, status, register, generation, values, error=0):
    payload = struct.pack("<IBBBBHh", tag, op, status, register, len(values), generation, error)
    payload += struct.pack(f"<{len(values)}H", *values)
    head = HEADER.pack(b"LDF1", 1, 5, 0, 255, len(payload), 65535, 99, 0, 0, 0, 0)
    return head[:28] + struct.pack("<I", crc(head[:28])) + payload + struct.pack("<I", crc(payload))


class FakeDevice:
    """CDC port answering LDC1 commands like the firmware: replies between frames,
    then a frame whose BEGIN reports the new register generation."""
    in_waiting = 0

    def __init__(self, *args, **kwargs):
        self.dtr, self.port = True, None
        self.registers = {r: 0x1000 + r for r in range(256)}
        self.generation = 0
        self.outgoing = bytearray()
        self.lock = threading.Lock()
        self.commands = []
        self.accept_writes = True
        self.primed = False
        self.in_flight = False
        self.drop_next = False

    def open(self):
        pass

    def close(self):
        pass

    def write(self, data):
        if not self.accept_writes:
            raise server.serial.SerialTimeoutException("Write timeout")
        if data == b"\0":
            self.primed = True
            return 1
        assert self.primed, "the first packet after opening is a discardable priming byte"
        self.assert_command(data)
        with self.lock:
            assert not self.in_flight, "only one command may be in flight"
            self.in_flight = True
        if self.drop_next:
            self.drop_next = False  # Lost packet: the host must resend after its timeout.
            with self.lock:
                self.in_flight = False
            return len(data)
        magic, op, count, reg, _, value, _, tag = struct.unpack("<4sBBBBHHI", data[:16])
        self.commands.append((op, reg, count, value))
        values = []
        if op == 1:
            values = [self.registers[reg + n] for n in range(count)]
        elif op == 2:
            self.registers[reg] = value
            self.generation += 1
            values = [value]
        with self.lock:
            self.outgoing += control_reply(tag, op, 0, reg, self.generation, values)
            self.outgoing += wire(fixture(frame_id=10 + len(self.commands)), self.generation)
            self.in_flight = False
        return len(data)

    @staticmethod
    def assert_command(data):
        assert len(data) == 20 and data[:4] == b"LDC1" and struct.unpack("<I", data[16:])[0] == crc(data[:16])

    def read(self, _):
        with self.lock:
            out, self.outgoing = bytes(self.outgoing), bytearray()
        if not out:
            time.sleep(.01)
        return out


class RegisterControlTests(unittest.TestCase):
    def wait(self, condition, seconds=3):
        deadline = time.monotonic() + seconds
        while not condition() and time.monotonic() < deadline:
            time.sleep(.02)
        self.assertTrue(condition())

    def test_commands_replies_and_settings_identity(self):
        device = FakeDevice()
        viewer = server.Viewer()
        with patch.object(server, "usb_ports", return_value=["COM30"]), \
                patch.object(server.serial, "Serial", return_value=device):
            viewer.connect(port="COM30")
        try:
            # Any register and value: no restriction in the host path.
            viewer.register_write(0x53, 0xBEEF)
            self.wait(lambda: viewer.latest is not None and viewer.latest["register_generation"] == 1)
            self.assertTrue(viewer.latest["config_id"].endswith(":1"))
            history_generation = viewer.generation
            # A 10-register read is split into device-sized chunks of 4, 4 and 2.
            viewer.register_read(0x60, 10)
            self.wait(lambda: len(viewer.register_state()["values"]) == 11)
            self.assertEqual([c[1:3] for c in device.commands[1:]], [(0x60, 4), (0x64, 4), (0x68, 2)])
            state = viewer.register_state()
            self.assertEqual(state["values"]["53"]["value"], 0xBEEF)
            self.assertEqual(state["values"]["61"]["value"], 0x1061)
            self.assertEqual(state["generation"], 1)
            self.assertEqual(state["pending"] + state["timed_out"], 0)
            self.assertEqual([e["status"] for e in state["log"]], ["ok"] * 4)
            # Reads do not change settings identity; a write resets display history.
            self.assertEqual(viewer.generation, history_generation)
            viewer.register_write(0x61, 0x0022)
            self.wait(lambda: viewer.latest["register_generation"] == 2)
            self.assertGreater(viewer.generation, history_generation)
            # A lost command is resent once after the reply timeout.
            device.drop_next = True
            viewer.register_read(0x40, 1)
            self.wait(lambda: "40" in viewer.register_state()["values"])
            self.assertEqual(device.commands[-1][1:3], (0x40, 1))
            # Firmware that never reads commands must not hang the server.
            device.accept_writes = False
            viewer.register_write(0x61, 0x0021)
            self.wait(lambda: viewer.register_state()["log"][-1]["status"].startswith("not accepted"))
            self.assertEqual(viewer.register_state()["pending"], 0)
        finally:
            viewer.disconnect()

    def test_viewer_iq_calibration_needs_a_frame_and_restarts_history(self):
        viewer = server.Viewer()
        with self.assertRaises(ValueError):
            viewer.iq_calibration(True)
        viewer.raw_frame = ProcessingTests.imbalanced(-2, -15)
        generation = viewer.generation
        summary = viewer.iq_calibration(True)
        self.assertAlmostEqual(summary["phase_deg"][0], -15, delta=0.3)
        self.assertGreater(viewer.generation, generation)
        self.assertIsNone(viewer.iq_calibration(False))
        self.assertIsNone(viewer.pipeline.iq_cal)

    def test_register_control_requires_live_usb_and_valid_ranges(self):
        viewer = server.Viewer()
        with self.assertRaises(ValueError):
            viewer.register_write(0x61, 0x21)
        viewer.status, viewer.transport = "live", FakeDevice()
        for call in (lambda: viewer.register_read(0xFF, 2), lambda: viewer.register_write(0x100, 0),
                     lambda: viewer.register_write(0x10, 0x10000), lambda: viewer.register_read(0, 0)):
            with self.assertRaises(ValueError):
                call()


class HTTPTests(unittest.TestCase):
    def test_local_control_requires_token_and_matching_origin(self):
        viewer = server.Viewer()
        httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.make_handler(viewer, "test-token"))
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        connection = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=2)
        try:
            for headers in ({}, {"X-Viewer-Token": "test-token", "Origin": "https://example.org"}):
                connection.request("POST", "/api/settings", json.dumps(DEFAULT_SETTINGS), headers)
                response = connection.getresponse()
                self.assertEqual(response.status, 403)
                response.read()
            connection.request("POST", "/api/settings", json.dumps(DEFAULT_SETTINGS), {"X-Viewer-Token": "test-token"})
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            response.read()
            connection.request("GET", "/../server.py")
            response = connection.getresponse()
            self.assertEqual(response.status, 404)
            response.read()
        finally:
            connection.close()
            httpd.shutdown()
            httpd.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
