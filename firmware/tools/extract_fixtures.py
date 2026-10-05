"""Extract small byte-exact golden inputs from the original Saleae CSV."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = "0a6d19e5329865a709f2bf306d8ff629fc72ddf868dd70e82c65f492be3ea1b4"


def main():
    source = ROOT / "radar_powerup.csv"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != EXPECTED:
        raise SystemExit("Original capture hash differs; do not replace golden inputs.")
    csv.field_size_limit(10_000_000)
    rows = []
    with source.open(newline="", encoding="utf-8-sig") as stream:
        for line, row in enumerate(csv.DictReader(stream), 2):
            rows.append((line, row["start_time"], bytes.fromhex(row["miso"].removeprefix("0x"))))
            if line == 17:
                break
    fixtures = [
        ("boot.bin", [rows[11]], "32 boot records; first 31 have no normal trailer"),
        ("steady-chirp0.bin", rows[12:14], "512 pairs; checksum 0x07E6"),
        ("steady-chirp1.bin", rows[14:16], "512 pairs; checksum 0xD99D"),
    ]
    out = ROOT / "firmware/tests/fixtures"
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"source": source.name, "source_sha256": digest, "lane": "CSV miso / RX2", "files": []}
    for name, selected, description in fixtures:
        data = b"".join(row[2] for row in selected)
        (out / name).write_bytes(data)
        manifest["files"].append({"file": name, "bytes": len(data),
                                  "sha256": hashlib.sha256(data).hexdigest(),
                                  "csv_lines_including_header": [r[0] for r in selected],
                                  "start_s": selected[0][1], "description": description})
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Extracted boot plus two steady packets from the unchanged power-up capture.")


if __name__ == "__main__":
    main()
