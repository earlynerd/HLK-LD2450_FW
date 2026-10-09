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

from .processing import Pipeline, DEFAULT_SETTINGS, unpack_iq, load_calibration
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


def from_samples(z, frame_id=7, config="ab" * 32, start_us=1000):
    """Raw frame from complex samples z: receivers x chirps x 512."""
    chirps = z.shape[1]
    lanes = []
    for lane in range(2):
        records = []
        for chirp in range(chirps):
            iq = np.clip(np.stack((z[lane, chirp].real, z[lane, chirp].imag), axis=-1).round(), -32768, 32767)
            iq = iq.astype(">i2").tobytes()
            records.append(struct.pack(">I", 0xaa200201 | lane << 22 | chirp << 11) + iq +
                           struct.pack(">HH", sum(struct.unpack(">1024H", iq)) & 65535,
                                       lane << 14 | 0x2000 | (chirp & 15) << 8 | 0x55))
        lanes.append(b"".join(records))
    stamps = [(start_us + 1200 * i) & 0xffffffff for i in range(chirps)]
    return dict(chirps=chirps, frame_id=frame_id, config_sha256=config, started_us=stamps[0],
                ended_us=stamps[-1], device_skipped=0, device_rejected=0, device_queue_peak=0,
                lanes=lanes, timestamps_us=[stamps, stamps])


def scene(movers=(), static=(), noise=4.0, chirps=64, seed=1, d_over_lambda=0.5, frame_id=7, start_us=1000):
    """Point targets as (range_bin, doppler_bin, angle_deg, amplitude); RX2 leads RX1 by
    2 pi (d/lambda) sin(angle). Static targets have zero Doppler."""
    rng = np.random.default_rng(seed)
    n, c = np.arange(512)[None, :], np.arange(chirps)[:, None]
    z = np.zeros((2, chirps, 512), complex) + (900 - 400j)
    for k, dop, angle, amp in list(movers) + [(k, 0, a, amp) for k, a, amp in static]:
        tone = amp * np.exp(2j * np.pi * (k * n / 512 + dop * c / chirps))
        phase = 2 * np.pi * d_over_lambda * np.sin(np.radians(angle))
        z[0] += tone
        z[1] += tone * np.exp(1j * phase)
    z += noise * (rng.standard_normal(z.shape) + 1j * rng.standard_normal(z.shape))
    return from_samples(z, frame_id=frame_id, start_us=start_us)


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


