# Decision Log

Forward-facing, append-only record of architectural and behavioral decisions for this project. Search this file when structural history can affect the task; newer applicable decisions supersede conflicting older statements.

When a decision is reversed or superseded, append a new entry rather than rewriting the old one.

## 2026-10-03 — Start a BR23 firmware component from the observed interfaces

- **Decision:** Target the likely AC695N/AC6956C using the pinned JieLi BR23 SDK and the RD-03D-derived pin map. Initialize dual receive-only SPI, I2C, module/debug UARTs, and power/bias GPIOs; keep radar power off at startup until configuration traffic is captured. Use direct SPI initialization because the stock driver configures PB1/RESET as an output. CS remains a separately observed input. Provide one-shot DMA and a portable DS RAW record decoder, retaining short boot I/Q as unvalidated.
- **Why:** The schematic and captures support peripheral setup now, while register initialization, continuous acquisition, and tracking require further evidence. Separate the host-tested component from the SDK image-link and hardware validation stages.
- **Supersedes:** (initial)
- **Affects:** `firmware/`, internal interface reference, future radar boot/acquisition implementation.

## 2026-10-04 — Build configurable radar initialization components

- **Decision:** Generate firmware register profiles from the recovered stock tables plus guarded, one-based write-occurrence overrides. Preserve the 75/5 split and provide an explicit fail-fast I2C stage writer. Use the signed official toolchain unpacked into the project cache for target compilation; keep automatic radar startup disabled pending measured power/bias timing and application integration.
- **Why:** Register experiments need reproducible custom builds, and repeated register addresses must retain their startup roles. The first bootable test application can use the logic analyzer for sample observation while application linking and a board-specific loading method are established.
- **Supersedes:** The initial 2026-10-03 component scope now includes recovered/customizable register data and actual target component compilation; its power-off startup contract remains.
- **Affects:** `firmware/` profile generation, init API, component builder, and register experiment workflow.

## 2026-10-04 — Plan UART updates around the existing module UART

- **Decision:** Use a project-owned, bounded UART update receiver over PA1 TX / PA0 RX and the vendor UFW staging engine, with `UART_UPDATA` selecting `uart_user.bin`. Keep the entry service in every replacement application and preserve it when radar startup fails. This records the integration design; the receiver is not yet implemented.
- **Why:** The bundled protocol and library establish the route, while the example receiver has compile-guard, buffer, retry, and baud-state defects. Its separate low-level driver also directly claims UART1, conflicting with dynamic UART ownership.
- **Supersedes:** (initial UART update design)
- **Affects:** `firmware/docs/UART_UPDATE.md`, future application startup, UART ownership, and UFW packaging.

## 2026-10-04 — Link a UART recovery application and package stock-layout UFWs

- **Decision:** Run a bounded custom UART receiver synchronously in `app_core`, using the vendor update engine and preserved `uart_user.bin`. Require successful staging, STOP acknowledgement and verified handoff-record persistence before reset. Link the minimal SDK startup at the stock `0x1E00120` entry, retain the selected register table, and keep radar supply/bias off. Package all four flash variants using a SHA-pinned stock UFW and fixed application slots; keep building separate from the explicit-port PC uploader.
- **Why:** This supplies reproducible complete images and a repeatable-update entry service without importing conflicting soundbox UART or board initializers. One UART owner avoids queued-frame races. Stock-template packaging preserves the known bootloader/layout while byte-identical no-op roundtrips and an independent decoder check its transforms. The clock default and all physical loader/boot behavior still require bench verification.
- **Supersedes:** The UART implementation-pending status above and the earlier component-only build scope. Automatic radar startup remains pending captured supply/bias timing.
- **Affects:** `firmware/target/br23/image/`, UART protocol/PC peer, compiler setup, image builder/packager, and `firmware/docs/IMAGE_BUILD.md`.

## 2026-10-04 — Apply the captured radar profile at boot in recovered stock order

- **Decision:** Enable supply with REXT low, wait at least 20 ms, apply the selected profile's first 75 writes, configure both SPI receivers, assert REXT, wait at least 3 ms, and apply the final five writes. Leave REXT asserted. The SDK timer has 10 ms resolution, so waits round up with a full tick of margin. A radar failure powers it down but preserves UART updating. Acquisition remains separate.
- **Why:** The capture matches all 80 mode-2 writes, and stock code establishes late REXT assertion. Initial REXT low and the settling margins are engineering choices; the captured 2.424396 ms boundary includes SPI/GPIO work, and the stock 1000-loop argument has no established time unit. The user authorized using this evidence without requiring rail captures.
- **Supersedes:** Earlier automatic-startup-disabled and capture-prerequisite decisions.
- **Affects:** Startup, independent supply/bias control, SPI preparation, host failure tests, and image/experiment documentation. Target builds are not bench validation.

