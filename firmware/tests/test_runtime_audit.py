"""Prevent the missing SDK logger initialization seen in the PA9 crash."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_runtime import audit_calls


SYMBOLS = {name: (addr, 4) for name, addr in {
    'setup_arch': 0x1e01000, 'log_early_init': 0x1e02000,
    'clock_dump': 0x1e03000, 'os_mutex_create': 0x2700,
    'malloc': 0x1e04000, 'os_init': 0x2800, 'task_create': 0x1e05000,
    'os_start': 0x2900}.items()}
GOOD = '''setup_arch:
 100: 80 ea 00 00 call 0 <log_early_init : 1e02000 >
 104: 80 ea 00 00 call 0 <clock_dump : 1e03000 >
log_early_init:
 200: 80 ea 00 00 call 0 <unrelated_alias_label : 2002700 >
 204: 80 ea 00 00 call 0 <malloc : 1e04000 >
main:
 300: 80 ea 00 00 call 0 <unrelated_alias_label : 2002800 >
 304: 80 ea 00 00 call 0 <setup_arch : 1e01000 >
 308: 80 ea 00 00 call 0 <task_create : 1e05000 >
 30c: 80 ea 00 00 call 0 <unrelated_alias_label : 2002900 >
'''


class RuntimeAuditTests(unittest.TestCase):
    def test_valid_including_ram_alias_calls(self):
        self.assertTrue(audit_calls(SYMBOLS, GOOD)['logger_mutex_constructor_linked'])

    def test_retained_initializer_without_call_is_rejected(self):
        # A symbol-presence check alone would miss this regression.
        broken = GOOD.replace('call 0 <log_early_init : 1e02000 >', 'nop')
        with self.assertRaisesRegex(ValueError, 'setup_arch -> log_early_init'):
            audit_calls(SYMBOLS, broken)

    def test_missing_mutex_constructor_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'log_early_init -> os_mutex_create'):
            audit_calls(SYMBOLS, GOOD.replace('2002700', '2002704'))

    def test_late_logger_is_rejected(self):
        bad = GOOD.replace('log_early_init : 1e02000', 'TEMP')
        bad = bad.replace('clock_dump : 1e03000', 'log_early_init : 1e02000')
        bad = bad.replace('TEMP', 'clock_dump : 1e03000')
        with self.assertRaisesRegex(ValueError, 'before clock dump'):
            audit_calls(SYMBOLS, bad)

    def test_scheduler_before_setup_is_rejected(self):
        bad = GOOD.replace('setup_arch : 1e01000', 'TEMP')
        bad = bad.replace('unrelated_alias_label : 2002900', 'setup_arch : 1e01000')
        bad = bad.replace('TEMP', 'unrelated_alias_label : 2002900')
        with self.assertRaisesRegex(ValueError, 'ordering changed'):
            audit_calls(SYMBOLS, bad)


if __name__ == '__main__':
    unittest.main()
