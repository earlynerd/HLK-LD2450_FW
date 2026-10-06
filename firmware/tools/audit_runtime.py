"""Check selected SDK initialization edges in the final PI32V2 executable.

This is a pinned-codegen regression guard, not general control-flow proof.
Unexpected inlining or disassembler changes fail closed for review.
"""
import re
from audit_image import Elf32


def audit_runtime(elf, disassembly):
    symbols = Elf32(elf.read_bytes()).symbols
    return audit_calls(symbols, disassembly)


def audit_calls(symbols, disassembly):
    by_address = {}
    for name, (address, size) in symbols.items():
        by_address.setdefault(address, set()).add(name)
    functions = {}
    current = None
    for line in disassembly.splitlines():
        label = re.fullmatch(r'([\w.$]+):', line)
        if label:
            current = label.group(1)
            functions[current] = []
        # The tool can label a RAM execution alias with an unrelated nearest
        # symbol. Resolve the numeric target against ELF symbols ourselves.
        call = re.search(r'\bcall\s+-?\d+\s+<.*:\s*([0-9a-fA-F]+)\s*>', line)
        if current and call:
            target = int(call.group(1), 16)
            names = by_address.get(target)
            if names is None and 0x02000000 <= target < 0x02030000:
                names = by_address.get(target - 0x02000000)
            functions[current].append(names or set())

    def position(caller, callee):
        calls = functions.get(caller, [])
        found = [i for i, names in enumerate(calls) if callee in names]
        if len(found) != 1:
            raise ValueError(f'Runtime audit: expected one {caller} -> {callee} call')
        return found[0]

    init = position('setup_arch', 'log_early_init')
    if init >= position('setup_arch', 'clock_dump'):
        raise ValueError('Runtime audit: logger must initialize before clock dump')
    position('log_early_init', 'os_mutex_create')
    position('log_early_init', 'malloc')
    setup = position('main', 'setup_arch')
    if not (position('main', 'os_init') < setup <
            position('main', 'task_create') < position('main', 'os_start')):
        raise ValueError('Runtime audit: OS/setup/task/scheduler ordering changed')
    return {'logger_init_before_clock_dump': True,
            'logger_mutex_constructor_linked': True,
            'logger_buffer_allocation_linked': True,
            'setup_before_application_tasks_and_scheduler': True,
            'device_execution_verified': False}
