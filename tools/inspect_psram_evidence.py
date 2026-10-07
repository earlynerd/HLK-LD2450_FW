"""Inspect known stock startup/boot metadata for PSRAM evidence; no device I/O.

Immediate names/offsets follow the startup ABI checked by audit_image.py.
This establishes static configuration evidence, not physical RAM presence.
"""
from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
FIELDS = [
    (0x14, "c0ff", "psram_load_address"),
    (0x1a, "c1ff", "psram_virtual_address"),
    (0x20, "c2ff", "psram_copy_bytes"),
    (0x36, "c3ff", "bss_address"),
    (0x3e, "c2ff", "bss_bytes"),
    (0x62, "c4ff", "data_address"),
    (0x68, "c1ff", "data_load_address"),
    (0x6e, "c2ff", "data_bytes"),
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inspect(stem, version):
    base = ROOT / "output/ufw_analysis" / stem / "flash_images/flash.bin"
    app_path = base / "files/app.bin"
    app = app_path.read_bytes()
    fields = {}
    for offset, opcode, name in FIELDS:
        if app[offset:offset + 2] != bytes.fromhex(opcode):
            raise ValueError(f"{version}: unexpected startup instruction at {offset:#x}")
        value = struct.unpack_from("<I", app, offset + 2)[0]
        fields[name] = {"instruction_offset": hex(offset), "value": value,
                        "hex": hex(value)}

    config_path = base / "top/isd_config.ini"
    config = config_path.read_bytes()
    # These two known packed configurations have a 34-byte prefix, followed
    # by length, NUL-terminated ASCII key, and exactly length bytes of value.
    if config[34:39] != b"\x07SPI\x00":
        raise ValueError(f"{version}: unrecognized packed boot configuration")
    entries = []
    offset = 34
    while offset < len(config):
        start = offset
        size = config[offset]
        end = config.index(0, offset + 1)
        key = config[offset + 1:end].decode("ascii")
        offset = end + 1 + size
        if offset > len(config):
            raise ValueError("Truncated boot configuration value")
        entries.append({"offset": hex(start), "key": key,
                        "value_hex": config[end + 1:offset].hex()})
    boot = (base / "top/uboot.boot").read_bytes()
    return {
        "version": version,
        "app": {"path": app_path.relative_to(ROOT).as_posix(),
                "sha256": digest(app), "startup": fields},
        "boot_config": {"path": config_path.relative_to(ROOT).as_posix(),
                        "sha256": digest(config), "entries": entries,
                        "psram_key_present": any(e["key"].upper() == "PSRAM" for e in entries)},
        "bootloader_sha256": digest(boot),
        "bootloader_psram_string_offset": boot.find(b"PSRAM\x00"),
    }


def main():
    report = {
        "scope": "Static analysis only; no device connection or RAM probe",
        "limitation": "No boot key and zero startup copy do not prove physical absence or exclude later initialization",
        "sources": [inspect("oncstzcza54pd", "V2.04"),
                    inspect("5o09fdkye1jo8", "V2.14")],
    }
    output = ROOT / "output/psram_analysis/static_evidence.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for source in report["sources"]:
        fields = source["app"]["startup"]
        print(f"{source['version']}: PSRAM copy={fields['psram_copy_bytes']['value']} bytes; "
              f"data address={fields['data_address']['hex']}; "
              f"PSRAM boot key={source['boot_config']['psram_key_present']}")
    print(output)


if __name__ == "__main__":
    main()
