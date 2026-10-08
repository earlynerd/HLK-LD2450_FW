"""Check the BR23 hardware FFT self-test output (PA9 log) against NumPy.

The firmware (target/br23/image/fft_selftest.c, --fft-selftest builds) prints
FFTSELF summary lines and FFTD word dumps at start-up. This script regenerates
the identical pseudo-random inputs, computes reference transforms and, for each
case, fits the dump to the reference under several candidate layouts. It reports
the best layout, the complex gain (scale) and the residual error.

Example:
    python firmware/tools/fft_selftest_check.py output/fft_selftest/pa9.txt
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np

SENTINEL = 0x5A5A5A5A


def lcg_values(seed, count, full_scale):
    state, out = seed, []
    for _ in range(count):
        state = (state * 1103515245 + 12345) & 0xFFFFFFFF
        top = state >> 16
        out.append((top - 65536 if top & 0x8000 else top) if full_scale else (top & 0x3FFF) - 8192)
    return np.array(out, dtype=np.int64)


def parse(text):
    summary, dumps = {}, {}
    for line in text.splitlines():
        m = re.match(r"FFTSELF (\S+) (.*)", line.strip())
        if m:
            fields = dict(re.findall(r"(\w+)=(-?\w+)", m.group(2)))
            summary.setdefault(m.group(1), {}).update(fields)
            continue
        m = re.match(r"FFTD (\S+) ([0-9a-f]+)((?: [0-9a-f]{8})+)", line.strip())
        if m:
            words = [int(w, 16) for w in m.group(3).split()]
            dumps.setdefault(m.group(1), {})[int(m.group(2), 16)] = words
    arrays = {}
    for name, rows in dumps.items():
        flat = []
        for start in sorted(rows):
            if start != len(flat):
                raise ValueError(f"{name}: dump gap at {start:#x}")
            flat += rows[start]
        arrays[name] = np.array(flat, dtype=np.uint32)
    return summary, arrays


def signed(words):
    return words.astype(np.int64) - ((words.astype(np.int64) & 0x80000000) << 1)


def written(words):
    idx = np.nonzero(words != SENTINEL)[0]
    return int(idx[-1]) + 1 if len(idx) else 0


def bitrev(n):
    bits = n.bit_length() - 1
    return np.array([int(f"{i:0{bits}b}"[::-1], 2) for i in range(n)])


def fit(y, ref):
    """Least-squares complex gain g with y ~ g*ref; returns (g, relative residual dB)."""
    g = np.vdot(ref, y) / np.vdot(ref, ref)
    res = np.sum(np.abs(y - g * ref) ** 2) / max(np.sum(np.abs(y) ** 2), 1e-30)
    return g, 10 * np.log10(max(res, 1e-30))


def best(y, x, n, inverse=False):
    """Try candidate output conventions; return sorted (residual_dB, name, gain)."""
    f = (lambda v: np.fft.ifft(v) * n) if inverse else np.fft.fft
    refs = {"natural": f(x), "conjugate": np.conj(f(x)), "bitrev": f(x)[bitrev(n)],
            "swapped-iq-input": f(x.imag + 1j * x.real), "swapped-iq-output": None}
    out = []
    for name, ref in refs.items():
        yy = y.imag + 1j * y.real if name == "swapped-iq-output" else y
        r = f(x) if ref is None else ref
        g, err = fit(yy, r)
        out.append((round(float(err), 1), name, g))
    return sorted(out, key=lambda t: t[0])


def describe(g):
    return dict(gain_abs=float(abs(g)), gain_log2=round(float(np.log2(abs(g))), 3) if abs(g) else None,
                gain_phase_deg=round(float(np.degrees(np.angle(g))), 2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", type=Path)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    summary, arrays = parse(a.log.read_text(errors="replace"))
    report = dict(summary=summary, cases={})

    def complex_case(name, seed, n, full_scale=False, inverse_of=None):
        if name not in arrays:
            return
        words = arrays[name]
        y = signed(words[:2 * n])
        y = y[0::2] + 1j * y[1::2]
        if inverse_of is not None:
            x = inverse_of
        else:
            v = lcg_values(seed, 2 * n, full_scale)
            x = v[0::2] + 1j * v[1::2]
        ranked = best(y, x, n, inverse=inverse_of is not None)
        err, layout, g = ranked[0]
        report["cases"][name] = dict(points=n, words_written=written(words), best_layout=layout,
                                    residual_db=err, alternatives={r[1]: r[0] for r in ranked[1:]},
                                    max_abs_output=int(np.max(np.abs(signed(words[:2 * n])))), **describe(g))

    complex_case("C512", 1, 512)
    complex_case("C512F", 7, 512, full_scale=True)
    complex_case("C256", 3, 256)
    if "C512" in arrays:
        y = signed(arrays["C512"][:1024])
        complex_case("I512", None, 512, inverse_of=y[0::2] + 1j * y[1::2])
    if "IMP" in arrays:
        y = signed(arrays["IMP"])
        report["cases"]["IMP"] = dict(first_words=[int(v) for v in y[:16]], note="input: 16384 at sample 0")
    if "R512" in arrays:
        words = arrays["R512"]
        n_written = written(words)
        x = lcg_values(5, 512, False).astype(float)
        y = signed(words[:max(n_written, 2)])
        y = y[0::2] + 1j * y[1::2]
        ref = np.fft.rfft(x)
        cands = {}
        for name, r in (("rfft-n/2+1", ref), ("rfft-n/2", ref[:256]), ("full-fft-first-half", np.fft.fft(x)[:len(y)])):
            m = min(len(y), len(r))
            if m:
                g, err = fit(y[:m], r[:m])
                cands[name] = (round(float(err), 1), describe(g))
        # Packed real FFT: bin 0 real = DC, bin 0 imag = Nyquist (common convention).
        if len(y) >= 256:
            packed = ref[:256].copy()
            packed[0] = ref[0].real + 1j * ref[256].real
            g, err = fit(y[:256], packed)
            cands["packed-dc-nyquist"] = (round(float(err), 1), describe(g))
        report["cases"]["R512"] = dict(words_written=n_written, candidates=cands)
    text = json.dumps(report, indent=1, default=str)
    print(text)
    if a.json:
        a.json.write_text(text + "\n")


if __name__ == "__main__":
    main()
