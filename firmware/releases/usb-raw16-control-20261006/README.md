# Raw 16-chirp stream with live register control (stock sweep)

Installed 2026-10-06 to 2026-10-08 and used for all live register experiments (LDC1 READ,
WRITE and REINIT over native USB). Stock mode-2 radar profile
(`firmware/config/radar_baseline_mode2.json`, 24.025 GHz, steps +/-17, about 204 MHz).
Archived on 2026-10-08 when it was replaced by `usb-raw16-sweep240-20261008`.

Image SHA-256 is recorded in `manifest.json` (`flashed_ufw_sha256`). Its 36 repository build
inputs match the current source exactly; the only difference from the 240 MHz release is the
radar configuration file, so the source is in `../usb-raw16-sweep240-20261008/source.zip`.
