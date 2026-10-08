# BR23 images with UART recovery

This pipeline produces a complete `.ufw` containing a project-owned BR23
application. It uses the pinned vendor startup, RTOS, hardware libraries and
update engine. The application UART receiver is our code; the second-stage
flash-writing loader is the vendor `ota.bin/uart_user.bin` with the two
[bench-established UART fixes](UART_LOADER_BENCH.md) applied as a separate packaging step. We are not
replacing the ROM bootloader or claiming a new implementation of the flash
writer.

## Build on Windows

From the repository root, with Python 3.11+:

```powershell
python firmware/tools/setup_sdk.py --download
python firmware/tools/setup_toolchain.py --download
python firmware/tools/build_image.py
```

The setup commands verify pinned SHA-256 hashes before extracting. Compiler
setup extracts the `pi32` directory from the official 2.5.2 installer using
the pinned innoextract archive. It does not execute the installer or change
PATH. Existing SDK contents are verified rather than replaced. Offline inputs
can be supplied with `setup_sdk.py --archive PATH`, and
`setup_toolchain.py --installer PATH --extractor-archive PATH`.

The builder accepts `--sdk`, `--toolchain`, `--template` and `--out` overrides.
Its current complete-image route uses the Windows compiler executables.
For the example register experiment:

```powershell
python firmware/tools/build_image.py --radar-config firmware/config/radar_no_idle_powerdown.json --out firmware/build/no-idle-powerdown
```

The selected table is retained in the linked binary, checked before packaging,
and applied automatically at boot. The default mode-2 table matches all 80
writes in [the captured I2C sequence](../../output/i2c_init_comparison/report.txt).

Outputs in `firmware/build/image`:

- `sdk.elf`, `sdk.map`, `sdk.ld`: target code, memory map and preprocessed layout.
- `app.bin`: application bytes in the SDK section order.
- `update.ufw`: complete stock-template container with the new application.
- `update.manifest.json`, `build-result.json`, `commands.json`: hashes,
  input provenance, package verification and exact compile/link commands.
- `generated/`: selected register data and provenance.

The build runs only compiler/linker and Python packaging operations. It does
not run SDK `make`, `download.bat`, `isd_download`, or access UART/USB devices.
Check for a successful command exit and current build-result manifest before
using an output; a failed rebuild can leave files from an earlier build.

## Minimal hello-world with updater

```powershell
python firmware/tools/build_image.py --application hello
python firmware/tools/patch_stock_uart_loader.py --input firmware/build/hello/update.ufw --out firmware/build/hello/update-two-wire.ufw
```

This creates a separate diagnostic image without compiling the radar application,
register table or sample decoder. It retains the SDK runtime, flash/filesystem
services and update engine needed for subsequent UART updates. `--application
radar` (the default) builds the radar application; use a separate `--out` when
preserving an earlier artifact.

Both images now enable the SDK early console on **PA9, 115200 8N1**. UART0 is
explicitly reserved for it before the SDK debug allocator runs; module PA1 TX /
PA0 RX uses the next free UART, normally UART1. SDK logs and hello messages never
go onto the update port, except for the hello profile's explicit idle heartbeat
described below. The debug console remains available through peripheral
cleanup and initialization failures. Image builds use this fixed debug baud;
the standalone component's dynamic debug-UART path remains separate.

The shared board initializer runs after SDK early/platform callbacks, calls
`power_init` and selects LDO15 with sleep disabled. It preserves supported
inherited VDDIO selections; weak level zero (2.1 V) becomes 2.4 V because the
linked SDK asserts on zero. The SDK may raise the strong level to its required
minimum relative to the weak level. External DCDC control is explicitly absent.
It holds PC2 high
and PC3 low to keep radar supply and bias off. It does not initialize soundbox
ADC, audio, keys, charger, Bluetooth or radar communication peripherals.

Expected diagnostic sequence on COM11 (interspersed with SDK logs):

```text
BOOT: clocks ready; PA9 console ready
BOOT: sys=240000000 lsb=48000000 uart=48000000 UART0_BAUD=103
BOOT: MCU power init
BOOT: MCU power ready; radar held off
BOOT: app_main reached
Hello world! Starting UART updater
UPDATE: ready on PA1/PA0 at 256000 baud
Hello world!
```

