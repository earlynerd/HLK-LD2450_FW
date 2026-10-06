# BR23 bring-up audit — 2026-10-04

This is a source and linked-code audit following the silent first custom boot.
The baseline findings below are historical. The subsequent hello-world/updater
revision implements early debug, MCU board-power setup and visible failure
handling in both image profiles; see [current behavior](IMAGE_BUILD.md#minimal-hello-world-with-updater).
Its console reserves UART0 on PA9, so the update UART now normally uses UART1.
It does not establish the cause of that hardware failure. The programmed
baseline remains preserved in `build/image`; the latest revised candidate is
separate in `build/hello-audited` and has not been flashed.

## Clocks: corrected mismatch and dependent limit

The captured stock V2.14 debug log in
`output/stock_uart_compatibility/fifth_custom_flash_full_debug/debug-com11-1mbaud.bin`
reports `sys clk_get=240000000` and `spi clk_get=60000000`. The original custom
image requested 24 MHz CPU. `app_config.h` now requests 240 MHz.

The oscillator reference is a separate setting: it remains 24 MHz. Both linked
stock and custom oscillator initialization use the same principal control
constants and capacitor settings; the system-clock observation does not imply
a 240 MHz crystal. The SDK PLL tables also support 24 MHz CPU operation, so the
original CPU setting alone is not proof of a boot failure.

The SDK clock-limit table permits 60 MHz LSB at 240 MHz CPU. Its IIC register
definition (`include_lib/driver/cpu/br23/asm/br23.h`, `JL_IIC_TypeDef`) makes BAUD
eight bits. At 100 kHz, `LSB / (2 * baud) - 1` would be 299, exceeding 255.
Our peripheral initialization correctly rejects that before opening UARTs;
blindly copying the SDK IIC assignment would instead truncate it.

Project `target/br23/image/bringup.c` calls
`clock_reset_lsb_max_freq(48000000)` before the vendor `setup_arch`. The build
renames the vendor entry point only for its translation unit. Inspection of
the revised executable confirms the 48 MHz limit is written to the 240 MHz
clock-table row before `clk_early_init` selects dividers. CPU remains 240 MHz;
the expected LSB is 48 MHz and IIC BAUD is 239. Host tests cover 48 MHz, the
51.2 MHz representability boundary, and rejection at 60 MHz. Actual clock
frequencies still require a running target.

## Pin mux audit

This table describes the originally flashed image. The current hello-world
console uses UART0/channel 0 on PA9; the module uses UART1/channel 1 on PA1/PA0.

| Interface | Project routing | SDK / linked-code finding |
| --- | --- | --- |
| Module TX | PA1 | No BR23 fixed TX match; `uart_dev_open` selects a free UART, normally UART0, and calls `gpio_output_channle(PA1, CH0_UT0_TX)`. |
| Module RX | PA0 | Same UART uses `gpio_uart_rx_input(PA0, 0, 0)` when UART0 is free. Linked helper sets input selection, direction and digital input enable. |
| Debug TX | PA9 | Matches BR23 UART2 group 1. Linked `gpio_set_uart2(1)` selects that group and configures PA9 output/digital enable. It also configures unused PA10 RX, despite the TX-only application request. |
| Radar I2C | PC4 SCL / PC5 SDA | Matches hardware IIC group B, `IOMAP.CON1[19:18]=1`. Digital inputs enabled; external pulls are on switched radar power. |
| SPI1 receive | PB2 DI / PB0 CLK | Matches SPI1 group A, selected by clearing `IOMAP.CON1[4]`. PB1 remains input because it is module reset, not an available SPI output. |
| SPI2 receive | PB8 DI / PB9 CLK | Matches SPI2 group A, selected by clearing `IOMAP.CON1[16]`. PB10 remains input. |

No routing mismatch was found in these paths. This does not prove the pins
were configured on the silent target. The SDK GPIO header's UART comments
explicitly describe BR22 and differ from the BR23 `uart_dev.c` tables; the
linked helpers agree with the latter. The output-remap helper deliberately
programs pull-up, pull-down, direction and digital-enable bits as part of its
channel selection. Do not overwrite those bits afterward with generic UART
GPIO cleanup. The current code does not do so.

## Missing example bring-up stages

1. **Early debug UART.** SDK `cpu/br23/setup.c` calls `debug_uart_init` after
   clocks/tick initialization only with `CONFIG_DEBUG_ENABLE` or
   `CONFIG_DEBUG_LITE_ENABLE`. Neither is enabled in our image. Its early
   print path has no physical UART output; project PA9 output starts only
   after all peripheral initialization. This is a confirmed diagnostic gap.
   Enabling it requires an explicit UART ownership plan: the example's debug
   driver and our dynamically allocated module UART must not claim UART0
   simultaneously or route SDK log output onto the binary update interface.
2. **Board power initialization.** The example's
   `apps/soundbox/common/init.c:app_init` calls `board_init`, and the demo board
   calls `board_power_init` / `power_init`, ADC/reference setup, config parsing,
   device setup and `power_set_mode`. Our image links the library's minimal
   `main` / `app_task_init`, which runs registered initcalls and `app_main` but
   does not call that board initializer. The early SDK oscillator/core-voltage
   initialization *is* present. Missing board power setup is a lead, not proof
   of a fault: speaker, battery, wake and low-power settings cannot be copied
   wholesale to this board.
3. **Visible early failure handling.** `src/app.c` returns immediately on
   peripheral failure, and image `main.c` resets before printing its banner.
   Thus the original image can reset silently before either normal boot line.
   Any diagnostic revision should print a stage and error before radar init
   and preserve a working update UART independently where possible.

These stages were not changed in the initial clock-only revision. They are
implemented in the subsequent hello-world/updater revision described above;
hardware validation is still pending.

## Second audit: exact startup, AC63 example and power preconditions

The stock boot log identifies
`apps/spp_and_le/board/br23/board_ac635n_demo.c` in an AC63 SDK tree.
The [official AC63 example](https://github.com/Jieli-Tech/fw-AC63_BT_SDK/blob/fdc018de81629e21e594d677cf05f87d288be0f0/apps/spp_and_le/board/br23/board_ac635n_demo.c)
was fetched at commit `fdc018de81629e21e594d677cf05f87d288be0f0` for comparison;
the exact files and hashes are under `output/firmware_build/ac63_reference`.
This is a current comparison source, not a claim to have recovered the exact
SDK revision used to build stock V2.14. Our pinned soundbox SDK remains unchanged.
Jieli's [bootloader family table](https://github.com/Jieli-Tech/fw-Bootloader)
places AC635N, AC695X and AC695N in BR23; their product names alone do not
establish a CPU/ROM-family mismatch.

Two changes address differences in our unflashed board initializer:

- **Unsupported inherited weak voltage.** The previous hello executable tests
  the inherited VDDIOW value at `0x1e04c56` and takes an assertion/reset path
  when it is zero (`cpu_assert_debug` at `0x1e04c7a`). Blindly preserving that
  value is unsafe for this SDK contract, even with sleep disabled. `board.c`
  now maps only zero to `VDDIOW_VOL_24V`, logging the adjustment. Other supported
  inherited values remain. Disassembly of the audited image shows the guard
  at `0x1e049f2`, assigning level 1 before entering `power_init`.
- **Initialization order.** The SDK example initializes filesystem/event
  callbacks and platform configuration before `board_init`. Our early callback
  ran ahead of these. The project power initializer now uses `__initcall`,
  which the linked library invokes after the platform callbacks and before
  module/late callbacks. This restores example ordering; no specific crash
  caused by the former order has been demonstrated. LRC selection and the
  absence of an external DCDC pin are now explicit too.

These changes cannot explain the original silent image: that image did not
call our board power initializer. They prevent carrying new hazards into the
next attempt.

| Area checked | Evidence / result |
| --- | --- |
| Boot entry | Stock and custom enter at `0x1e00120`, call `boot_info_init`, establish SP/SSP, clear BSS, copy initialized RAM, clear the same ICFG bits, process update result, then jump to `main`. |
| Boot parameters | Stock/custom `boot_info_init` copy the same fields. Custom boot-info storage lies between stack and BSS, outside both initialization writes. |
| Flat application | Text then initialized data matches SDK `download.bat`; startup source/destination/length agree with the linked sections. Unused four-byte overlay placeholders remain, with no runtime audio-overlay use. |
| Reserved RAM | Stack, boot info, BSS, heap, fixed interrupt table, TLB and update handoff area do not overlap. The builder now checks these and 13 startup immediate operands before packaging. |
| Clock setup | Oscillator LDO/capacitor setup and adaptive core-voltage sequence agree with the BR23 examples. Stock runs 240 MHz; original 24 MHz CPU was supported by the SDK and is not proven to be the failure. PLL reference remains 24 MHz; current LSB cap is 48 MHz. |
| UART routing | Debug owns UART0/output channel 0; module remap owns UART1/output channel 1 and input channel 1. Linked GPIO helpers address different mux fields. PA9 is not repurposed later in this application. |
| Runtime | SDK memory/tick/exception/system-timer setup and initcall dispatch are linked. Required `app_core`, `sys_event`, `systimer` and update task descriptions are present. |
| Flash-size setting | 256 KiB controls the linker budget; stock reports 1024 KiB physical capacity. Packaging independently preserves directory geometry and enforces the stock application slot. |
| SDK chip checks | Both stock and custom contain chip/key validation. They remain enabled; their presence alone is not evidence of incompatibility. |

Five native suites and 26 Python tests pass, including deliberately corrupted
startup addresses, overlap, callback phase and packed-data cases. Both hello
and radar profiles target-link and pass the post-link checks. The hello UFW
has the bench-established two-wire loader patch. Detailed artifact provenance
is in `output/firmware_build/boot_audit_validation.json`.

The first physical marker still follows vendor memory, oscillator/PLL and tick
setup. A failure in those stages, a ROM/library incompatibility, or an image
not actually executing could remain silent. No cause of the first device's
failure has been established, and this revision has not been flashed.

## USB recovery lead relevant to the Pico

The [jl-uboot-tool author's entry notes](https://github.com/kagaimiq/jl-uboot-tool/blob/main/docs/how-to-enter-uboot.md)
describe two stages: send the `0x16EF` key and detect acknowledgement, then
hand the target to a real USB host so it can receive SOF packets for oscillator
calibration. Seeing a key acknowledgement alone does not establish successful
enumeration. The notes flag BR23 retry-count details as unverified. This is a
useful capture distinction, not a tested recovery procedure for our board.
The public [Pico prototype](https://github.com/ElectronicCats/jieli-ble-badge-research/tree/main/tools/pi-pico-jl-dongle)
targets BR35 and explicitly describes incomplete hardware validation; it is
not evidence of a working BR23 recovery dongle.

## 2026-10-05 PA9 crash: full logger without mutex initialization

The second module executes the hello-heartbeat image (UFW SHA256
`1b215c1abf083cb50897cc8a53241ea85dbc8d2d5bc7bef58496e78def57cbee`).
Its cold-start capture confirms early custom output and sys=240 MHz / LSB=48 MHz,
then `cpu_write_data_over_limit` before the board-power and app_main markers.
Capture: `output/stock_uart_compatibility/pa9_hello_boot_20261005T170332Z/`.

**High-confidence cause of the captured exception:** our lightweight-debug
configuration still links the vendor full logger but never initializes its mutex.
`target/br23/image/app_config.h:6` defines `CONFIG_DEBUG_LITE_ENABLE`, whereas
`cpu/br23/setup.c:217-218` calls `log_early_init(1024)` only under
`CONFIG_DEBUG_ENABLE`. The project source list in `tools/build_image.py:77-87`
omits the example's `apps/common/debug/debug.c`; that file normally replaces
`printf` and `log_print` with no-ops when full debug is disabled. We therefore
retain the full archived logger without its required initialization.

Evidence from the exact flashed ELF and vendor object:

- `log_mutex` is at 0x4b44, size 80. The exception has r0=0x4b68, its receiving
  event list at offset 36. `mutex_rets_addr=0x1e00e44` is the return from
  `log_output_lock` in `log_print`.
- `log_output_lock` passes 0x4b44 to `os_mutex_pend`; that calls
  `xQueueGenericReceive`, then `vTaskPlaceOnEventList`, then `vListInsert`.
- The captured r3=0 agrees with an invalid list link. `vListInsert` at 0x1a36
  writes `[r3+8] = r1`, consistent with a low-address write-protection exception.
  The pipeline-reported RETI is 0x2088, the caller's return address; the trace
  includes 0x1a34 immediately before that store.
- Extracted `system.a:log.c.o` LLVM IR declares `log_mutex` zero-initialized.
  `log_early_init` creates it with `os_mutex_create`, then allocates the log buffer.
  There is no other mutex constructor reference in this object. The initializer
  is absent from both the original failed ELF and the hello-heartbeat ELF.
- Before scheduling, `os_mutex_pend` can bypass the wait path when interrupts
  are disabled, explaining why early output can precede the task-context fault.
- Preprocessing the exact setup compile command confirms the flashed configuration
  omits the initialization; adding `CONFIG_DEBUG_ENABLE` restores the call.

Proposed correction: select full `CONFIG_DEBUG_ENABLE` instead of the lite
configuration, matching the SDK example, so its setup initializes the logger
before task startup. Full-debug assertions also halt for diagnosis rather than
immediately resetting; this is an intentional behavior to review with the fix.
Do not disable memory protection or alter RTOS lists to mask the fault.
This investigation did not change firmware sources or flash another image.
The first module has the same omission, but without its crash capture the same
physical failure mechanism is not proven there.

Extracted object/IR, preprocessed comparison, compact disassembly and machine-readable
findings are under `output/firmware_build/pa9_crash_analysis/`. A corrected build
and device boot are still required to validate the remedy and expose any later
startup problems.

## 2026-10-05 fix and focused SDK dependency review

`app_config.h` now selects full `CONFIG_DEBUG_ENABLE`. The unchanged SDK setup
therefore calls `log_early_init(1024)` before clock-dump logging and task startup.
The hello candidate is `build/hello-logfix/update-two-wire.ufw`. Both hello and
radar profiles build with this correction; no new image was flashed.

Why the earlier review missed it: it verified individual stages and image layout
without following the complete dependency from debug-mode selection, through
omitted example source files, into the full archived logger and its constructor.
The host tests exercised project peripherals/protocols, not the vendor logger
in task context. Successful linking was insufficient evidence that initialization
was complete. The earlier confidence about readiness exceeded those checks.

The new build guard inspects final disassembly rather than merely testing a
configuration macro or retained symbol. It verifies `setup_arch -> log_early_init`,
the mutex constructor and log-buffer allocation, and `os_init -> setup_arch ->
application task creation -> os_start` order. It rejects the exact flashed
hello-heartbeat ELF. Negative tests cover an initializer retained but never
called, missing mutex construction, and misplaced initialization. This guard
checks selected direct calls in pinned code generation, not all control-flow paths.

The additional review was limited to dependencies of retained services:

| Service | Required setup found in current source / executable | Assessment |
| --- | --- | --- |
| Full logger | `log_early_init` constructs mutex and allocates 1024-byte log buffer during setup | Missing dependency corrected; full-debug assertion halt behavior retained intentionally |
| RTOS and memory | Library main calls OS init before setup; setup performs memory/MMU setup before logger allocation; app task creation and scheduler start follow setup | No further omission identified |
| System timers | `sys_timer_init` constructs semaphore and timer lists, creates `systimer`, then configures timer; invoked in setup | No further omission identified |
| System events | Early `sys_event_init` callback creates buffers and task; event task creates its semaphore before waiting | No further omission identified |
| Flash filesystem | Early `sdfile_init` callback and retained `sdfile_vfs_ops`; flash open, partition lookup and mount path remain linked | Initialization present; actual mount/update behavior still needs target execution |
| Configuration storage | Platform `syscfg_tools_init` iterates three retained 28-byte operation records: BTIF, VM and file initialization | Indirect constructors verified from ELF table contents |
| Board power | Project initializer runs after early/platform callbacks, before late chip checks and app_main | Already guarded by startup audit; actual voltage/clock behavior still needs bench evidence |
| UART | `uart_dev_open` invokes selected UART open routine; SDK constructs RX/TX semaphores and registers ISR before enabling transfer | No omitted semaphore/IRQ initialization identified |
| CRC service | SDK setup constructs the CRC mutex before returning | No further omission identified |
| Update engine | App calls `update_module_init(state_changed)` before polling; SDK example registers the equivalent call through `app_update_init`; update task entry retained | Project deliberately replaces example callback; testbox, Bluetooth and soundbox hooks are outside this application's scope |
| Example board-early hook | Soundbox common init has an empty weak default; reviewed BR23/AC635N board has no override | No extra early-stage work identified for this board |

No second confirmed missing initializer was found within that scope. This does
not certify every linked library path, validate runtime allocation success, or
remove the need for a boot test. No RTOS-list, memory-protection, UART-pin or
radar-setting change was made to address this exception.

Evidence: `output/firmware_build/logfix_validation.json`,
`output/firmware_build/logfix_tests.txt`, and
`output/firmware_build/pa9_crash_analysis/logfix-service-calls.json`.
Five native suites and 31 Python tests pass. Both profile ELFs pass the layout
and runtime audits, and hello has the previously bench-established two-wire
loader patch. Next physical test must establish hello boot and repeat UART update.
