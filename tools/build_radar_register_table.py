"""Annotate recovered LD2450 writes under the S5KM312CL = ICL1122 assumption.

Produces ordered JSON/CSV/Markdown inputs for the spreadsheet builder. Reads
the pinned EVB source as data only. Does not execute vendor code or touch a device.
"""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "tmp/evb1122_analysis/repository"
OUT = ROOT / "output/evb1122_analysis"
COMMIT = "86b10850e55f5287a27018768c24b88345463bb3"
BASE = f"https://github.com/HQU-gxy/EVB1122_USBHS_Datatransfer/blob/{COMMIT}/"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


SOURCES = {
    "H": ("SDK register names and output masks", "Middleware/common/inc/banyan.h", "39-69"),
    "R": ("SDK receiver, RAW and FFT accessors", "Middleware/common/src/banyan.c", "94-214"),
    "P": ("EVB example register list", "Middleware/common/src/banyan_param.c", "6-86"),
    "S": ("SDK stop/start and power sequences", "Middleware/common/src/banyan.c", "31-92"),
    "G": ("Calibration comments and timing/step packing", "App/common/src/gaincalibration.c", "25-131"),
    "D": ("RX merge and header-format accessors", "App/common/src/dataprocess.c", "737-795"),
    "A": ("ADC reset sequence", "App/common/src/cmdprocess.c", "84-97"),
    "U": ("GUI manual: waveform timing, RAW sampling and parameter ranges",
          "docs/20240304-UM10035P_EVB1122波形配置与演示GUI用户手册_Rev.1.0_20240228.pdf", "PDF pages 20-23"),
    "I": ("ICL1122 datasheet: automatic NOP power-down and 50 MHz system-clock diagram",
          "docs/DS10012RN_ICL1122_Rev.1.2_20230910.pdf", "PDF pages 10 and 17"),
    "B": ("Repository author: identity assumption, incomplete map, no hardware test", "README.md", "1-20"),
}


def pair(values, address, mask=0xFFFF):
    return ((values[address] & mask) << 16) | values[address + 1]