## 2026-10-04 — Require explicit stock-to-custom and restoration compatibility

- **Decision:** Treat installing over stock and restoring stock as required compatibility directions, not implied consequences of SDK protocol support. Accept both SDK START payload forms in the PC uploader. Keep stock entry unsupported until the version-specific wrapper and handoff are integrated and validated.
- **Why:** The user expected both directions. V2.14 has a recovered configuration-command 0xB2 wrapper; V2.04 lacks that handler. Stock STOP/baud and zero-valued handoff pin fields need further interpretation. Restoring V2.04 also removes our application's UART entry service.
- **Supersedes:** Any implication that the custom application/host pair alone establishes stock firmware interoperability.
- **Affects:** UART updater, compatibility report and UART integration documentation. No device update was performed.

## 2026-10-04 — Add stock UART entry with a BLE bridge for V2.04

- **Decision:** Implement the recovered Hi-Link B2 wrapper as an explicit uploader mode and provide a separate no-image probe that stops before acknowledging START. For V2.04, use the stock BLE updater to reach V2.14 first, as accepted by the user. Keep the PC peer available across staging whether or not stock emits STOP 0x80.
- **Why:** V2.14 contains a concrete UART entry service; V2.04 lacks the corresponding handler. The official Ai-Thinker PC tool independently supports the remote-file protocol, but its product entry and baud handling differ. Entry success alone cannot validate loader handoff or flashing.
- **Supersedes:** The implementation-pending portion of "Require explicit stock-to-custom and restoration compatibility"; physical validation remains required.
- **Affects:** `stock_uart.py`, `uart_upload.py`, UART entry tests and integration documentation.


## 2026-10-04 — Patch the pinned vendor UART loader for the module's two-wire port

- **Decision:** Add an explicit, hash-guarded packaging step that forces PA1 TX on valid handoff and clears UART1 CON1 while retaining PA0 RX, the vendor flash writer, and application bytes.
- **Why:** Stock hands off TX=RX=PA0; fixing TX exposed START but no reception. Clearing the baud-dependent CON1 value then produced a complete programming transaction at 256000. Preserve this narrow known-image correction with exact hashes and instruction checks.
- **Supersedes:** The requirement to preserve `uart_user.bin` byte-for-byte in "Link a UART recovery application and package stock-layout UFWs". Programming success does not establish custom boot or repeated updating.
- **Affects:** Loader patcher, UART build/bench guides, and stock-to-custom packaging.

## 2026-10-04 — Match stock CPU clock with an explicit I2C clock constraint

- **Decision:** Request 240 MHz CPU, retain the 24 MHz PLL reference, and cap LSB at 48 MHz through the SDK before clock-tree initialization. Preserve the 100 kHz radar I2C rate and eight-bit divider validation. Wrap the vendor setup entry point at build time without editing pinned SDK files.
- **Why:** Captured stock reports 240 MHz CPU. The default 60 MHz LSB at that rate cannot represent a 100 kHz IIC divider and would fail before UART initialization.
- **Supersedes:** The 24 MHz system-clock assumption of the initial minimal image; oscillator reference is unchanged.
- **Affects:** Image configuration/build, project bring-up wrapper, and `firmware/docs/IMAGE_BUILD.md`. Remaining diagnostic/power-init leads are documented in `firmware/docs/BRINGUP_AUDIT.md`.

## 2026-10-04 — Minimal hello-world retains UART recovery and early diagnostics

- **Decision:** Add a hello-world image profile with UART updates, without radar initialization or I2C/SPI setup. Both image profiles reserve UART0 for an early 115200-baud PA9 console, initialize MCU power with sleep disabled and existing VDDIO selections, and report initialization failure instead of immediately resetting. Hold radar supply/bias off until the radar profile explicitly enables them.
- **Why:** Isolate basic boot and repeat updating while making the last reached startup stage visible. The user explicitly required the updater to remain.
- **Supersedes:** Late-only debug and silent peripheral-failure reset in the initial application. PA1/PA0 transport and 256000-baud update entry remain unchanged.
- **Affects:** `build_image.py --application hello`, image console/board/main, UART-only peripheral API, and `firmware/docs/IMAGE_BUILD.md`.

## 2026-10-04 — Enforce SDK power preconditions and audit executable startup

- **Decision:** Run MCU board power after early/platform callbacks; retain supported inherited VDDIO values, but replace unsupported weak level zero with 2.4 V. Keep sleep disabled, LRC explicit and external DCDC control absent. Reject image packaging when linked startup operands or reserved memory layout disagree with the pinned BR23 contract.
- **Why:** The SDK's linked `power_init` asserts on weak level zero, and its example places board setup after filesystem/platform initialization. The next device attempt merits executable-level checks as well as package CRC checks.
- **Supersedes:** Unconditional preservation of weak VDDIO and early-phase board power in the preceding hello-world decision. The SDK still applies its strong-versus-weak rail constraint internally.
- **Affects:** `image/board.c`, clock diagnostics in `image/console.c`, `tools/audit_image.py`, the image builder, and `firmware/docs/IMAGE_BUILD.md`. Original boot failure remains unresolved; no new flash was performed.

