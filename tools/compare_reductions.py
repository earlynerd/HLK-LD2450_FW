"""Compare candidate on-device data reductions against full raw processing.

Each option turns a 512-sample complex chirp into fewer values, as firmware or
the radar chip could. Every option is evaluated in the DFT domain on the bins
we intend to keep (|bin| <= --keep), against the full 512-point DFT of the raw
chirp:

  fir-D[:L] centred, circular L-tap (odd, default 49) FIR low-pass with Q15
            coefficients, then every D-th sample; int16 output. Circular
            indexing keeps the result exactly describable in the DFT domain.
  skip-D    keep every D-th sample (the chip's larger raw sample step if it
            simply drops samples).
  avg-D     average each D consecutive samples (the step if it boxcar-filters).
  fftsel    512-point FFT, export only the kept bins as int16 after a fixed
            right shift (hardware-FFT bin selection; the engine's real scaling
            is unmeasured, so --fft-shift is a parameter).

Metrics (dB, lower is better unless noted), per receiver then averaged:
  static_err   coherent mean chirp spectrum error relative to the reference
  change_err   chirp-to-chirp change error relative to the reference change
               (motion plus noise; what Doppler and motion detection see)
  noise_delta  chirp-to-chirp power in the outer kept bins minus the
               reference (positive = the option adds noise/aliases there)
  doppler_err  16-chirp Hann Doppler map error over |bin| <= --doppler-bins
  bytes/frame  I/Q payload for a full 64-chirp, two-receiver frame

Example:
    python tools/compare_reductions.py output/live_radar/20261008-011009-capture-d25c19/stream.ldf
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "firmware/tools"))
import frame_stream as fs  # noqa: E402

N = 512


def load(path, limit):
    parser, frames, out = fs.Parser(), fs.Frames(), []
    with open(path, "rb") as f:
        while len(out) < limit:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            for m in parser.feed(chunk):
                fr = frames.accept(m)
                if fr:
                    out.append(fr)
    iq = np.stack([np.stack([np.frombuffer(l, ">i2").reshape(fr["chirps"], 1028)[:, 2:-2].reshape(-1, N, 2)
                             for l in fr["lanes"]]) for fr in out]).astype(np.int64)
    return iq[..., 0] + 1j * iq[..., 1]               # frame, rx, chirp, sample


def q16(z):
    """Round to int16 I/Q with saturation; returns (values, clipped fraction)."""
    re, im = np.round(z.real), np.round(z.imag)
    clip = np.mean((np.abs(re) > 32767) | (np.abs(im) > 32767))
    return np.clip(re, -32768, 32767) + 1j * np.clip(im, -32768, 32767), float(clip)


def fir_taps(d, taps, keep):
    """Low-pass for decimation by d: pass to the kept band, stop before the first alias of it."""
    out_nyq = N / (2 * d)                           # output Nyquist in input bins
    pass_edge, stop_edge = keep, 2 * out_nyq - keep  # aliases land outside |k| <= keep
    h = signal.remez(taps, [0, pass_edge / N, stop_edge / N, 0.5], [1, 0], fs=1.0)
    return np.round(h * 32768) / 32768


def reduce(x, option, keep, fft_shift):
    """Return (Y bins aligned to reference bins -keep..keep scaled to the 512-point DFT, bytes per chirp, clip)."""
    kind, _, arg = option.partition("-")
    ks = np.arange(-keep, keep + 1)
    if kind == "fftsel":
        X = np.fft.fft(x, axis=-1) / 2 ** fft_shift
        Xq, clip = q16(X)
        return Xq[..., ks % N] * 2 ** fft_shift, len(ks) * 4, clip   # export exactly the kept bins
    d = int(arg.split(":")[0])
    m = N // d
    if kind == "fir":
        h = fir_taps(d, int(arg.split(":")[1]) if ":" in arg else 49, keep)
        # Zero-phase: centre the symmetric (odd-length) filter on sample 0, as
        # firmware does by indexing the circular record around each output.
        H = np.fft.fft(np.roll(np.pad(h, (0, N - len(h))), -(len(h) - 1) // 2))
        y = np.fft.ifft(np.fft.fft(x, axis=-1) * H, axis=-1)[..., ::d]
    elif kind == "skip":
        y = x[..., ::d]
    elif kind == "avg":
        y = x.reshape(*x.shape[:-1], m, d).mean(-1)
    else:
        raise ValueError(option)
    y, clip = q16(y)
    Y = np.fft.fft(y, axis=-1) * d                  # same bin spacing as the 512-point DFT
    return Y[..., ks % m], m * 4, clip


def metrics(X, Y, keep, doppler_bins):
    ks = np.arange(-keep, keep + 1)
    outer = np.abs(ks) >= keep // 2
    db = lambda a, b: 10 * np.log10(np.sum(np.abs(a) ** 2) / np.sum(np.abs(b) ** 2))
    out = {}
    for rx in range(X.shape[1]):
        Xr, Yr = X[:, rx], Y[:, rx]
        xs, ys = Xr.mean((0, 1)), Yr.mean((0, 1))
        dX, dY = np.diff(Xr, axis=1), np.diff(Yr, axis=1)
        w = np.hanning(Xr.shape[1])[None, :, None]
        dk = np.abs(ks) <= doppler_bins
        DX = np.fft.fft((Xr - Xr.mean(1, keepdims=True))[..., dk] * w, axis=1)
        DY = np.fft.fft((Yr - Yr.mean(1, keepdims=True))[..., dk] * w, axis=1)
        out[f"rx{rx + 1}"] = dict(
            static_err=round(db(ys - xs, xs), 1),
            change_err=round(db(dY - dX, dX), 1),
            noise_delta=round(10 * np.log10(np.mean(np.abs(dY[..., outer]) ** 2) / np.mean(np.abs(dX[..., outer]) ** 2)), 2),
            doppler_err=round(db(DY - DX, DX), 1))
    out["mean"] = {k: round(float(np.mean([out[r][k] for r in out])), 2) for k in out["rx1"]}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("streams", nargs="+", type=Path)
    ap.add_argument("--frames", type=int, default=200)
    ap.add_argument("--keep", type=int, default=40, help="kept bins |k| <= keep (240 MHz: 8 m is about bin 12)")
    ap.add_argument("--doppler-bins", type=int, default=16)
    ap.add_argument("--fft-shift", type=int, default=6, help="right shift applied before int16 bin export")
    ap.add_argument("--options", default="fir-4,fir-4:33,fir-8,skip-2,avg-2,skip-4,avg-4,fftsel")
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    report = {}
    for path in a.streams:
        x = load(path, a.frames)
        ks = np.arange(-a.keep, a.keep + 1)
        X = np.fft.fft(x, axis=-1)[..., ks % N]
        rows = {}
        print(f"\n{path} : {x.shape[0]} frames x {x.shape[2]} chirps, keep |bin| <= {a.keep}")
        print(f"{'option':12s} {'static':>7s} {'change':>7s} {'noise+':>7s} {'doppler':>8s} {'B/frame':>8s} {'clip%':>6s}")
        for opt in a.options.split(","):
            kind, _, arg = opt.partition("-")
            d = int(arg.split(":")[0]) if arg else 1
            if a.keep >= N // (2 * d):
                print(f"{opt:12s} skipped: keeps fewer than {a.keep} bins")
                continue
            Y, bpc, clip = reduce(x, opt, a.keep, a.fft_shift)
            m = metrics(X, Y, a.keep, a.doppler_bins)
            frame_bytes = bpc * 64 * 2
            rows[opt] = dict(m, bytes_per_frame=frame_bytes, clip_fraction=clip)
            mm = m["mean"]
            print(f"{opt:12s} {mm['static_err']:7.1f} {mm['change_err']:7.1f} {mm['noise_delta']:7.2f} "
                  f"{mm['doppler_err']:8.1f} {frame_bytes:8d} {100 * clip:6.3f}")
        report[str(path)] = rows
    if a.json:
        a.json.write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