def annotate(seq, reg, v1, v2, profiles):
    values = (v1, v2)
    label = "Unmapped register"
    meaning = [f"Write 0x{v:04X}. Function and fields not identified." for v in values]
    basis, notes, source, flag = "Unmapped", "", "P", "Unmapped"

    # The first 75 and last 5 writes are deliberately kept as separate events.
    if reg == 0x40:
        label, basis, source, flag = "Run / configuration control", "Sequence inference", "S, P", "Inference"
        if seq == 1:
            meaning = ["Set bit 14. Likely hold the pattern generator in its configuration/stop state."] * 2
            notes = "0x4207 occurs in the SDK stop list. Bit 14 is the only difference from final 0x0207. Exact reset/run polarity is inferred from sequence."
        else:
            meaning = ["Clear bit 14. Likely release the configured pattern generator and start acquisition."] * 2
            notes = "Last write, after SPI receive setup. 0x0207 also ends the EVB start list. Other bits are not decoded."
    elif reg == 0x41:
        label, basis, source, flag = "Power control / inter-frame low power", "Datasheet field + sequence", "I, S, P", "Partial definition"
        meaning = ["Bit 4 = 0: automatically power down RF and baseband during frame NOP."] * 2
        notes = ("Initial power/control state. Remaining bits of 0x0004 are unmapped." if seq == 2 else
                 "Running power/control state. C844 differs from calibration C864 by bit 5, whose function is not defined. Power-down permission does not prove actual NOP duration.")
    elif reg == 0x09:
        label, basis, source, flag = "Digital configuration / hold control", "Sequence inference", "S, P, G", "Inference"
        meaning = (["Set bit 15 while configuring. Specific block held/reset is unknown."] * 2 if seq == 3 else
                   ["Clear bit 15 relative to boot E901. Likely release a digital hold/reset."] * 2)
        notes = "Both E901 then 6901 occur in the SDK examples. The observed change is exactly bit 15. No field name establishes what that bit controls."
    elif reg == 0x01:
        label, basis, source, flag = "Digital function / data output selection", "SDK field", "H, R", "Partial definition"
        if seq == 4:
            meaning = ["Clear DS RAW, range FFT, Doppler FFT and Doppler-peak output flags."] * 2
            notes = "An initialization state, not the final selected output. Other function bits also cleared."
        else:
            meaning = ["DS RAW enabled (bit 1). Range FFT (2), Doppler FFT (12) and peak (4) flags clear."] * 2
            notes = "Matches captured DS RAW packets. Receiver auto-select mask 0x0180 is clear. Set bits 15, 9 and 5 are not explained by these output masks. FFT output off does not define every internal processing enable."
    elif reg == 0x67:
        label, basis, source, flag = "ADC reset / power-control state", "SDK usage + sequence", "A, S", "Partial definition"
        meaning = (["Initial ADC/control state: all bits zero."] * 2 if seq == 5 else
                   ["Write the SDK ADC-reset sequence's final value, 0x1E40."] * 2)
        notes = ("Also zero in the SDK stop/low-power list. Specific ADC-control fields are unknown." if seq == 5 else
                 "SDK resets ADC during NOP by writing 1E00 then 1E40, toggling bit 6. LD2450 writes only the final value here. Reset polarity and the 0x1E00 fields are unknown.")
    elif reg == 0x72:
        label, basis, source, flag = "TX calibration / power-profile control", "SDK usage + sequence", "G, S", "Partial definition"
        meaning = (["Write TX-related setup/power value 0x0650."] * 2 if seq == 6 else
                   ["Set bits 1 and 0 relative to initial 0x0650. Likely enable a TX/RF operating state."] * 2)
        notes = "SDK explicitly associates this register with TX calibration and uses 0650/0653 in low/normal-power lists. TX power in dBm and individual enable meanings are not exposed."
    elif reg in (0x42, 0x43, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A, 0x4B, 0x4C):
        start = reg if reg % 2 == 1 else reg - 1
        if reg in (0x42, 0x43):
            start = 0x42
        names = {0x42: "Total chirp duration", 0x45: "T0: startup / preparation",
                 0x47: "T1: rising sweep", 0x49: "T2: falling sweep", 0x4B: "T3: stopped / idle"}
        label = names[start] + (" (high word)" if reg == start else " (low word)")
        basis, source, flag = "Pattern inference", "P, G, U", "Inference"
        codes = [pair(p, start, 0x0FFF) for p in profiles]
        part = "upper count bits" if reg == start else "lower 16 count bits"
        meaning = [f"Write {part}. Pair 0x{start:02X}/0x{start+1:02X} = {n:,} counts. Candidate duration {n/200:g} us at 200 counts/us." for n in codes]
        notes = "T0 + T1 + T2 + T3 equals the total exactly in both LD profiles and the EVB example. Stage order follows the GUI waveform model."
        if start == 0x47:
            basis = "SDK packing + pattern inference"
            notes += " SDK directly packs this pair as T_FSM01, masking the high word to 12 bits."
        else:
            notes += " The 12-bit high-count packing is inferred by analogy with 0x47."
        if reg in (0x47, 0x49):
            notes += " Upper nibble (1 or 2) is excluded from the count and remains unmapped."
        notes += " The 200 counts/us conversion is a hypothesis from the SDK's 410*200 scaling, not a documented timer clock."
    elif reg == 0x44:
        label, basis, source, flag = "Candidate chirps per frame / pattern control", "Pattern inference", "P, G, U", "Uncertain field"
        meaning = [f"Candidate low-byte chirp count = {v & 255}. Upper byte = 0x{v >> 8:02X}." for v in values]
        notes = "LD values 32 and 64 are plausible chirp counts. Calibration also uses 0020. EVB example uses 7C40, suggesting additional packed fields. No accessor identifies this field. Do not replace the incompatible reg 0D accessor with this guess as a fact."
    elif reg in (0x4D, 0x4E, 0x4F, 0x50, 0x51, 0x52):
        start = reg if reg % 2 else reg - 1
        label, basis, source, flag = "Candidate frame-sequencer parameter", "Pattern inference", "P, U", "Uncertain field"
        codes = [pair(p, start) for p in profiles]
        meaning = [f"Candidate pair 0x{start:02X}/0x{start+1:02X} = {n:,}." for n in codes]
        notes = "Adjacent to the inferred chirp timers. Could hold frame timing, prescaler or repetition control. Full 32-bit pairing and precise role are not established."
        if start != 0x4D:
            meaning = [f"Candidate paired count = {n:,}. If timed at 200 counts/us: {n/200:g} us." for n in codes]
            notes += " GUI names T_PRE and T_NOP, but no source maps either name to this address pair."
        else:
            notes += " Pair value 1 makes a divider/repeat/control interpretation at least as plausible as a duration."
    elif reg in (0x53, 0x54):
        label, basis, source, flag = "Candidate waveform frequency / PLL parameter", "Pattern inference", "P, G, U", "Uncertain field"
        meaning = ["Write one part of candidate waveform/frequency code 0x0A02AAAB."] * 2
        notes = "Immediately precedes the known frequency-step pairs. Fraction-like AAAB and EVB values ending 5556 suggest a fixed-point synthesizer parameter. Pairing, scaling, reference divider and actual RF frequency are unknown."
    elif reg in (0x55, 0x56, 0x57, 0x58):
        start = 0x55 if reg < 0x57 else 0x57
        up = start == 0x55
        label, basis, source, flag = ("Rising" if up else "Falling") + " sweep step word", "SDK packing + pattern inference", "G, P", "Partial definition"
        codes = [pair(p, start) for p in profiles]
        signed = [n - (1 << 32) if n & (1 << 31) else n for n in codes]
        meaning = [f"Write {'high' if reg == start else 'low'} 16 bits. Combined word 0x{n:08X}, {'unsigned' if up else 'candidate signed'} step {s}." for n, s in zip(codes, signed)]
        notes = "SDK packs these pairs as Step01/Step10. No reliable conversion to Hz is supplied."
        if not up:
            notes += " Negative interpretation assumes two's complement. Mode 1 down/up magnitude ratio 136/35 closely follows T1/T2 = 42000/11000. Mode 2 is symmetric (17 and -17, equal times)."
    elif reg in (0x59, 0x5A):
        label, basis, source, flag = "Candidate additional waveform step/control", "Pattern inference", "P, G", "Uncertain field"
        meaning = ["Write zero in both words immediately following Step01 and Step10."] * 2
        notes = "Could be another step, offset or waveform-control parameter. A third zero step is consistent with a held-frequency phase, but no code names these addresses."
    elif reg in (0x5B, 0x5C, 0x5D, 0x5E):
        label, basis, source, flag = "Candidate waveform / analog trim control", "Pattern inference", "P, G", "Uncertain field"
        meaning = [f"Write packed setting 0x{v:04X}. Individual fields unknown." for v in values]
        notes = "At the end of the waveform block and before receiver controls. 5B/5C also occur in the calibration replacement list. Could be PLL or analog settings. No specific gain, filter or divider can be assigned."
    elif reg in (0x61, 0x62, 0x63, 0x64):
        label, basis, source, flag = "Candidate RX I/Q baseband trim", "Pattern inference", "P, G, H", "Uncertain field"
        meaning = ["Write identical 0x0021 settings to four consecutive registers."] * 2
        notes = "Four registers are compatible with I/Q controls for two RX paths. SDK has IVCM calibration variables, but never connects them to these addresses. Channel assignment and common-mode/gain interpretation remain guesses."
    elif reg == 0x66:
        label, basis, source, flag = "LPF receiver-channel enable", "SDK field", "H, R", "Partial definition"
        meaning = ["Upper enable nibble = 0xF. SDK RX1 mask 0xA and RX2 mask 0x5 both nonzero."] * 2
        notes = "With reg 6E=C3FC and reg 01 auto-mask clear, SDK selection returns both receivers. Does not establish LPF gain/cutoff or prove both physical data lanes were captured."
    elif reg == 0x6E:
        label, basis, source, flag = "LNA receiver enable / gain control", "SDK field + usage", "H, R, G", "Partial definition"
        meaning = ["Bits 15:14 = 3. Both LNA receiver-select masks are set in SDK helper."] * 2
        notes = "SDK comments link this register to RX gain calibration. Other C3FC bits are not mapped to gain in dB. Receiver selection can also be supplied by reg 66."
    elif reg in (0x6C, 0x6D):
        label, basis, source, flag = "TX calibration / power-profile setting", "SDK usage", "G, S", "Partial definition"
        meaning = [f"Write TX-related calibration/power code 0x{v:04X}." for v in values]
        notes = "SDK explicitly identifies 6C and 6D as updated by TX calibration and changes them in power profiles. No conversion to TX dBm or per-field meaning is available."
    elif reg == 0x70:
        label, basis, source, flag = "Analog power-profile setting", "SDK usage", "S, P", "Partial definition"
        meaning = ["Write 0x26A0 to a register the SDK changes between low and normal power."] * 2
        notes = "SDK uses 1020 in low power and 32A0 in normal power. LD value differs from both. This supports a power/bias role without identifying the fields or proving an incompatible setting."
    elif reg == 0x76:
        notes = "Exact 0021 occurs in the EVB example. No register name or field definition found. Value equality alone supplies no functional meaning."
    elif reg == 0x02:
        label, basis, source, flag = "Candidate RAW sample offset / decimation", "Pattern inference", "P, G, U", "Uncertain field"
        meaning = [f"Candidate sample offset = {v & 0x3FF}. Bits 13:12 = {(v >> 12) & 3}; possible sampling-interval code." for v in values]
        notes = "LD low bits are 60, matching GUI default RAW offset and reg 0B low bits. EVB lists likewise pair 02=000D/0032 with 0B ending 000D/0032. Gain calibration zeros the low bits of both. If code 0/1 means interval 1/2, it follows doubled T1. Neither field is explicitly defined."
    elif reg == 0x04:
        label, basis, source, flag = "DS RAW point count / peak-data size", "SDK field", "H, R", "Partial definition"
        meaning = ["Bits 10:8 = 3: 512 complex RAW samples. Low 5 bits = 12: SDK peak-data size 48 bytes."] * 2
        notes = "512 I/Q pairs agrees with captures. Peak output is not selected by final reg 01, so its size is inactive for DS RAW. Remaining bits are not decoded."
    elif reg == 0x05:
        label, basis, source, flag = "FFT / Doppler output count", "SDK field", "H, R, U", "Conditional / ambiguous"
        meaning = ["SDK FFT-point accessor returns 16. Doppler data-count accessor also returns 16 if ROI mode is off."] * 2
        notes = "ROI register 32 is unwritten, so its state is unknown. GUI distinguishes FFT calculation size (64/128/256) from output count. Treat 16 as an output-count lead, not a 16-point FFT computation claim. FFT output is not selected."
    elif reg == 0x06:
        label, basis, source, flag = "Receiver data merge control", "SDK field", "H, D", "Partial definition"
        meaning = ["Bit 13 = 0: RX merge flag is off under the SDK interpretation."] * 2
        notes = "Consistent with separate receiver streams. Other 0122 bits remain unknown. A single captured lane does not establish that the other receiver is disabled."
    elif reg in (0x07, 0x08):
        label, basis, source, flag = "Candidate digital data-processing control", "Pattern inference", "P, H", "Uncertain field"
        meaning = [f"Write 0x{v:04X}, exactly matching the EVB example." for v in values]
        notes = "Between known digital controls 06 and 0A in both lists. Likely part of digital processing/output configuration. No bit meanings found."
    elif reg == 0x0A:
        label, basis, source, flag = "FFT settings", "SDK register name", "H, P, G", "Partial definition"
        meaning = [f"Write FFT-setting code 0x{v:04X}." for v in values]
        notes = "SDK names the address but supplies no FFT-setting masks. The profiles differ only at bit 14. Output flags select DS RAW, but unknown FFT fields cannot be assumed irrelevant to every internal operation."
    elif reg == 0x0B:
        label, basis, source, flag = "Candidate shared sample/FFT offset control", "Pattern inference", "P, G, U", "Uncertain field"
        meaning = ["Candidate low-10-bit offset = 60. Upper field = 0xC000, unmapped."] * 2
        notes = "Low offset tracks reg 02 in LD and all inspected EVB configurations, and both become zero in calibration. Might be an FFT window offset or another sample-selection offset. Do not equate the two functions solely from matching values."
    elif reg == 0x0D:
        label, basis, source, flag = "SDK pattern / Doppler chirp count", "SDK field (mismatch)", "H, R, P", "Incompatibility"
        meaning = [f"SDK frame-chirp accessor (value & 0x01FF) returns 0. Upper byte is {v >> 8}." for v in values]
        notes = "Zero does not describe observed nonzero chirp-indexed DS RAW frames. Could be an inactive FFT count, a changed field location or a variant mismatch. SDK section is labeled banyanET. Cannot transfer this count interpretation directly."
    elif reg == 0x0E:
        label, basis, source, flag = "Candidate digital chirp/window control", "Pattern inference", "P, H", "Uncertain field"
        meaning = [f"Upper byte = {v >> 8}, lower byte = 0. Could hold a packed count or mode." for v in values]
        notes = "Neighbour of SDK chirp-count register 0D. Values 32/64 mirror candidate frame counts in 44, but this does not identify the field. EVB default writes zero here."
    elif reg in (0x14, 0x15, 0x17):
        label, basis, source, flag = "Unmapped digital setting", "Unmapped", "P", "Unmapped"
        notes = "Not written in the inspected EVB default list. Register location alone suggests a digital setting, but not its function. Absence is a coverage gap, not proof of chip incompatibility."
    elif 0x20 <= reg <= 0x2F:
        label, basis, source, flag = "Candidate coefficient / threshold table", "Pattern inference", "P", "Uncertain field"
        meaning = [f"Write table-like word 0x{v:04X} ({v})." for v in values]
        notes = "LD writes a contiguous 16-word block: three zeros, then decreasing values ending in a repeated plateau. Shape suggests coefficients or thresholds. No evidence chooses a filter, window, calibration curve or detector threshold. These addresses are absent from the EVB default list."
    return dict(function=label, mode1_meaning=meaning[0], mode2_meaning=meaning[1],
                basis=basis, flag=flag, notes=notes, sources=source)