## 2026-10-05 — Pico USB entry helper with calibration and automatic reversal

- **Decision:** Add an Arduino-Pico PlatformIO helper on GP10/D+ and GP11/D-. Use open-drain PIO for the key, qualify an ACK with the lines released, then supply 1 kHz calibration edges before a manual cable swap. Alternate key clock/data roles every 500 ms without ACK; stop after 30 seconds or completion. Optional GP15 button starts/stops the sequence.
- **Why:** The user requested a Pico recovery aid, enabled calibration and automatic reversed-pin retries. Published successful Pico examples support this approach on other Jieli chips; BR23 acceptance remains to be measured. External 2.2 kOhm pull-ups detach with the Pico so they do not remain on the PC USB bus.
- **Supersedes:** (initial)
- **Affects:** `tools/pico-usb-key/README.md`, its source/configuration and build artifacts. No automatic target flashing or USB pass-through is implemented.

## 2026-10-05 � Switch Pico W pull-up supply through GP12

- **Decision:** Move the two 1 kOhm resistor supply ends to GP12; drive GP10/11/12 at 12 mA. GP12 stays low outside an active attempt. Allow three seconds for a continuous 500 us high startup interval before key transmission. Keep manual power coordination; no extra sense wire.
- **Why:** User reports possible back-power and intermittent immediate preflight failures. User selected Pico W and declined additional wiring.
- **Supersedes:** Fixed 3V3 resistor supply and immediate preflight rejection in the preceding Pico helper entry.
- **Affects:** `tools/pico-usb-key/README.md` and helper source/configuration. Turning off GP12 makes the external resistors pull down; unplug the entire injector before PC connection.

## 2026-10-05 - Hello heartbeat on the module UART

- **Decision:** The hello profile emits an immediate and one-second ASCII heartbeat on PA1/COM13 at 256000 baud. Keep PA9 early diagnostics. Run the heartbeat in app_core outside the blocking updater, suppressing it throughout update transactions.
- **Why:** User wants boot/liveness visible on the existing serial connection.
- **Supersedes:** Protocol-only idle output for the hello profile. Radar profile behavior is unchanged.
- **Affects:** `image/main.c`, `firmware/docs/IMAGE_BUILD.md`; candidate in `firmware/build/hello-heartbeat`. Target build/startup audit and host tests pass; not flashed.

## 2026-10-05 - Initialize the retained full logger before task startup

- **Decision:** Use `CONFIG_DEBUG_ENABLE` with SDK `log_early_init(1024)`, preserving mutex/buffer initialization; SDK assertions flush logs and halt. Reject packaging unless selected logger constructor and OS/setup/task/scheduler calls are present in the final executable in the reviewed order.
- **Why:** PA9 captured the full logger using an uninitialized mutex under the previous lite-debug configuration. Macro/source/library dependencies must be checked together.
- **Supersedes:** Lite-debug selection in the early-console image configuration. UART pins, baud rates, loader transport and radar configuration remain unchanged.
- **Affects:** Image configuration, runtime audit, image builder, and `firmware/docs/BRINGUP_AUDIT.md`. Physical success remains to be tested.


## 2026-10-05 - Reserve a boot recovery window before application initialization

- **Decision:** Both profiles open the 256000-baud updater first and poll for at least three seconds before application/radar work. A valid READY latches recovery until reset, including failed transfers. Radar setup preserves the existing UART and its RX buffer.
- **Why:** A later application failure must remain recoverable by starting the uploader and power-cycling. Avoid making radar initialization a dependency of UART entry.
- **Supersedes:** Radar-before-updater startup and immediate hello heartbeat. SDK startup still precedes recovery; no independent rescue image or automatic watchdog reset is added.
- **Affects:** image/main.c, image/uart_loader.c, peripherals.c, host boot/peripheral tests, and firmware/docs/IMAGE_BUILD.md. Target builds/tests pass; recovery-window firmware is not flashed.


## 2026-10-05 - Separate bounded SPI capture profile

- **Decision:** Keep hello/radar behavior separate from a capture profile with two aligned 8 KiB buffers, armed before REXT. Stop radar/DMA before serial dump; bound acquisition to two seconds and cancel on updater entry. Mark incomplete buffers explicitly and retain raw bytes.
- **Why:** Capture both receiver lanes without an external analyzer or concurrent acquisition/UART throughput assumptions, while preserving the tested boot recovery path.
- **Supersedes:** No acquisition in the capture profile; hello and radar profiles retain their prior scope.
- **Affects:** capture.c, app.c, image/main.c, image builder, capture tests/decoder and firmware/docs/IMAGE_BUILD.md. First dual-lane capture validated; detailed bench provenance lives in the image guide.


