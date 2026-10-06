"""Explicit bench run: simultaneous PA9 capture and authorized hello upload."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import threading
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'firmware/tools'))
import serial
from stock_uart import StockSession
from uart_upload import Peer, upload
from package_ufw import container

p = argparse.ArgumentParser()
p.add_argument('--entry', choices=['stock', 'custom', 'capture'], required=True)
p.add_argument('--seconds', type=float, default=20)
p.add_argument('--image-build', choices=['hello-logfix', 'hello-repeat'], default='hello-logfix')
a = p.parse_args()
out = ROOT / 'output/stock_uart_compatibility' / ('hello_logfix_' + a.entry + '_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
out.mkdir(parents=True)
image = ROOT / 'firmware/build' / a.image_build / 'update-two-wire.ufw'
raw = image.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
assert sha == {'hello-logfix': '1ee98f1c057629b5ffefbd5e9605f73255826cea6ac182fae82b7b91ee59a51a',
               'hello-repeat': '05fafed95ed20aba1400bbeae2884a054d9716edae345850e02ceff23c4b1edb'}[a.image_build]
container(raw)
report = dict(image=str(image), image_sha256=sha, entry=a.entry, result='starting')
start = time.monotonic()
stop = threading.Event()
ports = []
debug = bytearray()
post = bytearray()

def open_port(name, baud):
    s = serial.Serial(port=None, baudrate=baud, timeout=0.02, write_timeout=2, rtscts=False, dsrdtr=False)
    s.dtr = False
    s.rts = False
    s.port = name
    s.open()
    ports.append(s)
    return s

def capture(s):
    try:
        with (out / 'com11-115200.bin').open('wb') as f, (out / 'pa9-chunks.jsonl').open('w') as log:
            while not stop.is_set():
                data = s.read(max(1, s.in_waiting))
                if data:
                    debug.extend(data)
                    f.write(data)
                    f.flush()
                    log.write(json.dumps(dict(seconds=round(time.monotonic()-start, 6), hex=data.hex()))+'\n')
                    log.flush()
    except Exception as exc:
        report['capture_error'] = repr(exc)

class RecordingPeer(Peer):
    def reply(self, payload):
        events.write(json.dumps(dict(seconds=round(time.monotonic()-start, 6), payload=payload.hex()))+'\n')
        events.flush()
        return super().reply(payload)

thread = None
peer = None
try:
    pa9 = open_port('COM11', 115200)
    module = open_port('COM13', 256000)
    thread = threading.Thread(target=capture, args=(pa9,))
    thread.start()
    print('PA9 capture active; evidence:', out, flush=True)
    if a.entry == 'stock':
        session = StockSession(module)
        try:
            session.command(0xff, b'\x01\x00')
            version = session.command(0xa0)
            report['version_hex'] = version.hex(' ')
            print('Stock version:', report['version_hex'], flush=True)
            if version != bytes.fromhex('00 01 14 02 12 24 11 25'):
                raise RuntimeError('Unexpected stock version; no firmware transfer attempted')
            session.command(0xb2)
        except Exception:
            try: session.command(0xfe)
            except Exception: pass
            raise
        finally:
            (out / 'stock-commands.json').write_text(json.dumps(session.trace, indent=2))
    if a.entry != 'capture':
        peer = RecordingPeer(raw, 256000)
        with (out / 'update-events.jsonl').open('w') as events:
            upload(module, peer)
        print('Device reported final success; collecting boot output.', flush=True)
    deadline = time.monotonic() + a.seconds
    while time.monotonic() < deadline:
        data = module.read(max(1, module.in_waiting))
        if data:
            post.extend(data)
    report['result'] = 'capture complete' if a.entry == 'capture' else 'device reported final success'
except Exception as exc:
    report['result'] = 'failed'
    report['error'] = repr(exc)
finally:
    stop.set()
    if thread: thread.join(timeout=3)
    for s in ports: s.close()
    (out / 'pa9.txt').write_text(debug.decode('utf-8', errors='replace'), encoding='utf-8')
    (out / 'com13-post.bin').write_bytes(post)
    (out / 'com13-post.txt').write_text(post.decode('utf-8', errors='replace'), encoding='utf-8')
    report.update(pa9_bytes=len(debug), postflash_bytes=len(post), heartbeat_count=post.count(b'HLK-LD2450_FW: hello; UART updater ready'), elapsed_seconds=round(time.monotonic()-start, 3))
    if peer: report.update(read_requests=peer.read_requests, complete=peer.complete, loader_staged=peer.loader_staged, device_error=peer.error, reported_size=peer.reported_size)
    (out / 'result.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2), flush=True)
    print('PA9 tail:\n' + debug[-2000:].decode('utf-8', errors='replace'), flush=True)