class TargetTests(unittest.TestCase):
    MOVERS = ((6.3, 5.4, 20.0, 1500), (11.0, -8.0, -35.0, 1200))
    STATIC = ((3.0, 5.0, 6000),)

    def detect(self, frame, settings=DEFAULT_SETTINGS, calibration=None):
        result = Pipeline(calibration).process(frame, settings)
        self.assertEqual(result["stage_errors"], {})
        return result["products"]["targets"]

    def test_moving_targets_range_velocity_and_angle(self):
        cal = load_calibration()
        out = self.detect(scene(self.MOVERS, self.STATIC), calibration=cal)
        found = sorted(out["targets"], key=lambda t: t["range_bin"])
        self.assertEqual(len(found), 2, found)
        hz_per_bin = 1 / (64 * 0.0012)
        for t, (k, dop, angle, _) in zip(found, self.MOVERS):
            self.assertAlmostEqual(t["range_bin"], k, delta=0.25)
            self.assertAlmostEqual(t["doppler_hz"] / hz_per_bin, dop, delta=0.3)
            self.assertAlmostEqual(t["angle_deg"], angle, delta=1.5)
            self.assertAlmostEqual(t["range_m"], cal["range"]["m_per_bin"] * t["range_bin"] + cal["range"]["offset_m"], places=2)
            self.assertAlmostEqual(t["velocity_mps"], t["doppler_hz"] * cal["wavelength_m"] / 2, places=3)
            self.assertAlmostEqual(np.hypot(t["x_m"], t["y_m"]), t["range_m"], places=2)
            self.assertGreater(t["coherence"], 0.95)
            self.assertFalse(t["angle_ambiguous"])
        self.assertTrue(out["moving_only"])
        self.assertFalse(out["calibrated"]["angle"])

    def test_noise_alone_gives_no_detections(self):
        for seed in range(5):
            self.assertEqual(self.detect(scene(seed=seed))["targets"], [])

    def test_static_reflector_needs_static_mode(self):
        frame = scene(static=self.STATIC)
        self.assertEqual(self.detect(frame)["targets"], [])
        found = self.detect(frame, dict(DEFAULT_SETTINGS, remove_static=False))["targets"]
        self.assertEqual(len(found), 1)
        self.assertAlmostEqual(found[0]["range_bin"], 3.0, delta=0.25)
        self.assertAlmostEqual(found[0]["angle_deg"], 5.0, delta=1.0)

    def test_max_range_and_angle_calibration(self):
        cal = load_calibration()
        cal["detection"]["max_range_m"] = cal["range"]["m_per_bin"] * 9 + cal["range"]["offset_m"]
        found = self.detect(scene(self.MOVERS), calibration=cal)["targets"]
        self.assertEqual([round(t["range_bin"]) for t in found], [6])
        # A boresight offset equal to the target's phase puts it straight ahead; the sign mirrors.
        cal["angle"].update(phase_offset_deg=float(np.degrees(np.pi * np.sin(np.radians(20)))))
        self.assertAlmostEqual(self.detect(scene(self.MOVERS), calibration=cal)["targets"][0]["angle_deg"], 0, delta=1.5)
        cal["angle"].update(phase_offset_deg=0.0, sign=-1)
        self.assertAlmostEqual(self.detect(scene(self.MOVERS), calibration=cal)["targets"][0]["angle_deg"], -20, delta=1.5)

    def test_range_scale_follows_live_sweep_step(self):
        cal = load_calibration()
        frame = scene(self.MOVERS)
        base = sorted(self.detect(frame)["targets"], key=lambda t: t["range_bin"])
        frame["live_registers"] = {0x56: 83}   # 1 GHz sweep: bins 83/20 times finer.
        out = self.detect(frame)
        wide = sorted(out["targets"], key=lambda t: t["range_bin"])
        self.assertAlmostEqual(out["m_per_bin"], cal["range"]["m_per_bin"] * 20 / 83, places=4)
        self.assertEqual(out["sweep_step"], 83)
        self.assertFalse(out["calibrated"]["range"])
        for a, b in zip(base, wide):
            self.assertAlmostEqual(b["range_bin"], a["range_bin"], places=2)
            self.assertAlmostEqual(b["range_m"], out["m_per_bin"] * b["range_bin"] + cal["range"]["offset_m"], places=2)
        frame["live_registers"] = {0x56: 20}
        self.assertAlmostEqual(self.detect(frame)["m_per_bin"], cal["range"]["m_per_bin"], places=4)

    def test_device_bins_give_the_same_targets(self):
        raw = scene(self.MOVERS, self.STATIC)
        a = sorted(self.detect(raw)["targets"], key=lambda t: t["range_bin"])
        b = sorted(self.detect(decode_one(bins_wire(raw)))["targets"], key=lambda t: t["range_bin"])
        self.assertEqual(len(a), len(b))
        for x, y in zip(a, b):
            for key, tol in (("range_bin", 0.02), ("doppler_hz", 0.2), ("angle_deg", 0.2)):
                self.assertAlmostEqual(x[key], y[key], delta=tol)


