"""Inspect UFW containers and extract flash images without executing firmware.

The inner filesystem decoder is the reviewed jl-misctools implementation at
0a5b12db0ef38f3042acffbe2452730a37fd2405. Only its definitions are loaded;
its CLI is not run. binascii.crc_hqx replaces its crcmod dependency for CRC16.
Original packages are opened read-only. See the output manifest for validation.
"""
from __future__ import annotations

import argparse
import ast
import binascii
import contextlib
import hashlib
import io
import json
import re
import struct
import sys
import types
from pathlib import Path

TOOL_COMMIT = '0a5b12db0ef38f3042acffbe2452730a37fd2405'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def crc16(data, initial=0):
    return binascii.crc_hqx(data, initial)


def descramble(data, key=0xffff):
    out = bytearray(data)
    for i in range(len(out)):
        out[i] ^= key & 255
        key = ((key << 1) ^ (0x1021 if key & 0x8000 else 0)) & 0xffff
    return bytes(out)


def safe_name(raw):
    name = raw.split(b'\0', 1)[0].decode('ascii')
    if not re.fullmatch(r'[A-Za-z0-9_. -]+', name) or name in ('.', '..'):
        raise ValueError(f'Invalid file name: {name!r}')
    return name


def load_decoder(root):
    library = root / 'firmware'
    sys.path.insert(0, str(library.resolve()))
    shim = types.ModuleType('jltech.crc')
    shim.jl_crc16 = crc16
    sys.modules['jltech.crc'] = shim
    source = library / 'fwunpack_newfw.py'
    tree = ast.parse(source.read_text(encoding='utf-8'), filename=str(source))
    # Omit the CLI, argument parser, and unused third-party YAML import.
    tree.body = [node for node in tree.body if
                 isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.ImportFrom))
                 or isinstance(node, ast.Import) and
                 all(alias.name not in ('yaml', 'argparse') for alias in node.names)]
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and \
                node.func.attr == 'mkdir' and not any(k.arg == 'exist_ok' for k in node.keywords):
            node.keywords.append(ast.keyword(arg='exist_ok', value=ast.Constant(value=True)))
    ast.fix_missing_locations(tree)
    namespace = {'__name__': 'reviewed_jl_newfw_decoder'}
    exec(compile(tree, str(source), 'exec'), namespace)
    original_iterator = namespace['JLFSIterator']
    entry_checks = []

    class CheckedIterator(original_iterator):
        def __next__(self):
            entry = super().__next__()
            safe_name(entry.raw_name)
            entry_checks.append(entry)
            # 0x81 directory links can carry a 0xffffffff placeholder length.
            if not entry.flags & 0x10 and entry.flags != 0x81:
                if entry.data_offset < 0 or entry.data_size < 0 or \
                        entry.data_offset + entry.data_size > len(self.buff):
                    raise ValueError(f'File outside image: {entry}')
            return entry

    namespace['JLFSIterator'] = CheckedIterator

    def decode_verified(info, image, output):
        entry_checks.clear()
        namespace['parse_newfw'](info, image, output)
        info['validated_inner_entry_headers'] = len(entry_checks)
        info['regular_file_crc_checks'] = []
        for entry in entry_checks:
            if entry.flags == 0x82:
                actual = crc16(image[entry.data_offset:entry.data_offset + entry.data_size])
                info['regular_file_crc_checks'].append(dict(
                    name=entry.name, size=entry.data_size, expected=entry.data_crc,
                    actual=actual, valid=actual == entry.data_crc))
                if actual != entry.data_crc:
                    raise ValueError(f'Inner file data CRC mismatch: {entry.name}')

    return decode_verified, sha256(source.read_bytes())


def extract_ota_loaders(data, destination):
    """The first payload offset delimits this bundle's 32-byte entry table."""
    table_end = struct.unpack_from('<I', data, 4)[0]
    if table_end < 32 or table_end % 32 or table_end > len(data):
        raise ValueError('Invalid OTA loader table bounds')
    destination.mkdir(parents=True, exist_ok=True)
    result = []
    for start in range(0, table_end, 32):
        hcrc, dcrc, offset, size, flags, reserved, index, raw_name = \
            struct.unpack_from('<HHIIBBH16s', data, start)
        name = safe_name(raw_name)
        if crc16(data[start+2:start+32]) != hcrc:
            raise ValueError(f'OTA loader header CRC mismatch: {name}')
        if offset < table_end or offset + size > len(data):
            raise ValueError(f'OTA loader outside bundle: {name}')
        payload = data[offset:offset+size]
        if crc16(payload) != dcrc:
            raise ValueError(f'OTA loader data CRC mismatch: {name}')
        (destination / name).write_bytes(payload)
        result.append(dict(name=name, offset=offset, size=size, flags=flags,
                           index=index, header_crc_valid=True, data_crc_valid=True,
                           sha256=sha256(payload)))
    return result


