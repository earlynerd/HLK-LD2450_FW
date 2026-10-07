"""Validate bounded ASCII SPI dumps and scan for checksum-valid DS RAW records."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import struct
from collections import Counter

def records(raw):
    result=[]
    for offset in range(len(raw)-7):
        h=int.from_bytes(raw[offset:offset+4], 'big')
        rx=(h>>22)&3; chirp=(h>>11)&511; pairs=(h&2047)-1
        if raw[offset]!=0xaa or rx>1 or ((h>>20)&3)!=2 or pairs<1: continue
        n=8+4*pairs
        if offset+n>len(raw): continue
        packet=raw[offset:offset+n]
        tail=(rx<<14)|0x2000|((chirp&15)<<8)|0x55
        if int.from_bytes(packet[-2:],'big')!=tail: continue
        words=struct.unpack('>'+str(pairs*2)+'H',packet[4:-4])
        checksum=sum(words)&65535
        if checksum!=int.from_bytes(packet[-4:-2],'big'): continue
        iq=struct.unpack('>'+str(pairs*2)+'h',packet[4:-4])
        result.append(dict(offset=offset,size=n,header=f'{h:08x}',rx=rx,chirp=chirp,pairs=pairs,
                           checksum=f'{checksum:04x}',i_min=min(iq[::2]),i_max=max(iq[::2]),
                           q_min=min(iq[1::2]),q_max=max(iq[1::2]),iq_sha256=hashlib.sha256(packet[4:-4]).hexdigest()))
    return result

def decode(text, out):
    lanes={}
    for line in text.splitlines():
        m=re.fullmatch(r'CAPTURE BEGIN lane=(\d+) size=(\d+) complete=([01])',line)
        if m:
            lane,size,complete=map(int,m.groups())
            if lane in lanes or lane>1 or not 32<=size<=65535 or size%32: raise ValueError('Unexpected/duplicate capture header')
            lanes[lane]={'raw':bytearray(),'size':size,'dma_complete':bool(complete),'ended':False}
            continue
        m=re.fullmatch(r'DATA (\d+) ([0-9a-f]{4}) ([0-9a-f]{64})',line)
        if m:
            lane=int(m[1]); offset=int(m[2],16)
            if lane not in lanes or lanes[lane]['ended'] or offset!=len(lanes[lane]['raw']) or offset+32>lanes[lane]['size']: raise ValueError('Missing/reordered dump line')
            lanes[lane]['raw'].extend(bytes.fromhex(m[3])); continue
        m=re.fullmatch(r'CAPTURE END lane=(\d+)',line)
        if m:
            lane=int(m[1])
            if lane not in lanes or lanes[lane]['ended']: raise ValueError('Unexpected/duplicate end')
            lanes[lane]['ended']=True
    if set(lanes)!={0,1}: raise ValueError('Both lane dumps are required')
    report={'lanes':{}}
    for lane,item in lanes.items():
        raw=bytes(item.pop('raw'))
        if not item['ended'] or len(raw)!=item['size']: raise ValueError('Incomplete serial dump')
        (out/f'lane{lane}.bin').write_bytes(raw)
        report['lanes'][lane]={**item,'sha256':hashlib.sha256(raw).hexdigest(),
                              'unique_bytes':len(set(raw)),'most_common':Counter(raw).most_common(8),
                              'prefix_hex':raw[:64].hex(),'valid_records':records(raw)}
    report['lanes_identical']=report['lanes'][0]['sha256']==report['lanes'][1]['sha256']
    with (out/'iq.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['lane','rx_index','chirp','sample','i','q'])
        for lane,item in report['lanes'].items():
            raw=(out/f'lane{lane}.bin').read_bytes()
            for rec in item['valid_records']:
                packet=raw[rec['offset']:rec['offset']+rec['size']]
                (out/f'lane{lane}-offset{rec["offset"]}-chirp{rec["chirp"]}.bin').write_bytes(packet)
                iq=struct.unpack('>'+str(rec['pairs']*2)+'h',packet[4:-4])
                writer.writerows([lane,rec['rx'],rec['chirp'],n,iq[2*n],iq[2*n+1]] for n in range(rec['pairs']))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('dump',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    report=decode(a.dump.read_text(encoding='ascii'),a.out)
    (a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
