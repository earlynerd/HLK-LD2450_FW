"""Execute the small PIO instruction arrays extracted from the actual ELF.

This checks program timing/bit order, not electrical rise times or RP2040 I/O.
Usage: python tests/check_waveform.py [.pio/build/pico/firmware.elf]
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'firmware/tools'))
from audit_image import Elf32


def program(elf, suffix):
    name, (addr, size) = next((n, v) for n, v in elf.symbols.items() if n.endswith(suffix))
    h = next(h for h in elf.headers if h[1] == 1 and h[3] <= addr < h[3] + h[5])
    offset = h[4] + addr - h[3]
    return struct.unpack_from('<' + 'H' * (size // 2), elf.raw, offset)


def simulate(code, side_set, limit):
    pc = tick = x = data_dir = clock_dir = 0
    word = ((~0x16ef) & 0xffff) << 16
    edges, lows = [], []
    for _ in range(limit):
        ins = code[pc]
        op, arg, val = ins >> 13, (ins >> 5) & 7, ins & 31
        delay = (ins >> 8) & (15 if side_set else 31)
        old_clock = clock_dir
        if side_set:
            clock_dir = (ins >> 12) & 1
        next_pc = (pc + 1) % len(code)
        if op == 7:  # SET
            if arg == 1: x = val
            elif arg == 4:
                if side_set: data_dir = val
                else: clock_dir = val
            else: raise AssertionError('Unexpected SET target')
        elif op == 3:  # OUT PINDIRS,1
            assert side_set and arg == 4 and val == 1
            data_dir = (word >> 31) & 1
            word = (word << 1) & 0xffffffff
        elif op == 0:  # JMP X--
            assert arg == 2
            if x: next_pc = val
            x = (x - 1) & 0xffffffff
        elif op == 4:  # PULL
            assert side_set and pc == 0
        elif op == 6:  # IRQ ends key word
            assert side_set and data_dir == clock_dir == 0
            break
        elif op == 5:  # NOP = MOV Y,Y
            assert (ins & 255) == 0x42
        else:
            raise AssertionError(hex(ins))
        if old_clock == 1 and clock_dir == 0: edges.append((tick, 1 - data_dir))
        if old_clock == 0 and clock_dir == 1: lows.append(tick)
        tick += delay + 1
        pc = next_pc
    return edges, lows


elf = Elf32(Path(sys.argv[1] if len(sys.argv) > 1 else '.pio/build/pico/firmware.elf').read_bytes())
edges, lows = simulate(program(elf, '7keyCodeE'), True, 100)
assert len(edges) == len(lows) == 16
assert ''.join(str(bit) for t, bit in edges) == '0001011011101111'
assert all(t - lo == 10 for (t, bit), lo in zip(edges, lows))
assert all(b[0] - a[0] == 20 for a, b in zip(edges, edges[1:]))
edges, lows = simulate(program(elf, '9pulseCodeE'), False, 300)
assert len(lows) >= 4
assert all(b - a == 1000 for a, b in zip(lows, lows[1:]))
assert all(t - lo == 10 for (t, bit), lo in zip(edges, lows))
print('ELF PIO programs: MSB-first 0x16EF, 50 kHz key, 1 kHz calibration/10 us lows: passed')