def extract_package(path, destination, decode):
    data = path.read_bytes()
    header = descramble(data[:64])
    hcrc, table_crc, image_size, count, unknown16, unknown32, chip = \
        struct.unpack('<HHIHHI48s', header)
    if crc16(header[2:]) != hcrc:
        raise ValueError('UFW header CRC mismatch')
    table_end = 64 + count * 80
    if image_size != len(data) or table_end > len(data):
        raise ValueError('Invalid container length/table bounds')
    if crc16(data[64:table_end]) != table_crc:
        raise ValueError('UFW entry-table CRC mismatch')
    destination.mkdir(parents=True, exist_ok=True)
    components = destination / 'components'
    components.mkdir(exist_ok=True)
    result = dict(source=str(path.resolve()), size=len(data), sha256=sha256(data),
                  chip=safe_name(chip), header_crc_valid=True,
                  entry_table_crc_valid=True, entry_count=count,
                  header_unknown16=unknown16, header_unknown32=unknown32,
                  entries=[])
    for index in range(count):
        start = 64 + index * 80
        entry_type, entry_index, expected_crc, unknown, offset, size, padded_size, extra, raw_name = \
            struct.unpack('<HHHHIII44s16s', descramble(data[start:start+80]))
        name = safe_name(raw_name)
        if offset < table_end or offset + max(size, padded_size) > len(data):
            raise ValueError(f'Entry outside package: {name}')
        payload = data[offset:offset+size]
        (components / name).write_bytes(payload)
        record = dict(name=name, type=entry_type, index=entry_index,
                      offset=offset, size=size, padded_size=padded_size,
                      expected_crc16=expected_crc, raw_crc16=crc16(payload),
                      raw_crc_valid=crc16(payload) == expected_crc,
                      sha256=sha256(payload), extra=extra.hex())
        # Some metadata entries use the same fixed-key scrambling as the header.
        decoded = descramble(payload)
        record['descrambled_crc_valid'] = crc16(decoded) == expected_crc
        if payload and not record['raw_crc_valid'] and record['descrambled_crc_valid']:
            decoded_path = components / (name + '.decoded')
            decoded_path.write_bytes(decoded)
            record['decoded_file'] = str(decoded_path.relative_to(destination))
            record['decoded_sha256'] = sha256(decoded)
        if name == 'ota.bin':
            record['ota_loaders'] = extract_ota_loaders(payload, destination / 'ota_loaders')
        if entry_type in (0, 32, 33, 34):
            flash_output = destination / 'flash_images' / name
            flash_output.mkdir(parents=True, exist_ok=True)
            flash = bytearray(payload)
            info = {}
            log = io.StringIO()
            try:
                with contextlib.redirect_stdout(log):
                    decode(info, flash, flash_output)
                record['inner_decode_complete'] = True
            except Exception as exc:
                record['inner_decode_complete'] = False
                record['inner_decode_error'] = f'{type(exc).__name__}: {exc}'
            record['inner_info'] = info
            (flash_output / 'decode_log.txt').write_text(log.getvalue(), encoding='utf-8')
            (flash_output / 'decoded_flash.bin').write_bytes(flash)
            (flash_output / 'info.json').write_text(json.dumps(info, indent=2), encoding='utf-8')
        result['entries'].append(record)
    result['extracted_files'] = []
    for extracted in sorted(destination.rglob('*')):
        if not extracted.is_file() or extracted.name.endswith('.strings.tsv'):
            continue
        contents = extracted.read_bytes()
        result['extracted_files'].append(dict(path=str(extracted.relative_to(destination)),
                                              size=len(contents), sha256=sha256(contents)))
        if extracted.suffix in ('.bin', '.boot', '.ini', '.decoded'):
            strings = ['offset_hex\ttext']
            for match in re.finditer(rb'[\x20-\x7e]{5,}', contents):
                strings.append(f'{match.start():08x}\t{match.group().decode("ascii")}')
            extracted.with_name(extracted.name + '.strings.tsv').write_text(
                '\n'.join(strings) + '\n', encoding='utf-8')
    return result