The corrected hello image's PA9 capture reports sys=240000000, lsb=48000000,
uart=48000000 and UART0_BAUD=0. These are SDK getters/register readings, not
independent clock measurements.
The final hello repeats approximately every second while idle. An active update
transaction temporarily occupies the same task. COM13 stays at **256000 8N1**
for custom updater entry. The hello profile prints
`HLK-LD2450_FW: hello; UART updater ready` on that port after the boot recovery
window and approximately once per second while idle. The heartbeat runs
in the same task as the blocking updater, so no heartbeat is emitted during its
handshake, transfer or loader handoff. The host parser ignores any idle text
already buffered before START. Early startup diagnostics still require PA9;
the COM13 heartbeat begins only after application/UART initialization succeeds.
The radar profile does not emit this heartbeat. Hello-world calls
`ld2450_uart_init`, which never initializes I2C or SPI and rejects radar-enable
requests. Update cleanup also leaves those uninitialized peripherals alone.
Initialization failure prints its numeric error repeatedly instead of resetting
before the first message. The first boot marker follows SDK memory/clock/tick
setup, so failures earlier than that can still be silent.

The corrected hello-world image was flashed from stock V2.14 on 2026-10-05,
reached app_main and the UART updater, and emitted 15 COM13 heartbeats in the
15-second postflash observation. It also booted after a user-confirmed power
cycle. Radar bring-up subsequently passed the initialization check below. The first failed-boot
artifact remains in `build/image`.

