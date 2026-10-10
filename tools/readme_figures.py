"""Draw the README figures from live-viewer recordings, using the viewer's own processing.

    python tools/readme_figures.py --walk <capture folder> --still <capture folder> [--out resources]

A capture folder is what the viewer's Record button writes (output/live_radar/*-capture-*,
holding stream.ldf). Either recording may be left out.

walk:  one person walking towards and away from the sensor. Draws the micro-Doppler
       spectrogram (Doppler speed against time, summed over the detection range) above the
       range-time map (moving power per range bin).
still: one person sitting still, facing the sensor. Draws the slow-time displacement of the
       range bin the viewer's Auto chose most often. With --still-hold, a zoom of a breath
       hold below it shows the heartbeat, each beat marked. Each frame's newest
       displacement sample is kept; the viewer never revises samples, so this is exactly
       the trace the viewer drew.
"""
import argparse
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "firmware" / "tools"))
from frame_stream import Parser, Frames  # noqa: E402
from radar_viewer.processing import Pipeline, DEFAULT_SETTINGS  # noqa: E402

BG, FG, GRID = "#0f1115", "#d8dde6", "#2a2f3a"
ACCENT = "#ff9f43"


def frames(folder):
    parser, assembler = Parser(), Frames()
    with (Path(folder) / "stream.ldf").open("rb") as stream:
        while data := stream.read(1 << 16):
            for message in parser.feed(data):
                frame = assembler.accept(message)
                if frame is not None:
                    yield frame


def seconds(stamps_us):
    """Frame start times in s from the first frame (32-bit microsecond stamps wrap)."""
    steps = np.diff(np.asarray(stamps_us, dtype=np.int64)) & 0xffffffff
    return np.concatenate([[0.0], np.cumsum(steps) / 1e6])


def style(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=9)
    for side in ax.spines.values():
        side.set_color(GRID)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)


def edges(centres):
    """Cell edges for pcolormesh from (possibly uneven) cell centres."""
    c = np.asarray(centres, dtype=float)
    mid = (c[1:] + c[:-1]) / 2
    return np.concatenate([[c[0] - (mid[0] - c[0])], mid, [c[-1] + (c[-1] - mid[-1])]])


def walk(folder, out, steady=True):
    pipeline = Pipeline()
    stamps, doppler_rows, range_rows = [], [], []
    for frame in frames(folder):
        result = pipeline.process(frame, DEFAULT_SETTINGS)
        d = result["products"]["doppler"]
        rng = pipeline.cal["range"]
        lo, hi = d["fast_bins"]
        bins = np.arange(lo, hi + 1)
        top = int(np.ceil((pipeline.cal["detection"]["max_range_m"] - rng["offset_m"]) / rng["m_per_bin"]))
        shown = (bins >= 1) & (bins <= top)
        power = (10 ** (np.array(d["db"]) / 10)).sum(axis=0)[:, shown]   # Doppler x range, both receivers
        hz = np.array(d["hz"])
        moving = np.abs(hz) > 1.5 * (hz[1] - hz[0])    # Static removal leaves the zero row near empty.
        stamps.append(frame["started_us"])
        doppler_rows.append(power.sum(axis=1))
        range_rows.append(power[moving].sum(axis=0))
    if not stamps:
        raise SystemExit(f"{folder}: no frames")
    t = seconds(stamps)
    speed = hz * pipeline.cal["wavelength_m"] / 2 * pipeline.cal["velocity"]["sign"]
    metres = bins[shown] * rng["m_per_bin"] + rng["offset_m"]
    md = 10 * np.log10(np.array(doppler_rows).T + 1e-12)
    # Power falls as range^4; compensating it lets a far walker show as brightly as a near one.
    rt = 10 * np.log10(np.array(range_rows).T * metres[:, None] ** 4 + 1e-12)
    if steady:
        # Each row minus its median over the recording: removes lines that never change (fans),
        # the same job the viewer's clutter map does.
        md -= np.median(md, axis=1, keepdims=True)
        rt -= np.median(rt, axis=1, keepdims=True)

    fig, (a, b) = plt.subplots(2, 1, figsize=(10, 6.2), sharex=True, facecolor=BG,
                               gridspec_kw={"height_ratios": [1.5, 1]})
    a.pcolormesh(edges(t), edges(speed), md, cmap="inferno", vmin=md.max() - 40, vmax=md.max(),
                 shading="flat", rasterized=True)
    a.set_ylabel("Doppler speed (m/s)")
    a.set_title("Micro-Doppler: body and limbs of one person walking towards (negative) and away", fontsize=11)
    rt_lo, rt_hi = (0, 32) if steady else (rt.max() - 40, rt.max())
    b.pcolormesh(edges(t), edges(metres), rt, cmap="viridis", vmin=rt_lo, vmax=rt_hi,
                 shading="flat", rasterized=True)
    b.set_ylabel("Range (m)")
    b.set_xlabel("Time (s)")
    b.set_title("Range-time: moving power in each range bin (range^4 compensated)", fontsize=11)
    for ax in (a, b):
        style(ax)
    note = "; steady lines removed" if steady else ""
    fig.text(0.99, 0.005, "HLK-LD2450, custom firmware, 24.005-24.245 GHz; range scale not yet calibrated" + note,
             color="#7d8590", fontsize=7.5, ha="right", va="bottom")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    path = Path(out) / "walk_micro_doppler.png"
    fig.savefig(path, dpi=150, facecolor=BG)
    print(f"{path}: {len(t)} frames over {t[-1]:.1f} s")


