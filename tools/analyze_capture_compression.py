"""Host-only lossless chirp compression experiment; not a target codec.

Each lane starts with a verbatim packet. Later packets keep their 8 framing
bytes and predict IQ from either the first or previous chirp. Escape coding
uses one byte for [-127,127], otherwise 0x80 plus the absolute int16 value.
Block coding uses a one-byte bit width and unsigned zigzag residuals in
32-value blocks. Each packet has a mode byte and falls back to raw IQ if
compression would expand it. All encoded packets are decoded and compared.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'firmware/tools'))
from decode_capture import records


def encode(values, reference, codec):
    delta = [a-b for a, b in zip(values, reference)]
    out = bytearray()
    if codec == 'escape8':
        for value, d in zip(values, delta):
            out.extend(bytes([d & 255]) if -127 <= d <= 127 else b'\x80'+struct.pack('>h', value))
    else:
        for start in range(0, len(delta), 32):
            zigzag = [2*d if d >= 0 else -2*d-1 for d in delta[start:start+32]]
            width = max(zigzag).bit_length()
            out.append(width)
            packed = 0
            for d in zigzag:
                packed = (packed << width) | d
            out.extend(packed.to_bytes((width*len(zigzag)+7)//8, 'big'))
    raw = struct.pack('>'+str(len(values))+'h', *values)
    return b'\x01'+out if len(out) < len(raw) else b'\x00'+raw


def decode(data, reference, codec):
    if data[0] == 0:
        return list(struct.unpack('>'+str(len(reference))+'h', data[1:]))
    result, pos = [], 1
    if codec == 'escape8':
        for value in reference:
            d = data[pos]
            pos += 1
            if d == 128:
                result.append(struct.unpack('>h', data[pos:pos+2])[0])
                pos += 2
            else:
                result.append(value+(d if d < 128 else d-256))
    else:
        for start in range(0, len(reference), 32):
            width = data[pos]
            pos += 1
            count = min(32, len(reference)-start)
            size = (width*count+7)//8
            packed = int.from_bytes(data[pos:pos+size], 'big')
            pos += size
            for n in range(count):
                z = (packed >> (width*(count-n-1))) & ((1 << width)-1)
                result.append(reference[start+n]+(z//2 if z % 2 == 0 else -(z//2)-1))
    assert pos == len(data)
    return result


def analyze(path):
    raw = path.read_bytes()
    recs = records(raw)
    assert recs and sum(r['size'] for r in recs) == len(raw)
    assert [r['offset'] for r in recs] == [sum(x['size'] for x in recs[:n]) for n in range(len(recs))]
    assert len({r['pairs'] for r in recs}) == 1
    assert len({r['rx'] for r in recs}) == 1
    assert all(b['chirp'] == a['chirp']+1 for a, b in zip(recs, recs[1:]))
    packets = [raw[r['offset']:r['offset']+r['size']] for r in recs]
    values = [list(struct.unpack('>'+str((len(p)-8)//2)+'h', p[4:-4])) for p in packets]
    result = dict(source=str(path), sha256=hashlib.sha256(raw).hexdigest(),
                  packets=len(packets), raw_bytes=len(raw), methods={})
    for prediction in ['first', 'previous']:
        residuals = [a-b for n in range(1, len(values)) for a, b in zip(values[n], values[0 if prediction == 'first' else n-1])]
        result[prediction+'_residuals'] = dict(min=min(residuals), max=max(residuals),
            fraction_signed8=sum(-127 <= d <= 127 for d in residuals)/len(residuals))
        for codec in ['escape8', 'block32']:
            sizes = [1+len(packets[0])]
            rebuilt = [packets[0]]
            restored = values[0]
            for n in range(1, len(values)):
                reference = values[0] if prediction == 'first' else restored
                payload = encode(values[n], reference, codec)
                restored = decode(payload, reference, codec)
                reconstructed = packets[n][:4]+struct.pack('>'+str(len(restored))+'h', *restored)+packets[n][-4:]
                assert reconstructed == packets[n]
                rebuilt.append(reconstructed)
                sizes.append(8+len(payload))
            assert b''.join(rebuilt) == raw
            result['methods'][prediction+'_'+codec] = dict(encoded_bytes=sum(sizes),
                ratio=len(raw)/sum(sizes), fraction_of_raw=sum(sizes)/len(raw),
                packet_bytes=sizes, roundtrip_exact=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = dict(scope='Existing 16-chirp startup capture only; no target timing or USB validation.',
        overhead='Includes original packet framing, first raw packet, per-packet mode, and block width bytes; excludes outer transport framing.',
        lanes=[analyze(args.capture/f'lane{lane}.bin') for lane in range(2)])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
