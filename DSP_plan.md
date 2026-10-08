# Radar processing and data export plan

Updated: 2026-10-06. Status: continuous acquisition, lossless compression and native USB CDC have a concurrent 30-second hardware pass: 159 complete host-validated frames, zero acquisition/queue errors. Reduced export cadence is intentional; broader scene and runtime-resource qualification remains open.

This is the working plan and session handoff for the shared radar processing front end. Update progress and handoff notes as work proceeds; keep detailed build and bench evidence in the linked artifacts.

## Objective and priorities

Receive both radar channels on the Jieli, preserve useful complex intermediate data for several processing streams, and export intermediates or smaller derived results within measured memory, compute, and transport budgets.

- Preserve amplitude, phase, receiver relationships and chirp timing where consumers need them. Keep application-specific clutter rejection and detection in separate consumers.
- Make retained range regions, precision and export cadence configurable. Document the information each choice discards.
- Keep raw snapshots as reference evidence; continuous full-rate raw export is not a prerequisite.
- Use stock firmware as an example of how this hardware can work, not a design to reproduce exactly.
- Accept reduced whole-frame export cadence. Distinguish intentional skips from missing chirps or corrupt data; frame gaps do not preserve all motion information.
- Share intermediates between consumers and measure their incremental costs before adding them onboard.

## First milestone

The current milestone is complete raw 16-chirp export windows from both receivers, streamed over USB during acquisition. The user selected this shorter window after motion repeatedly exceeded the compressed 64-chirp export budget. Retain chirps 0-15 and all 512 complex samples per chirp; continue validating the full physical 64-chirp burst. Each uncompressed 67,100-byte export fits the producer queue, independent of scene compressibility. Reduced whole-frame cadence is acceptable; missing chirps within a declared window is not. Keep radar running and intentionally skip whole physical frames while output drains. Full 64-chirp export remains an available build mode and future optimization target; 16 chirps trade fourfold coarser slow-time FFT bins for a bounded raw export.

Use those frames to select and evaluate an actual processing workflow on the host. Only then move its early stages onto the Jieli and transmit the resulting reduced representation over USB. Compare target results with the host reference and measure the information discarded by each reduction. This sequencing supersedes the earlier intermediate-first, UART-first milestone.

The earlier proposal of 64 retained range bins remains a candidate memory budget, not a committed representation, calibrated range interval or established stock setting. Establish sample-to-sweep mapping and evaluate workflows before choosing the transform or reduction.

### Information retained and discarded by the candidate range-bin reduction

The range FFT alone does not provide the eightfold reduction in this proposal.
Selecting 64 of 512 output bins does. The selected complex coefficients retain
amplitude, phase, both receivers and all 64 chirps; Doppler and bearing processing
can still operate on them. Excluded coefficients cannot be recovered. Keeping
adjacent bins at the original FFT length narrows the represented frequency/range
span without making the retained bin spacing eight times coarser. Actual range
coverage depends on the sweep and sampling interpretation; complex I/Q does not
automatically permit discarding half the spectrum as redundant.

Windowing, sample selection, quantization and clipping are additional information
choices. Retaining complex coefficients does not preserve the ability to redo
every front-end choice from raw samples. Validate those choices against raw
references, especially near retained-region boundaries and for weak returns.
Do not assume the proposed 64-bin selection is a small sacrifice until the
application coverage and calibration support it.

## Baseline at planning

| Item | Established state |
| --- | --- |
| Updating | Stock-to-custom and custom-to-custom UART updates validated; three-second recovery window and retry after failed handshake validated. |
| Radar initialization | Mode-2 profile matches the I2C capture; custom firmware reports all 80 initialization writes ACKed. |
| Acquisition | One-shot capture yields 16 consecutive, checksum-valid 512-I/Q-pair records per receiver. Radar stops before hexadecimal serial dump. |
| Storage | Two 32,896-byte buffers. Main and secondary heap reservations are 91,296 and 11,648 bytes; these are not runtime free-space measurements. |
| Timing reference | Earlier stock captures show approximately 1.199844 ms between adjacent chirps and 88.99 ms between 64-chirp frames. Confirm under continuous custom acquisition. |
| Unverified work | Continuous acquisition, sweep segmentation, calibrated range processing, high-rate binary export, USB throughput and concurrent DSP consumers. |

