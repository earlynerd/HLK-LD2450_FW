"""Host predictor screening, with exact Rice bit-count estimates (no wire codec).

Retains a raw first chirp, eight original framing bytes per packet, a one-byte
packet mode, and one parameter byte per 32-value residual block. Blocks are
byte aligned and may fall back to 16-bit raw samples. I and Q are predicted
separately. Estimates exclude external transport headers. Reconstructs samples
causally to verify every prediction/residual pair, but does not encode/decode
a Rice bitstream or measure target execution time.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from analyze_capture_compression import records


def predict(method, history, current, j):
    up = history[-1][j]
    left = current[j-2] if j >= 2 else 0
    corner = history[-1][j-2] if j >= 2 else 0
    if method == 'previous_chirp':
        return up
    if method == 'previous_sample':
        return left
    if method == 'linear_sample':
        return 2*left-current[j-4] if j >= 4 else left
    if method == 'linear_chirp':
        return 2*up-history[-2][j] if len(history) >= 2 else up
    if method == 'gradient_2d':
        return up+left-corner if j >= 2 else up
    if method == 'median_2d':
        return sorted([up, left, up+left-corner])[1] if j >= 2 else up
    raise ValueError(method)


def screen(path):
    raw = path.read_bytes()
    recs = records(raw)
    assert recs and sum(r['size'] for r in recs) == len(raw)
    assert all(r['pairs'] == 512 for r in recs)
    assert len({r['rx'] for r in recs}) == 1
    assert all(b['chirp'] == a['chirp']+1 for a, b in zip(recs, recs[1:]))
    values = [list(struct.unpack('>1024h', raw[r['offset']+4:r['offset']+r['size']-4])) for r in recs]
    result = dict(source=str(path), sha256=hashlib.sha256(raw).hexdigest(), raw_bytes=len(raw), estimates={})
    for method in ['previous_chirp', 'previous_sample', 'linear_sample', 'linear_chirp', 'gradient_2d', 'median_2d']:
        history = [values[0]]
        sizes = [recs[0]['size']+1]
        for original in values[1:]:
            rebuilt, residual = [], []
            for j, value in enumerate(original):
                prediction = predict(method, history, original[:j], j)
                d = value-prediction
                residual.append(2*d if d >= 0 else -2*d-1)
                rebuilt.append(predict(method, history, rebuilt, j)+d)
            assert rebuilt == original
            history.append(rebuilt)
            size = 0
            for start in range(0, len(residual), 32):
                block = residual[start:start+32]
                bits = min(sum((z >> k)+1+k for z in block) for k in range(18))
                size += 1+min((bits+7)//8, 2*len(block))
            sizes.append(8+1+min(size, 2*len(original)))
        result['estimates'][method] = dict(bytes=sum(sizes), fraction_of_raw=sum(sizes)/len(raw),
            packet_bytes=sizes, predictor_reconstruction_exact=True)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('capture', type=Path)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    result = dict(scope='Startup capture only; Rice sizes calculated, not an implemented wire codec; no target timing.',
                  lanes=[screen(a.capture/f'lane{n}.bin') for n in range(2)])
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    for name in result['lanes'][0]['estimates']:
        total = sum(lane['estimates'][name]['bytes'] for lane in result['lanes'])
        raw_total = sum(lane['raw_bytes'] for lane in result['lanes'])
        print(f'{name}: {total} bytes, {total/raw_total:.1%} of original capture')