## 2026-10-05 - Expand one-shot capture to sixteen whole records per lane

- **Decision:** Allocate 32896 bytes per lane (16 x 2056-byte DS RAW records), retaining the two-second deadline, stop-before-dump behavior and boot recovery. Decoder accepts bounded, line-aligned lengths and exports IQ CSV plus individual validated packets.
- **Why:** The first 8 KiB snapshots ended partway through their fourth record; larger buffers allow consecutive-chirp comparisons while leaving 91296 bytes of main RAM heap reservation.
- **Supersedes:** Two 8 KiB buffers in the earlier bounded capture decision.
- **Affects:** capture.c, capture tests, decode_capture.py, plot_capture.py and IMAGE_BUILD.md. Hardware produced sixteen checksum-valid records on each lane; raw evidence is in output/spi_capture/dual_lane_16chirps.


## 2026-10-05 - Plan shared range processing and configurable export

- **Decision:** Use `DSP_plan.md` as the working plan and session handoff. Target a complete 64-chirp, two-receiver frame of configurable complex range intermediates, initially budgeting 64 bins subject to sample interpretation and measured numeric/resource limits. Accept reduced whole-frame export cadence and keep losses explicit.
- **Why:** Shared intermediates support Doppler, bearing and small-motion consumers with independent filtering. Stock firmware offers examples rather than a required architecture. Continuous raw export is not a prerequisite.
- **Supersedes:** No implemented behaviour; this records the agreed next direction.
- **Affects:** `DSP_plan.md` and README navigation. Continuous acquisition, range processing and binary export remain planned. The existing recovery contract remains required.


## 2026-10-06 - Capture raw frames over USB before selecting onboard reduction

- **Decision:** First implement bounded acquisition, streaming lossless compression and USB export of complete raw frames at reduced cadence. Use those frames to evaluate and select a host processing workflow, then port its early stages and transmit the reduced representation over USB.
- **Why:** Representative full frames let us measure algorithm performance and information loss before committing to a reduction. Concurrent USB draining reduces the required capture backlog.
- **Supersedes:** The intermediate-first milestone and UART-first export sequence in "Plan shared range processing and configurable export" (2026-10-05). The 64-bin representation becomes a candidate rather than the initial target.
- **Affects:** DSP_plan.md. Preserve the UART boot recovery contract and diagnostic raw capture. Target throughput, compression timing and full-frame capture remain unvalidated.


## 2026-10-06 - Establish a bounded lossless frame stream before USB integration

- **Decision:** Implement LDF1 with independent paired 64-chirp frames, previous-chirp block32 lossless coding, raw fallback, preserved radar bytes and CRCs. Use a caller-owned queue with atomic messages, reserved ABORT capacity, explicit skips/rejections and a bounded-copy transport callback. Publish only complete verified frames on the host.
- **Why:** The existing capture supports this codec and exact host reconstruction. A transport-independent producer permits stall/overflow testing before continuous acquisition; the SDK CDC wrapper's mutex and bulk-write loop are not yet qualified for that path.
- **Supersedes:** Host-experiment-only codec status; the raw-first milestone remains. This is a component, not an enabled streaming image.
- **Affects:** firmware/src/stream.c, firmware/include/ld2450_stream.h, firmware/tools/frame_stream.py, firmware/docs/FRAME_STREAM.md, component builds/tests and DSP_plan.md. Preserve UART recovery and existing application profiles; measure USB/acquisition/timing before integration claims.


## 2026-10-06 - Integrate continuous acquisition and native CDC streaming

- **Decision:** Add stream and radar-off usb-bench profiles. Use four record-sized DMA slots per lane, IRQ rearm, TIMER3 observation timestamps, paired chirp-zero synchronization, a 48 KiB output queue and a project-owned 64-byte CDC endpoint buffer. Keep SDK USB buffers outside audio overlays. The pinned SDK remains unchanged.
- **Recovery contract:** Keep the three-second boot recovery window and 256000-baud UART updater. Use bounded idle UART reads; stop radar/USB before entering the existing updater. ASCII ? on module UART stops first, then reports on PA9. No acquisition-time debug printing.
- **Loss contract:** USB absence/backpressure skips or rejects complete export frames. A DMA ownership overrun stops the radar until restart; never rearm mid-record. USB reset/suspend/DTR/SOF loss invalidates partial output. Complete paired acquisition is counted independently of export.
- **Evidence:** stream SHA256 388a98cf4c637a0d8863df2fedb7c248b77d027016525d1f74104075c9e0c8c4 is flashed. A 10.58 s acquisition-only run has 117 complete paired frames, zero corrupt/sequence/DMA errors; active UART updater reentry passes. Twelve CTest suites and 34 Python tests pass; both target profiles link and package.
- **Supersedes:** Component-only status in the prior frame-stream decision. Native USB is not wired: enumeration, concurrent codec/USB timing, throughput/stalls and physical memory accounting remain unqualified. See firmware/docs/FRAME_STREAM.md and output/firmware_build/stream_integration_validation_20261006.json.


