"""Bench-only READY probe; intentionally does not answer START or send firmware."""
import json
from pathlib import Path
import sys
import time
from datetime import datetime, timezone
import serial

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'firmware/tools'))
from uart_upload import frame, Parser

out = ROOT / 'output/stock_uart_compatibility' / ('recovery_latch_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
out.mkdir()
ports=[]
pa9=bytearray()
module=bytearray()
report={'firmware_bytes_sent':0, 'result':'waiting for user power cycle'}
t0=time.monotonic()
probe_at=None
latched_at=None
boot_offset=0
parser=Parser()
starts=0
def open_port(name,baud):
    s=serial.Serial(port=None,baudrate=baud,timeout=.01,write_timeout=2,rtscts=False,dsrdtr=False)
    s.dtr=False;s.rts=False;s.port=name;s.open();ports.append(s);return s
try:
    debug=open_port('COM11',115200)
    uart=open_port('COM13',256000)
    print('Both captures active; power-cycle radar now. Evidence: '+str(out),flush=True)
    with (out/'events.jsonl').open('w') as log:
        def record(port,data):
            log.write(json.dumps({'seconds':round(time.monotonic()-t0,6),'port':port,'hex':data.hex()})+'\n');log.flush()
        while time.monotonic()-t0<120:
            data=debug.read(max(1,debug.in_waiting))
            if data: pa9.extend(data);record('COM11 RX',data)
            data=uart.read(max(1,uart.in_waiting))
            if data:
                module.extend(data);record('COM13 RX',data)
                for payload in parser.feed(data):
                    if probe_at is not None and payload[:1]==b'\x01': starts+=1
            if probe_at is None and b'UPDATE: boot recovery window 3000 ms; radar held off' in pa9:
                boot_offset=len(module)
                wire=frame(b'\x06');uart.write(wire);uart.flush();record('COM13 TX',wire)
                probe_at=time.monotonic()
                print('Boot window seen; sent READY once. Deliberately ignoring START.',flush=True)
            if probe_at is not None and latched_at is None and b'UPDATE: recovery latched until reset' in pa9:
                latched_at=time.monotonic()
                print('Recovery latch banner observed; watching for eight seconds without replying.',flush=True)
            if latched_at is not None and time.monotonic()-latched_at>=8:
                break
            if probe_at is not None and time.monotonic()-probe_at>20:
                raise RuntimeError('Recovery latch did not complete within observation limit')
    report.update(start_requests=starts,probe_sent=probe_at is not None,latched=latched_at is not None,
                  seconds_to_latch=None if latched_at is None else round(latched_at-probe_at,3),
                  observation_after_latch=None if latched_at is None else round(time.monotonic()-latched_at,3),
                  application_started=b'Hello world! Starting UART updater' in pa9,
                  heartbeat_after_probe=module[boot_offset:].count(b'HLK-LD2450_FW: hello; UART updater ready'))
    report['result']='passed' if report['latched'] and starts and not report['application_started'] and not report['heartbeat_after_probe'] else 'failed'
except Exception as exc:
    report.update(result='failed',error=repr(exc))
finally:
    for s in ports:s.close()
    (out/'com11.bin').write_bytes(pa9);(out/'com13.bin').write_bytes(module)
    (out/'pa9.txt').write_text(pa9.decode('utf-8',errors='replace'),encoding='utf-8')
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
