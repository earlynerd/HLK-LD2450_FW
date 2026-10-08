# Raw 16-chirp stream, 240 MHz sweep profile

Flashed 2026-10-08 over COM13 (custom UART entry, 417 reads, success). Same firmware as
`usb-raw16-control-20261006` (raw 16-chirp LDF1 export plus live LDC1 register control);
only the radar startup table differs: `firmware/config/radar_sweep240_mode2.json`,
start 24.005 GHz, steps +/-20, about 240 MHz (24.005-24.245 GHz), about 0.64 m per bin.

Image SHA-256: `413aaf0f7c5d76f1e07c041cadf4b1a7e65c557a25e47f1bf0f02540bb1d1b56`.
Stream configuration: `c8dd4388ad2e37ecc13482b3d5df19322a73a655f963d64823e73b920d5320af`.
All 36 repository build inputs match the hashes in `build-result.json`.

After flashing, the viewer reconnected on COM30 at register generation 0 and 0x53-0x58 read
back the profile values. The x1.18 spectrum stretch was measured with live writes on a static
scene on 2026-10-07 (`output/live_radar/register_tuning_20261007.jsonl`). Register reference:
`docs/S5KM312CL_REGISTER_MAP.md` in source.zip. Rationale: `DECISIONS.md`, 2026-10-08.
