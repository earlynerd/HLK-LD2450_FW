"""Replace app.bin inside a pinned stock UFW without changing its flash layout.

No executable vendor tools, serial ports, or USB devices are used. The known
JieLi ENC/SFC XOR transforms and CRC16/XMODEM framing were cross-checked with
kagaimiq/jl-misctools at 0a5b12db0ef38f3042acffbe2452730a37fd2405.
"""
import argparse
import binascii
import hashlib
import json
from pathlib import Path
import struct

TEMPLATES = {
    'b50856945e587f02e04e693002e8ff23640412d048464e2ceeb041a17b95c093': 182760,
    'a1b090ccb9aeaede130bec24d4414c09b5aa85ba81020f6ce123d1c9d6b4a277': 178308,
}
FLASH_TYPES = (0, 32, 33, 34)
ENTRY_POINT = 0x1e00120
CHIP_KEY = 0xa80f

def sha(data): return hashlib.sha256(data).hexdigest()
def crc(data): return binascii.crc_hqx(data, 0)
def enc(data, key=0xffff):
    out = bytearray(data)
    for i in range(len(out)):
        out[i] ^= key & 255
        key = ((key << 1) ^ (0x1021 if key & 0x8000 else 0)) & 0xffff
    return out
def sfc(data):
    out = bytearray()
    for pos in range(0, len(data), 32):
        out.extend(enc(data[pos:pos+32], CHIP_KEY ^ (pos >> 2)))
    return out
def name(raw): return raw.split(b'\0', 1)[0].decode('ascii')
def entry(data, offset):
    hcrc, dcrc, addr, size, flags, reserved, index, raw_name = struct.unpack_from('<HHIIBBH16s', data, offset)
    if crc(data[offset+2:offset+32]) != hcrc: raise ValueError('JLFS header CRC mismatch')
    return dict(crc=dcrc, offset=addr, size=size, flags=flags, index=index, name=name(raw_name))
def update_header(data, pos, dcrc):
    struct.pack_into('<H', data, pos+2, dcrc)
    struct.pack_into('<H', data, pos, crc(data[pos+2:pos+32]))
def container(data):
    if len(data) < 64: raise ValueError('Truncated UFW')
    h=enc(data[:64]); _,tc,size,count,_,_,_=struct.unpack('<HHIHHI48s',h)
    end=64+80*count
    if size!=len(data) or end>len(data) or crc(h[2:])!=int.from_bytes(h[:2],'little') or crc(data[64:end])!=tc:
        raise ValueError('Invalid UFW header/table')
    items=[]
    for pos in range(64,end,80):
        e=enc(data[pos:pos+80]);typ,index,dcrc,_,off,n,pad,_,raw_name=struct.unpack('<HHHHIII44s16s',e)
        if off<end or off+max(n,pad)>len(data): raise ValueError('UFW payload outside file')
        items.append(dict(pos=pos, header=e, type=typ, crc=dcrc, offset=off, size=n, name=name(raw_name)))
    return h,items
def flash_view(raw):
    header=enc(raw[:32])
    if crc(header[2:])!=int.from_bytes(header[:2],'little'): raise ValueError('Invalid flash header')
    base=None
    for pos in range(32,160,32):
        e=entry(enc(raw[pos:pos+32]),0)
        if e['name']=='app_dir_head': base=e['offset']
    if base not in (0x2200,0x3000): raise ValueError('Unexpected application base')
    area=sfc(raw[base:]); top=entry(area,0)
    if top['name']!='app_area_head' or top['offset']!=ENTRY_POINT or top['size']>len(area):
        raise ValueError('Unexpected application area')
    if crc(area[32:top['size']])!=top['crc']: raise ValueError('Application area CRC mismatch')
    app=None
    for pos in range(32,0x120,32):
        e=entry(area,pos)
        if e['flags']==0x82:
            if e['offset']+e['size']>top['size']: raise ValueError('File outside app area')
            if crc(area[e['offset']:e['offset']+e['size']])!=e['crc']: raise ValueError('File CRC mismatch')
        if e['name']=='app.bin': app=(pos,e)
        if e['index']: break
    if not app: raise ValueError('No application')
    return base,area,top,app

def package(template, application, destination):
    original=template.read_bytes(); digest=sha(original)
    if digest not in TEMPLATES: raise ValueError('Template is not one of the pinned stock UFWs')
    app=application.read_bytes()
    if not app or len(app)>TEMPLATES[digest]: raise ValueError('Application exceeds template slot or is empty')
    data=bytearray(original); header,items=container(original); changes=[]
    for item in items:
        if item['type'] not in FLASH_TYPES: continue
        off,n=item['offset'],item['size']; raw=original[off:off+n]
        if crc(raw)!=item['crc']: raise ValueError('Stock flash payload CRC mismatch')
        base,area,top,(pos,e)=flash_view(raw)
        if e['size']!=TEMPLATES[digest]: raise ValueError('Unexpected app capacity')
        padded=app+b'\xff'*(e['size']-len(app))
        area[e['offset']:e['offset']+e['size']]=padded
        update_header(area,pos,crc(padded))
        update_header(area,0,crc(area[32:top['size']]))
        replacement=raw[:base]+sfc(area)
        # Reparse newly encrypted flash, including directory/data CRCs.
        _,verified,_,(_,ve)=flash_view(replacement)
        if verified[ve['offset']:ve['offset']+ve['size']]!=padded: raise ValueError('App roundtrip mismatch')
        data[off:off+n]=replacement
        eh=item['header']; struct.pack_into('<H',eh,4,crc(replacement))
        data[item['pos']:item['pos']+80]=enc(eh)
        changes.append(dict(name=item['name'],app_bytes=len(app),slot_bytes=e['size'],app_sha256=sha(app)))
    if len(changes)!=4: raise ValueError('Expected four flash variants')
    struct.pack_into('<H',header,2,crc(data[64:64+80*len(items)]))
    struct.pack_into('<H',header,0,crc(header[2:]))
    data[:64]=enc(header)
    _,out_items=container(data)
    for before,after in zip(items,out_items):
        off,n=after['offset'],after['size']
        if after['type'] not in FLASH_TYPES:
            if data[off:off+n]!=original[off:off+n] or before['header']!=after['header']:
                raise ValueError('Non-flash component changed')
        elif crc(data[off:off+n])!=after['crc']: raise ValueError('Output flash CRC mismatch')
    if destination.resolve() in (template.resolve(),application.resolve()): raise ValueError('Refusing to overwrite inputs')
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
    report=dict(template_sha256=digest,ufw_sha256=sha(data),ufw_bytes=len(data),
                application_sha256=sha(app),application_bytes=len(app),entry_point=hex(ENTRY_POINT),
                changed_flash_variants=changes,non_flash_components_preserved=True,
                crc_roundtrip_verified=True,device_flashed=False,bench_validated=False)
    destination.with_suffix('.manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--template',type=Path,required=True);p.add_argument('--app',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    print(json.dumps(package(a.template,a.app,a.out),indent=2))
