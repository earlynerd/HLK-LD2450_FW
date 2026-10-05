# Radar experiment image with UART recovery

This pipeline produces a complete `.ufw` containing a project-owned BR23
application. It uses the pinned vendor startup, RTOS, hardware libraries and
update engine. The application UART receiver is our code; the second-stage
flash-writing loader remains the stock `ota.bin/uart_user.bin`. We are not
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

## Application behavior and assumptions

`target/br23/image/main.c` invokes `ld2450_app_start()` from `app_core`:

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
resets the MCU. PA1 TX / PA0 RX use 256000 baud, 8N1. PA9 prints init status
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

The clock configuration in `target/br23/image/app_config.h` assumes a 24 MHz
crystal and 24 MHz system clock, taken from the SDK baseline. The module's
crystal has not yet been verified. The flash configuration is 256 KiB, matching
the preserved stock directory layout; the application entry is `0x1E00120`.
Stock soundbox board, key, audio, charge and UART initializers are excluded.
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
authoring tool. Compatibility checks inside the physical loader have not yet
been exercised. Stock product identifiers remain those of the template.

## UART transfer, when ready for hardware testing

The PC peer is supplied in `tools/uart_upload.py`. Installing pyserial is
only required for hardware transfer, not building or offline tests:

```powershell
python -m pip install pyserial
python firmware/tools/uart_upload.py firmware/build/image/update.ufw --port COM7
```

**The second command writes firmware to the device.** Substitute the actual
port. The script sends our READY entry at 256000, serves bounded file reads,
acknowledges keepalives/status, and stays connected after loader-stage STOP
`0x80` until final STOP `0`. `--baud` changes the negotiated transfer rate;
entry remains 256000. No port scanning or reset-pin toggling is performed.

This entry command is defined for our application. We have not established
the stock Hi-Link/Ai-Thinker application's entry wrapper. Initial installation
therefore depends on the user's USB bootloader work or another established
stock-compatible loading route. A UFW is an update container, not a raw flash
dump to write at address zero.

First hardware validation should establish the clock, install the baseline
image, and observe its PA9 init status and I2C/SPI output. Verify UART loading
of another custom image and a repeated update, plus stock restoration through
the established recovery route.

## Validation performed

[Startup validation record](../../output/firmware_build/radar_startup_validation.json)
records both current images and their source hashes. The earlier
`validation.json` describes the preceding recovery-only application.

`python firmware/tools/test_host.py` runs five native C suites and twelve
Python tests: captured packet parsing, pin/peripheral behavior, radar table
generation, bounded UART framing, actual adapter logic with modeled device
I/O, two-stage PC protocol handling and packaging boundaries. Startup tests
check the exact 80-write payload/order, supply/bias/SPI states at each stage,
minimum delays at all ten timer phases, timer wraparound, and all 320 possible address/data NACK
locations, including UART availability after failure. Both stock
applications repack to byte-identical original UFWs. Both example profiles
target-link; the chosen table survives LTO. A separate jl-misctools-based
decoder verifies custom applications in all four flash variants.

The SDK update engine and the preserved flash writer have not executed in
these host tests. No image has been flashed or booted on the radar module.
