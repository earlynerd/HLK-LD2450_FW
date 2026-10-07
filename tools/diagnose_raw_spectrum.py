"""Compare independently validated DS RAW captures without changing the viewer.

All spectra use unmodified I/Q, apart from documented per-record DC removal
and Hann windowing. FFT bins are not calibrated range. Input files are read-only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy.signal import find_peaks
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'firmware/tools'))
from frame_stream import Parser, Frames


def read_capture(path):
    parser, decoder = Parser(), Frames()
    iq, ids, timestamps = [], [], []
    digest = hashlib.sha256()
    with path.open('rb') as source:
        while data := source.read(65536):
            digest.update(data)
            for message in parser.feed(data):
                frame = decoder.accept(message)
                if frame:
                    iq.append(np.stack([
                        np.frombuffer(lane, dtype='>i2').reshape(frame['chirps'], 1028)
                        [:, 2:-2].reshape(frame['chirps'], 512, 2)
                        for lane in frame['lanes']]))
                    ids.append(frame['frame_id'])
                    timestamps.append(frame['started_us'])
    if not iq:
        raise ValueError(f'No complete captures: {path}')
    report = dict(source=str(path), sha256=digest.hexdigest(), frames=len(iq),
                  rejected_before_eof=decoder.rejected, aborts=decoder.abort_reasons,
                  protocol_errors=decoder.protocol_errors, discarded_bytes=parser.discarded_bytes,
                  partial_tail=bool(parser.buffer or decoder.current),
                  first_id=ids[0], last_id=ids[-1])
    return np.stack(iq), np.asarray(timestamps, dtype=np.int64), report


def analyze(iq):
    z = iq[..., 0].astype(np.float64) + 1j * iq[..., 1]
    centered = z - z.mean(axis=-1, keepdims=True)
    window = np.hanning(512)
    fft = np.fft.fftshift(np.fft.fft(centered * window, axis=-1), axes=-1) / window.sum()
    power = np.mean(abs(fft)**2, axis=2)
    mean_db = 10*np.log10(np.maximum(power.mean(axis=0), 1e-12))
    summary = []
    for rx in range(2):
        peaks, _ = find_peaks(mean_db[rx], prominence=3)
        peaks = sorted(peaks, key=lambda k: mean_db[rx, k], reverse=True)[:15]
        summary.append(dict(receiver=rx+1,
                            ac_rms=float(np.sqrt(np.mean(abs(centered[:, rx])**2))),
                            peaks=[dict(bin=int(k-256), db=float(mean_db[rx, k])) for k in peaks]))
    return z, power, mean_db, summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, nargs='+', required=True)
    ap.add_argument('--labels', nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if len(args.input) != len(args.labels):
        ap.error('One label required for each input')
    args.out.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(len(args.input), 3, figsize=(16, 4*len(args.input)), squeeze=False)
    reports = []
    for row, (path, label) in enumerate(zip(args.input, args.labels)):
        iq, stamps, report = read_capture(path)
        z, power, db, summary = analyze(iq)
        report.update(label=label, receivers=summary)
        reports.append(report)
        for rx in range(2):
            axes[row, 0].plot(np.arange(-256, 256), db[rx], label=f'RX{rx+1}', lw=.8)
            axes[row, 1].plot(np.arange(-20, 21), db[rx, 236:277], label=f'RX{rx+1}')
        axes[row, 0].set(title=label+' / full FFT', xlabel='Signed FFT bin', ylabel='dB re 1 count', ylim=(-25, 75))
        axes[row, 1].set(title='Same data / central bins', xlabel='Signed FFT bin', ylabel='dB re 1 count', ylim=(-25, 75))
        # Retained rows are not uniform in time; show captured frame ordinal.
        image = axes[row, 2].imshow(10*np.log10(np.maximum(power[:, 0, 236:277], 1e-12)),
                                    origin='lower', aspect='auto', extent=(-20.5, 20.5, 0, len(iq)),
                                    vmin=0, vmax=60, cmap='viridis')
        axes[row, 2].set(title='RX1 / central-bin history', xlabel='Signed FFT bin', ylabel='Retained frame ordinal')
        for ax in axes[row, :2]:
            ax.grid(alpha=.2)
            ax.legend()
        fig.colorbar(image, ax=axes[row, 2], label='dB re 1 count')
    fig.suptitle('DS RAW diagnostic: DC removed, Hann window; no background subtraction or range calibration')
    fig.tight_layout()
    fig.savefig(args.out/'comparison.png', dpi=150)
    (args.out/'analysis.json').write_text(json.dumps(reports, indent=2)+'\n')
    print(json.dumps(reports, indent=2))


if __name__ == '__main__':
    main()
