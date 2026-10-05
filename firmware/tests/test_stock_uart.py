from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from stock_uart import CommandParser, StockSession, command_frame
from uart_upload import frame


def ack(command, status=0, data=b''):
    return command_frame(command | 0x100, struct.pack('<H', status)+data)


class FakePort:
    baudrate = 256000

    def __init__(self, replies):
        self.replies = replies
        self.rx = bytearray()
        self.writes = []

    def write(self, data):
        self.writes.append(data)
        self.rx.extend(self.replies.get(data, b''))
        return len(data)

    def flush(self):
        pass

    def read(self, size):
        data = bytes(self.rx[:size])
        del self.rx[:size]
        return data


class StockTests(unittest.TestCase):
    def test_command_bytes(self):
        self.assertEqual(command_frame(0xff, b'\x01\x00').hex(),
                         'fdfcfbfa0400ff00010004030201')
        self.assertEqual(command_frame(0xb2).hex(), 'fdfcfbfa0200b20004030201')

    def test_parser_noise_corruption_partial_unrelated(self):
        p = CommandParser()
        valid = ack(0xa0, data=b'version')
        bad = bytearray(valid)
        bad[-1] ^= 1
        noise = b'\xaa\xff\x03\x00targets\x55\xcc'
        self.assertEqual(p.feed(noise+bad+valid[:5]), [])
        self.assertEqual(p.feed(valid[5:]), [b'\xa0\x01\x00\x00version'])
        self.assertEqual(p.feed(bytes.fromhex('fdfcfbfaffff')+valid),
                         [b'\xa0\x01\x00\x00version'])

    def test_probe_does_not_ack_start_or_serve_image(self):
        port = FakePort({
            command_frame(0xff, b'\x01\x00'): ack(0xff),
            command_frame(0xa0): ack(0xfe)+ack(0xa0, data=b'version'),
            command_frame(0xb2): ack(0xb2),
            frame(b'\x06'): frame(b'\x01')+frame(b'\x02'+struct.pack('<II', 0, 512)),
        })
        session = StockSession(port)
        self.assertEqual(session.enter(), b'version')
        self.assertEqual(session.probe(), b'\x01')
        self.assertEqual(port.writes, [command_frame(0xff, b'\x01\x00'),
            command_frame(0xa0), command_frame(0xb2), frame(b'\x06')])

    def test_negative_ack_stops_entry(self):
        port = FakePort({command_frame(0xff, b'\x01\x00'): ack(0xff, 1)})
        with self.assertRaisesRegex(RuntimeError, 'rejected'):
            StockSession(port).enter()
        self.assertEqual(len(port.writes), 1)

    def test_unrelated_ack_does_not_extend_deadline(self):
        port = FakePort({command_frame(0xb2): ack(0xa0)*10})
        session = StockSession(port)
        ticks = iter(i*0.01 for i in range(1000))
        with patch('stock_uart.time.monotonic', side_effect=lambda: next(ticks)):
            with self.assertRaisesRegex(TimeoutError, '0xb2'):
                session.command(0xb2, timeout=0.5)
        self.assertEqual(port.writes, [command_frame(0xb2)])

    def test_ready_timeout_never_sends_start(self):
        port = FakePort({})
        session = StockSession(port)
        ticks = iter(i*0.01 for i in range(1000))
        with patch('stock_uart.time.monotonic', side_effect=lambda: next(ticks)):
            with self.assertRaisesRegex(TimeoutError, 'START'):
                session.probe(timeout=2.5)
        self.assertTrue(port.writes)
        self.assertTrue(all(data == frame(b'\x06') for data in port.writes))


if __name__ == '__main__':
    unittest.main()
