"""Radar register bit-flip sweep through the live viewer, with per-receiver metrics.

For each register: read the original value, then for each bit mask XOR it in,
capture frames tagged with the new register generation, measure, and restore.
If the stream stops, REINIT and re-write the original value. Results are
appended as JSON lines. The viewer must be connected live to the
register-control firmware; it is the only path used (no direct port access).

Metrics per receiver (static scene assumed): DC offset of I and Q, AC level of
I and Q, mirror image factor alpha fitted as X(-k) = alpha * conj(X(k)) over
bins 2-12 of the drift-removed coherent mean chirp, level of bins 4-5, the
non-coherent noise floor over bins 100-199, the chirp-to-chirp change over bins
8-40 and the observed radar frame period.

Example:
    python tools/register_sweep.py --out output/live_radar/sweep.jsonl 65 66 67
    python tools/register_sweep.py --relatch --bits all --confirm --out output/live_radar/sweep.jsonl 00-7F
"""
import argparse
import base64
import json
import time
import urllib.request
from pathlib import Path

import numpy as np

LIMITS = dict(dc_i=150, dc_q=150, ac_i_db=0.5, ac_q_db=0.5, image_db=0.7, image_deg=4,
              refl_db=0.7, noise_db=1.0, chirp_noise_db=1.0)
PERIOD_LIMIT = 0.02  # relative change in observed radar frame period


class Viewer:
    def __init__(self, url):
        self.url = url
        self.token = json.load(urllib.request.urlopen(url + "/api/options"))["token"]

    def post(self, path, body):
        req = urllib.request.Request(self.url + "/api/" + path, json.dumps(body).encode(),
                                     {"Content-Type": "application/json", "X-Viewer-Token": self.token,
                                      "Origin": self.url})
        return json.load(urllib.request.urlopen(req))

    def state(self, since=0):
        return json.load(urllib.request.urlopen(f"{self.url}/api/state?since={since}"))

    def reply(self, tag, timeout=8):
        end = time.time() + timeout
        while time.time() < end:
            for entry in self.state()["registers"]["log"]:
                if entry["tag"] == tag:
                    return entry
            time.sleep(.03)
        return None

    def write(self, reg, value):
        return self.reply(self.post("register/write", {"register": reg, "value": value})["tags"][0])

    def read(self, reg):
        entry = self.reply(self.post("register/read", {"register": reg, "count": 1})["tags"][0])
        return entry["values"][0] if entry and entry["status"] == "ok" and entry["values"] else None

    def reinit(self, attempts=3):
        # A re-init has failed once with an I2C NACK and succeeded on retry (2026-10-08).
        for _ in range(attempts):
            entry = self.reply(self.post("register/reinit", {})["tags"][0], timeout=10)
            time.sleep(2)
            if entry and entry["status"] == "ok":
                break
        return entry

    def capture(self, generation, frames_wanted=14, settle=0.4, timeout=6):
        time.sleep(settle)
        frames, version, end = [], -1, time.time() + timeout
        while time.time() < end and len(frames) < frames_wanted:
            s = self.state(version)
            version = s["version"]
            f = s.get("frame")
            if f and f["register_generation"] == generation and (not frames or f["frame_id"] != frames[-1]["frame_id"]):
                frames.append(f)
            time.sleep(.06)
        if len(frames) < 4:
            return None
        # Observed radar frame period: frame IDs count skipped frames too.
        ids = np.array([f["frame_id"] for f in frames], float)
        us = np.array([f["started_us"] for f in frames], float)
        steps = np.diff(ids)
        self.frame_period_us = float(np.median(np.diff(us)[steps > 0] / steps[steps > 0])) if (steps > 0).any() else None
        return np.array([np.frombuffer(base64.b64decode(f["iq_base64"]), "<i2").reshape(f["iq_shape"])
                         for f in frames])

    def relatch(self):
        """Hold and restart the sweep generator (0x40 bit 14) so waveform/timing writes take effect."""
        reply = None
        for value in (0x4207, 0x0207):
            reply = self.write(0x40, value)
            if not reply or reply["status"] != "ok":
                return None
        return reply


