"""Radar register bit-flip sweep through the live viewer, with per-receiver metrics.

For each register: read the original value, then for each bit mask XOR it in,
capture frames tagged with the new register generation, measure, and restore.
If the stream stops, REINIT and re-write the original value. Results are
appended as JSON lines. The viewer must be connected live to the
register-control firmware; it is the only path used (no direct port access).

Metrics per receiver (static scene assumed): DC offset of I and Q, AC level of
I and Q, mirror image factor alpha fitted as X(-k) = alpha * conj(X(k)) over
bins 2-12 of the drift-removed coherent mean chirp, level of bins 4-5, and the
non-coherent noise floor over bins 100-199.

Example:
    python tools/register_sweep.py --out output/live_radar/sweep.jsonl 65 66 67
"""
import argparse
import base64
import json
import time
import urllib.request
from pathlib import Path

import numpy as np

LIMITS = dict(dc_i=150, dc_q=150, ac_i_db=0.5, ac_q_db=0.5, image_db=0.7, image_deg=4,
              refl_db=0.7, noise_db=1.0)


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

    def reinit(self):
        entry = self.reply(self.post("register/reinit", {})["tags"][0], timeout=10)
        time.sleep(2)
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
        return np.array([np.frombuffer(base64.b64decode(f["iq_base64"]), "<i2").reshape(f["iq_shape"])
                         for f in frames])


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
        out[f"rx{rx + 1}"] = dict(
            dc_i=round(float(I.mean()), 1), dc_q=round(float(Q.mean()), 1),
            ac_i_db=round(float(10 * np.log10((Ic ** 2).mean() + 1e-12)), 2),
            ac_q_db=round(float(10 * np.log10((Qc ** 2).mean() + 1e-12)), 2),
            image_db=round(float(20 * np.log10(abs(alpha) + 1e-12)), 2),
            image_deg=round(float(np.degrees(np.angle(alpha))), 1),
            refl_db=round(float(20 * np.log10(abs(X[4]) + abs(X[5]) + 1e-9)), 2),
            noise_db=round(float(10 * np.log10(P[..., 100:200].mean() + 1e-12)), 2),
            peak_abs=int(np.abs(iq[:, rx]).max()))
    return out


def changes(ref, m):
    flagged = {}
    for rx in ("rx1", "rx2"):
        for key, limit in LIMITS.items():
            d = m[rx][key] - ref[rx][key]
            if abs(d) > limit:
                flagged[f"{rx}.{key}"] = round(d, 2)
    return flagged


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("registers", nargs="+", help="hex register addresses")
    ap.add_argument("--out", type=Path, required=True, help="JSON-lines result file (appended)")
    ap.add_argument("--bits", default="0001,0010,0100,1000", help="comma-separated hex XOR masks")
    ap.add_argument("--url", default="http://127.0.0.1:8765")
    ap.add_argument("--reference-register", default="5b", help="benign register rewritten to mark a stock generation")
    a = ap.parse_args()
    viewer = Viewer(a.url)
    masks = [int(x, 16) for x in a.bits.split(",")]
    a.out.parent.mkdir(parents=True, exist_ok=True)

    def log(entry):
        entry["at"] = time.time()
        with a.out.open("a") as fh:
            fh.write(json.dumps(entry) + "\n")
        print(json.dumps({k: v for k, v in entry.items() if k != "metrics"}), flush=True)

    ref_reg = int(a.reference_register, 16)
    ref_value = viewer.read(ref_reg)
    ref = metrics(viewer.capture(viewer.write(ref_reg, ref_value)["generation"], frames_wanted=28))
    log(dict(kind="reference", metrics=ref))
    for reg in (int(x, 16) for x in a.registers):
        original = viewer.read(reg)
        if original is None:
            log(dict(kind="unreadable", reg=f"0x{reg:02X}"))
            continue
        for mask in masks:
            value = original ^ mask
            entry = dict(kind="test", reg=f"0x{reg:02X}", original=f"0x{original:04X}", value=f"0x{value:04X}",
                         mask=f"0x{mask:04X}")
            reply = viewer.write(reg, value)
            if not reply or reply["status"] != "ok":
                entry.update(result="write failed", detail=reply and reply["status"])
                log(entry)
                continue
            back = viewer.read(reg)
            entry["readback"] = None if back is None else f"0x{back:04X}"
            iq = viewer.capture(reply["generation"])
            if iq is None:
                entry["result"] = "stream stopped"
            else:
                m = metrics(iq)
                entry.update(result="ok", changes=changes(ref, m), metrics=m)
            restore = viewer.write(reg, original)
            if iq is None or not restore or restore["status"] != "ok":
                recovered = viewer.reinit()
                viewer.write(reg, original)
                entry["recovered_by_reinit"] = bool(recovered and recovered["status"] == "ok")
                check = viewer.capture(viewer.write(ref_reg, ref_value)["generation"], frames_wanted=6)
                entry["after_recovery"] = "stream ok" if check is not None else "STREAM STILL STOPPED"
            log(entry)
    viewer.reinit()
    log(dict(kind="done"))


if __name__ == "__main__":
    main()
