"""Compare decoded USB-only synthetic frames against the independent pattern."""
import argparse
import json
from pathlib import Path
import struct


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('decoded',type=Path)
    a=p.parse_args()
    expected=[]
    for lane in range(2):
        raw=bytearray()
        for chirp in range(64):
            words=[(17*j+chirp+lane)&65535 for j in range(1024)]
            raw+=struct.pack('>I',0xaa200201|(lane<<22)|(chirp<<11))
            raw+=struct.pack('>1024H',*words)
            raw+=struct.pack('>HH',sum(words)&65535,(lane<<14)|0x2000|((chirp&15)<<8)|0x55)
        expected.append(raw)
    frames=sorted(a.decoded.glob('frame-*'))
    if not frames:p.error('No complete decoded frames')
    for frame in frames:
        for lane in range(2):
            if (frame/f'lane{lane}.bin').read_bytes()!=expected[lane]:
                raise ValueError(f'Known-pattern mismatch: {frame}, lane {lane}')
    print(json.dumps({'complete_frames_exact':len(frames),'raw_bytes_verified':len(frames)*sum(map(len,expected))},indent=2))


if __name__=='__main__':main()