def metrics(iq):
    iq = iq.astype(float)
    n = np.arange(512) - 255.5
    w = np.hanning(512)
    out = {}
    for rx in range(2):
        I, Q = iq[:, rx, ..., 0], iq[:, rx, ..., 1]
        z = (I + 1j * Q).mean(axis=(0, 1))
        zc = z - z.mean()
        zc = zc - (zc @ n / (n @ n)) * n
        X = np.fft.fft(zc * w) / w.sum()
        k = np.arange(2, 13)
        alpha = np.sum(X[-k] * X[k]) / np.sum(np.abs(X[k]) ** 2)
        zz = I + 1j * Q
        zz = zz - zz.mean(axis=-1, keepdims=True)
        P = np.abs(np.fft.fft(zz * w, axis=-1) / w.sum()) ** 2
        Ic = I - I.mean(axis=-1, keepdims=True)
        Qc = Q - Q.mean(axis=-1, keepdims=True)
        # Chirp-to-chirp change in the near-range bins: transmitter-correlated noise
        # (it tracks TX power 1:1 at stock) plus any motion.
        d = np.diff(zz, axis=1)
        D = np.abs(np.fft.fft(d * w, axis=-1) / w.sum()) ** 2 / 2
        out[f"rx{rx + 1}"] = dict(
            dc_i=round(float(I.mean()), 1), dc_q=round(float(Q.mean()), 1),
            ac_i_db=round(float(10 * np.log10((Ic ** 2).mean() + 1e-12)), 2),
            ac_q_db=round(float(10 * np.log10((Qc ** 2).mean() + 1e-12)), 2),
            image_db=round(float(20 * np.log10(abs(alpha) + 1e-12)), 2),
            image_deg=round(float(np.degrees(np.angle(alpha))), 1),
            refl_db=round(float(20 * np.log10(abs(X[4]) + abs(X[5]) + 1e-9)), 2),
            noise_db=round(float(10 * np.log10(P[..., 100:200].mean() + 1e-12)), 2),
            chirp_noise_db=round(float(10 * np.log10(D[..., 8:41].mean() + 1e-12)), 2),
            peak_abs=int(np.abs(iq[:, rx]).max()))
    return out


def changes(ref, m):
    flagged = {}
    for rx in ("rx1", "rx2"):
        for key, limit in LIMITS.items():
            d = m[rx][key] - ref[rx][key]
            if abs(d) > limit:
                flagged[f"{rx}.{key}"] = round(d, 2)
    if ref.get("frame_period_us") and m.get("frame_period_us"):
        rel = m["frame_period_us"] / ref["frame_period_us"] - 1
        if abs(rel) > PERIOD_LIMIT:
            flagged["frame_period"] = round(rel, 3)
    return flagged


def parse_masks(text):
    if text == "all":
        return [1 << b for b in range(16)]
    return [int(x, 16) for x in text.split(",")]


