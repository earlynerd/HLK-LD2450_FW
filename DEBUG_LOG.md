# Debug log

## 2026-10-04 — V2.14 entry probe required the actual module UART rate

- **Observation:** After a BLE update, the entry probe at 256000 received only zero bytes and no configuration ACK.
- **Root cause:** `firmware/tools/stock_uart.py:129` defaults to 256000; the connected module was measurably transmitting valid target frames at 9600. The reason the device rate changed is not established.
- **Fix:** Use the existing `--baud 9600` option. First attempt had a corrupt FF ACK header; an unchanged retry obtained FF/A0/B2 acknowledgements and START. No image data was sent, and no parser relaxation was needed.
- **Class:** baud-assumption
- **Recently-touched?** Yes, the probe was newly implemented; its valid-frame filtering correctly rejected the damaged ACK.


## 2026-10-04 — Stock staged UART loader needed two-wire corrections

- **Observation:** Stock V2.14 staged 45 loader blocks, reset, and resumed stock with `UPDATA_DEV_ERR (0x5a04)`. The application had not been programmed.
- **Root cause:** Stock handoff at `0x1e19552` supplies TX=RX=PA0; loader `0xa40e` uses that TX value. After forcing PA1, START appeared but its receive DMA buffer remained empty. Loader `0xa482` also produced CON1=0x30 at 256000; clearing that register value enabled reception. The precise semantics of every CON1 bit are not claimed.
- **Fix:** `firmware/tools/patch_stock_uart_loader.py` applies the two hash-guarded instruction substitutions and rebuilds LZ4/header/UFW CRCs. Application bytes are unchanged. Adding a 10 ms host reply delay alone did not help.
- **Verification:** 22 Python tests pass; final bench transfer completed 419 reads and returned `03 00`. Custom boot remains unresolved: COM11 at 115200 and a COM13 READY probe were silent. Full traces and hashes are linked from `firmware/docs/UART_LOADER_BENCH.md`.
- **Class:** loader-pin-and-control-configuration
- **Recently-touched?** The host/image pipeline was new; the original vendor loader and stock handoff contained the incompatible settings. This entry resolves the handoff defect, not the outstanding boot issue.


## 2026-10-04 — No custom startup output after programming and power cycle

- **Observation:** User reports no UART output/RX LED activity even during power cycling. COM11 at 115200 capture remains empty; the capture session has ended and released the port.
- **Root cause:** Unresolved. `firmware/src/app.c:15` returns without printing on basic peripheral initialization failure, and `firmware/target/br23/image/main.c:16-21` resets before the banner in that case. Both normal radar-init status and the banner occur after peripheral setup; neither is an early boot marker. This is a concrete observability gap, not proof of the failing stage.
- **Fix:** None applied; preserve the programmed artifact. Next diagnosis needs visibility before peripheral/radar initialization and confirmation of a usable recovery/loading path.
- **Class:** early-boot-observability
- **Recently-touched?** Yes; this is the first hardware execution attempt of the project-owned application/startup integration.

## 2026-10-04 — Bring-up clock and pin-routing audit

- **Observation:** First custom image remains silent after programming and power cycle; user identified clocks and pin mux as leads.
- **Root cause:** Still unresolved. `firmware/target/br23/image/app_config.h` requested 24 MHz CPU while captured stock reports 240 MHz. Raising CPU alone would introduce another silent failure: `peripherals.c:79-81` rejects divider 299 at 60 MHz LSB / 100 kHz I2C before UART opens. The IIC BAUD register is eight bits in the pinned SDK.
- **Fix:** Request 240 MHz CPU, retain the separate 24 MHz oscillator reference, and apply the SDK 48 MHz LSB limit before vendor clock initialization through project `bringup.c`. No pin remapping or power-mode change was justified by the audit.
- **Verification:** Target image links/packages in `firmware/build/bringup-240mhz`; linked instructions apply the limit before clock initialization. Five native suites and 22 Python tests pass, including 48 MHz divider and 60 MHz rejection coverage. Not flashed. See `firmware/docs/BRINGUP_AUDIT.md` for missing early debug/board-power stages and pin-path evidence.
- **Class:** startup-clock-contract
- **Recently-touched?** Yes; custom startup integration is new. This does not establish that the original 24 MHz setting caused the silent boot.

