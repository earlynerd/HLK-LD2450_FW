"""Decode the actual 16-chirp C producer, including short writes and skips."""
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from frame_stream import Parser,Frames

# Optional second argument: radar record size the producer was built with.
pairs=int(sys.argv[2]) if len(sys.argv)>2 else 512
record=8+4*pairs
window=88+36+32*(45+4*pairs)
with tempfile.TemporaryDirectory() as folder:
    wire=Path(folder)/'stream.ldf'
    subprocess.run([sys.argv[1],str(wire)],check=True)
    data=wire.read_bytes()
    assert len(data)==2*window
    p,f=Parser(),Frames();complete=[]
    for offset in range(0,len(data),61):
        for m in p.feed(data[offset:offset+61]):
            if m is not None and m.kind==2:assert m.payload[0]==0
            frame=f.accept(m)
            if frame:complete.append(frame)
    assert [x['frame_id'] for x in complete]==[1,3]
    assert p.errors==f.rejected==f.protocol_errors==0
    for frame in complete:
        assert frame['chirps']==16 and frame['pairs']==pairs
        assert list(map(len,frame['lanes']))==[16*record]*2
        for lane in range(2):
            for chirp in range(16):
                raw=frame['lanes'][lane][chirp*record:(chirp+1)*record]
                assert struct.unpack(f'>{2*pairs}H',raw[4:-4])==tuple((chirp*7919+j*71+lane*12345)&65535 for j in range(2*pairs))
    # END must not turn a truncated window into a complete one.
    messages=list(Parser().feed(data[:window]));bad=Frames()
    for m in messages[:-2]:assert bad.accept(m) is None
    assert bad.accept(messages[-1]) is None
    assert bad.completed==0 and bad.rejected==1
print(f'16-chirp raw C/Python exact roundtrip ({pairs} pairs), skipped frame, and truncation passed')