def parse_registers(items):
    regs = []
    for item in items:
        if "-" in item:
            lo, hi = (int(x, 16) for x in item.split("-"))
            regs.extend(range(lo, hi + 1))
        else:
            regs.append(int(item, 16))
    return regs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("registers", nargs="+", help="hex register addresses or ranges such as 05-17")
    ap.add_argument("--out", type=Path, required=True, help="JSON-lines result file (appended)")
    ap.add_argument("--bits", default="0001,0010,0100,1000", help="comma-separated hex XOR masks, or 'all' for 16 single bits")
    ap.add_argument("--exclude", nargs="*", default=[], help="hex registers or ranges to skip")
    ap.add_argument("--relatch", action="store_true",
                    help="hold/restart the sweep generator (0x40) after each write and restore; "
                         "required for waveform/timing registers to take effect")
    ap.add_argument("--frames", type=int, default=14, help="frames captured per test")
    ap.add_argument("--rereference", type=int, default=0, help="new stock reference every N tests (0: once)")
    ap.add_argument("--confirm", action="store_true", help="repeat flagged tests once at the end")
    ap.add_argument("--url", default="http://127.0.0.1:8765")
    ap.add_argument("--reference-register", default="5b", help="benign register rewritten to mark a stock generation")
    a = ap.parse_args()
    viewer = Viewer(a.url)
    masks = parse_masks(a.bits)
    excluded = set(parse_registers(a.exclude))
    registers = [r for r in parse_registers(a.registers) if r not in excluded and r != 0x40]
    a.out.parent.mkdir(parents=True, exist_ok=True)

    def log(entry):
        entry["at"] = time.time()
        with a.out.open("a") as fh:
            fh.write(json.dumps(entry) + "\n")
        print(json.dumps({k: v for k, v in entry.items() if k != "metrics"}), flush=True)

    ref_reg = int(a.reference_register, 16)
    ref_value = viewer.read(ref_reg)

    def take_reference(frames):
        reply = viewer.relatch() if a.relatch else viewer.write(ref_reg, ref_value)
        iq = viewer.capture(reply["generation"], frames_wanted=frames)
        if iq is None:
            return None
        m = metrics(iq)
        m["frame_period_us"] = viewer.frame_period_us
        return m

    def run_test(reg, original, mask, ref):
        value = original ^ mask
        entry = dict(kind="test", reg=f"0x{reg:02X}", original=f"0x{original:04X}", value=f"0x{value:04X}",
                     mask=f"0x{mask:04X}", relatch=a.relatch)
        reply = viewer.write(reg, value)
        if reply and reply["status"] == "ok" and a.relatch:
            reply = viewer.relatch()
        if not reply or reply["status"] != "ok":
            entry.update(result="write failed", detail=reply and reply["status"])
            iq = None
        else:
            back = viewer.read(reg)
            entry["readback"] = None if back is None else f"0x{back:04X}"
            iq = viewer.capture(reply["generation"], frames_wanted=a.frames)
            if iq is None:
                entry["result"] = "stream stopped"
            else:
                m = metrics(iq)
                m["frame_period_us"] = viewer.frame_period_us
                entry.update(result="ok", changes=changes(ref, m), metrics=m)
        restore = viewer.write(reg, original)
        if restore and restore["status"] == "ok" and a.relatch:
            restore = viewer.relatch()
        if iq is None or not restore or restore["status"] != "ok":
            recovered = viewer.reinit()
            viewer.write(reg, original)
            entry["recovered_by_reinit"] = bool(recovered and recovered["status"] == "ok")
            entry["after_recovery"] = "stream ok" if take_reference(6) is not None else "STREAM STILL STOPPED"
        return entry

    ref = take_reference(28)
    log(dict(kind="reference", metrics=ref))
    flagged, count = [], 0
    for reg in registers:
        original = viewer.read(reg)
        if original is None:
            log(dict(kind="unreadable", reg=f"0x{reg:02X}"))
            continue
        for mask in masks:
            if a.rereference and count and count % a.rereference == 0:
                ref = take_reference(14) or ref
                log(dict(kind="reference", metrics=ref))
            count += 1
            entry = run_test(reg, original, mask, ref)
            log(entry)
            if entry.get("result") != "ok" or entry.get("changes"):
                flagged.append((reg, original, mask))
    if a.confirm and flagged:
        ref = take_reference(28) or ref
        log(dict(kind="reference", metrics=ref, confirm=True))
        for reg, original, mask in flagged:
            entry = run_test(reg, original, mask, ref)
            entry["kind"] = "confirm"
            log(entry)
    viewer.reinit()
    log(dict(kind="done", tests=count, flagged=len(flagged)))


if __name__ == "__main__":
    main()