## 2026-10-04 — Make bring-up visible and isolate hello-world from radar startup

- **Observation:** All original project messages came after peripheral setup, and peripheral failure reset the CPU without printing. The SDK example's board power setup was absent.
- **Root cause:** Those source-level gaps are confirmed; the original device's failure stage is still unknown.
- **Fix:** Enable the SDK early debug hook with a dedicated PA9 console, add MCU power initialization with sleep disabled, and replace immediate failure reset with repeated numeric diagnostics. Add a UART-only hello-world profile with the existing updater and a one-second idle greeting. No radar register table, I2C or receive-SPI initialization runs in that profile.
- **Verification:** Hello and radar images link and package. Five native suites and 22 Python tests pass, including UART-only initialization/update preparation/cleanup without I2C/SPI or radar GPIO operations in that path. Board startup deliberately holds only the two radar power controls off. Target disassembly confirms early console setup and retained update engine; no device was flashed.
- **Class:** early-boot-observability
- **Recently-touched?** Yes. This resolves the source omissions and diagnostic behavior, not the unobserved hardware boot failure.

## 2026-10-04 — Second offline audit before another device attempt

- **Observation:** Original custom application is still silent; user requested another example/binary review before risking another module.
- **Root cause:** Original failure remains unresolved. In the unflashed hello revision, `image/board.c` copied weak VDDIO level zero into `power_init`, whose linked code asserts on zero (`build/hello/sdk-disasm.txt`, address `0x1e04c7a`). Its early callback also preceded the filesystem/platform callbacks, unlike the SDK example's board setup. Neither issue was present in the original image, which omitted this initializer.
- **Fix:** Guard unsupported weak level zero with the SDK's minimum accepted 2.4 V level; explicitly select LRC/no external DCDC control; move board power to the normal initcall phase. Print clock getters and UART divider after early console setup. Add post-link checks for startup operands, RAM/reserved-region separation, section packing and board callback phase.
- **Verification:** Exact stock/custom startup comparison found matching boot-parameter and RAM initialization conventions. Both profiles target-link; five native suites and 26 Python tests pass. Vendor objcopy independently matches text/data; the separate jl-misctools decoder recovers identical applications from all four candidate flash variants. Original flashed artifact hash is unchanged. Candidate `build/hello-audited/update-two-wire.ufw` SHA256 `1899120fc63c818ac899e12a76c80dd4db3eae08721e5a66b5dc309a4f90b264`; no device access. Evidence: `output/firmware_build/boot_audit_validation.json`.
- **Class:** startup-power-preconditions-and-layout
- **Recently-touched?** Yes; the power guard and ordering address the latest unflashed board integration. Hardware boot and repeat updating remain unverified.

## 2026-10-05 � Gate Pico pull-ups and allow startup settling

- **Observation:** One apparent entry indication but no PC enumeration; repeated both-lines-high preflight failures. User suspects resistor back-power.
- **Root cause:** Previous `tools/pico-usb-key/src/main.cpp:104-116` aborted on the first low sample. Previous `releaseLines()` at line 48 could not control resistors wired directly to 3V3. Physical back-power and failed enumeration remain unconfirmed causes.
- **Fix:** GP12 controls the resistor feed, low on all exits; bounded startup high qualification replaces immediate rejection; set all three GPIO drive strengths to 12 mA. Preserve Pico W board selection and avoid redundant CYW43 LED writes in polling.
- **Verification:** Pico W target build, ELF waveform simulation and native startup/ACK timing tests pass. Packaged `build/pico-w-usb-key.uf2`; no hardware flashed or electrical/USB behavior verified.
- **Class:** startup-precondition-and-external-pull-control
- **Recently-touched?** Yes; helper introduced in the preceding work.

## 2026-10-05 - PA9 confirms custom execution and an RTOS memory-write exception

