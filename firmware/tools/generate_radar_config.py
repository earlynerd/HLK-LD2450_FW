"""Generate a C init profile and provenance report; never access a device.

Overrides address one-based write occurrences, not just register addresses:
register 0x41, for example, appears in both startup stages with different values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
MANIFEST = PROJECT / "output/radar_init/manifest.json"
PROFILE_NAMES = ("mode_1_rom", "mode_2_ram_initial")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def integer(value, label, maximum):
    if isinstance(value, bool):
        raise ValueError(f"{label} must be an integer")
    if isinstance(value, str):
        try:
            value = int(value, 0)
        except ValueError as error:
            raise ValueError(f"Invalid {label}: {value!r}") from error
    if not isinstance(value, int) or not 0 <= value <= maximum:
        raise ValueError(f"{label} must be in 0..{maximum}")
    return value


def table_bytes(writes):
    return b"".join(struct.pack("<BBH", w["register"], 0, w["value"]) for w in writes)


def load_profiles():
    raw_manifest = MANIFEST.read_bytes()
    manifest = json.loads(raw_manifest)
    for key, expected in {"record_bytes": 4, "entries_per_profile": 80,
                          "pre_spi_count": 75, "post_spi_count": 5,
                          "i2c_address_7bit": 0x20}.items():
        if manifest.get(key) != expected:
            raise ValueError(f"Unexpected extraction metadata: {key}")
    sources = manifest["sources"]
    if len(sources) != 2 or {s["version"] for s in sources} != {"V2.04", "V2.14"}:
        raise ValueError("Expected both V2.04 and V2.14 extraction sources")
    profiles, provenance = {}, []
    for source in sources:
        ufw = PROJECT / (source["stem"] + ".ufw")
        app = PROJECT / source["application"]
        ufw_raw, app_raw = ufw.read_bytes(), app.read_bytes()
        if digest(ufw_raw) != source["ufw_sha256"] or digest(app_raw) != source["app_sha256"]:
            raise ValueError(f"Firmware source hash mismatch: {source['version']}")
        provenance.append({k: source[k] for k in ("version", "stem", "ufw_sha256", "app_sha256")})
        for name in PROFILE_NAMES:
            table = source["tables"][name]
            entries = table["entries"]
            if len(entries) != 80:
                raise ValueError("Expected exactly 80 ordered writes")
            writes = []
            for sequence, entry in enumerate(entries, 1):
                stage = "pre_spi" if sequence <= 75 else "post_spi"
                if entry["sequence"] != sequence or entry["stage"] != stage:
                    raise ValueError("Write order/stage mismatch")
                reg = integer(entry["register"], "register", 0xff)
                value = integer(entry["value"], "value", 0xffff)
                if not reg:
                    raise ValueError("Unexpected register-zero sentinel in table")
                writes.append(dict(sequence=sequence, stage=stage, register=reg, value=value))
            raw = table_bytes(writes)
            offset = table["app_file_offset"]
            if digest(raw) != table["sha256"] or app_raw[offset:offset + len(raw)] != raw:
                raise ValueError(f"Recovered table integrity mismatch: {name}")
            if app_raw[offset + len(raw):offset + len(raw) + 4] != b"\0" * 4:
                raise ValueError(f"Missing recovered table sentinel: {name}")
            if name in profiles and profiles[name] != writes:
                raise ValueError(f"Profiles differ between firmware releases: {name}")
            profiles[name] = writes
    return profiles, {"extraction_manifest_sha256": digest(raw_manifest), "sources": provenance}


def customize(config, profiles):
    if not isinstance(config, dict) or set(config) != {"name", "base_profile", "overrides"}:
        raise ValueError("Config requires exactly name, base_profile, and overrides")
    name = config["name"]
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", name):
        raise ValueError("Profile name must be 1..80 ASCII letters/digits/dot/dash/underscore")
    base = config["base_profile"]
    if not isinstance(base, str) or base not in PROFILE_NAMES:
        raise ValueError(f"base_profile must be one of {PROFILE_NAMES}")
    if not isinstance(config["overrides"], list):
        raise ValueError("overrides must be a list")
    writes = [dict(w) for w in profiles[base]]
    changes, seen = [], set()
    for change in config["overrides"]:
        fields = {"sequence", "register", "expected", "value", "reason"}
        if not isinstance(change, dict) or set(change) != fields:
            raise ValueError(f"Each override requires exactly {sorted(fields)}")
        seq = integer(change["sequence"], "sequence", 80)
        if not seq or seq in seen:
            raise ValueError("Override sequences must be unique and in 1..80")
        seen.add(seq)
        reg = integer(change["register"], "register", 0xff)
        expected = integer(change["expected"], "expected", 0xffff)
        value = integer(change["value"], "value", 0xffff)
        reason = change["reason"]
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Every override requires a reason")
        entry = writes[seq - 1]
        if entry["register"] != reg or entry["value"] != expected:
            raise ValueError(f"Sequence {seq} register/expected guard does not match baseline")
        if value == expected:
            raise ValueError(f"Sequence {seq} override does not change the value")
        entry["value"] = value
        changes.append(dict(sequence=seq, stage=entry["stage"], register=f"0x{reg:02X}",
                            old=f"0x{expected:04X}", new=f"0x{value:04X}", reason=reason))
    return writes, changes


def generate(config_path, out):
    config_path, out = Path(config_path).resolve(), Path(out).resolve()
    config_raw = config_path.read_bytes()
    config = json.loads(config_raw)
    profiles, provenance = load_profiles()
    writes, changes = customize(config, profiles)
    raw = table_bytes(writes)
    header = ('/* Generated by generate_radar_config.py; edit the JSON profile instead. */\n'
              '#ifndef LD2450_RADAR_CONFIG_GENERATED_H\n#define LD2450_RADAR_CONFIG_GENERATED_H\n'
              '#include "ld2450_radar_init.h"\n#endif\n')
    source = ['/* Generated; preserves the stock write order and SPI boundary. */',
              '#include "radar_config_generated.h"', '',
              'static const struct ld2450_radar_write writes[LD2450_RADAR_INIT_COUNT] = {']
    for entry in writes:
        source.append(f'    {{0x{entry["register"]:02X}, 0x{entry["value"]:04X}}}, '
                      f'/* {entry["sequence"]:2}: {entry["stage"]} */')
    source += ['};', '', 'const struct ld2450_radar_profile ld2450_build_radar_profile = {',
               f'    "{config["name"]}", "{digest(raw)}", writes, LD2450_RADAR_INIT_COUNT', '};', '']
    metadata = dict(profile_name=config["name"], base_profile=config["base_profile"],
                    config_file=str(config_path), config_sha256=digest(config_raw),
                    baseline_table_sha256=digest(table_bytes(profiles[config["base_profile"]])),
                    table_sha256=digest(raw), write_count=80, pre_spi_count=75, post_spi_count=5,
                    i2c_address_7bit=0x20, changes=changes, **provenance,
                    generator_sha256=digest(Path(__file__).read_bytes()),
                    target_built=False, device_tested=False)
    out.mkdir(parents=True, exist_ok=True)
    (out / "radar_config_generated.h").write_text(header, encoding="utf-8")
    (out / "radar_config_generated.c").write_text("\n".join(source), encoding="utf-8")
    (out / "radar_config_records.bin").write_bytes(raw)
    (out / "radar_config_wire_inferred.bin").write_bytes(b"".join(
        bytes([0x40, w["register"], w["value"] >> 8, w["value"] & 0xff]) for w in writes))
    # These binaries are table/transaction data, never flashable images.
    (out / "radar_config_provenance.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/radar_baseline_mode2.json")
    parser.add_argument("--out", type=Path, default=ROOT / "build/radar-config")
    args = parser.parse_args()
    try:
        result = generate(args.config, args.out)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"Radar config generation failed: {error}\n")
    print(f"Generated {result['profile_name']}: 80 writes, {len(result['changes'])} changes")
    print(f"Table SHA-256: {result['table_sha256']} (source/data only; no target build)")


if __name__ == "__main__":
    main()