## 2026-10-06 - Isolate raw USB transport and budget the codec service time

- **Decision:** Add --raw-usb-bench only to the radar-off usb-bench profile. Label its identity synthetic/paced/raw-only; reuse existing LDF1 raw mode and require exact host comparison. Keep this known-pattern image as the current hardware baseline while concurrent real-radar export remains under investigation.
- **Timing contract:** Stream/acquisition/parser compile with -O2. CRC uses a byte table and startup-copied internal RAM; packing computes each residual once and writes bytes rather than bits. Preserve all integrity checks and the wire format. A stopped UART report snapshots USB/DTR/endpoint counters and clock registers without hot-path printing.
- **Why:** Correct 240 MHz clock setup did not make the original per-bit loops meet the DMA deadline. Raw USB separates transport correctness from that CPU budget and the distinct output-queue budget.
- **Affects:** firmware/docs/FRAME_STREAM.md; detailed evidence and remaining limits in DEBUG_LOG.md and output/firmware_build/usb_debug_validation_20261006.json.


## 2026-10-06 - Interrupt-driven CDC and bounded live frame export

- **Decision:** Retain native CDC bulk endpoint 4 and the existing LDF1 wire format. Use a 4 KiB owned staging ring, separate USB DMA buffer and completion-driven packet submission. The main producer copies at most 2 KiB per call; queue and USB ownership are serialized against reset/completion interrupts. Flush short tails/ZLP only at output boundaries. Epoch changes discard staged bytes; hosts resynchronize independently.
- **CPU contract:** Slicing-by-four IEEE CRC with a 4 KiB RAM table; -O2 for project hot paths and the generated SDK USB dispatcher. Acquisition passes a VALID decoder result for its unchanged owned candidate, eliminating the second radar checksum pass. The ordinary API validates, and header/payload/raw CRCs remain mandatory. At two pending DMA records, reject the current export with ABORT reason 6 and continue input validation. Four-slot DMA ownership overflow still stops safely.
- **Memory contract:** 88 KiB producer queue, generated together with configuration identity. Queue indices remain size_t and support crossing 64 KiB. Final link reservations are 24,320 main heap plus 11,648 secondary heap bytes; no PSRAM assumption. SDK-reported free heap is not trusted. Frame skips and explicit rejection remain permitted; retained frames must contain all 128 records.
- **Evidence:** 159 host-validated complete frames in 30.003 s, ~680 kB/s compressed wire data; zero acquisition errors, output overflows or CPU-budget rejections in that run. Raw-pattern throughput ~790 kB/s, 29 exact frames. Reader pause/reopen recovers. Details and qualifications: firmware/docs/FRAME_STREAM.md and output/firmware_build/usb_optimized_validation_20261006.json.


## 2026-10-06 - Extensible local live radar visualizer

- **Decision:** Use a loopback Python server with NumPy processing and a browser Canvas UI. Reuse the LDF1 decoder as the sole integrity boundary; publish only complete paired frames. Discover native USB by VID/PID/serial and assert DTR without touching updater/debug UARTs.
- **Flow contract:** Separate USB reading, decoding and processing. Bound the byte queue at 4 MiB and stop visibly on overflow. Keep only the latest pending processing frame, counting display drops independently of device export skips. A frozen or closed browser never pauses acquisition. Raw recordings preserve original wire bytes with hashes; snapshots preserve complete lane binaries.
- **Extension contract:** Named processing stages consume a shared frame context and publish products with explicit units. Source/configuration changes clear references and history. Keep FFT-bin and slow-time-Hz axes until distance, velocity and angle calibration exists; do not label features as targets.
- **Canonical guide:** docs/LIVE_RADAR_VIEWER.md. Firmware and wire format are unchanged.


## 2026-10-06 - Distinguish firmware export protection from host invalidation

