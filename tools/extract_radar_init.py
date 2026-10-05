"""Recover the two radar register profiles from the verified LD2450 applications.

The default extraction uses only Python's standard library, reads source files
without modifying them, and fails if their hashes/layout differ from this study.
Optional PI32v2 disassembly uses the pinned, project-local SLEIGH definitions.
This tool extracts data; it does not connect to or configure hardware.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 0x01E00120
COUNT = 80
PRE_SPI_COUNT = 75
SLEIGH_COMMIT = "8b7d50bef0dd15b1d56d668b75eb07d55b4cd92e"
PROFILE_HASHES = {
    "mode_1_rom": "e7a64440dcd2c8fb74fab45d31b0fd3d25499b4ee5aaf9f8ad2818d6c97ecd1b",
    "mode_2_ram_initial": "ff0a3715d077a864283e1222cf6746d9736749644bf5b5a4eb1ebd1fe89c5ec5",
}
SOURCES = [
    {
        "version": "V2.04", "stem": "oncstzcza54pd",
        "ufw_sha256": "a1b090ccb9aeaede130bec24d4414c09b5aa85ba81020f6ce123d1c9d6b4a277",
        "app_sha256": "a982ebd9030d4927c2777cd94f93ddd162a61a947e2bce008df24461a72157d5",
        "rom_offset": 0x21A24, "data_offset": 0x274B0,
        "data_size": 0x43AC, "ram_table_address": 0x40E4,
        "mode_address": 0x42B1,
        "write_helper": 0x10F7C, "pre_writer": 0x1B5A6,
        "post_writer": 0x1B900, "spi_init": 0x1B7C6,
        "boot_calls": {"pre_spi": 0x1B9FE, "spi": 0x1BA06, "post_spi": 0x1BA0E},
        "rom_pointer_refs": [0x1B5B8, 0x1B956],
        "ram_pointer_refs": [0x1B5D6, 0x1B930],
        "regions": [
            ("copy_initial_data_to_ram", 0x62, 0x7E),
            ("i2c_busy_wait", 0x10DBE, 0x10DC8),
            ("i2c_write_word", 0x10F7C, 0x10FF6),
            ("write_first_75", 0x1B5A6, 0x1B5F6),
            ("spi_initialization", 0x1B7C6, 0x1B900),
            ("write_last_5", 0x1B900, 0x1B976),
            ("radar_init_call_order", 0x1B9CA, 0x1BA18),
            ("saved_mode_selection_part", 0x1B04E, 0x1B07C),
            ("command_updates_ram_table", 0x117CC, 0x11804),
        ],
    },
    {
        "version": "V2.14", "stem": "5o09fdkye1jo8",
        "ufw_sha256": "b50856945e587f02e04e693002e8ff23640412d048464e2ceeb041a17b95c093",
        "app_sha256": "af7303edd409e18cebd38b7a06ca38f82a7cffc41907a582b2fd3eacc6dc03dc",
        "rom_offset": 0x22684, "data_offset": 0x285C4,
        "data_size": 0x43FC, "ram_table_address": 0x4124,
        "mode_address": 0x42F1,
        "write_helper": 0x10FEC, "pre_writer": 0x11368,
        "post_writer": 0x11758, "spi_init": 0x1163C,
        "boot_calls": {"pre_spi": 0x1C624, "spi": 0x1C62C, "post_spi": 0x1C634},
        "rom_pointer_refs": [0x1137A, 0x117AE],
        "ram_pointer_refs": [0x11398, 0x11788],
        "regions": [
            ("copy_initial_data_to_ram", 0x62, 0x7E),
            ("i2c_busy_wait", 0x10E2E, 0x10E38),
            ("i2c_write_word", 0x10FEC, 0x11066),
            ("write_first_75", 0x11368, 0x113B8),
            ("spi_initialization", 0x1163C, 0x11758),
            ("write_last_5", 0x11758, 0x117CE),
            ("radar_init_call_order", 0x1C620, 0x1C63C),
        ],
    },
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def app_path(source):
    return ROOT / "output/ufw_analysis" / source["stem"] / "flash_images/flash.bin/files/app.bin"


def require(condition, description):
    if not condition:
        raise ValueError(description)


def extract_source(source):
    path = app_path(source)
    data = path.read_bytes()
    require(digest(data) == source["app_sha256"], f"Unexpected application: {path}")
    ufw = ROOT / (source["stem"] + ".ufw")
    require(digest(ufw.read_bytes()) == source["ufw_sha256"], f"Unexpected UFW: {ufw}")
    # The boot entry loads destination RAM address zero, source .data address,
    # and copy byte count, before its word-copy loop at file offsets 0x74..0x7c.
    require(data[0x62:0x68] == bytes.fromhex("c4ff00000000"), "RAM copy destination changed")
    require(data[0x68:0x6E] == b"\xc1\xff" + struct.pack("<I", BASE + source["data_offset"]),
            "RAM copy source changed")
    require(data[0x6E:0x74] == b"\xc2\xff" + struct.pack("<I", source["data_size"]),
            "RAM copy size changed")
    require(data[0x74:0x7E] == bytes.fromhex("a2a212031305c305f25c"), "RAM word-copy loop changed")
    require(source["ram_table_address"] + COUNT * 4 + 4 <= source["data_size"],
            "RAM table exceeds initialized data")
    mode_initial = data[source["data_offset"] + source["mode_address"]]
    require(mode_initial == 2, "Compiled initial mode changed")
    for off in source["rom_pointer_refs"]:
        require(data[off:off+4] == struct.pack("<I", BASE + source["rom_offset"]),
                "ROM table code reference changed")
    for off in source["ram_pointer_refs"]:
        require(data[off:off+4] == struct.pack("<I", source["ram_table_address"]),
                "RAM table code reference changed")
    tables = {}
    for name, offset in [
        ("mode_1_rom", source["rom_offset"]),
        ("mode_2_ram_initial", source["data_offset"] + source["ram_table_address"]),
    ]:
        blob = data[offset:offset+COUNT*4]
        require(digest(blob) == PROFILE_HASHES[name], f"Unexpected {name} table")
        require(data[offset+COUNT*4:offset+COUNT*4+4] == bytes(4), "Missing zero terminator")
        entries = []
        for index in range(COUNT):
            reg, pad, value = struct.unpack_from("<BBH", blob, 4*index)
            require(pad == 0 and reg != 0, f"Unexpected record format at {index}")
            wire = bytes([0x40, reg, value >> 8, value & 255])
            entries.append({
                "sequence": index + 1,
                "stage": "pre_spi" if index < PRE_SPI_COUNT else "post_spi",
                "register": reg, "register_hex": f"0x{reg:02X}",
                "value": value, "value_hex": f"0x{value:04X}",
                "raw_record_hex": blob[index*4:index*4+4].hex(" ").upper(),
                "wire_bytes_inferred_hex": wire.hex(" ").upper(),
                "app_file_offset": offset + index*4,
            })
        tables[name] = {
            "app_file_offset": offset,
            "storage_address": BASE + offset if name == "mode_1_rom" else source["ram_table_address"],
            "sha256": digest(blob), "entries": entries,
        }
    metadata = {key: value for key, value in source.items() if key != "regions"}
    metadata.update(application=str(path.relative_to(ROOT)).replace("\\", "/"),
                    initialized_mode=mode_initial, tables=tables)
    return metadata, data


def prepare_spec():
    checkout = ROOT / "tmp/pi32_analysis/ghidra-jieli"
    revision = subprocess.run(["git", "-C", str(checkout), "rev-parse", "HEAD"],
                              check=True, capture_output=True, text=True).stdout.strip()
    require(revision == SLEIGH_COMMIT, "Unexpected processor-definition revision")
    target = ROOT / "tmp/pi32_analysis/spec"
    shutil.copytree(checkout / "data/languages", target, dirs_exist_ok=True)
    main = target / "pi32v2.slaspec"
    text = main.read_text(encoding="utf-8")
    text, count = re.subn(r"(?m)^(\w*:)\^", r'\1""^', text)
    require(count > 0, "Expected constructor-display compatibility changes missing")
    main.write_text(text, encoding="utf-8")
    flow = target / "pi32v2_ins_progflow.sinc"
    text = flow.read_text(encoding="utf-8")
    require(text.count("delayslot(nwords);") == 1, "Expected repeat delay-slot rule missing")
    text = text.replace("delayslot(nwords);",
                        "# Dynamic repeat delay slot omitted for disassembly-only use.")
    flow.write_text(text, encoding="utf-8")
    compiler = ROOT / "tmp/pi32_analysis/python/pypcode/bin/sleigh.exe"
    subprocess.run([str(compiler), str(main), str(target / "pi32v2.sla")],
                   check=True, timeout=60)


def decode_worker(args):
    sys.path.insert(0, str(ROOT / "tmp/pi32_analysis/python"))
    import pypcode
    language = next(lang for lang in pypcode.Arch(
        "JieLi", str(ROOT / "tmp/pi32_analysis/spec/JieLi.ldefs")
    ).languages if lang.id.startswith("pi32v2"))
    context = pypcode.Context(language)
    data = app_path(SOURCES[args.source_index]).read_bytes()
    offset = args.start
    records = []
    while offset < args.end:
        try:
            context.reset()
            ins = context.disassemble(data[offset:args.end], base_address=BASE+offset,
                                      max_instructions=1).instructions[0]
            require(ins.length >= 2 and offset + ins.length <= args.end, "Invalid instruction length")
            length, mnemonic, body = ins.length, ins.mnem, ins.body
        except Exception as error:
            length, mnemonic, body = min(2, args.end-offset), "UNDECODED", str(error)
        records.append(dict(offset=offset, address=BASE+offset, length=length,
                            bytes=data[offset:offset+length].hex(), mnemonic=mnemonic, body=body))
        offset += length
    print(json.dumps(records))


def disassemble(output):
    result = []
    # Isolate each region: incomplete third-party constructors can hang on some
    # instructions. A timeout makes that an explicit gap, never a fabricated decode.
    for index, source in enumerate(SOURCES):
        regions, flat = [], []
        for name, start, end in source["regions"]:
            command = [sys.executable, str(Path(__file__).resolve()), "--decode-worker",
                       "--source-index", str(index), "--start", str(start), "--end", str(end)]
            try:
                process = subprocess.run(command, check=True, capture_output=True,
                                         text=True, timeout=8)
                records = json.loads(process.stdout)
            except (subprocess.SubprocessError, json.JSONDecodeError) as error:
                raise RuntimeError(f"Could not decode {source['version']} {name}: {error}") from error
            require(all(rec["mnemonic"] != "UNDECODED" for rec in records),
                    f"Decoder gap in selected region: {source['version']} {name}")
            regions.append(dict(name=name, start_offset=start, end_offset=end, instructions=records))
            flat.extend(records)
        # Check the three startup calls independently of the table byte extraction.
        by_offset = {record["offset"]: record for record in flat}
        for stage, target_key in [("pre_spi", "pre_writer"), ("spi", "spi_init"), ("post_spi", "post_writer")]:
            record = by_offset[source["boot_calls"][stage]]
            require(record["mnemonic"] == "call" and record["body"] == hex(BASE+source[target_key]),
                    f"Unexpected startup call: {source['version']} {stage}")
        json_name = source["version"].lower().replace(".", "") + "_init_disassembly.json"
        asm_name = json_name.replace(".json", ".asm")
        (output / json_name).write_text(json.dumps(regions, indent=2), encoding="utf-8")
        lines = ["; Static PI32v2 decoding; offsets refer to extracted app.bin.",
                 "; This is disassembly evidence, not validated firmware emulation."]
        for region in regions:
            lines.extend(["", "; " + region["name"]])
            lines.extend(f"{rec['offset']:06x}  {rec['address']:08x}  {rec['bytes']:16s}  "
                         f"{rec['mnemonic']} {rec['body']}" for rec in region["instructions"])
        (output / asm_name).write_text("\n".join(lines) + "\n", encoding="utf-8")
        result.append(dict(version=source["version"], regions=len(regions),
                           instructions=len(flat), undecoded=0, json=json_name, asm=asm_name))
        print(f"Decoded {source['version']}: {len(regions)} selected regions, {len(flat)} instructions", flush=True)
    return result


def write_header(output, profiles):
    lines = [
        "/* Data recovered from LD2450 V2.04 and V2.14; both versions match.",
        " * Analysis artifact only. Contains no bus driver or hardware actions.",
        " * Apply indices 0..74 BEFORE SPI receive setup, 75..79 AFTER it.",
        " * Mode 2 is the initial RAM image, which runtime commands may change.",
        " * Register semantics and physical startup timing remain unvalidated.",
        " * I2C 7-bit address: 0x20; inferred data: register, value MSB, value LSB.",
        " */", "#ifndef LD2450_EXTRACTED_RADAR_INIT_DATA_H",
        "#define LD2450_EXTRACTED_RADAR_INIT_DATA_H", "#include <stdint.h>",
        "typedef struct { uint8_t reg; uint16_t value; } ld2450_init_write_t;",
        "enum { LD2450_INIT_COUNT = 80, LD2450_INIT_PRE_SPI_COUNT = 75 };", "",
    ]
    for name, table in profiles.items():
        lines.append(f"static const ld2450_init_write_t ld2450_{name}[LD2450_INIT_COUNT] = {{")
        for entry in table["entries"]:
            if entry["sequence"] == 76:
                lines.append("    /* SPI RECEIVE SETUP OCCURS BEFORE THESE LAST FIVE WRITES. */")
            lines.append(f"    {{0x{entry['register']:02X}, 0x{entry['value']:04X}}}, "
                         f"/* {entry['sequence']:2d}: {entry['stage']} */")
        lines.extend(["};", ""])
    lines.append("#endif")
    (output / "radar_init_data.h").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(output, manifest):
    profiles = manifest["sources"][0]["tables"]
    lines = [
        "LD2450 RADAR INITIALIZATION DATA RECOVERY", "=========================================", "",
        "Recovered TWO ordered 80-write profiles from BOTH applications.",
        "Each profile is identical between normal V2.04 and transparent V2.14.",
        "The profiles differ in 18 values; their register order is identical.", "",
        "The fixed ROM profile is selected for mode byte 1. The second profile",
        "is initialized into RAM and selected for mode byte 2. Compiled initial",
        "mode is 2 in both images; stored configuration can override it. These",
        "labels refer to the binary's internal selector, not a proven mapping",
        "to user-facing single/multiple-target or Bluetooth mode settings.", "",
        "Both call paths split startup into 75 writes, SPI receive setup, then",
        "5 writes. The user's V2.04 UART boot log has exactly this grouping.",
        "The log omits register values and cannot identify which profile ran.", "",
        "RECORD AND WIRE FORMAT", "----------------------",
        "Each binary record is: register byte, zero padding, uint16 little endian.",
        "The writer takes r0=0x40, r1=register, r2=value, emits START, address,",
        "register, value high byte, value low byte, ACK checks and STOP.",
        "0x40 is the write address byte for 7-bit I2C device address 0x20.",
        "Example record 40 00 07 42 means reg 0x40 = 0x4207; inferred bus bytes",
        "are 40 40 42 07. Byte order is supported by the writer's rev8 and shifts.",
        "Wire bytes remain a static interpretation, awaiting an I2C capture.", "",
        "SOURCE LOCATIONS (file offsets in extracted app.bin)", "---------------------------------------------------",
    ]
    for source in manifest["sources"]:
        lines.extend([
            source["version"] + " / " + source["stem"] + ".ufw",
            f"  application SHA256: {source['app_sha256']}",
            f"  mode 1 ROM: offset 0x{source['rom_offset']:X}, address 0x{BASE+source['rom_offset']:08X}",
            f"  mode 2 initial data: offset 0x{source['tables']['mode_2_ram_initial']['app_file_offset']:X}",
            f"  .data copy: file 0x{source['data_offset']:X} -> RAM 0, size 0x{source['data_size']:X}",
            f"  mode 2 table RAM address: 0x{source['ram_table_address']:X}",
            f"  selector RAM address: 0x{source['mode_address']:X}, initial value 2",
            f"  I2C word writer: file 0x{source['write_helper']:X}",
            f"  first 75 writer: file 0x{source['pre_writer']:X}",
            f"  SPI setup: file 0x{source['spi_init']:X}",
            f"  final 5 writer: file 0x{source['post_writer']:X}", "",
        ])
    lines.extend([
        "CONTROL-FLOW EVIDENCE", "---------------------",
        "First loop: r4=0, table pointer in r5, record stride 4; stops at r4=0x12C",
        "(300 bytes = 75 records). Mode 1 uses ROM; other modes use RAM.",
        "Last loop: mode 2 uses RAM starting at entry 75, stopping at a zero",
        "register sentinel. Other modes use ROM offsets 300..316 (five records).",
        "The recovered arrays both have 80 nonzero registers and a zero sentinel.",
        "The RAM profile is initialized by the entry-point copy at offsets",
        "0x62..0x7C: destination 0, source .data, size / 4, word load/store loop.",
        "Thus the second table is part of the image, not a guess from live RAM.", "",
        "The mode byte can be loaded from a stored one-byte setting (record",
        "0x19 in V2.04). The app's register-write command path can modify matching",
        "entries in the RAM table; the export preserves its initial image values.",
        "These observations do not recover the module's current stored settings.", "",
        "The post-SPI function sets PC3/bias high, then calls the same busy-wait",
        "helper used for bit-banged I2C with argument 1000. The helper runs a",
        "NOP/decrement/branch loop. This is a loop count, not a proven time unit.",
        "Do not interpret it as 1000 us or 1000 ms without clock/cycle validation.", "",
        "ORDERED TABLES (retain repeated writes and the stage boundary)",
        "------------------------------------------------------------",
        "Seq Stage     Reg   Mode 1 value  Mode 2 initial  Mode 2 inferred bus bytes",
    ])
    for one, two in zip(profiles["mode_1_rom"]["entries"], profiles["mode_2_ram_initial"]["entries"]):
        if one["sequence"] == 76:
            lines.append("--- SPI receive initialization occurs here ---")
        lines.append(f"{one['sequence']:3d} {one['stage']:9s} {one['register_hex']:5s} "
                     f"{one['value_hex']:13s} {two['value_hex']:15s} {two['wire_bytes_inferred_hex']}")
    lines.extend([
        "", "LIMITS", "------",
        "Register names/bit meanings have not been recovered from a full chip",
        "programming manual. The last five writes are proven to follow SPI setup;",
        "describing individual bits as start/enable is still a hypothesis.",
        "The full reset, power, bias and delay contract is not yet validated.",
        "No target firmware was built, patched, flashed or tested on hardware.",
        "The existing firmware startup gate is unchanged.", "",
        "REPRODUCTION", "------------",
        "From the project root: python tools/extract_radar_init.py",
        "This verifies exact original and application hashes, boot copy operands,",
        "table references, both table hashes, record shape, sentinel and counts.",
        "For the retained local decoder: python tools/extract_radar_init.py --disassemble",
        "To regenerate compatible SLEIGH: add --prepare-spec before --disassemble.",
        "Processor definitions: https://github.com/virtualabs/ghidra-jieli",
        "Pinned revision: " + SLEIGH_COMMIT,
        "Pypcode 4.0.0 cp313 Windows wheel is retained under tmp/pi32_analysis/wheels.",
        "Two compatibility edits add an empty display-string prefix to constructor",
        "concatenations and omit the variable repeat delay-slot semantic statement.",
        "The decoder is incomplete; selected proof ranges decoded without gaps.",
        "A gap-free decode does not validate every displayed register operand or",
        "parallel-instruction semantic; the raw instruction bytes are retained.",
        "No emulation or general correctness claim is made for its instruction semantics.", "",
        "FILES", "-----",
        "manifest.json: source offsets, hashes, entries, inferred wire bytes and method.",
        "radar_init_data.h: both typed C arrays, without a bus driver.",
        "mode_1_rom.bin / mode_2_ram_initial.bin: exact 320-byte source tables.",
        "mode_1_rom_wire_inferred.bin / mode_2_ram_initial_wire_inferred.bin:",
        "  ordered 4-byte transactions, omitting START/STOP/ACK and timing.",
        "v204_init_disassembly.* / v214_init_disassembly.*: selected instruction evidence.",
        "provenance.json: source-definition and local adapter hashes.",
    ])
    (output / "report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "output/radar_init")
    parser.add_argument("--prepare-spec", action="store_true")
    parser.add_argument("--disassemble", action="store_true")
    parser.add_argument("--decode-worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--source-index", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--start", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--end", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.decode_worker:
        decode_worker(args)
        return
    if args.prepare_spec:
        prepare_spec()
    sources = []
    for source in SOURCES:
        metadata, _ = extract_source(source)
        sources.append(metadata)
    for name in PROFILE_HASHES:
        require(sources[0]["tables"][name]["sha256"] == sources[1]["tables"][name]["sha256"],
                "Profiles differ between firmware versions")
    profiles = sources[0]["tables"]
    differences = [
        {"sequence": one["sequence"], "register": one["register"],
         "mode_1_value": one["value"], "mode_2_initial_value": two["value"]}
        for one, two in zip(profiles["mode_1_rom"]["entries"], profiles["mode_2_ram_initial"]["entries"])
        if one["value"] != two["value"]
    ]
    require(len(differences) == 18, "Unexpected profile comparison")
    require(all(one["register"] == two["register"] for one, two in zip(
        profiles["mode_1_rom"]["entries"], profiles["mode_2_ram_initial"]["entries"])),
        "Register order differs between modes")
    args.output.mkdir(parents=True, exist_ok=True)
    provenance = {
        "method": "static table extraction, RAM initializer mapping, selected PI32v2 disassembly",
        "processor_source": "https://github.com/virtualabs/ghidra-jieli",
        "processor_source_commit": SLEIGH_COMMIT,
        "pypcode_version": "4.0.0",
        "sleigh_compatibility_changes": [
            "Empty display-string prefix before constructor concatenation",
            "Omit variable repeat delay-slot semantic statement; disassembly only",
        ],
        "script_sha256": digest(Path(__file__).read_bytes()),
    }
    for key, path in [
        ("wheel", ROOT / "tmp/pi32_analysis/wheels/pypcode-4.0.0-cp313-cp313-win_amd64.whl"),
        ("patched_main", ROOT / "tmp/pi32_analysis/spec/pi32v2.slaspec"),
        ("patched_flow", ROOT / "tmp/pi32_analysis/spec/pi32v2_ins_progflow.sinc"),
        ("compiled_sla", ROOT / "tmp/pi32_analysis/spec/pi32v2.sla"),
    ]:
        if path.is_file():
            provenance[key + "_sha256"] = digest(path.read_bytes())
    proof = disassemble(args.output) if args.disassemble else None
    if proof is None and (args.output / "provenance.json").is_file():
        prior = json.loads((args.output / "provenance.json").read_text(encoding="utf-8"))
        proof = prior.get("disassembly")
        if proof:
            for item in proof:
                require(digest((args.output / item["asm"]).read_bytes()) == item["asm_sha256"],
                        "Prior instruction evidence changed; rerun --disassemble")
    if proof:
        for item in proof:
            item["asm_sha256"] = digest((args.output / item["asm"]).read_bytes())
        provenance["disassembly"] = proof
    manifest = {"app_memory_base": BASE, "record_bytes": 4, "profile_count": 2,
                "entries_per_profile": COUNT, "pre_spi_count": PRE_SPI_COUNT,
                "post_spi_count": COUNT-PRE_SPI_COUNT, "i2c_address_7bit": 0x20,
                "wire_address_write_byte": 0x40, "sources": sources,
                "profile_differences": differences, "hardware_validation": False}
    for name, table in profiles.items():
        blob = b"".join(bytes.fromhex(entry["raw_record_hex"]) for entry in table["entries"])
        (args.output / (name + ".bin")).write_bytes(blob)
        wire = b"".join(bytes.fromhex(entry["wire_bytes_inferred_hex"]) for entry in table["entries"])
        (args.output / (name + "_wire_inferred.bin")).write_bytes(wire)
    write_header(args.output, profiles)
    write_report(args.output, manifest)
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (args.output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print("Recovered 2 profiles x 80 writes; 75 before SPI, 5 after; 18 mode differences.")
    print("Both profiles are identical across V2.04 and V2.14; all source/table hashes verified.")
    print("Output:", args.output)


if __name__ == "__main__":
    main()
