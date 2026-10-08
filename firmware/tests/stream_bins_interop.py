"""Decode the actual range-bin (codec 2) C producer and check every bin against NumPy."""
import math
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from frame_stream import Parser, Frames

PAIRS, K = 512, 40


def lround(v):
    return math.floor(v + 0.5) if v >= 0 else math.ceil(v - 0.5)


def sample(lane, chirp, n, q):
    """Mirror of test_stream_bins.c sample()."""
    a = 6.283185307179586 * ((5 + lane) * n) / PAIRS + 0.1 * chirp
    v = ((math.sin(a) if q else math.cos(a)) * (3000.0 + 40.0 * chirp) + (-700.0 if q else 1200.0)
         + n * (3.0 if lane else -2.0) + ((n * 37 + chirp * 11 + q) % 23))
    return lround(v)


with tempfile.TemporaryDirectory() as folder:
    wire = Path(folder) / 'stream.ldf'
    subprocess.run([sys.argv[1], str(wire)], check=True)
    data = wire.read_bytes()
    p, f, complete = Parser(), Frames(), []
    for offset in range(0, len(data), 61):
        for m in p.feed(data[offset:offset + 61]):
            frame = f.accept(m)
            if frame:
                complete.append(frame)
    assert p.errors == f.protocol_errors == 0, (p.errors, f.protocol_errors)
    assert [x['frame_id'] for x in complete] == [1] and f.abort_reasons == {2: 1}, f.abort_reasons
    frame = complete[0]
    assert (frame['codec_version'], frame['bins_half'], frame['pairs'], frame['chirps']) == (2, K, PAIRS, 64)
    ks = np.arange(-K, K + 1)
    worst, shifts = 0.0, []
    for lane in range(2):
        bins = np.frombuffer(frame['lanes'][lane], '<i4').reshape(64, 2 * K + 1, 2)
        for chirp in range(64):
            x = np.array([complex(sample(lane, chirp, n, 0), sample(lane, chirp, n, 1)) for n in range(PAIRS)])
            X = np.fft.fft(x)[ks % PAIRS]
            got = bins[chirp, :, 0] + 1j * bins[chirp, :, 1]
            shift = frame['shifts'][lane][chirp]
            shifts.append(shift)
            dc = K
            assert abs(got[dc] - X[dc]) <= 1.5, (lane, chirp, got[dc], X[dc])
            err = np.abs(np.delete(got - X, dc))
            tol = (2 ** shift) / 2 + 1.5            # half an LSB after the shift, plus DFT rounding
            assert err.max() <= tol * math.sqrt(2), (lane, chirp, shift, err.max())
            worst = max(worst, float(err.max() / 2 ** shift))
            # The shift is the smallest that fits: without it some bin would overflow int16.
            peak = np.max(np.abs(np.concatenate([np.delete(got.real, dc), np.delete(got.imag, dc)])))
            assert shift == 0 or peak > 32767 * 2 ** (shift - 1) - 2 ** shift, (shift, peak)
    assert max(shifts) > 0, 'test inputs should exercise a non-zero shift'
print(f'range-bin C/Python roundtrip: 128 records, shifts {min(shifts)}..{max(shifts)}, '
      f'worst error {worst:.2f} LSB, failing transform rejected')