- **Decision:** Retain valid LDF1 ABORT reasons in host decoder diagnostics and display buffer-full, CPU-backlog, other-abort and non-ABORT invalidation counts separately. Total rejected exports still includes all rejected candidates; no incomplete frame becomes displayable. Device telemetry updates on each validated BEGIN, even when no candidate completes. Active wire rate must not be zeroed solely because completed-frame age grows.
- **Why:** A motion demonstration exposed both real firmware resource limits and misleading/stale viewer diagnostics. Clear counters identify the limit without treating it as a checksum failure or claiming the streaming limitation is fixed.
- **Scope:** Host diagnostics only; no wire format, firmware, sample-retention or protective-threshold change. See DEBUG_LOG.md and docs/LIVE_RADAR_VIEWER.md for evidence and remaining work.


## 2026-10-06 - Raw 16-chirp live export windows

- **Decision:** Export physical chirps 0-15 from both receivers in fixed-size LDF1 raw mode, retaining all 512 complex samples per chirp. Continue validating all 64 physical chirps and skip whole frame starts while output drains. Declare 16 chirps in BEGIN; decoder/viewer support both 16 and 64.
- **Why:** The user chose shorter captures after moving scenes repeatedly exceeded the compressed 64-chirp CPU/queue budget. A complete 67,100-byte raw export fits the existing 90,112-byte queue without USB service. Preserve all integrity checks and protective guards.
- **Tradeoff:** Later 48 chirps are deliberately omitted; slow-time bins become about 52.1 Hz instead of 13.0 Hz at 1.2 ms/chirp. Radar configuration is unchanged.
- **Supersedes:** The 128-record retained-frame requirement for this live profile in Interrupt-driven CDC and bounded live frame export. Full64 remains a build option.
- **Affects:** firmware/docs/FRAME_STREAM.md, DSP_plan.md, docs/LIVE_RADAR_VIEWER.md.


## 2026-10-06 - Preserve full spectrum with selectable central zoom

- **Decision:** Default spectrum/history view to signed bins-16..16, with0..32 and full-256..255 options. Crop only at drawing time, retaining full FFT, history and raw samples. Keep axes uncalibrated and leave Doppler processing unchanged.
- **Why:** Sampling/sweep experiments distinguish fixed outer tones from sweep-sensitive central structure that was compressed into a few screen pixels. Do not notch or label outer tones as targets.
- **Firmware:** Sampling/slope profiles are diagnostics only; restore the archived raw16 baseline after comparison. No permanent RF-setting change.
- **Affects:** docs/LIVE_RADAR_VIEWER.md; detailed bench evidence in DEBUG_LOG.md and output/radar_analysis/spur_four_way_comparison/.


## 2026-10-06 - Live radar register control over native USB

- **Decision:** Add LDC1 host commands on the CDC bulk OUT endpoint: READ, WRITE and REINIT for the radar's I2C registers, answered by LDF1 type-5 REPLY messages between frames. BEGIN's former reserved u16 becomes the register generation (every live WRITE/REINIT since boot). The viewer gains a Radar registers panel and identifies settings by build configuration plus generation.
- **Why:** Access to every chip setting is a main purpose of the custom firmware; flashing one image per register experiment is too slow, and there is no chip documentation to work from. The user explicitly asked for no register, value, frequency or power restrictions: this is a home-laboratory instrument and the user takes responsibility for staying in the legal band.
- **Integrity:** Writes run only in the inter-frame gap so no frame mixes settings; every frame states its generation; replies travel in the recorded wire stream. REINIT disarms DMA before power-cycling, so restarts never begin mid-record.
- **Supersedes:** "The viewer never sends radar commands" (docs/LIVE_RADAR_VIEWER.md) and BEGIN reserved=0. Images without control still send generation 0 and ignore commands.
- **Status (2026-10-06):** Installed as `firmware/build/stream-raw16-control5/update-two-wire.ufw`. The I2C read protocol (register byte, repeated start, two big-endian bytes) is verified: a 120-register dump matches every stock-written value (`output/live_radar/register_dump_20261006.json`). Final image `stream-raw16-control5`: all 128 registers 0x00-0x7F read repeatably with no lost commands; REINIT verified. Two SDK/chip constraints shape the design (DEBUG_LOG.md): the SDK bulk-OUT read may only be entered with a packet waiting, and some registers read slowly, so commands execute one transaction per inter-frame gap and the host keeps one command in flight.
- **Affects:** firmware/include/ld2450_radar_control.h, src/radar_control.c, src/stream.c, src/app.c, target/br23/image/stream_app.c, firmware/tools/frame_stream.py, firmware/tools/build_image.py, tools/radar_viewer/, firmware/docs/FRAME_STREAM.md, docs/LIVE_RADAR_VIEWER.md.


## 2026-10-06 - Software I/Q mismatch correction