- **Observation:** Second module cold-start capture at COM11/115200 prints the custom early boot marker, sys=240000000 and lsb=48000000, then `cpu_write_data_over_limit`. No board-power/app_main/heartbeat marker was captured.
- **Evidence:** `output/stock_uart_compatibility/pa9_hello_boot_20261005T170332Z/` contains raw bytes, timestamped chunks, readable boot text and ELF symbol mapping. RETI/RETS 0x2088 maps to `vTaskPlaceOnEventList`; trace 0x1a1a/0x1a34 maps to `vListInsert`. These locate the exception context, not its cause. The VDDIO LVD reset-source line alone is not proof of a supply fault.
- **Status:** No fix applied; execution before app_main is now confirmed. Investigate runtime task/list state and configured write protection against this exact ELF. No further flash performed.
- **Class:** runtime-startup-memory-write-exception
- **Recently-touched?** Yes; custom runtime integration and hello profile.

## 2026-10-05 - Logging mutex omission identified in the captured startup crash

- **Observation:** PA9 exception occurs in the logging mutex receive-list path, before app_main.
- **Root cause:** High-confidence source/binary diagnosis: `firmware/target/br23/image/app_config.h:6` selects lite debug, omitting the mutex initializer guarded by full debug at SDK `cpu/br23/setup.c:217-218`; the custom builder also omits the lite-mode no-op logger replacements. Full `log_print` remains linked and waits on an uninitialized `log_mutex`.
- **Evidence:** Crash r0=0x4b68 equals `log_mutex` 0x4b44 + 36; mutex return points into `log_print`; vendor LLVM IR identifies the omitted constructor. The first flashed ELF also lacks it. Exact setup preprocessing with full debug restores the initialization call. See `firmware/docs/BRINGUP_AUDIT.md` and `output/firmware_build/pa9_crash_analysis/`.
- **Fix status:** Proposed full-debug configuration; no firmware source edit or flash in this investigation. Physical correction not yet validated.
- **Class:** missing-runtime-initialization
- **Recently-touched?** Yes; minimal SDK integration and debug configuration.

## 2026-10-05 - Restore full logger initialization and reject its omission at build time

- **Root cause:** Previous entry identifies the logging mutex constructor skipped by the lite/full configuration mismatch.
- **Fix:** `firmware/target/br23/image/app_config.h` selects full SDK debugging. New `audit_runtime.py` runs before packaging to enforce logger constructor calls and setup/task/scheduler order in final disassembly.
- **Verification:** Exact failing ELF is rejected; corrected hello and radar images pass. Five native suites and 31 Python tests pass. Focused retained-service review found no second confirmed omission; evidence and limits are in `firmware/docs/BRINGUP_AUDIT.md`.
- **Class:** missing-runtime-initialization
- **Recently-touched?** Yes. Source correction and build checks complete; hardware correction is unverified and no further flash occurred.


## 2026-10-05 - Logger fix boots and UART application replacement succeeds

- **Observation:** Fresh stock V2.14 at 256000 accepted hello-logfix (419 reads), reached app_main/updater and sent 15 heartbeats in 15 seconds. User-confirmed power cycle produced a fresh boot and resumed heartbeats.
- **Root cause / fix:** Hardware result supports the missing logger-mutex initialization diagnosis and full-debug correction; no additional application changes were needed.
- **Repeat-update evidence:** Identical image staged its loader and returned successfully but reported zero update bytes (50 reads). Rebuilt identical source as hello-repeat; custom entry then made 417 reads, reported 184320 bytes, returned success, booted with the new timestamp (19:47:06 versus 10:17:33), and emitted 12 heartbeats in 12 seconds.
- **Artifacts:** output/stock_uart_compatibility/hello_logfix_stock_20261006T024407Z/, hello_logfix_capture_20261006T024444Z/, hello_logfix_custom_20261006T024621Z/, and hello_logfix_custom_20261006T024728Z/. UTC directory names correspond to the Pacific bench date above.
- **Remaining limits:** Flash-length, VM/CRC and missing cfg_tool.bin diagnostics persist; storage correctness remains unverified. Radar profile and stock restoration were not tested. Both ports released.
- **Class:** missing-runtime-initialization
- **Recently-touched?** Yes; runtime fix physically verified on this module.


