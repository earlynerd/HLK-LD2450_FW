# Minimal UART recovery image

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

The selected table is retained in the linked binary and its bytes are checked
before packaging. This first application's main loop does **not** apply it:
automatic power/bias sequencing and acquisition still need implementation
from the planned capture.

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

`target/br23/image/main.c` starts the known peripherals, with PC2 high and
PC3 low (radar supply/bias disabled). It then initializes the SDK update
runtime and polls for READY on PA1 TX / PA0 RX at 256000 baud, 8N1. PA9 emits
the `HLK-LD2450_FW UART recovery application 0.1` banner at 115200 baud.
There are no Bluetooth, tracking or target-report services in this image.

The update transaction runs synchronously in `app_core` (`task_en=0`), so
one task owns the UART/parser throughout. Reads are split into at most 512
bytes with four attempts, exact offset/length matching and CRC16/XMODEM.
Successful staging requires the SDK success report, a successful EXIT,
an acknowledged STOP `0x80`, and a verified flash handoff-record write.
Only then does the application close peripherals, copy the 112-byte record
into the reserved update RAM and reset. The record carries the actual
negotiated baud, PA1/PA0 pins and a ten-second loader timeout. Failure leaves
the receiver at its 256000-baud entry rate for another session.

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

First hardware validation should establish the clock, install the recovery
image, observe its PA9 banner and power-off GPIO state, then use UART to load
a second custom image and repeat once more. Confirm stock restoration through
the recovery route before proceeding to radar register experiments.

## Validation performed

`python firmware/tools/test_host.py` runs five native C suites and twelve
Python tests: captured packet parsing, pin/peripheral behavior, radar table
generation, bounded UART framing, actual adapter logic with modeled device
I/O, two-stage PC protocol handling and packaging boundaries. Both stock
applications repack to byte-identical original UFWs. Both example profiles
target-link; the chosen table survives LTO. A separate jl-misctools-based
decoder verifies custom applications in all four flash variants.

The SDK update engine and the preserved flash writer have not executed in
these host tests. No image has been flashed or booted on the radar module.
