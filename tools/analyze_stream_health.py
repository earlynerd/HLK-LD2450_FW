"""Explain LDF1 aborts and screen lossless predictors on validated records.

Aborted frame prefixes are used only for codec-size screening, never promoted
to complete radar frames. Estimates are not an implemented wire codec or target
CPU timing. Input bytes remain unchanged.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import struct
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "firmware" / "tools"))
from frame_stream import Parser, Frames

REASONS = {1: "prior frame incomplete", 2: "invalid radar record or sequence",
           3: "output queue full", 4: "timeout (reserved)",
           5: "acquisition or USB gap", 6: "CPU backlog guard"}


def estimate(values, previous):
    if previous is None:
        return {name: 2057 for name in ("previous_chirp", "previous_sample", "gradient_2d")}
    delta = values - previous
    left = np.concatenate((previous[:2], values[:-2]))
    gradient = np.concatenate((delta[:2], delta[2:] - delta[:-2]))
    results = {}
    for name, residual in (("previous_chirp", delta), ("previous_sample", values - left),
                           ("gradient_2d", gradient)):
        zigzag = np.where(residual < 0, -2 * residual - 1, 2 * residual)
        maxima = zigzag.reshape(32, 32).max(axis=1)
        widths = np.frexp(maxima)[1]
        results[name] = min(2057, 9 + 32 + 4 * int(widths.sum()))
    return results


def analyze(path):
    parser, frames = Parser(), Frames()
    events, current = [], None
    digest = hashlib.sha256()
    initial_resync = None
    with path.open("rb") as stream:
        while data := stream.read(65536):
            digest.update(data)
            for message in parser.feed(data):
                before_errors = frames.protocol_errors
                complete = frames.accept(message)
                if message is None:
                    current = None
                    continue
                if frames.protocol_errors != before_errors:
                    current = None
                    continue
                if message.kind == 1:
                    current = dict(frame_id=message.frame, started_us=message.timestamp_us,
                                   wire_bytes=88, records=0, last_chirp=[-1, -1],
                                   estimated_wire_bytes=defaultdict(lambda: 88))
                elif current:
                    current["wire_bytes"] += 36 + len(message.payload)
                    if message.kind == 2 and frames.current:
                        records = frames.current["lanes"][message.lane]
                        raw = records[-1]
                        values = np.frombuffer(raw[4:-4], dtype=">i2").astype(np.int32)
                        previous = (np.frombuffer(records[-2][4:-4], dtype=">i2").astype(np.int32)
                                    if len(records) > 1 else None)
                        sizes = estimate(values, previous)
                        if sizes["previous_chirp"] != len(message.payload):
                            raise ValueError("Estimate disagrees with existing encoder: unsupported input codec")
                        for name, size in sizes.items():
                            current["estimated_wire_bytes"][name] += 36 + size
                        current["records"] += 1
                        current["last_chirp"][message.lane] = message.chirp
                    elif message.kind in (3, 4):
                        current["outcome"] = "complete" if complete else "abort"
                        current["elapsed_us"] = (message.timestamp_us - current["started_us"]) & 0xffffffff
                        for name in current["estimated_wire_bytes"]:
                            current["estimated_wire_bytes"][name] += 36 + len(message.payload)
                        if message.kind == 4:
                            reason, = struct.unpack("<I", message.payload)
                            current["abort_reason"] = reason
                            current["abort_label"] = REASONS.get(reason, "unknown")
                        if complete and initial_resync is None:
                            initial_resync = parser.discarded_bytes
                        events.append(current)
                        current = None
    groups = {}
    for outcome in ("complete", "abort"):
        selected = [event for event in events if event["outcome"] == outcome]
        totals = {name: sum(e["estimated_wire_bytes"][name] for e in selected)
                  for name in ("previous_chirp", "previous_sample", "gradient_2d")}
        groups[outcome] = dict(frames=len(selected), validated_records=sum(e["records"] for e in selected),
                               actual_wire_bytes=sum(e["wire_bytes"] for e in selected),
                               estimated_wire_bytes=totals)
    return dict(source=str(path), stream_sha256=digest.hexdigest(), bytes=path.stat().st_size,
                complete_frames=frames.completed, rejected_frames=frames.rejected,
                parser_errors=parser.errors, discarded_bytes=parser.discarded_bytes,
                initial_resync_bytes=initial_resync, protocol_errors=frames.protocol_errors,
                partial_tail=bool(parser.buffer or frames.current),
                abort_reasons=dict(Counter(e["abort_label"] for e in events if e["outcome"] == "abort")),
                predictor_screen=groups, events=events,
                scope="Validated records, including incomplete frame prefixes. Predictor size estimates only; target cost unmeasured.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    result = analyze(args.input)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "events"}, indent=2))
