"""Put stock Hi-Link V2.14 firmware back on an LD2450 that runs a custom image.

Running this CLI writes firmware to hardware (--check-only does not). It serves
the repository's pinned stock V2.14 UFW through the custom image's UART updater
on the module port at 256000 baud, then checks that stock firmware answers on
the same port: target report frames and a firmware-version reply at 9600 baud,
the rate V2.14 starts at after this update.

The stock application, bootloader and configuration files are sent unchanged.
Only the vendor flash-writing loader, which runs during the transfer, gets the
two bench-established two-wire UART fixes (patch_stock_uart_loader.py). Without
them the loader does not receive on the module's two-wire port at 256000.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import struct
import time

from patch_stock_uart_loader import patch_image
from uart_upload import Peer, upload

ROOT = Path(__file__).resolve().parents[2]
STOCK = ROOT/'5o09fdkye1jo8.ufw'
STOCK_SHA = 'b50856945e587f02e04e693002e8ff23640412d048464e2ceeb041a17b95c093'
RESTORE_SHA = '0e9d61d09de6653dc8e36a83f61e2b4ec4e74bc0ef233731099bd3f55c11316d'
REPORT_HEAD, REPORT_TAIL = b'\xaa\xff\x03\x00', b'\x55\xcc'
CMD_HEAD, CMD_TAIL = b'\xfd\xfc\xfb\xfa', b'\x04\x03\x02\x01'


def build(out):
    """Write the restore image (stock V2.14 with the patched loader) and return its bytes."""
    if hashlib.sha256(STOCK.read_bytes()).hexdigest() != STOCK_SHA:
        raise ValueError(f'{STOCK.name} is not the pinned stock V2.14 UFW')
    path = out/'update-two-wire.ufw'
    patch_image(STOCK, path)
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != RESTORE_SHA:
        raise ValueError('Restore image differs from the bench-verified build')
    return data


def signed(word):
    """Stock report coordinates: bit 15 set means positive."""
    return (word & 0x7fff) if word & 0x8000 else -(word & 0x7fff)


def report_frames(data):
    """Targets of every complete 30-byte stock report frame in data."""
    frames, i = [], 0
    while (i := data.find(REPORT_HEAD, i)) >= 0:
        if data[i+28:i+30] == REPORT_TAIL:
            targets = []
            for k in range(3):
                x, y, v, res = struct.unpack_from('<4H', data, i+4+8*k)
                if x or y or v or res:
                    targets.append(dict(x_mm=signed(x), y_mm=signed(y), speed_cms=signed(v), resolution_mm=res))
            frames.append(targets)
        i += 1
    return frames


def command(word, value=b''):
    body = struct.pack('<H', word)+value
    return CMD_HEAD+struct.pack('<H', len(body))+body+CMD_TAIL


def version(data):
    """Firmware version from a 0x01A0 acknowledgement, e.g. V2.14.25112412."""
    i = data.find(CMD_HEAD+b'\x0c\x00\xa0\x01\x00\x00')
    if i < 0 or data[i+18:i+22] != CMD_TAIL: return None
    body = data[i+6:i+18]
    return f'V{body[7]}.{body[6]:02X}.{struct.unpack_from("<I", body, 8)[0]:08X}'


def check(port_name, baud, seconds=10.0):
    """Wait for stock report frames, then ask for the firmware version."""
    import serial
    result = dict(port=port_name, baud=baud)
    with serial.Serial(port_name, baud, timeout=0.1) as port:
        data, end = b'', time.monotonic()+seconds
        while time.monotonic() < end and len(report_frames(data)) < 10:
            data += port.read(512)
        frames = report_frames(data)
        result.update(report_frames=len(frames), last_targets=frames[-1] if frames else None)
        port.reset_input_buffer()
        for word, value in ((0xff, b'\x01\x00'), (0xa0, b''), (0xfe, b'')):
            port.write(command(word, value)); time.sleep(0.3)
        result['firmware_version'] = version(port.read(4096))
    result['stock_running'] = bool(frames) and result['firmware_version'] is not None
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', required=True, help='Module UART port, e.g. COM13; never auto-detected')
    p.add_argument('--initial-baud', type=int, default=256000, help='Custom image updater rate')
    p.add_argument('--check-baud', type=int, default=9600, help='Stock rate after the update')
    p.add_argument('--check-only', action='store_true', help='Only check for stock firmware; write nothing')
    p.add_argument('--out', type=Path, help='Evidence folder (default output/stock_restore/<time>)')
    a = p.parse_args()
    out = a.out or ROOT/'output'/'stock_restore'/datetime.now().strftime('%Y%m%d-%H%M%S')
    out.mkdir(parents=True, exist_ok=True)
    result = dict(started=datetime.now().astimezone().isoformat())
    if not a.check_only:
        image = build(out)
        result.update(stock_sha256=STOCK_SHA, restore_sha256=RESTORE_SHA)
        import serial
        peer = Peer(image, a.initial_baud)
        port = serial.Serial(port=None, baudrate=a.initial_baud, timeout=0.02, write_timeout=2,
                             rtscts=False, dsrdtr=False)
        port.dtr = False; port.rts = False; port.port = a.port; port.open()
        print(f'Waiting for the custom updater on {a.port}. If nothing happens, power-cycle the module.')
        with port:
            upload(port, peer)
        result['read_requests'] = peer.read_requests
        print(f'Programming finished after {peer.read_requests} reads; checking for stock firmware.')
        time.sleep(2.0)
    result['check'] = check(a.port, a.check_baud)
    (out/'result.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    c = result['check']
    if c['stock_running']:
        print(f"Stock firmware {c['firmware_version']} is running: {c['report_frames']} report frames at {a.check_baud} baud.")
    else:
        print(f'Stock firmware did not answer at {a.check_baud} baud; see {out/"result.json"}.')
    raise SystemExit(0 if c['stock_running'] else 1)


if __name__ == '__main__': main()