The first successful hello candidate was **`build/hello-logfix/update-two-wire.ufw`**, which
retains the module-UART heartbeat and enables full SDK logging initialization.
It passes the startup and runtime dependency audits and has booted on hardware.
Its final SHA256 is
`1ee98f1c057629b5ffefbd5e9605f73255826cea6ac182fae82b7b91ee59a51a`.
Validation is recorded in `output/firmware_build/logfix_validation.json`.
Initial successful boot evidence is in
`output/stock_uart_compatibility/hello_logfix_stock_20261006T024407Z/`;
power-cycle evidence is in `hello_logfix_capture_20261006T024444Z/` beside it.
Evidence directory timestamps are UTC; the bench date above is Pacific time.
The boot still reports flash-length, VM and missing cfg_tool.bin warnings;
successful hello execution does not establish configuration/storage correctness.
Custom updater entry with the identical image completed but reported zero bytes
to update (50 reads), so that trial alone did not prove application replacement.
Rebuilding the same source as **`build/hello-repeat/update-two-wire.ufw`** changed
the embedded setup timestamp from `10:17:33` to `19:47:06` on Oct 5 2026.
That image was installed through the custom updater at 256000 baud: 417 reads,
184320 reported update bytes, final success, the new timestamp on PA9 and
12 COM13 heartbeats in the following 12 seconds. It was installed at that stage;
SHA256 `05fafed95ed20aba1400bbeae2884a054d9716edae345850e02ceff23c4b1edb`.
Evidence: `output/stock_uart_compatibility/hello_logfix_custom_20261006T024728Z/`.
Stock restoration was verified on 2026-10-08; see [Restoring stock firmware](UART_UPDATE.md#restoring-stock-firmware). Radar initialization results are recorded below.
Full debug mode also makes SDK assertions flush diagnostics and halt instead
of immediately resetting.

The preceding module-UART heartbeat candidate was
`build/hello-heartbeat/update-two-wire.ufw`. Its `build-result.json` records the
successful target build and startup audit; `update-two-wire.manifest.json`
records the loader patch and final hash. On 2026-10-05 it was flashed to a second
module: the loader reported success after 419 reads, but COM13 produced no
heartbeat in 12 seconds and no reply to a four-second READY-only probe.
A subsequent cold-start PA9 capture confirmed custom execution followed by a
logging-mutex exception; see the bring-up audit for its source/binary diagnosis.
See `output/stock_uart_compatibility/hello_heartbeat_flash_20261005T165015Z`.
The preceding audited candidate is `build/hello-audited/update-two-wire.ufw`;
its hashes and build/test evidence are in
[`boot_audit_validation.json`](../../output/firmware_build/boot_audit_validation.json).
`audit_image.py` now runs before packaging: it checks startup immediate operands
against ELF symbols, flat text/data packing, RAM/stack/boot-info separation,
interrupt/update reservations and the board callback's initialization phase.
The builder also disassembles the final ELF and runs `audit_runtime.py`. It
requires the logger initialization call in setup, its mutex constructor and
buffer allocation, and OS/setup/task/scheduler ordering. The exact flashed
image that lacked the initializer fails this check. These are selected structural
and call-order checks, not CPU emulation or hardware qualification; changed
compiler inlining or disassembly formatting may require explicit audit updates.

## Application behavior and assumptions

### Boot recovery before application work

Both profiles initialize the module UART and update service, then spend at least
3000 ms polling READY before starting the hello loop or radar initialization.
The board's earlier power callback holds the radar off. A CRC-valid READY that
reaches the updater during this window latches recovery until reset: failed
handshakes/transfers do not release the application. Successful updates follow
the existing loader handoff and reboot. After an unclaimed window, radar setup
adds I2C/SPI without reopening the UART or clearing its RX buffer; radar setup
errors leave the updater running. This is an application recovery gate, not an
independent bootloader: ROM/vendor SDK startup, memory, clocks and logger setup
still precede it. A fault there, corrupt flash, or interrupted programming can
still require external recovery. A later application hang requires a power
cycle; automatic watchdog recovery has not been added.

To catch the window, start the PC uploader at 256000 with `--entry custom`, then
power-cycle the module within its 20-second initial timeout. The uploader sends
READY every second until START. No terminal keystroke or precise timing is needed.
Do not send a READY probe during the window unless intending to stay in recovery.

On 2026-10-05, `build/hello-recovery/update-two-wire.ufw` was installed successfully.
PA9 receive timestamps measured 3.001075 seconds from the recovery-window banner
to the hello-start banner (host/USB timing, not a precision target measurement).
On a user-confirmed power cycle, one valid READY caused six unanswered START
attempts, then the recovery-latched banner after 4.237 seconds. Eight additional
seconds produced no application-start banner or COM13 heartbeat. No firmware
bytes were sent during that intentional handshake failure.

Without resetting, a new upload from this latched state installed a same-source
rebuild with a different embedded timestamp: 417 reads, 184320 reported update
bytes, final success, new PA9 timestamp `Oct 5 2026 20:06:25`, and 11 heartbeats
in the subsequent 12-second observation (which includes part of the boot window).
The installed image at that stage was **`build/hello-recovery-retry/update-two-wire.ufw`**,
SHA256 `5d77b20852c17a659cd5b83f8b2cd025720250c7e86475bbf3ab73f9d844283e`.
See `output/firmware_build/recovery_hardware_validation_20261005.json` for all
capture paths, build provenance and limits. Radar-recovery remains unflashed.
Six native suites and 31 Python tests passed before the bench test; both target
profiles pass startup/runtime audits. No firmware source changes were needed.

### Radar initialization bench result

On 2026-10-05 (Pacific), **`build/radar-bringup/update-two-wire.ufw`** was flashed
through the working custom updater: 417 reads, 184320 reported update bytes,
final success. This was the radar initialization image; SHA256
`1f7e69f8d5630fcee9ea50b9d242ba95990b40aeeb5fa132e21c500bc35c7e56`.
After the recovery window, PA9 reported `stock-mode2-baseline`, all 80 writes
ACKed at I2C address 0x20, SPI configured, bias enabled and DMA not armed.

Updater entry from that initialized radar state also succeeded. The identical
image trial made 50 reads and reported zero application update bytes, then
rebooted into a second successful 80-write initialization. This verifies updater
entry/handoff/return after radar startup, not a second application rewrite.
No logic-analyzer capture was available; acknowledgments are MCU driver reports.
SPI clocks, actual sample reception and RF performance are not yet validated.
COM13 is intentionally idle outside updates in the radar profile (no hello
heartbeat); PA9 carries initialization diagnostics. Radar supply/bias are left
enabled after successful init. Both host serial ports were released.

Diagnostics identify the failed stage, error, count of acknowledged writes and,
for a failed table transaction, its one-based write index, register and value.
No prints were added inside the SPI/REXT/final-write transition. Radar failures
still power it down and leave UART updating available. Six native suites and
31 Python tests pass; the target build and package passed existing audits.
Evidence: `output/firmware_build/radar_bringup_hardware_validation_20261005.json`.

### Bounded dual-lane capture

Build with `--application capture --out firmware/build/spi-capture`, then patch
its UFW using `patch_stock_uart_loader.py` as above. The separate capture profile
retains the boot recovery gate and the 80-write baseline. It arms two aligned
32896-byte DMA buffers (16 complete 2056-byte records each) after SPI setup and
before REXT enable. Completion of both
lanes or a two-second deadline stops the radar/DMA before any buffer is dumped.
An updater request or radar init failure cancels the capture. Module UART output
uses CAPTURE BEGIN/END records and offset-labelled 32-byte hexadecimal DATA
lines; each header reports whether that lane completed. A timed-out buffer is
preserved in full with its A5 prefill; no inferred partial byte count is claimed.

On 2026-10-05, the capture image completed both lanes, each with three contiguous
2056-byte checksum-valid DS RAW records and a partial fourth. Each complete record
contains 512 signed big-endian I/Q pairs. Headers identify RX0 on lane 0 and RX1
on lane 1, with chirps 0, 1 and 2 on both. The lanes contain distinct samples;
the six records provide 3072 validated I/Q pairs. This is data-transfer/framing
validation, not calibrated range/angle or proof of continuous lossless capture.

The first 8 KiB capture image's UFW SHA256 was
`501d05e5b5b960c51ce360e4c0e51f6b339ec21e40ec7962583fe4435fece3e5`.
It captures once per boot, leaves the radar powered off after dumping, and keeps
the updater available (READY/START probed after capture). To decode saved output:

```powershell
python firmware/tools/decode_capture.py PATH/TO/com13-post.txt --out output/spi_capture/decoded
```

The first upload attempt stalled in the existing radar image at SDK loader-stage
flash erase after seven reads; no new application was installed then. A user
power cycle let the host catch the boot recovery gate and install the capture
image successfully. Cause of the staging stall is unresolved; this is evidence
that boot recovery bypassed it, not proof that ordinary updater entry is always
reliable after radar activity.

Raw captures, six extracted records, IQ CSV, plot and checksum report are in
`output/spi_capture/first_dual_lane/`. Build/protocol provenance is in
`output/firmware_build/spi_capture_hardware_validation_20261005.json`.
Seven native suites and 34 Python tests pass (including three decoder tests).

The subsequent larger capture completed **16 contiguous records per lane**,
matching chirp numbers 0-15, with all headers/trailers/checksums valid and no
truncated record: 65792 raw bytes and 16384 decoded I/Q pairs. Main RAM heap
reservation is 91296 bytes after static allocation; this is not a measurement of
runtime free heap. The update from the stopped first-capture application completed
normally without a manual reset (417 reads, 184320 reported application bytes).
Both ports were released, and the radar is off after its one-shot dump.

The installed image at that stage was `build/spi-capture16/update-two-wire.ufw`, SHA256
`16381b9302ccceaa48af63f7459c293fccbeb042064be85432480fbb575f6fb5`.
Raw buffers, all 32 extracted packets, IQ CSV and plots are in
`output/spi_capture/dual_lane_16chirps/`; full evidence is in
`output/firmware_build/spi_capture16_hardware_validation_20261005.json`.
`decode_capture.py` accepts both capture sizes and exports records plus IQ CSV.
`plot_capture.py DIRECTORY` regenerates the chirp overlay/difference plot from
the decoder output. Differences are in sample units, without motion/range/angle
interpretation or RF calibration. Seven native suites and 34 Python tests pass.

With the radar profile, `target/br23/image/main.c` invokes `ld2450_app_start()`
from `app_core`, after the shared early console and board power setup:

1. Initialize UART/I2C with PC2 high (supply off), PC3 low (REXT disconnected)
   and both SPI receivers disabled.
2. Drive PC2 low, retaining PC3 low; wait at least 20 ms for supply startup.
3. Apply register writes 1..75 at address 0x20.
4. Configure both receive-only SPI controllers without driving PB1/RESET.
5. Drive PC3 high, wait at least 3 ms, then apply writes 76..80.
6. Leave supply and REXT enabled and poll the UART update service.

The 75/SPI/REXT/delay/5 ordering is recovered from stock code. The initial
low REXT state and 20 ms supply delay are engineering choices, not recovered
waveforms. The datasheet gives approximately 4 ms typical readiness, not a
worst-case guarantee. The capture's 2.424396 ms gap between writes 75 and 76
includes SPI setup, GPIO and a stock delay loop with argument 1000. Our 3 ms
bias delay is an initial margin, not a conversion of that loop count. The SDK
timer returns `jiffies * 10`, verified in the linked SDK disassembly: its
resolution is 10 ms. The delay adds a full tick to avoid finishing early.
Thus the 20 ms minimum normally takes 20..30 ms, and the 3 ms minimum takes
10..20 ms (task preemption can extend either). Neither exact timing nor RF
behavior has been bench-validated.

Any radar I2C NACK/timeout aborts further writes, powers down the radar and
leaves the initialized UART updater available. A basic peripheral setup failure
prints a repeated error; it cannot provide updating if UART setup failed.
PA1 TX / PA0 RX use 256000 baud, 8N1. PA9 prints init status
and `HLK-LD2450_FW radar experiment application 0.2` at 115200 baud.
SPI controllers are prepared but DMA is not armed: sustained acquisition,
Bluetooth, tracking and target-report services remain unimplemented.
External I2C/SPI capture can observe register experiments now.

The update transaction runs synchronously in `app_core` (`task_en=0`), so
one task owns the UART/parser throughout. Reads are split into at most 512
bytes with four attempts, exact offset/length matching and CRC16/XMODEM.
Successful staging requires the SDK success report, a successful EXIT,
an acknowledged STOP `0x80`, and a verified flash handoff-record write.
Only then does the application close peripherals, copy the 112-byte record
into the reserved update RAM and reset. The record carries the actual
negotiated baud, PA1/PA0 pins and a ten-second loader timeout. Failure leaves
the receiver at its 256000-baud entry rate for another session. Accepting
an update request powers down the radar; an aborted update leaves it off
until reboot.

The clock configuration in `target/br23/image/app_config.h` requests a 240 MHz
system clock, matching the captured stock V2.14 log. The 24 MHz PLL reference
is retained; stock oscillator/PLL setup is consistent with it, but the crystal
has not been measured independently. Project `bringup.c` caps LSB at 48 MHz
before the pinned SDK clock initialization, keeping the 100 kHz hardware-I2C
divider within its eight-bit register (239 at 48 MHz). The SDK's default
60 MHz LSB at this CPU rate would require 299 and fail our range check before
UART initialization. `build_image.py` renames only the SDK setup entry point
so the wrapper can run without editing vendor sources. This clock revision
has booted in the verified hello builds. See [the bring-up audit](BRINGUP_AUDIT.md).
`CONFIG_FLASH_SIZE` is a 256 KiB linker budget, not a measurement of physical
flash capacity: the stock log reports 1024 KiB. The package still preserves
the stock flash layout and enforces its smaller application slot independently.
The application entry is `0x1E00120`.
Stock soundbox board, key, audio and charge initializers are excluded. The
project board initializer supplies MCU power setup; the SDK debug UART initializer
now supplies the early PA9 console.
The vendor charge/PWM source supplies library helper dependencies; this image
does not call their board initialization functions.

## Packaging boundary

`package_ufw.py` accepts only the two SHA-pinned stock UFWs in this repository.
It replaces `app.bin` in all four flash variants, preserves each original
application slot size with `FF` padding, and rebuilds the known nested and
outer CRCs and scrambling. Capacity is 182760 bytes with the default V2.14
template or 178308 bytes with V2.04. It rejects larger applications.

Bootloader, flash parameters, config files, reserved-region descriptors, OTA
loaders and non-flash UFW entries are preserved. Their presence in a package
does not prove preservation of existing device VM contents during an update.
The original unexplained CRC fields on `isd_config.ini`, `script.ver` and
`blimit.bin` remain untouched; the independent decoder reports the same
unresolved fields for stock and custom containers.

This is a fixed-layout image builder for these templates, not a general UFW
authoring tool. The physical loader accepted and reported programming success for
the baseline with the two-wire patches; subsequent hello builds also booted and
accepted repeat updates. Stock product identifiers remain those of the template.

## UART transfer and current bench status

Follow [UART_LOADER_BENCH.md](UART_LOADER_BENCH.md) to apply the required two-wire
loader patches and invoke the uploader. Stock V2.14 B2 entry and complete
programming have now been exercised on COM13 at 256000. Stock V2.04 requires
an update to V2.14 through BLE first. Keep initial and negotiated rates equal
to the tested 256000 for this route.

Later hello, radar and capture runs established custom application boot,
radar initialization and repeat UART entry. The 2026-10-06 `stream` application
also passed continuous acquisition and updater entry while running; see
[FRAME_STREAM.md](FRAME_STREAM.md) for the exact image and evidence. Native
USB enumeration and concurrent export remain untested until USB is wired.

## Validation performed

[Startup validation record](../../output/firmware_build/radar_startup_validation.json)
records both current images and their source hashes. The earlier
`validation.json` describes the preceding recovery-only application.

`python firmware/tools/test_host.py` runs twelve CTest suites and the
Python tests: captured packet parsing, pin/peripheral behavior, radar table
generation, bounded UART framing, actual adapter logic with modeled device
I/O, two-stage PC protocol handling and packaging boundaries. Startup tests
check the exact 80-write payload/order, supply/bias/SPI states at each stage,
minimum delays at all ten timer phases, timer wraparound, and all 320 possible address/data NACK
locations, including UART availability after failure. Both stock
applications repack to byte-identical original UFWs. Both example profiles
target-link; the chosen table survives LTO. A separate jl-misctools-based
decoder verifies custom applications in all four flash variants.

Host tests do not execute the vendor engine or flash writer. The separate
[bench record](UART_LOADER_BENCH.md) establishes programming success using
the patched loader; later hello and radar initialization bench results above
also confirm application execution and updater reentry.