## 2026-10-05 - Boot recovery window and failed-handshake retry verified

- **Observation:** hello-recovery booted with 3.001075 s between PA9 recovery-window and hello-start markers. After a user power cycle, a READY-only probe received six START attempts; the app latched recovery after 4.237 s and remained there for another 8.006 s without starting hello or emitting a heartbeat.
- **Verification:** Without reset, a distinct same-source recovery build installed with 417 reads and 184320 reported update bytes. New timestamp 20:06:25 appeared on PA9; 11 heartbeats followed in the 12-second observation. Both serial ports released.
- **Fix:** No additional firmware changes required. The committed pre-application gate and recovery latch behaved as intended on this hello module.
- **Evidence:** output/firmware_build/recovery_hardware_validation_20261005.json links raw captures, protocol events, image hashes and build provenance.
- **Limits:** This exercises a failed START handshake, not interrupted flash programming or a deliberately crashing application. Radar remains off and untested; SDK startup faults precede this gate.
- **Class:** recovery-entry-validation
- **Recently-touched?** Yes; three-second gate and latch added immediately before this bench test.


## 2026-10-05 - Radar mode-2 initialization and updater reentry pass

- **Observation:** Radar-bringup installed through the custom updater (417 reads, 184320 reported bytes). After recovery expiry, PA9 reports stock-mode2-baseline and 80/80 I2C writes ACKed, SPI configured, bias enabled and DMA unarmed.
- **Verification:** Updater reentry from initialized radar succeeds; identical-image comparison skips application rewrite (50 reads, zero update bytes) and reboots into a second 80/80 initialization. Both serial ports released.
- **Change:** Added stage/write-index/register/value failure diagnostics without printing within the SPI/REXT/final-write transition. Existing fail-fast shutdown and UART recovery retained; no hardware bring-up correction required.
- **Evidence:** output/firmware_build/radar_bringup_hardware_validation_20261005.json contains hashes, build provenance and raw-capture paths. Six native suites and 31 Python tests passed before flashing.
- **Limits:** No logic analyzer available. ACKs are MCU driver reports, not independent bus measurements. No DMA/sample capture or RF validation; storage/configuration warnings persist. Radar remains enabled after successful init; COM13 has no periodic text in this profile.
- **Class:** radar-initialization-validation
- **Recently-touched?** Yes; diagnostic reporting was added for the first radar bench run.


## 2026-10-05 - Bounded DMA capture recovers both receiver streams

- **Observation:** Two 8192-byte DMA buffers completed. Each contains three contiguous 2056-byte DS RAW records with valid checksums/trailers, matching chirps 0-2, 512 I/Q pairs per record, and a truncated fourth. Lane 0 identifies RX0, lane 1 identifies RX1; samples differ. Total validated pairs: 3072.
- **Change:** Separate capture build arms both lanes before REXT, stops radar/DMA before dumping or after a two-second timeout, and preserves boot recovery. Seven native suites and 34 Python tests pass.
- **Recovery finding:** Initial upload stalled inside the previous radar image's loader staging after seven reads, last message erase_sec_addr=0x30000. New capture firmware was not yet installed. Power-cycle entry through the boot recovery gate then installed it. Cause of the staging stall remains unresolved.
- **Evidence:** output/firmware_build/spi_capture_hardware_validation_20261005.json links build, failed/successful upload, raw buffers, decoder results and postcapture READY/START probe. output/spi_capture/first_dual_lane contains IQ CSV and plot.
- **Limits:** Radar left powered off, updater responding, ports released. No continuous-capture or calibrated RF/angle claim; no logic analyzer used. Existing storage warnings remain unresolved.
- **Class:** spi-dma-capture-validation
- **Recently-touched?** Yes; bounded capture application and host decoder added for this test.


## 2026-10-06 - Continuous SPI startup and recovery corruption resolved

