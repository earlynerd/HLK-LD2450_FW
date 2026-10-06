"""Deliberate startup/layout corruption must fail before UFW packaging."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_image import audit_startup


def fixture(change=None):
    base = 0x1e00120
    symbols = dict(_start=base, text_begin=base, text_size=0xa0,
                   data_addr=0, data_size=0x20, data_begin=base + 0xa0,
                   _cpu0_sstack_begin=0x30, _cpu0_sstack_end=0x50,
                   boot_info=0x50, bss_begin=0x60, bss_size=0x20,
                   HEAP_BEGIN=0x80, HEAP_END=0x2bf00,
                   bss1_begin=0x2d200, bss1_size=0,
                   HEAP1_BEGIN=0x2d200, HEAP1_END=0x2ff80,
                   psram_laddr=base + 0xc0, psram_vaddr=0x800000,
                   psram_text_size=0, main=base + 0x9a,
                   __initcall_ld2450_board_power_init=base + 0x9c,
                   initcall_begin=base + 0x9c, initcall_end=base + 0xa0)
    if change:
        symbols.update(change)
    code = bytearray(0xa0)
    # Fixture encodes the ABI independently of the verifier's checks.
    for offset, opcode, value in [
        (4, 'eeff', 0x50), (10, 'edff', 0x50), (20, 'c0ff', base + 0xc0),
        (26, 'c1ff', 0x800000), (32, 'c2ff', 0), (54, 'c3ff', 0x60),
        (62, 'c2ff', 0x20), (76, 'c3ff', 0x2d200), (84, 'c2ff', 0),
        (98, 'c4ff', 0), (104, 'c1ff', base + 0xa0), (110, 'c2ff', 0x20),
        (146, 'c0ff', base + 0x9a)]:
        code[offset:offset + 6] = bytes.fromhex(opcode) + struct.pack('<I', value)
    code[152:154] = b'\xd0\x00'
    data = bytes(range(32))
    strings = bytearray(b'\0')
    symtab = bytearray(16)
    for name, value in symbols.items():
        symtab.extend(struct.pack('<IIIBBH', len(strings), value,
                                   0x10 if name == 'boot_info' else 0, 0, 0, 0xfff1))
        strings.extend(name.encode() + b'\0')
    sections = [('', 0, 0, 0, b'', 0, 0, 0),
                ('.text', 1, 6, base, code, 0, 0, 0),
                ('.data', 1, 3, 0, data, 0, 0, 0),
                ('.irq_stack', 8, 3, 0x20, b'', 0x40, 0, 0),
                ('.bss', 8, 3, 0x60, b'', 0x20, 0, 0),
                ('.mmu_tlb', 8, 3, 0x2c000, b'', 0x1200, 0, 0),
                ('.strtab', 3, 0, 0, strings, 0, 0, 0),
                ('.symtab', 2, 0, 0, symtab, 0, 6, 16)]
    names = b'\0' + b''.join(x[0].encode() + b'\0' for x in sections[1:]) + b'.shstrtab\0'
    sections.append(('.shstrtab', 3, 0, 0, names, 0, 0, 0))
    raw = bytearray(52)
    raw[:6] = b'\x7fELF\x01\x01'
    struct.pack_into('<I', raw, 24, base)
    headers = []
    for name, kind, flags, addr, contents, zero_size, link, entry_size in sections:
        headers.append((names.index(name.encode() + b'\0'), kind, flags, addr,
                        len(raw), zero_size or len(contents), link, 0, 4, entry_size))
        raw.extend(contents)
    struct.pack_into('<I', raw, 32, len(raw))
    struct.pack_into('<HHH', raw, 46, 40, len(headers), 8)
    for header in headers:
        raw.extend(struct.pack('<10I', *header))
    return raw, code + data


class BytesFile:
    def __init__(self, raw): self.raw = raw
    def read_bytes(self): return self.raw


class StartupAuditTests(unittest.TestCase):
    def test_valid_layout(self):
        elf, app = fixture()
        self.assertEqual(audit_startup(BytesFile(elf), app)['startup_immediates_checked'], 13)

    def test_wrong_packaged_data(self):
        elf, app = fixture()
        app[-1] ^= 1
        with self.assertRaisesRegex(ValueError, 'initialized RAM packaging'):
            audit_startup(BytesFile(elf), app)

    def test_bad_instruction_operand_in_both_elf_and_image(self):
        elf, app = fixture()
        app[106] ^= 4
        elf[52 + 106] ^= 4
        with self.assertRaisesRegex(ValueError, 'data_begin operand'):
            audit_startup(BytesFile(elf), app)

    def test_overlap_and_callback_order(self):
        for changes, message in [({'boot_info': 0x10}, 'overlap'),
                                 ({'HEAP_END': 0x30000}, 'interrupt vectors'),
                                 ({'HEAP1_END': 0x30000}, 'update record'),
                                 ({'__initcall_ld2450_board_power_init': 0}, 'follow platform')]:
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, message):
                elf, app = fixture(changes)
                audit_startup(BytesFile(elf), app)


if __name__ == '__main__':
    unittest.main()