- **Decision:** Correct each receiver's I/Q gain and phase mismatch in the viewer pipeline, fitted on demand from a static scene (Calibrate I/Q), rather than by register trims. Raw samples, recordings and the waveform/constellation views stay uncorrected.
- **Why:** The bench register sweep found no phase trim. The mirror is dominated by a quadrature phase error (-18 / -15 deg); 0x65 gain steps are 2.6 dB, too coarse for RX2's 0.8 dB gain error. The model alpha = (1 - u)/(1 + u) predicted every 0x65 step to 0.1 dB, and the correction lowers negative-bin energy by 15-16 dB.
- **Scope:** Session-local and cleared on any settings-identity change, like the background reference. Not persisted or applied on the device; a future onboard stage could use the same two parameters per receiver.
- **Evidence:** output/live_radar/register_sweep_20261006*.jsonl (two runs, 183/184 tests agree), register_experiments_20261006.json, docs/LIVE_RADAR_VIEWER.md.


## 2026-10-08 - Adopt the 240 MHz in-band sweep and close register reverse engineering

- **Decision:** Stream images start the radar with `firmware/config/radar_sweep240_mode2.json`: start 24.005 GHz (0x53/0x54 = 0x0A00/0x8889) and rise/fall steps +/-20 (0x56 = 0x0014, 0x58 = 0xFFEC), about 240 MHz over the unchanged 420 us ramp, ending about 24.245 GHz. Transmit power (5 dBm), receive gain, timing and sampling stay stock. `docs/S5KM312CL_REGISTER_MAP.md` is the register reference; reverse engineering is complete for DS RAW use.
- **Why:** About 15% finer range bins (~0.64 m) inside 24.0-24.25 GHz; the spectrum stretched x1.18/1.165 against a predicted 1.176, twice. ICLegend's EVBKS5 manual recommends exactly 24005-24245 MHz for a 240 MHz sweep. The vendor GUI decode explains the remaining data-path registers. More transmit power or receive gain does not improve near-range SNR: near-range chirp-to-chirp noise tracks transmit power. Brief user-approved sweeps to 2 GHz (top 26.0 GHz, minimum power) resolved returns ~0.24 m apart; the user chose to stay in band.
- **Rules:** Waveform/timing registers take effect only across a 0x40 hold (0x4207) and release (0x0207). Transmission outside 24.0-24.25 GHz or above stock power needs the user's explicit approval for that experiment.
- **Evidence:** UFW SHA-256 `413aaf0f7c5d76f1e07c041cadf4b1a7e65c557a25e47f1bf0f02540bb1d1b56`, flashed 2026-10-08 over COM13 (417 reads, success); stream configuration `c8dd4388...`; sweep registers read back. Archive `firmware/releases/usb-raw16-sweep240-20261008/`; bench data in `output/live_radar/register_tuning_20261007.jsonl`, `register_sweep_relatch_20261007.jsonl`, `wide_sweep_20261008/`, and `output/radar_analysis/evbks5_vendor_package/`.
- **Supersedes:** The stock mode-2 sweep (24.025 GHz, +/-17) in live stream images. The previously installed stock-sweep control image is archived as `firmware/releases/usb-raw16-control-20261006/`.
- **Affects:** firmware/config, firmware/releases, docs/S5KM312CL_REGISTER_MAP.md, tools/radar_viewer/register_findings.json, tools/register_sweep.py (hold/restart, all-bit masks, chirp-noise and frame-period metrics), FRAME_STREAM.md.


## 2026-10-08 - Export hardware-FFT range bins for all 64 chirps (LDF1 codec 2)

- **Decision:** Add a range-bin export mode (`--fft-bins K`). Each validated record is transformed on the BR23 FFT engine (512-point complex, unscaled), and bins -K..K are sent as codec-2 RECORD messages: DC as int32, other bins int16 with a per-record block shift. BEGIN version 2 adds FFT points, K and the bin format. Raw (codec 0/1) images and their wire format are unchanged. K = 40 is the working choice (about 25 m at 0.64 m/bin).
- **Why:** Every frame now carries all 64 chirps (13 Hz Doppler bins) at about 540 kB/s. Raw export could fit only 16. Offline comparison and hardware tests show the reduction is transparent in the kept band: the profile agrees with raw to about 1 dB, noise within 0.3 dB, zero device errors at 11.2 frames/s. The radar's own 256-sample mode was rejected as the main route because it drops samples without filtering, folding noise and a 535 kHz tone into the band. A software decimating FIR remains a fallback.
- **Integrity:** The radar checksum is verified on the device before the transform; the host verifies record identity, message CRCs, sequence and frame completeness. Raw-sample checks (raw CRC, radar checksum) are not possible for range-bin frames. Use a raw image for raw evidence.
- **Status:** Implemented, tested (21 CTest suites including C-to-Python round trip against NumPy) and bench-validated, but not installed. The viewer cannot display range-bin frames yet; the raw 16-chirp 240 MHz release stays installed until it can.
- **Affects:** firmware/include/ld2450_stream.h, src/stream.c, target/br23/image/stream_app.c, firmware/tools/build_image.py, firmware/tools/frame_stream.py, firmware/tests, firmware/docs/FRAME_STREAM.md, DSP_plan.md.


