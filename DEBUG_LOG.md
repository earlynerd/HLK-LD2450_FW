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