def compare_applications(packages, output):
    result = {'applications': [], 'unique_strings': {}}
    sets = []
    for package in packages:
        stem = Path(package['source']).stem
        app = output / stem / 'flash_images/flash.bin/files/app.bin'
        if not app.exists():
            return None
        data = app.read_bytes()
        strings = [{'offset': m.start(), 'offset_hex': f'0x{m.start():x}',
                    'text': m.group().decode('ascii')}
                   for m in re.finditer(rb'[\x20-\x7e]{5,}', data)]
        selected = [s for s in strings if re.search(
            r'(?i)(hlk_|radar|i2c_write|cidx|UART->|BLE->|DATA_TRANSFER|sensibility|'
            r'Hold Cnt|UART_UPDATE|fw-AC63_BT_SDK|Oct 19 2023|Nov 2[04] 2025|'
            r'BTCTRLER-@|UPDATE-@)', s['text'])]
        result['applications'].append(dict(package=stem, application=str(app),
                                            size=len(data), sha256=sha256(data),
                                            selected_strings=selected))
        sets.append({s['text'] for s in strings})
    for label, values in (('only_left', sets[0] - sets[1]),
                          ('only_right', sets[1] - sets[0])):
        result['unique_strings'][label] = sorted(s for s in values
            if len(s) > 8 and re.search(r'[A-Za-z_]{4}', s))
    cfg_path = output / Path(packages[0]['source']).stem / 'flash_images/flash.bin/top/isd_config.ini'
    cfg = cfg_path.read_bytes()
    position = 34  # 32-byte chip-key encoding followed by its CRC16.
    params = []
    while position < len(cfg):
        size = cfg[position]
        end = cfg.index(0, position + 1)
        key = cfg[position+1:end].decode('ascii')
        position = end + 1
        raw = cfg[position:position+size]
        if len(raw) != size:
            raise ValueError('Truncated inner bootloader configuration')
        position += size
        value = int.from_bytes(raw, 'little') if key in (
            'UTBD', 'UPDATE_JUMP', 'EOFFSET', 'BT_OFFSET') else raw.decode('ascii')
        params.append(dict(key=key, raw_hex=raw.hex(), value=value))
    result['bootloader_configuration'] = params
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unpacker-root', type=Path,
                        default=Path('tmp/ufw_analysis/jl-misctools'))
    parser.add_argument('--output', type=Path, default=Path('output/ufw_analysis'))
    parser.add_argument('inputs', type=Path, nargs='*',
                        default=[Path('oncstzcza54pd.ufw'), Path('5o09fdkye1jo8.ufw')])
    args = parser.parse_args()
    assert crc16(b'123456789') == 0x31c3
    decode, decoder_hash = load_decoder(args.unpacker_root)
    manifest = dict(tool_source='https://github.com/kagaimiq/jl-misctools',
                    tool_commit=TOOL_COMMIT, decoder_sha256=decoder_hash,
                    decoder_adaptations=['load definitions without upstream CLI',
                        'stdlib CRC16 adapter', 'validated extraction names and file bounds',
                        'repeatable directory creation', 'validate inner app/config data CRCs'],
                    packages=[])
    for path in args.inputs:
        result = extract_package(path, args.output / path.stem, decode)
        if sha256(path.read_bytes()) != result['sha256']:
            raise ValueError(f'Source changed during analysis: {path}')
        manifest['packages'].append(result)
        print(path.name, result['chip'], result['entry_count'], 'entries')
        for entry in result['entries']:
            print(' ', entry['name'], entry['size'],
                  'CRC OK' if entry['raw_crc_valid'] or entry['descrambled_crc_valid'] else 'CRC UNRESOLVED',
                  entry.get('inner_decode_error',
                    'inner files CRC OK' if entry.get('inner_decode_complete') else ''))
    if len(manifest['packages']) == 2:
        left, right = manifest['packages']
        right_by_name = {entry['name']: entry for entry in right['entries']}
        manifest['comparison'] = []
        for entry in left['entries']:
            other = right_by_name.get(entry['name'])
            if other:
                manifest['comparison'].append(dict(name=entry['name'],
                    identical=entry['sha256'] == other['sha256'],
                    left_size=entry['size'], right_size=other['size']))
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    if len(manifest['packages']) == 2:
        comparison = compare_applications(manifest['packages'], args.output)
        if comparison is not None:
            (args.output / 'application_comparison.json').write_text(
                json.dumps(comparison, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