class TrackTests(unittest.TestCase):
    PERIOD_US = 89000
    HZ_PER_BIN = 1 / (64 * 0.0012)

    def run_frames(self, movers_at, frames, noise=40.0, seed=0, start=1000, calibration=None):
        """movers_at(i, rng) -> movers for frame i; returns the tracks product per frame."""
        pipe, rng, out = Pipeline(calibration), np.random.default_rng(seed), []
        for i in range(frames):
            frame = scene(movers_at(i, rng), noise=noise, seed=seed * 1000 + i, frame_id=i,
                          start_us=start + i * self.PERIOD_US)
            result = pipe.process(frame, DEFAULT_SETTINGS)
            self.assertEqual(result["stage_errors"], {})
            out.append(result["products"]["tracks"])
        return out

    def walker(self, i, rng, speed=0.8, start_bin=9.0, angle=15.0):
        """Approaching point target with a fluctuating (Rayleigh) echo: about a third of
        frames fall below the detection threshold on their own."""
        cal = load_calibration()
        k = start_bin - speed * i * self.PERIOD_US / 1e6 / cal["range"]["m_per_bin"]
        dop = -2 * speed / cal["wavelength_m"] / self.HZ_PER_BIN
        return [(k, dop, angle, 2.2 * abs(rng.standard_normal() + 1j * rng.standard_normal()) / np.sqrt(2))]

    def test_fluctuating_walker_is_one_continuous_track(self):
        frames = self.run_frames(self.walker, 45)
        cal = load_calibration()
        seen = [f["tracks"] for f in frames]
        first = next(i for i, t in enumerate(seen) if t)
        self.assertLessEqual(first, 8)  # Three detections within five frames, despite fades.
        ids = {t["id"] for tracks in seen for t in tracks}
        self.assertEqual(len(ids), 1, ids)
        self.assertTrue(all(len(t) == 1 for t in seen[first:]), [len(t) for t in seen])
        end = seen[-1][0]
        expected = cal["range"]["m_per_bin"] * (9.0 - 0.8 * 44 * .089 / cal["range"]["m_per_bin"]) + cal["range"]["offset_m"]
        self.assertAlmostEqual(end["range_m"], expected, delta=0.25)
        self.assertAlmostEqual(np.mean([t[0]["angle_deg"] for t in seen[first:]]), 15, delta=3)
        self.assertAlmostEqual(end["range_rate_mps"], -0.8, delta=0.2)
        self.assertAlmostEqual(end["doppler_mps"], -0.8, delta=0.1)
        self.assertFalse(end["in_place"])
        self.assertTrue(any(t["coasting"] for tracks in seen[first:] for t in tracks))  # Misses were bridged.

    def test_noise_alone_confirms_no_tracks(self):
        frames = self.run_frames(lambda i, rng: [], 25, seed=3)
        self.assertEqual([t for f in frames for t in f["tracks"]], [])

    def fan_and_walker(self, i, rng):
        # A fan: fixed position, alternating Doppler sign, plus the walker elsewhere.
        return [(3.0, 8.0 if i % 2 else -8.0, -40.0, 3.0)] + self.walker(i, rng, start_bin=10.0, angle=20.0)

    def test_doppler_without_range_change_is_in_place(self):
        cal = load_calibration()
        cal["detection"]["clutter_tau_s"] = 0   # Tracker behaviour alone.
        last = self.run_frames(self.fan_and_walker, 30, seed=5, calibration=cal)[-1]["tracks"]
        fan = [t for t in last if t["range_m"] < 2.6]
        walk = [t for t in last if t["range_m"] >= 2.6]
        self.assertEqual((len(fan), len(walk)), (1, 1), last)
        self.assertTrue(fan[0]["in_place"])
        self.assertAlmostEqual(fan[0]["range_rate_mps"], 0, delta=0.1)
        self.assertFalse(walk[0]["in_place"])

    def test_clutter_map_learns_the_fan_but_not_the_walker(self):
        self.assertGreater(load_calibration()["detection"]["clutter_tau_s"], 0)
        frames = self.run_frames(self.fan_and_walker, 70, seed=5)
        fan = [[t for t in f["tracks"] if t["angle_deg"] < 0] for f in frames]      # Fan at -40 deg.
        walker = [[t for t in f["tracks"] if t["angle_deg"] >= 0] for f in frames]  # Walker at +20 deg.
        self.assertTrue(any(fan[:20]))       # Visible at first...
        self.assertFalse(any(fan[-20:]))     # ...then learned as clutter.
        self.assertTrue(all(len(w) == 1 for w in walker[10:]), [len(w) for w in walker])
        self.assertEqual(len({w[0]["id"] for w in walker[10:]}), 1)
        self.assertTrue(frames[0]["clutter_learning"])
        self.assertAlmostEqual(frames[-1]["clutter_age_s"], 69 * self.PERIOD_US / 1e6 + 0.1, delta=0.01)

    def test_time_gap_or_restart_clears_tracks(self):
        cal = load_calibration()
        cal["detection"]["clutter_tau_s"] = 0   # A fixed mover would be learned as clutter.
        pipe = Pipeline(cal)
        def frame(i, start):
            return scene([(6.0, 5.0, 0.0, 3.0)], noise=40, seed=i, frame_id=i, start_us=start)
        for i in range(6):
            tracks = pipe.process(frame(i, 1000 + i * self.PERIOD_US), DEFAULT_SETTINGS)["products"]["tracks"]
        self.assertEqual(len(tracks["tracks"]), 1)
        first_id = tracks["tracks"][0]["id"]
        tracks = pipe.process(frame(6, 1000 + 5 * self.PERIOD_US + 2_000_000), DEFAULT_SETTINGS)["products"]["tracks"]
        self.assertEqual(tracks["tracks"], [])  # Gap over max_gap_s: start again.
        for i in range(7, 12):
            tracks = pipe.process(frame(i, 3_000_000 + i * self.PERIOD_US), DEFAULT_SETTINGS)["products"]["tracks"]
        self.assertNotEqual(tracks["tracks"][0]["id"], first_id)


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

    def test_state_long_poll_returns_on_new_frame_or_timeout(self):
        viewer = server.Viewer()
        version = viewer.state()["version"]
        started = time.monotonic()
        self.assertNotIn("frame", viewer.state(version, 0.2))      # Nothing new: waits, then no frame.
        self.assertGreaterEqual(time.monotonic() - started, 0.15)

        def publish():
            time.sleep(0.05)
            with viewer.lock:
                viewer.latest = {"frame_id": 7}
                viewer.version += 1
                viewer.changed.notify_all()
        threading.Thread(target=publish).start()
        started = time.monotonic()
        state = viewer.state(version, 5.0)
        self.assertLess(time.monotonic() - started, 2.0)            # Returned on the new frame.
        self.assertEqual(state["frame"], {"frame_id": 7})
        self.assertEqual(state["version"], version + 1)

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
        self.fail_registers = set()   # Writes to these reply "bus error".
        self.initial = dict(self.registers)

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
        values, status = [], 0
        if op == 1:
            values = [self.registers[reg + n] for n in range(count)]
        elif op == 2 and reg in self.fail_registers:
            status = 1
        elif op == 2:
            self.registers[reg] = value
            self.generation += 1
            values = [value]
        elif op == 3:   # Re-init: the build profile again.
            self.registers = dict(self.initial)
            self.generation += 1
        with self.lock:
            self.outgoing += control_reply(tag, op, status, reg, self.generation, values)
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
            self.wait(lambda: len(viewer.register_state()["values"]) == 12)  # Plus the 0x56 read.
            # commands[0] is the rise-step read every live connection makes.
            self.assertEqual(device.commands[0][:3], (1, 0x56, 1))
            self.assertEqual([c[1:3] for c in device.commands[2:]], [(0x60, 4), (0x64, 4), (0x68, 2)])
            state = viewer.register_state()
            self.assertEqual(state["values"]["53"]["value"], 0xBEEF)
            self.assertEqual(state["values"]["61"]["value"], 0x1061)
            self.assertEqual(state["generation"], 1)
            self.assertEqual(state["pending"] + state["timed_out"], 0)
            self.assertEqual([e["status"] for e in state["log"]], ["ok"] * 5)
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