- **Observation:** First stream run had 243 DMA overruns and a 25,054 us maximum processing interval. Linear resynchronization reduced maximum processing to 1,378 us, but one startup overrun remained. The retained first bad record contains next-header bytes in its trailer and starts two payload bytes late after mid-record DMA restart.
- **Recently-touched?** Yes: stream_app.c DMA ownership/rearm, acquisition.c scanner, app.c/main.c startup prints and timestamps in the new acquisition loop.
- **Root causes / changes:** acquisition.c shifted a full candidate on every incoming byte; batch filling and one linear resync scan remove that quadratic copy cost. Blocking success prints after DMA arm in app.c/main.c delayed initial servicing; suppress them in stream builds. stream_app.c previously restarted DMA at an arbitrary point after an overrun, losing physical record alignment; now stop and require a fresh radar start. The poll timeout used a time captured before handling newer DMA timestamps, causing unsigned-age false timeouts; sample time again after processing.
- **Verification:** quiet_start received 7,536 valid records per lane and 117 complete paired 64-chirp frames over 10,584,937 local us, with zero bad/sync/unpaired/timeout/sequence/DMA errors, backlog one and maximum record processing 264 us. All export starts skipped because USB is not connected. Stopped and active same-image updater reentry passed and rebooted the application. Twelve CTest suites and 34 Python tests pass.
- **Evidence:** output/stream_bench/{first,linear_parser,record_diagnostic,quiet_start,restart,active_updater_reentry}; exact image/source and checks in firmware/releases/stream-acquisition-20261006 and output/firmware_build/stream_integration_validation_20261006.json.
- **Limits:** No native USB wiring or concurrent encoding/export validation. The reported SDK heap figure exceeds physical RAM and is not accepted as real free RAM. Existing VM/configuration startup warnings remain. Final application restarted without stop command; both serial ports closed.
- **Class:** acquisition-service-deadline / invalid-mid-record-restart / stale-timestamp


## 2026-10-06 - COM30 silence narrowed; raw USB transfer verified

- **Observation:** COM30 enumerated but returned zero bytes, including an explicit DTR low/high trial. Original stopped report found one DMA overrun. With diagnostics flashed, firmware received DTR=1, state=4 and fresh SOFs, and the first 4,314 USB bytes decoded as two records followed by ABORT; opening the reader triggered a 5,391 us acquisition/encode interval and DMA ownership overflow.
- **Root cause:** firmware/src/stream.c used per-bit CRC and bit packing plus repeated residual calculation; build_image.py selected -Oz for the hot path. The measured producer exceeded the approximately 1.2 ms two-lane arrival interval. Runtime clock report and CLK_CON0=0x1c3, CLK_CON2=0xc53, SYS_DIV=0x400 agree on PLL480/2=240 MHz CPU and 48 MHz LSB; no clock waveform measured.
- **Changes:** Byte-table CRC, byte packing, cached 32-value residual block, -O2 for hot sources, CRC code/table in internal RAM. Add USB state snapshots before stop, clock/register reports and stopped kernel timing. Do not bypass integrity checks. Expanded host checks pass 13 CTest suites plus 34 Python tests.
- **Result / remaining fault:** usb_ram_crc_capture received 854,628 bytes in 3.036 s with zero parser/protocol errors, zero DMA overruns and zero corrupt radar records. It explicitly aborted 17 exports at the bounded 48 KiB queue; zero complete real frames. This is progress, not a completed live-radar transfer fix. Main-loop USB draining while record work runs remains the next bottleneck to measure.
- **Raw isolation requested by user:** Raw-only, paced synthetic USB bench received 7,294,976 bytes in 10.005 s (~729 kB/s), 27 complete frames; all 7,105,536 reconstructed bytes match the known pattern. Parser errors are confined to a 64-byte DTR-transition prefix and a 1,557-byte cut-off tail. No interior corruption in the normal read run. Three-second read pause yielded one interior damaged region near input offset 16,768 and ten subsequent exact frames; reopen yielded eleven exact frames. The source of pause-time loss is not proven; this establishes recovery, not lossless stalls.
- **Final state:** Raw USB bench SHA256 4c7ef325f5ea3427ca6942030c990507f40bc470eaeffb48ffc16f625d294361 restarted through UART, radar off, COM30 ready for a reader, serial handles closed. Same-image update used 50 reads and zero rewrite bytes. Physical unplug/replug not exercised.
- **Evidence:** output/stream_bench/usb_*; firmware/releases/usb-raw-baseline-20261006; output/firmware_build/usb_debug_validation_20261006.json. Prior baseline release untouched.
- **Class:** producer-service-budget / synchronous-USB-drain-budget
- **Recently-touched?** Yes; original continuous streaming implementation.