Current reference image: `firmware/build/spi-capture16/update-two-wire.ufw`, SHA-256 `16381b9302ccceaa48af63f7459c293fccbeb042064be85432480fbb575f6fb5`. Build outputs are ignored; preserve this image, manifests and corresponding source state before replacing the baseline. This image was last reported installed in this conversation; check connected-device identity and state in a later session.

## Implementation stages

1. Preserve the working baseline and establish measurements.
   Save the current working image, source, and capture evidence as a reproducible milestone. Retain the three-second recovery window, 256 kbaud updater, and PA9 diagnostics.
   Add measurements for acquisition errors, processing time, buffer occupancy, actual free heap, and stack usage. Our memory budget must reflect runtime consumption, not just linker reservations.
   Checkpoint: experimental images remain recoverable, and failures identify the stage that failed.
2. Make acquisition work continuously with bounded memory.
   Replace one-shot capture with small alternating DMA buffers and explicit ownership. Validate headers, checksums, chirp sequence and receiver alignment. Initially consume and discard validated records while measuring reliability; identify complete frames and distinguish intentional skips from overruns.
   Checkpoint: sustained acquisition of both receivers without unexplained gaps, with measured service deadlines.
3. Capture complete raw frames through lossless compression and concurrent USB export.
   Benchmark USB payload throughput and host-stall behavior, then measure target codec time and memory. Begin with previous-chirp prediction and a simple lossless coder; choose block packing or Rice coding from measured costs. Give each retained frame an independent reference, retain raw fallback, and bound the output queue.
   Stream encoded chirps during acquisition rather than waiting for a complete frame in RAM. Include configuration identity, frame/chirp/receiver identifiers, timing, codec version, integrity checks and explicit loss/skip counters. Reject incomplete frames on overflow; do not silently drop samples. Preserve UART recovery and PA9 diagnostics.
   Collect settled, static, moving and stronger-return scenes to characterize compression variability. Keep immutable source captures and losslessly decoded host files.
   Checkpoint: the host reconstructs complete paired 64-chirp frames exactly; concurrent acquisition/encoding/USB meet measured deadlines and memory limits; worst observed queue occupancy and rejected/skipped frames are reported. Continuous full-rate export is not required.
4. Select a processing workflow on the host using those frames.
   Establish sweep segmentation, sample selection, windowing, FFT direction/scaling and range calibration. Compare candidate workflows against known-distance/motion scenes and the intended uses: range-Doppler, detection, relative receiver phase/bearing, and small-motion histories.
   Evaluate numerical precision, retained range coverage, clutter handling, and the sizes of intermediates. Define performance measures relevant to the selected workflow, including sensitivity, false detections, range/velocity/bearing errors where applicable, and the consequences of frame gaps. Keep application-specific filtering separate where multiple consumers benefit.
   Checkpoint: a reproducible host reference with useful measured performance and an explicit early-stage partition suitable for the Jieli. The reduced representation and information losses are justified by evidence, not chosen solely to fit a buffer.
5. Move the selected early stages onto the Jieli and export reduced data over USB.
   Process usable chirp segments promptly, share intermediates and release raw buffers. Choose fixed-point or floating-point arithmetic from target timing, numerical error and memory measurements. Export scaling, selection metadata and clipping counters.
   Compare target and host processing on identical inputs. Retain a diagnostic raw-capture mode for regressions and new algorithms. The earlier 64-bin complex frame (32 KiB at int16 I/Q) is one candidate, not a requirement.
   Checkpoint: reduced USB output agrees with the selected reference within documented tolerances and fits measured runtime margins; discarded information and supported consumers are explicit.
