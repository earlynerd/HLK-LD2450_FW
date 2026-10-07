"""Explicit image/ports/hash bench upload with PA9 capture and optional stop/report.
Run only with authorization to flash and operate the radar.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import threading
import time
import serial
from package_ufw import container
from uart_upload import Peer, upload


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image',type=Path,required=True)
    p.add_argument('--sha256',required=True)
    p.add_argument('--port',required=True)
    p.add_argument('--debug-port',required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--seconds',type=float,default=12)
    p.add_argument('--stop-report',action='store_true')
    a=p.parse_args()
    raw=a.image.read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=a.sha256: p.error('Image hash does not match requested image')
    container(raw)
    a.out.mkdir(parents=True,exist_ok=False)
    report=dict(image=str(a.image.resolve()),sha256=digest,port=a.port,debug_port=a.debug_port,
                started_utc=datetime.now(timezone.utc).isoformat(),stop_report=a.stop_report)
    ports=[];stop=threading.Event();debug=bytearray();thread=None
    def open_port(name,baud):
        s=serial.Serial(port=None,baudrate=baud,timeout=0.02,write_timeout=2,rtscts=False,dsrdtr=False)
        s.dtr=s.rts=False;s.port=name;s.open();ports.append(s);return s
    def collect(port):
        try:
            with (a.out/'pa9.bin').open('xb') as f:
                while not stop.is_set():
                    data=port.read(max(1,port.in_waiting))
                    if data: debug.extend(data);f.write(data);f.flush()
        except Exception as e: report['capture_error']=repr(e)
    peer=Peer(raw,256000)
    try:
        pa9=open_port(a.debug_port,115200);module=open_port(a.port,256000)
        thread=threading.Thread(target=collect,args=(pa9,));thread.start()
        print('Uploading SHA256',digest,'to',a.port,flush=True)
        upload(module,peer,timeout=20)
        report['upload_complete']=peer.complete
        deadline=time.monotonic()+a.seconds
        with (a.out/'module-post.bin').open('xb') as f:
            while time.monotonic()<deadline: f.write(module.read(max(1,module.in_waiting)))
            if a.stop_report:
                module.write(b'?');module.flush();deadline=time.monotonic()+2
                while time.monotonic()<deadline: f.write(module.read(max(1,module.in_waiting)))
    except Exception as e: report['error']=repr(e)
    finally:
        stop.set()
        if thread: thread.join(timeout=3)
        for s in ports: s.close()
        report.update(read_requests=peer.read_requests,reported_size=peer.reported_size,
                      loader_staged=peer.loader_staged,device_error=peer.error,pa9_bytes=len(debug))
        (a.out/'pa9.txt').write_text(debug.decode('utf-8',errors='replace'),encoding='utf-8')
        (a.out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2));print(debug[-3000:].decode('utf-8',errors='replace'))
    return 0 if report.get('upload_complete') and 'error' not in report and 'capture_error' not in report else 1


if __name__=='__main__': raise SystemExit(main())
