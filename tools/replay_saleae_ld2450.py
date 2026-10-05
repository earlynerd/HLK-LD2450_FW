"""Replay transaction CSVs through the actual HLA using an offline API stand-in.

No Logic 2 process, hardware access, or non-standard Python dependencies.
Byte timestamps are interpolated from transaction bounds: the CSV does not
contain individual clock edges. All HLA output intervals are checked for order.
"""

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from saleae_api_stub import AnalyzerFrame, OutputValidator, load_hla

Hla = load_hla()

EXPECTED = {
    "radar_powerup.csv": (1921, 31, 0),
    "radar_moving_reflector.csv": (6968, 0, 1),
    "radar_moving_reflector_side.csv": (10730, 0, 0),
}


def validate_boot_block(path, output_dir):
    """Check both displays on the measured boot block and export all its I/Q."""
    csv.field_size_limit(10_000_000)
    with path.open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            raw = bytes.fromhex(row["miso"][2:])
            if len(raw) > 2056:
                break
        else:
            raise AssertionError("Boot block not found")
    t, duration = float(row["start_time"]), float(row["duration"])
    step = duration / len(raw)
    samples = []
    headers = []
    summaries = {}
    for mode in ("Packets", "I/Q samples"):
        hla = Hla()
        hla.display = mode
        validator = OutputValidator()
        counts = Counter()
        for index, value in enumerate(raw):
            frames = hla.decode(AnalyzerFrame(
                "result", t + index * step, t + (index + 0.95) * step,
                {"miso": bytes([value])}))
            for frame in validator.accept(frames):
                counts[frame.type] += 1
                if mode == "I/Q samples":
                    if frame.type == "header":
                        headers.append(frame.data)
                    if "i" in frame.data:
                        samples.append(dict(frame.data, start_s=frame.start_time, end_s=frame.end_time))
        if counts["header"] != 32 or counts["fragment"] != 31:
            raise AssertionError("Boot record counts changed")
        if mode == "Packets" and counts["packet"] != 1:
            raise AssertionError("Complete startup packet missing")
        if mode == "I/Q samples" and counts["tail"] != 1:
            raise AssertionError("Startup trailer missing")
        summaries[mode] = dict(counts)
    if len(samples) != 7944 or sum(s["packet_valid"] for s in samples) != 256:
        raise AssertionError("Boot I/Q data was omitted or validated incorrectly")
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "boot_iq.csv"
    columns = ["start_s", "end_s", "record", "rx", "chirp", "sample", "raw_word",
               "i", "q", "packet_valid", "checksum_checked", "status"]
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(samples)
    result = {
        "capture": path.name, "bytes": len(raw), "start_s": t, "duration_s": duration,
        "display_frame_counts": summaries, "decoded_iq_pairs": len(samples),
        "unvalidated_pairs": sum(not s["packet_valid"] for s in samples),
        "validated_pairs": sum(s["packet_valid"] for s in samples),
        "headers": headers, "output_timestamps_ordered_and_nonoverlapping": True,
        "iq_csv": str(csv_path),
    }
    (output_dir / "boot_validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("Boot block: 32 decoded headers, 7,944 I/Q pairs; 7,688 unvalidated and 256 validated", flush=True)
    return result


def replay(path):
    hla = Hla()
    validator = OutputValidator()
    counts = Counter()
    sample_counts = Counter()
    checksum_failures = sequence_failures = rows = 0
    csv.field_size_limit(10_000_000)
    started = time.perf_counter()
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            rows += 1
            text = row["miso"]
            raw = bytes.fromhex(text[2:] if text.startswith("0x") else text)
            t, duration = float(row["start_time"]), float(row["duration"])
            validator.accept(hla.decode(AnalyzerFrame("enable", t, t, {})))
            if raw:
                step = duration / len(raw)
                for index, value in enumerate(raw):
                    frames = hla.decode(AnalyzerFrame(
                        "result", t + index * step, t + (index + 0.95) * step,
                        {"miso": bytes([value]), "mosi": b"\x00"}))
                    for frame in validator.accept(frames):
                        counts[frame.type] += 1
                        if frame.type == "packet":
                            sample_counts[frame.data["samples"]] += 1
                            checksum_failures += not frame.data["checksum_ok"]
                            sequence_failures += frame.data["sequence"].startswith(("GAP", "outside"))
                        elif frame.type == "fragment" and frame.data["status"] not in (
                                "INCOMPLETE", "STARTUP / NO TRAILER"):
                            raise AssertionError("Unexpected framing error at CSV row %d" % (rows + 1))
                        elif frame.type == "error":
                            raise AssertionError(frame.data["message"])
            validator.accept(hla.decode(AnalyzerFrame("disable", t + duration, t + duration, {})))
            if rows % 2500 == 0:
                print("%s: %d transactions, %d packets" % (path.name, rows, counts["packet"]), flush=True)

    pending = hla.stream.finish()
    if checksum_failures or sequence_failures:
        raise AssertionError("Checksum/sequence failed")
    expected = EXPECTED.get(path.name)
    actual = (counts["packet"], counts["fragment"], len(pending))
    if expected is not None and actual != expected:
        raise AssertionError("%s counts %r != expected %r" % (path.name, actual, expected))
    with path.open("rb") as stream:
        digest = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    result = {
        "capture": path.name,
        "sha256": digest.hexdigest(),
        "transactions": rows,
        "hla_frames": dict(counts),
        "complete_packets": counts["packet"],
        "sample_counts": dict(sample_counts),
        "checksum_failures": checksum_failures,
        "sequence_failures": sequence_failures,
        "capture_end_fragments": [
            {"header": "0x%08X" % e.header.word, "buffered_bytes": len(e.raw)} for e in pending],
        "output_timestamps_ordered_and_nonoverlapping": True,
        "elapsed_s": round(time.perf_counter() - started, 3),
    }
    print(json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("captures", nargs="*", type=Path)
    parser.add_argument("--boot-only", action="store_true", help="Validate/export just the measured startup block")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "output" / "saleae_ld2450" / "validation.json")
    args = parser.parse_args()
    boot = validate_boot_block(ROOT / "radar_powerup.csv", args.output.parent)
    if args.boot_only:
        return
    captures = args.captures or [ROOT / name for name in EXPECTED]
    results = [replay(path) for path in captures]
    report = {"validation": "offline HLA replay with documented Saleae API stand-in",
              "tested_inside_logic2": False, "display": "Packets", "spi_bits_per_transfer": 8,
              "extension_version": "0.2.0", "boot_block": boot, "captures": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