6. Add further consumers and move more work onboard when useful.
   Develop consumers against the shared intermediate on the host, then port individually when compute and memory allow. Avoid full-frame copies for each consumer and account for incremental cost. Preserve access to reference captures so later algorithms can be evaluated independently of earlier reductions.
   Checkpoint: each consumer has measured performance/resource costs and a clear information-retention contract.

The implementation order is raw capture over USB, host workflow selection, then onboard reduction and reduced USB export. Host interpretation can begin with existing captures in parallel with acquisition/transport development, but selecting the production front end depends on representative full-frame evidence.

## Progress and acceptance

Mark stages complete only when their checkpoints have evidence. Distinguish source implementation, host tests, target builds and hardware validation.

| Stage | Status | Evidence to record |
| --- | --- | --- |
| 1. Baseline and instrumentation | Baseline and flashed stream image archived; counters and live updater reentry checked | Runtime stack/physical heap accounting remains pending; SDK heap counter is inconsistent with physical RAM. |
| 2. Continuous bounded acquisition | 30-second concurrent codec/USB trial passed with zero acquisition errors; backlog one | Broader scenes, long-duration qualification and CPU-backlog guard activation remain open. |
| 3. Lossless raw frames over USB | Initial concurrent hardware pass: 159 complete frames in 30 s; raw pattern ~790 kB/s; pause/reopen recovery verified | Preserve artifacts in usb-optimized-20261006. Physical unplug and runtime stack/free-heap qualification remain open; no full-rate export claim. |
| 4. Host workflow selection | Planned | Representative frames, calibration, performance comparisons, information losses and chosen partition. |
| 5. Onboard early stages and reduced USB export | Planned | Same-input reference comparisons, numerical error, clipping, memory, compute and transport budgets. |
| 6. Multiple consumers | Planned | Host evaluation, incremental target costs and information-retention choices. |

USB measurement and streaming compression belong to the first capture milestone. Compression estimates from startup data are evidence of potential, not guaranteed buffer capacity or sustained throughput.

The current experimental stream image and exact bench evidence are documented in
[FRAME_STREAM.md](firmware/docs/FRAME_STREAM.md). It supersedes the installed
one-shot image described in the baseline table above, while retaining that
image as a separate reference. Both stopped and active stream updater reentry
passed; the final same-image restart leaves acquisition enabled. The clean
run counted 7,536 valid records per lane, with peak backlog one record and
264 us maximum record processing time without encoding or native USB traffic.

## Resource and information checks

- The [PSRAM investigation](docs/PSRAM_INVESTIGATION.md) found controller support but no confirmed attached/in-package memory. Both stock versions have zero PSRAM startup-copy length and no explicit PSRAM boot-config key. Physical presence remains unresolved; do not allocate it based only on a linker declaration.
- The SDK linker maps 192 KiB of internal RAM. Its PSRAM region declaration is not evidence that PSRAM is installed. Budget DMA, FFT scratch, histories, output queues, stacks and runtime allocations together.
- Replacing current raw buffers releases their memory, but new structures still require measured headroom. Avoid duplicating a full intermediate frame for every consumer.
- Current SPI DMA API lengths are limited to 65,535 bytes. Continuous capture requires explicit rearming, ownership and deadline validation; increasing the capture constant alone is insufficient.
- At complex 16-bit precision, 64 bins x 64 chirps x two receivers require 32 KiB per frame, or about 0.37 MB/s at the earlier cadence. Wider numeric formats and protocol overhead increase this.
- Binary UART transfer of that frame takes ideally 1.28 s at 256 kbaud or 0.328 s at 1 Mbaud using 8N1. Higher baud is a bench target, not a validated operating point.
- Distinguish startup records from steady-state data. A valid checksum establishes transport integrity, not RF settling or correct range interpretation.
- Lossless chirp prediction is a promising alternative to discarding bins for occasional full raw-frame capture. A host experiment on the existing 16-chirp startup capture reduced both lanes from 65,792 to 35,332 bytes with previous-chirp prediction and 32-value block bit packing, including references and original packet framing. Every packet reconstructed byte-for-byte. This is 53.7% of original size, not a worst-case guarantee. A proportional full-frame estimate is about 138 KiB; runtime memory, target compute, motion/noise, and USB throughput remain unvalidated. See [experiment](tools/analyze_capture_compression.py) and [results](output/spi_capture/compression_analysis.json). Test settled and moving scenes before making compression a buffer-capacity assumption; retain raw fallback and explicit whole-frame overflow handling.
- Export configuration identity, selected bins, receiver/chirp association, timing, scaling and clipping/loss counters. Flag invalid frames rather than presenting them as complete.
- Record phase continuity separately from packet integrity, including frame gaps, power cycles and processing resets.
- Keep the established updater baud and recovery gate ahead of experimental acquisition or transport initialization. Runtime data-baud changes must preserve that contract.