## 2026-10-06 - Concurrent compression and USB export works at reduced cadence

- **Recently-touched?** Yes: usb_stream.c staging/interrupt scheduling, build_image.py hot-path flags, stream.c CRC/queue/validation, stream_app.c service budget.
- **Observation:** Main-loop CDC achieved ~729 kB/s with paced raw data, but live compressed frames overflowed a 48 KiB output queue. Interrupt-driven USB alone achieved ~743 kB/s but reintroduced DMA overflow while encoding. A four-byte CRC reduced the stopped raw-record CRC from ~131 to ~95 us; speed-optimizing the dispatcher alone and RAM placement of the codec did not resolve the deadline (RAM codec placement reverted).
- **Measured cause / fix:** radar_record_decode cost ~76 us per record and ran twice on unchanged acquisition bytes. The validated-record path removes the redundant pass, retaining acquisition validation and all transport CRCs. This removed DMA overflow in the five-second trial; queue pressure then became isolated. An 80 KiB queue delivered 42 full frames in ten seconds. An 88 KiB trial with larger encoded records again exceeded the CPU budget, so stream_app.c now rejects export at two pending slots before the four-slot DMA ring overflows. This guard did not activate in the final successful run; deliberately exercising its activation remains open.
- **Final 30-second live result:** 20,402,188 wire bytes / 30.003224 s; host accepts 159 complete paired frames, zero protocol errors, only a 326-byte EOF tail. Device enqueued 160, zero DMA/corrupt/sequence/timeout/queue-overflow/CPU-rejection counters, backlog one, queue peak 80,924/90,112, max feed interval 866 us (includes IRQ preemption and paired first records). Deliberate whole-frame skips remain; no full-rate export claim.
- **Backpressure/reopen:** Three seconds without reading, then five seconds reading: 27 complete frames, one explicit reason-3 ABORT, 144-byte EOF tail and no interior parser resync. Reopen: 28 complete frames after a 64-byte in-flight prefix, EOF tail 1,816 bytes. Zero DMA/corrupt/sequence/timeout errors across both; one queue overflow handled explicitly. No physical unplug test.
- **Raw control:** 7,901,184 bytes / 10.004328 s (~790 kB/s), 29 complete frames, all 7,631,872 reconstructed bytes exact. Only a 611-byte EOF tail. Compared with prior ~729 kB/s, about 8.3% improvement. Remaining endpoint/host scheduling ceiling is not established; no PC FIFO change was made.
- **Checks/state:** 13 CTest suites plus 34 Python tests pass, including bitwise-reference CRC alignment/tails, 88 KiB queue boundaries, trusted metadata rejection and interrupt-ring ownership/wrap/reset/backpressure tests. Final live image 25e98a57868261ed3abfe1e7f218eca90a0574452d379be93904c81cce547bd8 restored via UART; a fresh five-second read validated 27 complete frames. Application remains running, all serial handles closed. Prior releases retained.
- **Evidence:** output/stream_bench/usb_budget_guard*, usb_optimized_raw_final*, usb_optimized_final*; firmware/releases/usb-optimized-20261006; output/firmware_build/usb_optimized_validation_20261006.json. Memory reservations are link-time, runtime heap/stack still unqualified. Existing VM/configuration warnings unchanged.
- **Class:** redundant-validation / concurrent-USB-service / bounded-export-backlog


## 2026-10-06 - Motion triggers real export aborts; viewer exposes their causes

