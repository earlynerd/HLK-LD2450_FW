"""Stock LD2450 configuration entry and a no-image UART updater probe.

The probe sends configuration commands and READY only. It deliberately never
answers START or a file request, so it cannot stage a loader or write firmware.
An accepted B2 may leave the application in update mode until power-cycled.
"""
import argparse
import json
from pathlib import Path
import struct
import time

from uart_upload import Parser, frame

HEADER = bytes.fromhex('fd fc fb fa')
FOOTER = bytes.fromhex('04 03 02 01')


def command_frame(command, data=b''):
    payload = struct.pack('<H', command) + data
    return HEADER + struct.pack('<H', len(payload)) + payload + FOOTER


class CommandParser:
    def __init__(self):
        self.buffer = bytearray()

    def feed(self, data):
        self.buffer.extend(data)
        result = []
        while len(self.buffer) >= 4:
            if self.buffer[:4] != HEADER:
                del self.buffer[0]
                continue
            if len(self.buffer) < 6:
                break
            size = struct.unpack_from('<H', self.buffer, 4)[0]
            if not 4 <= size <= 256:
                del self.buffer[0]
                continue
            if len(self.buffer) < size + 10:
                break
            if self.buffer[size+6:size+10] != FOOTER:
                del self.buffer[0]
                continue
            result.append(bytes(self.buffer[6:size+6]))
            del self.buffer[:size+10]
        return result


class StockSession:
    def __init__(self, port, trace=None):
        self.port = port
        self.trace = trace if trace is not None else []
        self.start = time.monotonic()
        self.parser = CommandParser()
        self.version = None

    def record(self, direction, data):
        self.trace.append({'seconds': round(time.monotonic()-self.start, 6),
                           'direction': direction, 'baud': self.port.baudrate,
                           'hex': data.hex(' ')})

    def write(self, data):
        self.record('tx', data)
        if self.port.write(data) != len(data):
            raise IOError('Short serial write')
        self.port.flush()

    def read(self):
        data = self.port.read(1)
        if data:
            self.record('rx', data)
        return data

    def command(self, command, data=b'', timeout=2.0):
        self.parser.buffer.clear()
        self.write(command_frame(command, data))
        deadline = time.monotonic() + timeout
        last_byte = time.monotonic()
        while time.monotonic() < deadline:
            raw = self.read()
            now = time.monotonic()
            if raw:
                if now-last_byte > 0.1:
                    self.parser.buffer.clear()
                last_byte = now
            for payload in self.parser.feed(raw):
                response, status = struct.unpack_from('<HH', payload)
                if response != command | 0x100:
                    continue
                if status:
                    raise RuntimeError(f'Command 0x{command:02x} rejected: status 0x{status:04x}')
                return payload[4:]
        raise TimeoutError(f'No ACK for command 0x{command:02x}')

    def enter(self):
        self.command(0xff, b'\x01\x00')
        self.version = self.command(0xa0)
        print(f'Stock version response: {self.version.hex(" ")}')
        self.command(0xb2)
        return self.version

    def probe(self, timeout=3.0):
        parser = Parser()
        deadline = time.monotonic() + timeout
        ready_at = 0.0
        last_byte = time.monotonic()
        while time.monotonic() < deadline:
            now = time.monotonic()
            if now >= ready_at:
                self.write(frame(b'\x06'))
                ready_at = now + 1.0
            raw = self.read()
            if raw:
                if now-last_byte > 0.1:
                    parser.buffer.clear()
                last_byte = now
            for payload in parser.feed(raw):
                if payload == b'\x01' or (len(payload) == 5 and payload[0] == 1
                        and 9600 <= struct.unpack_from('<I', payload, 1)[0] <= 1000000):
                    return payload
        raise TimeoutError('No valid updater START after READY')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', required=True)
    parser.add_argument('--baud', type=int, default=256000)
    parser.add_argument('--log', type=Path, required=True)
    args = parser.parse_args()
    import serial
    port = serial.Serial(port=None, baudrate=args.baud, timeout=0.02,
                         write_timeout=2, rtscts=False, dsrdtr=False)
    port.dtr = False
    port.rts = False
    port.port = args.port
    trace = []
    report = {'port': args.port, 'baud': args.baud, 'image_bytes_sent': 0,
              'trace': trace, 'result': 'not started'}
    # Fail before touching the device if the required evidence path is unusable.
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.log.write_text(json.dumps(report, indent=2), encoding='utf-8')
    try:
        port.open()
        with port:
            session = StockSession(port, trace)
            try:
                report['version_hex'] = session.enter().hex(' ')
                report['start_hex'] = session.probe().hex(' ')
                report['result'] = 'updater START observed; not acknowledged'
            except (TimeoutError, RuntimeError) as exc:
                report['result'] = str(exc)
                # B2 can switch parsers before an ACK is observed. Try READY
                # without acknowledging START, then end configuration if absent.
                try:
                    report['start_hex'] = session.probe().hex(' ')
                    report['result'] += '; updater START observed; not acknowledged'
                except TimeoutError:
                    try:
                        session.command(0xfe)
                        report['cleanup'] = 'configuration ended'
                    except (TimeoutError, RuntimeError) as cleanup:
                        report['cleanup'] = str(cleanup)
            if session.version is not None:
                report['version_hex'] = session.version.hex(' ')
    finally:
        args.log.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(report['result'])
    print('No START acknowledgement or firmware data sent. Power-cycle after successful entry.')


if __name__ == '__main__':
    main()