## Evidence and code pointers

- [Image build and hardware validation guide](firmware/docs/IMAGE_BUILD.md)
- [Sixteen-chirp validation and image provenance](output/firmware_build/spi_capture16_hardware_validation_20261005.json)
- [Raw captures and decoded records](output/spi_capture/dual_lane_16chirps/), [capture report](output/spi_capture/dual_lane_16chirps/report.json), and [sequence summary](output/spi_capture/dual_lane_16chirps/sequence-summary.json)
- [One-shot capture](firmware/src/capture.c), [SPI/UART implementation](firmware/target/br23/peripherals.c), and [boot recovery gate](firmware/target/br23/image/main.c)
- [Record parser](firmware/src/radar_wire.c), [capture decoder](firmware/tools/decode_capture.py), and [plots](firmware/tools/plot_capture.py)
- [Register interpretation and earlier chirp timing](output/evb1122_analysis/register_write_table.md)
- [Structural decisions](DECISIONS.md) and [debug history](DEBUG_LOG.md)

## Session handoff

### Resume here

The first stream foundation is described in [FRAME_STREAM.md](firmware/docs/FRAME_STREAM.md). Existing radar and capture work remains uncommitted; inspect Git status and preserve it rather than treating it as disposable. No device was accessed during the stream-foundation work.

1. Keep the preserved `firmware/build/baseline-before-stream-20261006` archive and reference capture image.
2. Resume from `firmware/releases/usb-optimized-20261006/` and the evidence in `FRAME_STREAM.md`. The live radar stream is installed; the separate raw-pattern image is preserved.
3. Exercise broader scenes/long captures and deliberately load the CPU-backlog guard. Qualify stack usage and physical cable reconnect. The queue and all integrity checks remain bounded.
4. Use representative exported frames to choose the host processing workflow before committing to an onboard reduction.

Previous bench connections were COM13 for the module UART at 256000 baud and COM11 for PA9 at 115200 baud. Check port availability and device state when resuming. Controlled reflector placement needs coordination with the user.

### Update after each session

- Date, completed work and affected checkpoint.
- Source commit or working-tree state; image hash and artifact path.
- Image actually flashed, if any, and observed boot/recovery behaviour.
- Tests and measurements, including failures and unresolved uncertainty.
- Revised processing, memory, precision or transport choices; append structural decisions to `DECISIONS.md`.
- One concrete next action and any physical setup or user observation it requires.

### Work log