def still(folder, out, range_bin=None, span=None, hold=None):
    pipeline = Pipeline()
    stamps, samples, auto = [], [], []
    for frame in frames(folder):
        phase = pipeline.process(frame, DEFAULT_SETTINGS)["products"].get("phase", {})
        if "disp_mm" not in phase:
            continue    # History still filling (first few seconds).
        stamps.append(frame["started_us"])
        samples.append([row[-1] for row in phase["disp_mm"]])
        auto.append(phase["auto_bin"])
        range_m, range_bins = phase["range_m"], phase["range_bins"]
    if len(stamps) < 50:
        raise SystemExit(f"{folder}: too few frames with a slow-time phase product")
    t = seconds(stamps)
    disp = np.array(samples)                       # frames x bins, as drawn live
    if span:
        # A stretch without posture shifts (steps of several mm that dwarf the breaths).
        keep = (t >= span[0]) & (t <= span[1])
        t, disp, auto = t[keep] - t[keep][0], disp[keep], [a for a, k in zip(auto, keep) if k]

    # The bin the viewer's Auto chose most often (most slow-time motion), unless one is given.
    if range_bin is None:
        range_bin = max(set(auto), key=auto.count)
    k = range_bins.index(range_bin)
    trace = disp[:, k] - np.median(disp[:, k])
    title = f"Chest motion of a seated person at {range_m[k]:.1f} m, from the slow-time phase of one range bin"
    if not hold:
        fig, a = plt.subplots(figsize=(10, 3.4), facecolor=BG)
        axes = [a]
    else:
        fig, axes = plt.subplots(2, 1, figsize=(10, 6.4), facecolor=BG, gridspec_kw={"height_ratios": [1, 1.1]})
        a, h = axes
    a.plot(t, trace, color=ACCENT, lw=1.3)
    a.set_xlim(t[0], t[-1])
    a.set_xlabel("Time (s)")
    a.set_ylabel("Displacement (mm)")
    a.set_title(title, fontsize=11)
    a.grid(color=GRID, lw=0.6)
    summary = ""
    if hold:
        a.axvspan(*hold, color="#3b4f7a", alpha=0.35, lw=0)
        a.text(np.mean(hold), a.get_ylim()[1] * 0.85, "breath held", color=FG, fontsize=9, ha="center")
        # The hold, with a cubic removed (the viewer's 10 s drift filter settling after the last
        # breath); beats are maxima of the 0.7-3 Hz band, each the highest within 0.3 s.
        m = (t >= hold[0]) & (t <= hold[1])
        th, x = t[m], trace[m]
        x = (x - np.polyval(np.polyfit(th, x, 3), th)) * 1000          # micrometres
        grid = np.arange(th[0], th[-1], 0.05)
        xg = np.interp(grid, th, x)
        f = np.fft.rfftfreq(len(xg), 0.05)
        band = np.fft.irfft(np.fft.rfft(xg) * ((f > 0.7) & (f < 3.0)), len(xg))
        gap = int(round(0.3 / 0.05))
        beats = [i for i in range(gap, len(band) - gap)
                 if band[i] == band[i - gap:i + gap + 1].max()]
        rate = 60 / np.median(np.diff(grid[beats]))
        # Mark each beat on the highest frame sample within 0.2 s of the band-passed maximum.
        marks = []
        for i in beats:
            near = np.flatnonzero(np.abs(th - grid[i]) <= 0.2)
            marks.append(near[np.argmax(x[near])])
        h.plot(th, x, color=ACCENT, lw=1.1)
        h.plot(th[marks], x[marks], "o", ms=6, mfc="none", mec=FG, mew=1.0)
        h.set_xlim(th[0], th[-1])
        h.set_xlabel("Time (s)")
        h.set_ylabel("Displacement (um)")
        h.set_title(f"Breath held: each circle is a heartbeat, about {rate:.0f} per minute", fontsize=11)
        h.grid(color=GRID, lw=0.6)
        summary = f", hold {hold[0]}-{hold[1]} s: {len(beats)} beats, {rate:.1f}/min, rms {x.std():.0f} um"
    for ax in axes:
        style(ax)
    fig.text(0.99, 0.005, "HLK-LD2450, custom firmware; as drawn live; "
             "1 mm of motion turns the phase by 58 deg at 24 GHz; sign uncalibrated",
             color="#7d8590", fontsize=7.5, ha="right", va="bottom")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    path = Path(out) / "breathing.png"
    fig.savefig(path, dpi=150, facecolor=BG)
    print(f"{path}: bin {range_bin} at {range_m[k]} m, {np.ptp(trace):.2f} mm peak to peak over {t[-1]:.1f} s"
          + summary)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--walk", type=Path, help="Capture folder: one person walking towards and away")
    ap.add_argument("--still", type=Path, help="Capture folder: one person sitting still")
    ap.add_argument("--still-bin", type=int, help="Range bin for --still (default: the viewer's Auto choice)")
    ap.add_argument("--still-span", type=float, nargs=2, metavar=("START", "END"),
                    help="Seconds of --still to draw (skip posture shifts)")
    ap.add_argument("--still-hold", type=float, nargs=2, metavar=("START", "END"),
                    help="Seconds of --still when the breath was held: adds a zoom with the heartbeats")
    ap.add_argument("--keep-steady", action="store_true", help="Walk: keep lines that never change (fans)")
    ap.add_argument("--out", type=Path, default=ROOT / "resources")
    args = ap.parse_args()
    if not (args.walk or args.still):
        ap.error("give --walk and/or --still")
    if args.walk:
        walk(args.walk, args.out, steady=not args.keep_steady)
    if args.still:
        still(args.still, args.out, args.still_bin, args.still_span, args.still_hold)


if __name__ == "__main__":
    main()
