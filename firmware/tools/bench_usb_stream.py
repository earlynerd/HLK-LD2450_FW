"""Capture explicit native CDC data and optionally stop/report over module UART."""
import argparse
import hashlib
import json
from pathlib import Path
import threading
import time
import serial
from serial.tools.list_ports import comports


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port',required=True)
    p.add_argument('--module-port',required=True)
    p.add_argument('--debug-port',required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--seconds',type=float,default=5)
    p.add_argument('--stall-seconds',type=float,default=0)
    p.add_argument('--stop-report',action='store_true')
    a=p.parse_args()
    identities={x.device:x for x in comports()}
    device=identities.get(a.port)
    if not device or (device.vid,device.pid,device.serial_number)!=(0x4c4a,0x4155,'LD2450-STREAM-01'):
        p.error('Native USB identity does not match stream firmware')
    if a.seconds<=0 or a.stall_seconds<0:p.error('Invalid duration')
    a.out.mkdir(parents=True,exist_ok=False)
    report={'port':a.port,'identity':device.hwid,'seconds':a.seconds,
            'stall_seconds':a.stall_seconds,'requested_dtr':True,'stop_report':a.stop_report}
    stop=threading.Event();ports=[];thread=None;debug=bytearray()
    def open_port(name,baud,dtr=False):
        s=serial.Serial(port=None,baudrate=baud,timeout=0.05,write_timeout=2,rtscts=False,dsrdtr=False)
        s.dtr=dtr;s.rts=False;s.port=name;s.open();ports.append(s);return s
    def collect(s):
        try:
            with (a.out/'pa9.bin').open('xb') as f:
                while not stop.is_set():
                    data=s.read(max(1,s.in_waiting))
                    if data:debug.extend(data);f.write(data);f.flush()
        except Exception as e:report['debug_error']=repr(e)
    try:
        pa9=open_port(a.debug_port,115200);uart=open_port(a.module_port,256000)
        thread=threading.Thread(target=collect,args=(pa9,));thread.start()
        usb=open_port(a.port,115200)
        usb.dtr=True
        if a.stall_seconds:time.sleep(a.stall_seconds)
        start=time.monotonic();total=0;digest=hashlib.sha256()
        with (a.out/'stream.ldf').open('xb') as f:
            while time.monotonic()-start<a.seconds:
                data=usb.read(4096);f.write(data);digest.update(data);total+=len(data)
        report.update(received_bytes=total,read_elapsed_seconds=time.monotonic()-start,stream_sha256=digest.hexdigest())
        if a.stop_report:
            uart.write(b'?');uart.flush();time.sleep(2)
    except Exception as e:report['error']=repr(e)
    finally:
        stop.set()
        if thread:thread.join(timeout=3)
        for s in reversed(ports):s.close()
        (a.out/'pa9.txt').write_text(debug.decode(errors='replace'))
        (a.out/'capture.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2));print(debug[-3500:].decode(errors='replace'))
    return 1 if 'error' in report or 'debug_error' in report else 0


if __name__=='__main__':raise SystemExit(main())
