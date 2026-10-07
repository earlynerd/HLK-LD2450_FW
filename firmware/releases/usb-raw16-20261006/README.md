# Raw 16-chirp live radar milestone

Flashed and motion-tested on 2026-10-06. First 16 chirps, both receivers, 512 complex samples each; radar still runs 64. Fixed 67,100-byte LDF1 raw export.

Image SHA-256: `541c110a9707a110bf3afca69ae46f8ad1e57a406398ce956bf80212fa8506af`. Build and all input hashes verified. See `firmware/docs/FRAME_STREAM.md` in source.zip for reproduction and limitations.

The saved office-scene motion trial yielded 1,881 complete windows over 214.55 s, with no export abort or protocol error. Device diagnostics: no DMA, sequence, checksum, CPU or queue errors. Connection-boundary cumulative rejections remain separately documented. Same-image restart verified, viewer left live.

Evidence: `output/firmware_build/raw16_validation_20261006.json`, `output/live_radar/20261006-175804-capture-a2a17a/`, `output/stream_bench/raw16_motion_report/`. Tests: 15 CTest suites, 34 firmware Python, 16 viewer.

The previous 64-chirp image remains in `firmware/releases/usb-optimized-20261006/`.
