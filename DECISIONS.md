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