- **2026-10-05:** Expanded the existing plan with agreed priorities, baseline evidence, acceptance tracking and handoff instructions. All six implementation stages remain planned.
- **2026-10-05:** Investigated PSRAM through the pinned SDK, manufacturer datasheet and both stock startup/boot configurations. Recorded reproducible static evidence; no hardware probe or flash. No usable PSRAM established.
- **2026-10-05:** Tested lossless first/previous-chirp predictors with byte escapes and block bit packing on existing capture files. All four methods round-tripped exactly on both lanes. Recorded compression sizes; no target implementation, flash, or USB test performed.
- **2026-10-05:** Screened six causal predictors with calculated Rice-code lengths, including block parameters, byte padding, raw fallback, reference chirps and original framing. Previous-chirp prediction remained best on this capture: estimated 33,818 bytes (51.4% of original). Predictor/residual reconstruction was exact; this additional experiment calculates sizes and does not implement a Rice wire codec. See [script](tools/compare_chirp_predictors.py) and [results](output/spi_capture/predictor_comparison.json). Concurrent USB draining may matter more than the modest coding gain: at a hypothetical measured payload rate of 1 MB/s, about 77 kB could leave during a 77 ms burst. Using the earlier 141 kB compressed-frame extrapolation gives about 64 kB of end-of-burst backlog, before processing latency, burst variation and host stalls. This is a sizing scenario, not a measured peak queue or USB result. Benchmark concurrent acquisition, compression and USB before selecting a queue size; deliberately skip whole frames to drain when needed.

- **2026-10-06:** Agreed sequence: lossless raw-frame capture over USB first; evaluate and select a host processing workflow from those frames; port its early stages and export reduced data over USB afterward. Revised milestone, stage order and handoff to replace the earlier intermediate-first/UART-first plan. Documentation only; no firmware change or bench test.

- **2026-10-06:** Preserved 148 baseline files and implemented the portable C block32 previous-chirp codec, bounded LDF1 producer and Python offline/CDC receiver. Original 16-chirp fixtures reconstruct exactly at 35,332 bytes before transfer envelopes; simulated paired 64-chirp frames reconstruct exactly. Added rejection/resynchronization and bounded-queue tests. BR23 component compilation and host checks pass; no streaming image link, USB enumeration, device flash, runtime timing or new acquisition test. See [protocol and integration boundary](firmware/docs/FRAME_STREAM.md).

- **2026-10-07/08:** Radar settings pass before workflow selection. Adopted the in-band 240 MHz sweep (about 0.64 m/bin) as the stream startup profile and flashed it; documented the full register map in [docs/S5KM312CL_REGISTER_MAP.md](docs/S5KM312CL_REGISTER_MAP.md). Sample window, settle time, receive gain and transmit power offer no useful SNR gain: near-range chirp-to-chirp noise tracks transmit power. Raw-band analysis of the 16-chirp recordings: content lies within about +/-28 bins at the old sweep, with only interference tones beyond +/-32, so on-device decimation (or the chip's own 256-sample, step-4 mode) is the path to all 64 chirps per frame. A 240 MHz sweep moves 8 m to about bin 12. Next: prototype the fixed-point decimation filter offline against saved recordings, then a 64-chirp decimated firmware mode.

- **2026-10-08:** Reduction options measured. Offline (`tools/compare_reductions.py`, 240 MHz still/moving recordings): a 49-tap x4 or 97-tap x8 decimating FIR and hardware-FFT bin selection are transparent (changes reproduced 25-45 dB below the signal changes, no added noise). On hardware: the BR23 FFT engine computes exact, unscaled 512-point complex FFTs in 53 us ([HW_FFT.md](firmware/docs/HW_FFT.md)). The radar's own 256-sample, step-4 mode works end to end (11.2 windows/s) but drops samples without filtering, folding out-of-band noise (+0.8 dB) and the 535 kHz tone (to +/-37 bins) into the band. Firmware now supports 256/128-sample records as a build option. Next: choose the onboard reduction, probably a hardware-FFT range transform with exported bins for all 64 chirps.

- **2026-10-08:** Hardware-FFT range-bin export implemented (`--fft-bins K`, codec 2): all 64 chirps of every frame (11.2/s), bins -40..40, about 48 KB/frame, zero device errors, matching the host FFT of raw data to about 1 dB with no added noise. This meets the stage 5 checkpoint for the range transform. Next: viewer support for range-bin frames (spectrum, 64-chirp Doppler, change history; no time-domain views), then make it the installed image.