def main():
    manifest_path = ROOT / "output/radar_init/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    names = ("mode_1_rom", "mode_2_ram_initial")
    first = manifest["sources"][0]["tables"]
    entries = [first[name]["entries"] for name in names]
    # Retain the exact order, repeats and stage split, and check both firmware versions.
    for source in manifest["sources"]:
        for name, expected in zip(names, entries):
            got = source["tables"][name]["entries"]
            assert [(x["sequence"], x["register"], x["value"], x["stage"]) for x in got] == [
                (x["sequence"], x["register"], x["value"], x["stage"]) for x in expected]
    profiles = [{x["register"]: x["value"] for x in e} for e in entries]
    # Cross-check the new period inference against original, checksum-validated
    # SPI records. SPI header spacing is measured; RF phase durations are not.
    sys.path.insert(0, str(ROOT))
    from analyze_spi import read_capture
    capture_path = ROOT / "radar_moving_reflector.csv"
    packets, *_ = read_capture(capture_path)
    valid = [p for p in packets if p.valid and len(p.iq) == 512]
    intervals = [b.start_s - a.start_s for a, b in zip(valid, valid[1:]) if b.chirp == a.chirp + 1]
    median_us = statistics.median(intervals) * 1e6
    capture = dict(file=capture_path.name, sha256=sha(capture_path),
                   validated_packets=len(valid), adjacent_chirp_intervals=len(intervals),
                   median_interval_us=median_us, min_interval_us=min(intervals)*1e6,
                   max_interval_us=max(intervals)*1e6,
                   chirp_min=min(p.chirp for p in valid), chirp_max=max(p.chirp for p in valid))
    rows = []
    for a, b in zip(*entries):
        assert a["register"] == b["register"] and a["sequence"] == b["sequence"]
        rows.append(dict(sequence=a["sequence"], stage=a["stage"], register=a["register_hex"],
                         mode1_value=a["value_hex"], mode2_value=b["value_hex"],
                         profile_differs=a["value"] != b["value"],
                         **annotate(a["sequence"], a["register"], a["value"], b["value"], profiles)))
    for row in rows:
        reg = int(row["register"], 16)
        if reg in (0x42, 0x43):
            row["notes"] += f" RAM total at that scale is 1200 us, agreeing within 0.013% with measured SPI chirp spacing {median_us:.3f} us."
            row["sources"] += ", C"
        elif reg == 0x44:
            row["notes"] += f" Capture chirp indices {capture['chirp_min']}..{capture['chirp_max']} support the RAM candidate count of 64."
            row["sources"] += ", C"
        elif reg == 0x04 or (reg == 0x01 and row["sequence"] == 78):
            row["sources"] += ", C"
    assert len(rows) == 80 and sum(r["profile_differs"] for r in rows) == 18
    assert Counter(r["stage"] for r in rows) == {"pre_spi": 75, "post_spi": 5}
    assert [r["sequence"] for r in rows] == list(range(1, 81))

    evb_text = (REPO / "Middleware/common/src/banyan_param.c").read_text(encoding="utf-8")
    evb_body = re.search(r"InitRegList\[\].*?=\s*\{(.*?)\};", evb_text, re.S).group(1)
    evb = {int(a, 16): int(v, 16) for a, v in re.findall(r"\{\s*0x([0-9a-f]+)\s*,\s*0x([0-9a-f]+)\s*\}", evb_body, re.I)}
    evidence = []
    for name, p in list(zip(names, profiles)) + [("EVB example", evb)]:
        total = pair(p, 0x42, 0x0FFF)
        segments = [pair(p, a, 0x0FFF) for a in (0x45, 0x47, 0x49, 0x4B)]
        assert sum(segments) == total
        up, down = pair(p, 0x55), pair(p, 0x57)
        if down & 0x80000000:
            down -= 1 << 32
        evidence.append(dict(profile=name, total_counts=total, segments_counts=segments,
                             up_step=up, down_step_candidate_signed=down))

    source_rows = []
    for key, (label, path, loc) in SOURCES.items():
        url = BASE + path
        if not path.endswith(".pdf"):
            lo, hi = loc.split("-")
            url += f"#L{lo}-L{hi}"
        source_rows.append(dict(id=key, title=label, location=loc, url=url,
                                sha256=sha(REPO / path)))
    s5 = ROOT / "docs/datasheets/S5KM312CL_Rev.1.3_20221109.pdf"
    source_rows.append(dict(id="S5", title="S5KM312CL Rev.1.3: reg 41 bit 4 NOP power-down",
                            location="Printed page 8 / PDF page 9",
                            url="https://www.edworks.co.kr/wp-content/uploads/2023/10/S5KM312CL_Rev.1.3_20221109.pdf#page=9",
                            sha256=sha(s5)))
    source_rows.append(dict(id="C", title="Original radar_moving_reflector.csv SPI capture",
                           location=f"{len(valid)} valid 512-I/Q packets; {len(intervals)} adjacent-chirp intervals; median {median_us:.3f} us; indices 0..63",
                           url="", sha256=capture["sha256"]))
    for row in rows:
        if row["register"] == "0x41":
            row["sources"] += ", S5"
        assert all(k in SOURCES or k in ("S5", "C") for k in row["sources"].split(", "))
        assert row["notes"] and row["function"] and row["basis"]

    gaps = [
        ["0x31", "Header/data-format selection", "SDK uses bit 10, but neither LD profile writes this register. Reset default and later writes are unknown.", "H, D"],
        ["0x32", "Doppler ROI mode", "SDK defines bit 13, but its ROI helper mistakenly tests address 0x32 as the mask. Register is unwritten here.", "H, R"],
        ["0x33 / 0x34", "Doppler ROI chirp/data counts", "Unwritten in these profiles. Cannot resolve conditional FFT sizes without their state.", "H, R"],
        ["Calibration helper", "Source defect", "CreateNewRegList inner checkloop never increments. Read the packing expressions as evidence, not the function as validated behavior.", "G"],
        ["Timer clock", "Time conversion inference", f"410*200 in calibration suggests 200 counts/us. RAM total then gives 1200 us, within 0.013% of measured {median_us:.3f} us SPI chirp spacing. Datasheet labels PLLsys as 50 MHz. Separate timer/scaling is undocumented.", "G, I, C"],
    ]
    result = dict(assumption="S5KM312CL and ICL1122 have the same register meanings",
                  commit=COMMIT, input_manifest_sha256=sha(manifest_path),
                  profiles=names, firmware_versions=[s["version"] for s in manifest["sources"]],
                  profiles_are_identical_across_firmware_versions=True,
                  rows=rows, sources=source_rows, additional_gaps=gaps,
                  timing_evidence=evidence, basis_counts=dict(Counter(r["basis"] for r in rows)),
                  capture_cross_check=capture,
                  provisional_counts_per_us=200,
                  provenance="Firmware-derived initial values, not an I2C capture. Saved configuration/runtime writes may change RAM profile.")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "register_write_table.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    columns = ["sequence", "stage", "register", "mode1_value", "mode2_value", "function",
               "mode1_meaning", "mode2_meaning", "basis", "flag", "notes", "sources"]
    with (OUT / "register_write_table.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    text = ["# LD2450 register-write interpretation", "",
            "Working assumption: **S5KM312CL and ICL1122 share register meanings.** Explicit SDK definitions and our inferences are labelled separately.", "",
            "Both firmware versions (V2.04 and V2.14) contain these same two 80-write profiles. Mode 1 is the ROM table. Mode 2 is the initial RAM table, which saved configuration or runtime commands can modify. These are binary-derived initial values, not captured bus writes.", "",
            "The table preserves every repeated write. The first 75 precede SPI receive setup and the final five follow it. The profiles differ at 18 writes. Source IDs resolve below to the pinned repository or datasheet.", "",
            "| # | Stage | Register | Mode 1 | Mode 2 | Working interpretation | Mode 1 meaning | Mode 2 meaning | Basis | Notes / incompatibilities | Sources |",
            "|---:|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        fields = [str(r["sequence"]), r["stage"], r["register"], r["mode1_value"], r["mode2_value"],
                  r["function"], r["mode1_meaning"], r["mode2_meaning"], r["basis"], r["notes"], r["sources"]]
        text.append("| " + " | ".join(s.replace("|", "\\|") for s in fields) + " |")
    text += ["", "## Timing inference", "",
             "The SDK explicitly packs 47/48 as T_FSM01 and 55/56, 57/58 as Step01 and Step10. Extending that packing to the neighbouring pairs produces the following exact arithmetic:", "",
             "| Profile | Total at 42/43 | T0 at 45/46 | T1 at 47/48 | T2 at 49/4A | T3 at 4B/4C | Up step | Candidate signed down step |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for e in evidence:
        text.append("| " + " | ".join(map(str, [e["profile"], e["total_counts"], *e["segments_counts"], e["up_step"], e["down_step_candidate_signed"]])) + " |")
    text += ["", "The four phase counts sum to the total in all three configurations. For LD mode 1, 35 × 42000 = 1470000 and 136 × 11000 = 1496000, differing by about 1.77%. Mode 2 has equal up/down durations and step magnitudes. This strongly supports rising/falling sweep fields. Integer rounding or implementation details could explain the residual, but are not proven.", "",
             "If the calibration factor 200 represents timer counts per microsecond, the LD phase durations are **20, 210, 55, 845 us** (mode 1) and **20, 420, 420, 340 us** (mode 2), with totals **1130 and 1200 us**. The conversion is conditional. Neither the manual nor source supplies a definitive timer-clock definition, and the datasheet labels PLLsys as 50 MHz.", "",
             f"The original SPI capture provides a separate timing check: {len(intervals)} adjacent chirps among {len(valid)} checksum/framing-valid 512-I/Q packets have median spacing **{median_us:.3f} us**. This is within **0.013%** of the RAM total at the proposed scale. Chirp indices span {capture['chirp_min']}..{capture['chirp_max']}, consistent with the RAM candidate of 64 chirps at register 44. This supports the inferred conversion and RAM-profile match, but does not measure individual RF phases or prove which register caused the cadence. Source C.", "",
             "## Other gaps and source defects", ""]
    text += [f"- **{g[0]} ({g[1]}):** {g[2]} Sources: {g[3]}." for g in gaps]
    text += ["", "## Sources", "", f"Repository snapshot: `{COMMIT}`. SDK code is evidence for this assumed mapping, not bench validation.", ""]
    text += [f"- **{s['id']}:** " + (f"[{s['title']}]({s['url']})" if s['url'] else s['title']) + f", {s['location']}." for s in source_rows]
    (OUT / "register_write_table.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "profile_differences": 18,
                      "basis_counts": result["basis_counts"], "timing_evidence": evidence}, indent=2))


if __name__ == "__main__":
    main()