- **Observation:** Slight scene motion repeatedly increased rejected frames and could starve the live display; stillness restored completed frames.
- **Measured cause:** Preserved 50,612,581-byte demonstration: 305 completed, 125 rejected candidates. Valid ABORT messages identify 71 CPU-backlog guards (stream_app.c:91-93) and 53 queue overflows (stream.c:294-295). One additional candidate was invalidated during 869 interior resynchronization bytes; its cause remains unproven. Protocol errors zero. Recording SHA-256 matches its manifest.
- **Viewer defects fixed:** frame_stream.py discarded valid ABORT reason codes; server.py updated device counters only on successful frames and zeroed wire rate whenever complete frames became stale. Preserve/classify reason codes, update telemetry from validated BEGIN messages, retain active byte rate, and display export-limited status plus separate buffer/CPU/invalid counters. All full-frame integrity checks remain unchanged.
- **Qualification:** This fixes observability, not motion-dependent firmware overload. Neighbor-sample / gradient size screening saves about 16% / 17% on received records of aborted prefixes, but worsens the successful-frame group; target CPU cost and an adaptive codec remain untested. Firmware not changed or flashed.
- **Checks:** 15 viewer tests and 12 C-producer/Python-decoder interoperability tests pass. Live updated viewer independently reports both abort causes with zero protocol errors. Evidence: output/live_radar/20261006-173642-capture-3fc19b/.
- **Class:** scene-dependent-export-budget / misleading-error-telemetry
- **Recently-touched?** Yes; codec budget guard and viewer were introduced in this session.


## 2026-10-06 - Raw16 export survives the demonstrated motion

- **Observation:** Previous compressed 64-chirp exports repeatedly aborted during movement; only settled scenes displayed reliably.
- **Root cause:** firmware/target/br23/image/stream_app.c:88-93 protects DMA service by aborting at CPU backlog; firmware/src/stream.c queue capacity limits compressed output. Recorded ABORT reasons established both limits.
- **Fix:** User selected first16 raw chirps per receiver (firmware/src/acquisition.c:44-47; firmware/src/stream.c:265,287,300), with declared-window decoding and dynamic viewer dimensions. Retain all samples and integrity checks within that window.
- **Validation:** 1,881 complete windows over 214.55 s (8.76/s); user confirmed plots continued during movement. No recorded ABORT/protocol errors, no device-rejection increase during the recording. Stopped diagnostics: 174,592 valid records/lane, zero corrupt/sequence/DMA/CPU/queue errors, backlog1, queue peak54,512/90,112. Two boot-cumulative export rejections straddle connection boundaries; exact causes unobserved. No claim of exhaustive motion/stall qualification.
- **Build/tests:** Target audits passed; 15 CTest suites, 34 Python firmware tests, 16 viewer tests. Same-image UART restart passed; viewer left live on COM30.
- **Class:** scene-dependent-export-budget
- **Recently-touched?** Yes; prior codec/queue scheduling plus this bounded-window change.
- **Evidence:** output/firmware_build/raw16_validation_20261006.json; firmware/releases/usb-raw16-20261006/. Contract in DECISIONS.md.


## 2026-10-06 - Scene-independent mirrored spectral features (unresolved)

- **Observation:** User marks peaks near +/-74, +/-173, +/-220 and zero; frequencies remain fixed when radar is redirected. Treat ordinary stationary scene reflections as a poor explanation for these features.
- **Evidence:** Live raw-IQ snapshot frame6508 (raw16 configuration cdc8522d...) independently reproduces the off-center features with no background subtraction. At +/-173 and +/-219, positive/negative amplitudes nearly match; I/Q tone phases are near opposition in both receivers. This supports a periodic disturbance in the sampled signal but does not establish clock, power, ADC, layout or sweep cause.
- **Code audit:** tools/radar_viewer/processing.py:118 FFTs the whole512-sample record; firmware/src/stream.c:219 raw mode copies all2048 sample bytes unchanged. Stream build identity differs from the radar-off synthetic benchmark. Integrity checks do not prove sweep interpretation.
- **Next investigation:** Verify sample ordering and applied radar sweep/ADC configuration before interpreting these features as range; preserve originals and avoid notch filtering away the diagnostic evidence.
- **Class:** signal-interpretation-unresolved
- **Evidence files:** output/radar_analysis/scene_independent_spurs_20261006/{snapshot,analysis}.json.


## 2026-10-06 - DS RAW sampling and sweep experiments separate outer spurs