class SweepTests(unittest.TestCase):
    wait = RegisterControlTests.wait

    def live(self, device):
        viewer = server.Viewer()
        with patch.object(server, "usb_ports", return_value=["COM30"]), \
                patch.object(server.serial, "Serial", return_value=device):
            viewer.connect(port="COM30")
        self.wait(lambda: "56" in viewer.register_state()["values"])
        return viewer

    def test_out_of_band_needs_acknowledgement_timer_and_live_usb(self):
        viewer = server.Viewer()
        with self.assertRaises(ValueError):
            viewer.set_sweep(1000, 5, True)   # Not connected.
        viewer.status, viewer.transport = "live", FakeDevice()
        for args in ((1000, 5, False), (1000, 0, True), (1000, 31, True), (1000, "5", True), (300, 5, True)):
            with self.assertRaises(ValueError):
                viewer.set_sweep(*args)
        self.assertIsNone(viewer.sweep)

    def test_sweep_uses_minimum_power_scales_range_and_reverts_on_timer(self):
        device = FakeDevice()
        viewer = self.live(device)
        try:
            viewer.set_sweep(1000, 1, True)
            self.wait(lambda: viewer.sweep_state()["active"]["phase"] == "active")
            writes = [(c[1], c[3]) for c in device.commands if c[0] == 2]
            self.assertEqual(writes, server.sweep_writes(83))
            self.assertEqual(writes[:2], [(0x6D, 0x9740), (0x70, 0x26A0)])   # Power down first.
            self.assertEqual(device.registers[0x56], 83)
            state = viewer.sweep_state()
            self.assertFalse(state["in_band"])
            self.assertEqual((state["active"]["mhz"], state["active"]["top_ghz"]), (1000, 25.002))
            self.assertGreater(state["active"]["remaining_s"], 50)
            # Frames carry the live step, so range bins are scaled for the wider sweep.
            self.wait(lambda: viewer.latest and viewer.latest.get("products", {}).get("targets", {}).get("sweep_step") == 83)
            cal = load_calibration()["range"]
            self.assertAlmostEqual(viewer.latest["products"]["targets"]["m_per_bin"], cal["m_per_bin"] * 20 / 83, places=4)
            viewer.sweep["until"] = time.monotonic() - 1      # The user's timer runs out.
            self.wait(lambda: viewer.sweep is None)
            self.assertEqual(device.commands[-1][0], 3)
            self.assertEqual(device.registers, device.initial)
            self.assertEqual(viewer.sweep_state()["last"]["reason"], "revert timer")
            self.assertTrue(viewer.sweep_state()["in_band"])
        finally:
            viewer.disconnect()

    def test_failed_write_restore_and_disconnect_all_return_in_band(self):
        device = FakeDevice()
        viewer = self.live(device)
        try:
            device.fail_registers = {0x58}
            viewer.set_sweep(2000, 5, True)
            self.wait(lambda: viewer.sweep is None)
            self.assertEqual(viewer.sweep_last["reason"], "a sweep register write failed")
            self.assertEqual(device.registers, device.initial)
            device.fail_registers = set()
            viewer.set_sweep(480, 5, True)
            self.wait(lambda: viewer.sweep_state()["active"]["phase"] == "active")
            viewer.set_sweep(240)                               # Restore in band now.
            self.wait(lambda: viewer.sweep is None)
            self.assertEqual(viewer.sweep_last["reason"], "restored by user")
            viewer.set_sweep(1000, 5, True)
            self.wait(lambda: viewer.sweep_state()["active"]["phase"] == "active")
        finally:
            viewer.disconnect()
        self.assertEqual(device.commands[-1][0], 3)               # Re-init before the port closed.
        self.assertEqual(device.registers, device.initial)
        self.assertEqual(viewer.sweep_last["reason"], "viewer disconnected")


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
