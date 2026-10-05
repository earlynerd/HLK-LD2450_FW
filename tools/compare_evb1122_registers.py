"""Compare LD2450 recovered register profiles with a pinned EVB1122 SDK snapshot.

Read-only analysis of downloaded source; never runs its tools or firmware.
Candidate field meanings are kept separate from chip/hardware validation.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / "tmp/evb1122_analysis/repository"
COMMIT = "86b10850e55f5287a27018768c24b88345463bb3"
URL = "https://github.com/HQU-gxy/EVB1122_USBHS_Datatransfer"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    revision = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    if revision != COMMIT:
        raise ValueError("Repository revision differs from the inspected snapshot")
    paths = ["README.md", "Middleware/common/inc/banyan.h",
             "Middleware/common/src/banyan.c", "Middleware/common/src/banyan_param.c",
             "App/common/src/dataprocess.c", "App/common/src/cmdprocess.c",
             "App/common/src/gaincalibration.c",
             "docs/DS10012RN_ICL1122_Rev.1.2_20230910.pdf",
             "docs/20240304-UM10035P_EVB1122波形配置与演示GUI用户手册_Rev.1.0_20240228.pdf"]
    source_hashes = {path: sha((REPO / path).read_bytes()) for path in paths}
    text = (REPO / paths[3]).read_text(encoding="utf-8")
    body = re.search(r"InitRegList\[\].*?=\s*\{(.*?)\};", text, re.S).group(1)
    evb = [(int(a, 16), int(v, 16)) for a, v in re.findall(
        r"\{\s*0x([0-9a-f]+)\s*,\s*0x([0-9a-f]+)\s*\}", body, re.I)]
    assert evb[-1] == (0xFF, 0xFFFF)
    evb = evb[:-1]
    manifest = ROOT / "output/radar_init/manifest.json"
    profiles = json.loads(manifest.read_text(encoding="utf-8"))["sources"][0]["tables"]
    result = {"repository": URL, "commit": COMMIT, "source_sha256": source_hashes,
              "input_manifest_sha256": sha(manifest.read_bytes()),
              "evb_example_write_count": len(evb), "profiles": {},
              "hardware_validation": False, "chip_identity_verified": False}
    for name, table in profiles.items():
        ordered = [(entry["register"], entry["value"]) for entry in table["entries"]]
        final = dict(ordered)
        raw_selector = (final[4] >> 8) & 7
        raw_points = [64, 128, 256, 512, 1024][raw_selector]
        mode_bits = {"range_fft": bool(final[1] & 4), "doppler_fft": bool(final[1] & 0x1000),
                     "doppler_peak": bool(final[1] & 0x10), "ds_raw": bool(final[1] & 2)}
        auto = final[1] & 0x180
        if auto == 0x100:
            rx_code = 1
        elif auto == 0x180:
            rx_code = 3
        else:
            rx_code = (1 if (((final[0x66] >> 8) & 0xA) | ((final[0x6E] >> 14) & 2)) else 0)
            rx_code |= (2 if (((final[0x66] >> 8) & 5) | ((final[0x6E] >> 14) & 1)) else 0)
            rx_code = rx_code or 3
        step_up = (final[0x55] << 16) | final[0x56]
        step_down = (final[0x57] << 16) | final[0x58]
        if step_down & 0x80000000:
            step_down -= 1 << 32
        result["profiles"][name] = {
            "exact_pairs_found_in_evb_example": sum(pair in evb for pair in ordered),
            "comparison_note": "Pair membership, not a positional or whole-profile match",
            "candidate_decodes": {
                "reg01_output_flags": mode_bits,
                "reg04_raw_selector": raw_selector, "raw_complex_samples": raw_points,
                "reg06_rx_data_merge_bit13": bool(final[6] & 0x2000),
                "rx_enable_code_from_reg01_reg66_reg6e": rx_code,
                "reg47_low12_reg48_timing_code": ((final[0x47] & 0xFFF) << 16) | final[0x48],
                "reg55_reg56_step_code": step_up, "reg57_reg58_signed_step_code": step_down,
            },
            "incompatible_or_unverified": {
                "icl1122_reg0d_chirp_accessor_result": final[0x0D] & 0x1FF,
                "note": "Zero conflicts with our observed chirp frames; do not transfer this accessor blindly",
                "timing_and_frequency_units": "Not established for S5KM312CL by this comparison",
                "adc_reset_polarity": "SDK toggles reg 0x67 from 0x1E00 to 0x1E40; individual-bit semantics unverified",
            },
        }
        assert raw_points == 512 and mode_bits == {
            "range_fft": False, "doppler_fft": False, "doppler_peak": False, "ds_raw": True}
        assert not final[6] & 0x2000 and rx_code == 3
    output = ROOT / "output/evb1122_analysis"
    output.mkdir(parents=True, exist_ok=True)
    (output / "comparison.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = [
        "EVB1122 SDK COMPARISON WITH LD2450 INIT DATA", "==========================================", "",
        "Repository: " + URL, "Pinned commit: " + COMMIT, "",
        "This unofficial repository supplies a useful PARTIAL register vocabulary.",
        "Its README says the author lacks the full register map and has not tested",
        "the program on real hardware. The claimed ICL1122/S5KM312CL equivalence",
        "is the author's belief, not a manufacturer-confirmed identity.", "",
        "The ICL1122 datasheet in docs is manufacturer-authored. It documents DS RAW",
        "output but does not contain a full address/bit-field register map. The GUI",
        "manual describes exporting register lists, without exposing a full map.", "",
        "CANDIDATE FIELD DECODES (both recovered LD2450 profiles)",
        "-----------------------------------------------------",
        "0x01 = 0x8222: bit 1 is DS RAW; range FFT bit 2, Doppler FFT bit 12 and",
        "Doppler-peak bit 4 are clear. Source: banyan.h:39,52-55; banyan.c:195-214.",
        "0x04 = 0x030C: raw selector bits 10:8 = 3, mapped to 512 complex samples.",
        "Source: banyan.h:40,47,50; banyan.c:21-27,127-139.",
        "These interpretations agree with our observed 512-I/Q-pair DS RAW packets.",
        "This is supporting evidence; the transferred fields await a hardware check.", "",
        "0x06 = 0x0122: bit 13 clear, so the SDK's merged RX-data mode is off.",
        "Source: banyan.h:42; dataprocess.c:737-744.",
        "0x66 = 0x0F00 and 0x6E = 0xC3FC, with reg 0x01 auto mask 0x180 clear:",
        "the SDK's RX selection helper returns 3 (both receivers selected).",
        "Source: banyan.h:57-58; banyan.c:94-116. This does not prove that both",
        "physical output lanes were captured or are active on the LD2450 PCB.", "",
        "WAVEFORM AND ADC LEADS", "----------------------",
        "gaincalibration.c:88-119 combines low 12 bits of 0x47 with 0x48 as a",
        "timing code, and combines 0x55/0x56 and 0x57/0x58 as waveform step words.",
        "Applied to our two profiles:",
    ]
    for name, profile in result["profiles"].items():
        decode = profile["candidate_decodes"]
        lines.append(f"  {name}: timing code {decode['reg47_low12_reg48_timing_code']}, "
                     f"up step {decode['reg55_reg56_step_code']}, "
                     f"signed down step {decode['reg57_reg58_signed_step_code']}")
    lines.extend([
        "Timing code doubles, while step magnitudes decrease. Actual duration,",
        "sweep bandwidth and conversion units are not established by this comparison.",
        "The signed down-step value is our two's-complement interpretation of the",
        "stored 32-bit word; its physical meaning remains a candidate.",
        "cmdprocess.c:84-97 labels its 0x67=0x1E00 -> 0x1E40 sequence as an ADC",
        "reset during frame idle. Our final write is also 0x67=0x1E40, making this",
        "a useful functional lead without proving each bit's meaning or polarity.", "",
        "LIMITS AND COUNTEREXAMPLES", "-------------------------",
        "banyan.h's banyanET section maps chirp count to 0x0D. Its accessor reads",
        "the low nine bits. Both LD2450 values produce zero using that accessor,",
        "so this cannot be adopted as the LD2450 chirp-count interpretation.",
        "The repo's data-format selector is register 0x31, absent from our tables.",
        "Radar_GetDfftRoiEnable() tests the address constant 0x32 as a bit mask,",
        "despite a separate BIT(13) enable definition. Treat that helper as suspect.",
        "These differences and code issues require selective transfer of meanings.", "",
        "TABLE COMPARISON", "----------------",
        f"EVB default InitRegList contains {len(evb)} writes before its sentinel.",
    ])
    for name, profile in result["profiles"].items():
        lines.append(f"{name}: {profile['exact_pairs_found_in_evb_example']} of 80 register/value "
                     "pairs occur somewhere in the EVB example list.")
    lines.extend([
        "This is not a positional match or a claim that its configuration fits our PCB.", "",
        "REPRODUCTION", "------------",
        "python tools/compare_evb1122_registers.py",
        "comparison.json retains source hashes, exact comparison counts and candidate decodes.",
        "The repository is retained under tmp/evb1122_analysis/repository.",
        "No downloaded executable, build script or firmware was run.",
        "No production firmware or original extraction outputs were changed.",
    ])
    (output / "report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Pinned SDK comparison complete; candidate decodes and limits saved to", output)
    for name, profile in result["profiles"].items():
        print(name, profile["candidate_decodes"])


if __name__ == "__main__":
    main()