- **Observation:** User reports mirrored peaks remain fixed even when radar is moved/re-aimed.
- **Investigation:** Manufacturer Rev1.6 sections6.3/8.2.1 define DS RAW as downsampled signed16 I/Q before range FFT; existing decoder matches. Original stock captures also contain mirrored high-frequency features. Current raw copy and FFT paths do not fabricate those tones.
- **Bench:** Change only reg02 103C->003C: major outer pair219->110 bins. Restore reg02 and narrow sweep steps17/-17->8/-8: outer pair remains219/220 while central structure contracts. Restore original image: central4/5 and9-bin features return. Four wire captures yielded89/76/76/61 complete windows, no explicit aborts or protocol errors.
- **Finding:** Outer features do not follow sweep slope and should not be interpreted as target ranges. Approximately535kHz (assuming datasheet2.5MHz ADC and confirmed relative2:1 sampling) is consistent with internal converter400-650kHz; physical source remains unproven. Sweep-sensitive detail is concentrated near center and poorly visible at512-bin width.
- **Change:** Add center/positive/full spectrum and history span controls; crop display only, preserve original FFT and samples. Baseline raw16 image541c110a... restored and viewer live. User motion check of zoom remains pending.
- **Class:** spectral-spurs / display-scale-obscures-signal
- **Evidence:** output/radar_analysis/spur_four_way_comparison/experiment.json and comparison plots; diagnostic profiles retained separately.


## 2026-10-06 - Live register control: device stops, bus errors, lost commands

- **Observation:** First 8-register read correct. A 128-register dump stopped the USB stream (16 back-to-back commands). After a buffer fix, reads returned intermittent bus errors and implausible values; one dump again stopped the stream. Separately, a fraction of commands never got replies.
- **Causes found:**
  - SDK `usb_g_bulk_read` (cpu.a usb_phy.c; ROM listing usb_phy.c:337-380) keeps reading while packets are ready and copies whole packets without bounding them by the remaining length. Bursts of short packets overran the 64-byte receive buffer (usb_stream.c). Fix: 256-byte buffer and the host keeps one command in flight.
  - `timer_get_ms()` has 10 ms resolution (IMAGE_BUILD.md). The control path used a 5 ms, then 2 ms, I2C timeout, which can expire mid-transaction and reset the bus mid-byte: bus errors and stale values. Fix: 20 ms, as for startup writes (stream_app.c CONTROL_I2C_TIMEOUT_MS).
  - Padding commands to 64-byte packets made losses worse (about 75%); reverted.
- **Lost commands (resolved):** About a third of command packets, in runs, got no reply. The SDK `usb_g_bulk_read` (inlined at app_main+0x52a..+0x790 in the linked image) re-reads RXCSR and writes it back with RXCSRP_FlushFIFO (usb_phy.h:120) whenever it finds no packet ready, and after any short packet. The main loop polled it constantly, so a command arriving in that window was flushed. Fix (usb_stream.c ld2450_usb_read): call it only when RxPktRdy is set, with len equal to RXCOUNT, so it copies one packet and returns without reaching the flush path.
- **Stream stopped on table reads (resolved):** Reading 4 registers of 0x20-0x2F in one gap repeatedly overran DMA (radar powered down; later reads reported NOT_READY); single reads and other blocks were fine. Those registers evidently read much slower. Fix (radar_control.c): one bus transaction per execute step, and stream_app re-checks the inter-frame window before each step, so a command spans as many gaps as it needs.
- **Validation:** Image stream-raw16-control5: 12 repeated 4-register reads of 0x20 and 0x2C, then three full 0x00-0x7F dumps, all 96 commands first-attempt, identical values, stream uninterrupted. LDC1 REINIT also verified: it restored a powered-down radar without a power cycle. The host still sends a priming byte, keeps one command in flight and retries (harmless).
- **Bench mistake:** A diagnostic opened COM13 with pyserial defaults (DTR/RTS asserted) and rebooted the module. Project tools deassert both before opening; do the same.
- **Evidence:** output/live_radar/register_dump_20261006.json. Final image SHA-256 in that file.
- **Class:** sdk-api-contract / timer-resolution / transport-loss-unresolved
- **Recently-touched?** Yes; all in the register-control change of the same session.
