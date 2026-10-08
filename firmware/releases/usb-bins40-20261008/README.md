# Range-bin stream, all 64 chirps (240 MHz sweep)

Installed 2026-10-08 over COM13 (custom UART entry, 417 reads, success). Each validated radar
record is transformed on the BR23 hardware FFT (512-point complex, unscaled) and bins -40..40
are exported as LDF1 codec 2 (BEGIN version 2): DC as int32, other bins int16 with a
per-record block shift. All 64 chirps of every radar frame, about 48 KB/frame. Live register
control (LDC1) retained. Radar profile `firmware/config/radar_sweep240_mode2.json`.

Image SHA-256: `85015eb67aa15f7f15711aa2523e7c1bf54bc1ede8eac0a6e3a3b45fce34e714`.
All 36 repository build inputs match the hashes in `build-result.json`; the source is the
repository at the commit that adds this release (identical firmware sources to commit 196e84e).

Bench: 337 complete frames in 30 s (11.2/s), zero device errors, queue peak 840 B; bins match
the host FFT of a raw capture to about 1 dB with the noise floor within 0.3 dB
(`output/range_bins/20261008-013448-*`). After installation the live viewer, rewritten for
range bins, showed 64-chirp frames at 10.9/s and 542 kB/s with no stage errors.
The previous raw 16-chirp image remains in `usb-raw16-sweep240-20261008`.