## 2026-10-08 - Install the range-bin image; the viewer is range-bin only

- **Decision:** The installed image is the 64-chirp range-bin stream (`firmware/releases/usb-bins40-20261008/`, K = 40, 240 MHz sweep). The live viewer processes only range bins: device codec-2 bins, or a host FFT of older raw recordings (same 512 points, K = 40), through one bin-domain pipeline. DC removal, background, I/Q correction and the Hann window are exact bin-domain operations. Views and tools that need time samples are deleted: complex waveform, within-chirp spectrogram, linear-trend removal, raw-sample constellation, and `tools/register_sweep.py` (its results remain under output/ and in the register map; the tool is in git history before this change).
- **Why:** The user chose not to keep features that can no longer work with the installed format ("there's not likely to be steps backwards"). Raw firmware images remain buildable for raw evidence, and raw recordings remain replayable as bins.
- **Evidence:** Viewer tests (23) include device-format bins matching host conversion of raw frames within 0.05 dB for spectrum, Doppler and change, with and without I/Q mismatch. Live: 64 chirps, bins -39..39 displayed, 10.9 frames/s, 542 kB/s, 1.35 ms processing per frame, no stage errors.
- **Supersedes:** "Range-bin export ... Not installed" status in the previous entry, and the raw 16-chirp image as the installed image.
- **Affects:** tools/radar_viewer (processing.py, web/app.js, web/index.html, test_viewer.py), docs/LIVE_RADAR_VIEWER.md, firmware/releases.


## 2026-10-08 - Host detection with tracking and a clutter map; both receivers summed

- **Decision:** The viewer detects targets with CA-CFAR on the summed power of both receivers (threshold 10 dB, was 13) over the 64-chirp range-Doppler map. It measures angle from the RX2-RX1 phase, follows objects with a constant-velocity Kalman tracker (confirmed after 3 of 5 frames, coasting up to 1 s) and rejects persistent returns with a per-cell clutter map (10 s average, 10 dB margin). Parameters live in `tools/radar_viewer/calibration.json`.
- **Why:** The user asked whether requiring both receivers to see a target would cut noise. Injected targets in recorded noise, at equal false-alarm rate: summed power needs about 3 dB less signal than one receiver; best-angle coherent combining is no better; an RX1/RX2 coherence gate is worse (the Hann window already gives noise coherence about 0.5). False tracks in an empty room came from real but out-of-view returns (Doppler lines at multiples of about 102 Hz at 1.2-1.8 m), which both receivers see. So consistency over time and against the long-term average does the job instead.
- **Rules:** The clutter map starts empty and is not updated near confirmed, moving tracks younger than 4 s, so walkers are not learned. A person who stays put is eventually learned.
- **Evidence:** `output/live_radar/20261008-030525-capture-51fbe3` (noise), `20261008-113257-capture-7cd819` (empty room: no tracks once learned). Synthetic walker in that clutter: 94-99% of frames tracked at 0.3 and 1.0 m/s, about 50% at 0.6 m/s (on a clutter line).
- **Affects:** tools/radar_viewer (processing.py, calibration.json, web/), docs/LIVE_RADAR_VIEWER.md, DSP_plan.md.


## 2026-10-08 - Sweep width is the user's choice in the viewer

- **Decision:** The viewer's **02 / Sweep** panel sets the sweep to 240 MHz (in band, default) or 480 MHz, 1 GHz or 2 GHz (out of band) from 24.005 GHz. Out-of-band runs need the user's acknowledgement each time; the server writes minimum transmit power (0x6D 0x9740 / 0x70 0x26A0) before widening, and re-inits to the in-band build profile on a 1-30 minute timer, a failed write, **Restore in band now**, disconnect or shutdown. Each connection reads 0x56 and flags a radar left out of band.
- **Why:** 0.64 m range bins are coarse for indoor use; the user wanted to see wider-sweep performance and to decide "if and when to safely bend the rules" themselves, rather than have experiments started from scripts. The default stays in band at stock power.
- **Supersedes:** In the 240 MHz entry above, "transmission outside 24.0-24.25 GHz or above stock power needs the user's explicit approval for that experiment" is now met by the per-run acknowledgement in the viewer. Scripts still do not start out-of-band runs.
- **Limits:** A killed server cannot restore the sweep; power-cycling the module re-applies the in-band profile.
- **Evidence:** Viewer tests (37) with a simulated device cover write order, minimum power, range scaling to the live step and every restore path. Commit 2d0a2dc.
- **Affects:** tools/radar_viewer (server.py, processing.py, web/), docs/LIVE_RADAR_VIEWER.md.
