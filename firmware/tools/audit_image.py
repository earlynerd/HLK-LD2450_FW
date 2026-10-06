"""Post-link checks for the pinned BR23 startup ABI; no device access."""
import struct


class Elf32:
    def __init__(self, raw):
        self.raw = raw
        if raw[:6] != b'\x7fELF\x01\x01':
            raise ValueError('Expected little-endian ELF32')
        self.entry = struct.unpack_from('<I', raw, 24)[0]
        offset = struct.unpack_from('<I', raw, 32)[0]
        stride, count, names_index = struct.unpack_from('<HHH', raw, 46)
        if stride != 40 or offset + stride * count > len(raw):
            raise ValueError('Invalid ELF section table')
        self.headers = [struct.unpack_from('<10I', raw, offset + i * stride)
                        for i in range(count)]
        names = self.contents(self.headers[names_index])
        self.sections = {self.string(names, h[0]): h for h in self.headers}
        self.symbols = {}
        for h in self.headers:
            if h[1] != 2:
                continue
            strings = self.contents(self.headers[h[6]])
            if h[9] != 16 or h[5] % 16:
                raise ValueError('Invalid ELF symbol table')
            data = self.contents(h)
            for pos in range(0, len(data), 16):
                name, value, size, info, other, section = struct.unpack_from('<IIIBBH', data, pos)
                if section:
                    self.symbols[self.string(strings, name)] = (value, size)

    @staticmethod
    def string(data, offset):
        return data[offset:data.index(0, offset)].decode('ascii')

    def contents(self, section):
        offset, size = section[4:6]
        if offset + size > len(self.raw):
            raise ValueError('ELF section exceeds file')
        return self.raw[offset:offset + size]


def audit_startup(elf, app):
    """Check layout AND immediate operands actually executed before C startup.

    Instruction offsets/opcodes are from the pinned vendor startup.S.o, also
    observed at stock V2.14's 0x1e00120. Reject an ABI change for review rather
    than silently accepting a different startup implementation.
    """
    e = Elf32(elf.read_bytes())
    s = {name: value for name, (value, size) in e.symbols.items()}

    def require(ok, message):
        if not ok:
            raise ValueError('Startup audit: ' + message)

    require(e.entry == s['_start'] == s['text_begin'] == 0x1e00120, 'entry mismatch')
    for section, addr, size in [('.text', 'text_begin', 'text_size'),
                                ('.data', 'data_addr', 'data_size'),
                                ('.bss', 'bss_begin', 'bss_size')]:
        h = e.sections[section]
        require((h[3], h[5]) == (s[addr], s[size]), section + ' symbols disagree')
        require(s[addr] % 4 == s[size] % 4 == 0, section + ' is not word aligned')
    require(s['data_begin'] == s['text_begin'] + s['text_size'], 'data load address')
    require(app[:s['text_size']] == e.contents(e.sections['.text']), 'text packaging mismatch')
    require(app[s['text_size']:s['text_size'] + s['data_size']] ==
            e.contents(e.sections['.data']), 'initialized RAM packaging mismatch')
    stack = e.sections['.irq_stack']
    boot, boot_size = e.symbols['boot_info']
    require(s['data_addr'] + s['data_size'] <= stack[3] < s['_cpu0_sstack_begin'] <
            s['_cpu0_sstack_end'] <= boot < boot + boot_size <= stack[3] + stack[5] <=
            s['bss_begin'], 'RAM copy/stack/boot info/BSS overlap')
    require(s['bss_begin'] + s['bss_size'] <= s['HEAP_BEGIN'] < s['HEAP_END'] == 0x2bf00,
            'RAM0 heap overlaps BSS or interrupt vectors')
    tlb = e.sections['.mmu_tlb']
    require(tlb[3] == 0x2c000 and tlb[3] + tlb[5] <= s['bss1_begin'] and
            s['bss1_begin'] + s['bss1_size'] <= s['HEAP1_BEGIN'] < s['HEAP1_END'] == 0x2ff80,
            'RAM1 heap/TLB/update record overlap')
    require(s['psram_text_size'] == s['bss1_size'] == 0, 'unexpected PSRAM or RAM1 BSS')

    operands = [(0x04, 'eeff', '_cpu0_sstack_end'), (0x0a, 'edff', '_cpu0_sstack_end'),
                (0x14, 'c0ff', 'psram_laddr'), (0x1a, 'c1ff', 'psram_vaddr'),
                (0x20, 'c2ff', 'psram_text_size'), (0x36, 'c3ff', 'bss_begin'),
                (0x3e, 'c2ff', 'bss_size'), (0x4c, 'c3ff', 'bss1_begin'),
                (0x54, 'c2ff', 'bss1_size'), (0x62, 'c4ff', 'data_addr'),
                (0x68, 'c1ff', 'data_begin'), (0x6e, 'c2ff', 'data_size'),
                (0x92, 'c0ff', 'main')]
    for offset, opcode, name in operands:
        require(app[offset:offset + 2] == bytes.fromhex(opcode), name + ' opcode changed')
        require(struct.unpack_from('<I', app, offset + 2)[0] == s[name], name + ' operand mismatch')
    require(app[0x98:0x9a] == b'\xd0\x00', 'missing jump into C main')
    board = s['__initcall_ld2450_board_power_init']
    require(s['initcall_begin'] <= board < s['initcall_end'], 'board power must follow platform init')
    return {'entry': hex(e.entry), 'startup_immediates_checked': len(operands),
            'ram_sections_nonoverlapping': True, 'flat_text_and_data_verified': True,
            'board_power_after_platform_init': True,
            'ram0_heap_bytes': s['HEAP_END'] - s['HEAP_BEGIN'],
            'ram1_heap_bytes': s['HEAP1_END'] - s['HEAP1_BEGIN'],
            'device_execution_verified': False}
