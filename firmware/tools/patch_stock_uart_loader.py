"""Apply hash-guarded LD2450 two-wire fixes to the stock UART loader.

Stock V2.14 supplies TX=RX=PA0. The loader selects one-wire UART in that case.
For a valid nonzero handoff baud, force TX=PA1 while preserving RX and baud.
Also clear UART1 CON1: the original baud-dependent 0x30 value prevented RX
on the bench at 256000. The SDK's ordinary two-wire driver leaves it clear.
Only the pinned uart_user.bin is supported. No hardware is accessed.
"""
import argparse
import binascii
import hashlib
import json
from pathlib import Path
import struct

import lz4.block
from package_ufw import container, enc, crc

LOADER_SHA = '96e6fff47bf911e9a02f7ee62fb398fb37ccf44204a1e77ae782f5d1b3ab294e'
PATCH_OFFSET = 0xa40e - 0x9000
BEFORE = bytes.fromhex('d0 ec 40 18')  # r1 = [r4+128] (handoff TX)
AFTER = bytes.fromhex('41 21 00 00')   # r1 = 1 (PA1); nop
CON1_OFFSET = 0xa482 - 0x9000
CON1_BEFORE = bytes.fromhex('62 e1 30 20')  # r2 &= 0x30
CON1_AFTER = bytes.fromhex('42 20 00 00')   # r2 = 0; nop
PATCHES = ((PATCH_OFFSET, BEFORE, AFTER),
           (CON1_OFFSET, CON1_BEFORE, CON1_AFTER))


def unpack_loader(raw):
    if len(raw) < 32 or crc(raw[2:32]) != struct.unpack_from('<H', raw)[0]:
        raise ValueError('Loader header CRC mismatch')
    pos = 32
    code = bytearray()
    while pos < len(raw):
        packed, size = struct.unpack_from('<II', raw, pos)
        pos += 8
        if not 0 < size <= 4096 or pos+packed > len(raw):
            raise ValueError('Invalid compressed block bounds')
        part = lz4.block.decompress(raw[pos:pos+packed], uncompressed_size=size,
                                    dict=bytes(code[-65536:]))
        if len(part) != size:
            raise ValueError('Decompressed size mismatch')
        code.extend(part)
        pos += packed
    if len(code) != struct.unpack_from('<I', raw, 4)[0] or crc(code) != struct.unpack_from('<H', raw, 2)[0]:
        raise ValueError('Loader content integrity mismatch')
    return code


def patch_loader(raw):
    if hashlib.sha256(raw).hexdigest() != LOADER_SHA:
        raise ValueError('Unrecognized loader; refusing instruction patch')
    code = unpack_loader(raw)
    for offset, before, after in PATCHES:
        if code[offset:offset+len(before)] != before:
            raise ValueError(f'Unexpected instruction at 0x{offset+0x9000:x}')
        code[offset:offset+len(before)] = after
    result = bytearray(raw[:32])
    struct.pack_into('<H', result, 2, crc(code))
    struct.pack_into('<H', result, 0, crc(result[2:32]))
    for offset in range(0, len(code), 4096):
        part = bytes(code[offset:offset+4096])
        packed = lz4.block.compress(part, mode='high_compression', compression=12,
                    store_size=False, dict=bytes(code[max(0,offset-65536):offset]))
        result.extend(struct.pack('<II', len(packed), len(part)))
        result.extend(packed)
    if unpack_loader(result) != code:
        raise ValueError('Patched loader roundtrip failed')
    return bytes(result), bytes(code)


def patch_image(source, destination):
    if source.resolve() == destination.resolve():
        raise ValueError('Refusing to overwrite input image')
    original = source.read_bytes()
    data = bytearray(original)
    header, items = container(data)
    ota_items = [item for item in items if item['name'] == 'ota.bin']
    if len(ota_items) != 1:
        raise ValueError('Expected one OTA bundle')
    ota = ota_items[0]
    begin, size = ota['offset'], ota['size']
    bundle = bytearray(data[begin:begin+size])
    if crc(bundle) != ota['crc']:
        raise ValueError('OTA CRC mismatch')
    table_end = struct.unpack_from('<I', bundle, 4)[0]
    matches = []
    for pos in range(0, table_end, 32):
        if crc(bundle[pos+2:pos+32]) != struct.unpack_from('<H', bundle, pos)[0]:
            raise ValueError('OTA entry header CRC mismatch')
        if bundle[pos+16:pos+32].split(b'\0',1)[0] == b'uart_user.bin':
            matches.append(pos)
    if len(matches) != 1:
        raise ValueError('Expected one uart_user loader')
    pos = matches[0]
    offset, old_size = struct.unpack_from('<II', bundle, pos+4)
    loader = bytes(bundle[offset:offset+old_size])
    patched, code = patch_loader(loader)
    if len(patched) > old_size:
        raise ValueError('Patched loader exceeds its existing slot')
    bundle[offset:offset+old_size] = patched + b'\xff'*(old_size-len(patched))
    struct.pack_into('<H', bundle, pos+2, crc(patched))
    struct.pack_into('<I', bundle, pos+8, len(patched))
    struct.pack_into('<H', bundle, pos, crc(bundle[pos+2:pos+32]))
    data[begin:begin+size] = bundle
    struct.pack_into('<H', ota['header'], 4, crc(bundle))
    data[ota['pos']:ota['pos']+80] = enc(ota['header'])
    struct.pack_into('<H', header, 2, crc(data[64:64+80*len(items)]))
    struct.pack_into('<H', header, 0, crc(header[2:]))
    data[:64] = enc(header)
    _, checked = container(data)
    for a, b in zip(items, checked):
        if a['name'] != 'ota.bin':
            off, n = a['offset'], a['size']
            if a['header'] != b['header'] or data[off:off+n] != original[off:off+n]:
                raise ValueError('Unrelated component changed')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    destination.with_suffix('.loader.bin').write_bytes(code)
    report = dict(source_sha256=hashlib.sha256(original).hexdigest(),
        ufw_sha256=hashlib.sha256(data).hexdigest(),
        stock_loader_sha256=LOADER_SHA, patched_loader_sha256=hashlib.sha256(patched).hexdigest(),
        decompressed_loader_sha256=hashlib.sha256(code).hexdigest(),
        instructions=[dict(vma=f'0x{offset+0x9000:x}', before=before.hex(), after=after.hex())
                      for offset, before, after in PATCHES],
        old_loader_size=old_size, new_loader_size=len(patched),
        application_unchanged=True, hardware_validated=False)
    destination.with_suffix('.manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(patch_image(a.input,a.out),indent=2))
