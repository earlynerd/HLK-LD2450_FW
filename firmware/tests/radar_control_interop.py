"""Decode the C radar-control test stream: REPLY messages and BEGIN register generations."""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from frame_stream import Frames, Parser  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "control.ldf"
    subprocess.run([sys.argv[1], str(path)], check=True)
    parser, frames = Parser(), Frames()
    accepted = [f for m in parser.feed(path.read_bytes()) if (f := frames.accept(m))]
    assert parser.errors == 0 and frames.protocol_errors == 0 and frames.rejected == 0, vars(frames)
    assert [f["register_generation"] for f in accepted] == [0, 4, 4], [f["register_generation"] for f in accepted]
    assert len(frames.replies) == 1, frames.replies
    reply = frames.replies[0]
    assert (reply["tag"], reply["op"], reply["status"], reply["register"], reply["generation"],
            reply["values"]) == (0xABCD, 2, 0, 0x61, 4, [0x0023]), reply
    print("radar control interop: 3 frames, generations 0/4/4, WRITE reply decoded")
