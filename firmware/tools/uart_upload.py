"""Experimental PC peer for custom and stock-B2 UART update entry.

Running this CLI writes firmware to hardware. Building/importing it does not.
Stock-B2 entry is recovered from Hi-Link V2.14; V2.04 needs a BLE bridge first.
Stock transfer/handoff and target boot still require physical validation.
"""
import argparse
import binascii
from pathlib import Path
import struct
import time
from package_ufw import container


def frame(payload):
    if not 1 <= len(payload) <= 521: raise ValueError('Invalid payload length')
    raw=b'\xaa\x55'+struct.pack('<H',len(payload))+payload
    return raw+struct.pack('<H',binascii.crc_hqx(raw,0))


class Parser:
    def __init__(self): self.buffer=bytearray()
    def feed(self, data):
        self.buffer.extend(data)
        result=[]
        while len(self.buffer)>=2:
            if self.buffer[:2]!=b'\xaa\x55': del self.buffer[0]; continue
            if len(self.buffer)<4: break
            n=struct.unpack_from('<H',self.buffer,2)[0]
            if not 1<=n<=521: del self.buffer[0]; continue
            if len(self.buffer)<n+6: break
            raw=self.buffer[:n+6]; del self.buffer[:n+6]
            if binascii.crc_hqx(raw[:-2],0)==struct.unpack_from('<H',raw,n+4)[0]:
                result.append(bytes(raw[4:-2]))
        return result


class Peer:
    def __init__(self, image, baud):
        if not 9600<=baud<=1000000: raise ValueError('Unsupported baud')
        self.image=image; self.baud=baud; self.started=False
        self.loader_staged=False; self.complete=False; self.error=None
        self.read_requests=0; self.reported_size=0

    def reply(self, p):
        if not p: raise ValueError('Empty command')
        op=p[0]
        if op==1 and len(p) in (1,5):
            # The SDK/stock application sends START + current baud after
            # changing baud; our application sends the opcode alone.
            if len(p)==5 and not 9600<=struct.unpack_from('<I',p,1)[0]<=1000000:
                raise ValueError('Invalid device START baud')
            self.started=True
            return b'\x01'+struct.pack('<I',self.baud)
        if not self.started: raise ValueError('Data before START')
        if op==2 and len(p)==9:
            offset,count=struct.unpack_from('<II',p,1)
            if not 1<=count<=512 or offset+count>len(self.image):
                raise ValueError('Read outside UFW or supported chunk size')
            self.read_requests+=1
            return p+self.image[offset:offset+count]
        if op==3 and len(p)==2:
            if p[1]==0x80: self.loader_staged=True
            elif p[1]==0: self.complete=True
            else: self.error=p[1]
            return p
        if op==4 and len(p)==5:
            self.reported_size=struct.unpack_from('<I',p,1)[0]
            return b'\x04'
        if op==5 and len(p)==1: return b'\x05'
        raise ValueError(f'Unexpected opcode/length: {op}/{len(p)}')


def upload(port, peer, timeout=20.0):
    parser=Parser(); start=time.monotonic(); last=start; last_byte=start
    ready_at=0.0; completed_at=None; announced=False
    while True:
        now=time.monotonic()
        if now-last>timeout: raise TimeoutError('No valid device command before deadline')
        if not peer.started and now>=ready_at:
            port.write(frame(b'\x06')); port.flush(); ready_at=now+1.0
        data=port.read(1)
        if data:
            if now-last_byte>0.1: parser.buffer.clear()
            last_byte=now
        for p in parser.feed(data):
            reply=peer.reply(p)
            port.write(frame(reply)); port.flush(); last=time.monotonic()
            if p[0]==1 and port.baudrate!=peer.baud:
                port.baudrate=peer.baud  # Reply sent at old baud; next START uses new baud.
            if peer.loader_staged and not announced:
                print('Loader staged; waiting for its firmware requests.'); announced=True
            if peer.error is not None: raise RuntimeError(f'Device update error 0x{peer.error:02x}')
            if peer.complete and completed_at is None: completed_at=time.monotonic()
        # Allow retransmitted final STOP if its first acknowledgement was lost.
        if completed_at is not None and time.monotonic()-completed_at>2:
            return


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('image',type=Path)
    p.add_argument('--port',required=True,help='Explicit port, e.g. COM7; never auto-detected')
    p.add_argument('--baud',type=int,default=256000)
    p.add_argument('--initial-baud',type=int,default=256000,
                   help='Currently configured module UART rate')
    p.add_argument('--entry',choices=('custom','stock-b2'),default='custom',
                   help='stock-b2 sends configuration enable, version query and B2 first')
    a=p.parse_args(); raw=a.image.read_bytes(); container(raw)
    peer=Peer(raw,a.baud)
    try: import serial
    except ImportError: p.error('Install pyserial to use the hardware uploader.')
    # DTR/RTS remain deasserted; no assumed reset wiring.
    port=serial.Serial(port=None,baudrate=a.initial_baud,timeout=0.02,write_timeout=2,
                       rtscts=False,dsrdtr=False)
    port.dtr=False; port.rts=False; port.port=a.port; port.open()
    with port:
        if a.entry=='stock-b2':
            from stock_uart import StockSession
            session=StockSession(port)
            try:
                session.enter()
            except (TimeoutError,RuntimeError):
                try: session.command(0xfe)
                except (TimeoutError,RuntimeError): pass
                raise
        upload(port,peer)
    print(f'Device reported final success after {peer.read_requests} read requests. Verify the new boot banner.')


if __name__=='__main__': main()
