# LD2450 firmware foundation

An incremental C firmware component for the likely **JieLi AC695N / AC6956C
(BR23)** MCU, using the RD-03D schematic as the working LD2450 pin map. The
[hardware reference](../docs/radar_ic_and_internal_interfaces.md) records the
evidence and unresolved details. This first version initializes the known
peripherals and provides APIs for the recovered radar register profiles and
data handling. It now links a minimal PI32V2/r3 application and packages UFW
images. The [image guide](docs/IMAGE_BUILD.md) gives reproducible commands and
the [register experiment workflow](docs/REGISTER_EXPERIMENTS.md) describes
customizable profiles and the remaining radar startup work.
The [UART update investigation](docs/UART_UPDATE.md) establishes the SDK's
`UART_UPDATA` -> `uart_user.bin` path, protocol, integration points, and vendor
example defects. Its ABI probe compiles for BR23; the application update
receiver and complete image builder are implemented. Boot and hardware update
behavior remain unverified.

## Implemented

| Interface | MCU pins | Initialization and API |
| --- | --- | --- |
| Radar RX1 | PB2 data, PB0 clock, PB3 CS observation | SPI1 group A, slave, mode 0, 8-bit, receive only; one-shot DMA |
| Radar RX2 | PB8 data, PB9 clock, PB11 CS observation | SPI2 group A, same configuration; independent DMA buffer |
| Radar control | PC4 SCL, PC5 SDA | Hardware I2C master, nominal 100 kHz; raw write/read/repeated-start transactions with deadlines and NACK handling |
| Module UART | PA1 TX, PA0 RX | 256000 baud, SDK UART driver, 1024-byte RX ring; configurable pin swap |
| Debug UART | PA9 TX | 115200 baud, configurable/optional |
| Radar power | PC2 `PW_CTL` | Low enables power; initialized high/off |
| Radar bias gate | PC3 `REXT_CTL` | High enables bias ground path; initialized low/off |
| MCU reset | PB1 | Input with pull-up; never driven as SPI output |

The SPI implementation uses the vendor register definitions and GPIO APIs.
Calling the SDK's `spi_open()` would also configure PB1 as SPI1's output;
this board connects PB1 to MCU RESET. Our initialization avoids that call.
SPI0 belongs to the SDK's boot/flash infrastructure and is untouched.

The portable [DS RAW decoder](src/radar_wire.c) accepts an assembled logical
record. It decodes the big-endian header and signed I/Q, checks the payload
checksum and trailer, and preserves the observed 248-pair boot records with
`RADAR_RECORD_STARTUP_NO_TRAILER`. Those records remain unvalidated. The
header's count mask includes the observed bit 9; bit 10 remains unconfirmed.
It borrows the input buffer, so that buffer must remain alive during decoding.

## Startup contract

Call `ld2450_app_start()` once from an SDK application task, **after clocks,
RTOS, timer tick, interrupts, and the UART driver runtime are available**.
It initializes the peripherals and prints a debug banner. On successful setup
it returns `LD2450_CONFIG_CAPTURE_REQUIRED`, with `initialized=1` and radar
power still off. Negative setup errors identify the failed step and UART
allocation failures shut the peripherals down. A second initialization returns
`LD2450_BUSY`.

`ld2450_radar_power(1)` controls only the schematic's power/bias gates. It
does not configure the radar, add delays, or establish that RF output is ready.
The stock gate sequence and timing need a capture before implementing automatic
startup. The 80-write tables have been recovered from both stock firmware
images; [ld2450_radar_init.h](include/ld2450_radar_init.h) provides an explicit
75-write/5-write staged writer. No radar register writes occur in the startup
hook. The application caller owns power/bias timing, stage ordering, and SPI
arming; the stage writer stops at the first bus error.

The public APIs in [ld2450_peripherals.h](include/ld2450_peripherals.h) have a
single task owner; concurrent calls and ISR use are unsupported. I2C addresses
are seven-bit and register widths are deliberately unspecified. Each I2C
operation attempts STOP; a stuck operation times out and resets the controller.
A target holding SDA low may still require physical bus recovery. I2C's divisor
uses `clk_get("lsb")`, with an eight-bit range check. Keep that clock stable
while initialized; changing it requires reinitialization.

DMA buffers must be four-byte aligned and remain borrowed until completion or
power-off/deinitialization cancels them. Arm both receivers before radar
clocking starts. Polling returns each filled buffer and a CS level snapshot.
CS is a GPIO input: the pinned SDK exposes no SPI1/SPI2 slave CS pin mapping,
and this implementation does not gate transfers or assemble packets by CS.
A logical packet can span CS transactions. Continuous ISR rearming, startup
alignment, dropped-data reporting, and synchronizing both lanes are future work.
The one-shot API has not been shown to sustain continuous 16.67 Mbit/s traffic.

USB DM/DP are reserved for a future transport or bootloader integration.
USB/Bluetooth stacks, FFT/detection/tracking, UART target-report generation, and
automatic radar boot/acquisition remain future application integration work.

## Host build and checks

Requires Python **3.11+**, CMake, and a native C compiler. On this Windows host,
Visual Studio 2022's C tools are available:

```powershell
python firmware/tools/test_host.py
```

For GCC/Clang on Linux:

```sh
python3 firmware/tools/test_host.py --generator "Unix Makefiles"
```

The three CTest suites compile the actual decoder, peripheral, and init source with
warnings treated as errors. Peripheral tests use a host model of the SDK:
pin ownership, SPI/I2C configuration, UART failure rollback, independent DMA
completion, I2C repeated starts/NACK/deadline recovery, and startup status.
The packet suite checks 34 byte-exact captured records, all 7,944 boot pairs,
and checksum corruption, trailer corruption, and bounds handling.
Seven Python tests additionally check recovered table/source hashes, guarded
occurrence-specific overrides, generated bytes/provenance, fixture hashes,
archive path/symlink rejection, and preserving a changed SDK checkout rather
than overwriting it.

[Fixture provenance](tests/fixtures/manifest.json) records original CSV line
numbers, timestamps, and hashes. Recreate the fixtures only from the matching
original capture with `python firmware/tools/extract_fixtures.py`.

## Pinned target SDK and build

[sdk.lock.json](sdk.lock.json) pins the official
[JieLi AC695N Soundbox SDK](https://gitlab.zh-jieli.com/soundbox/novisualization/ac695n_soundbox_sdk),
release 3.1.2, commit `641e45dff1a8dc455fc6ccd688236fa59688b9ee`.
The archive SHA-256 and eight driver/build-file hashes are recorded. Vendor
sources live in the ignored `.cache/sdk` directory. Setup verifies the archive
and extracted contents without executing vendor programs:

```powershell
python firmware/tools/setup_sdk.py --download
python firmware/tools/build_br23.py --plan
```

The sources are already cached on this workspace. `--plan` checks the pinned
API files and writes explicit compile/archive commands; it does not compile.
The official Windows toolchain 2.5.2 is now extracted in this project's cache,
with package/signature/tool provenance in [toolchain.lock.json](toolchain.lock.json).
The builder selects it automatically and checks its executable hashes:

```powershell
python firmware/tools/build_br23.py
python firmware/tools/build_br23.py --radar-config firmware/config/radar_no_idle_powerdown.json --out firmware/build/br23-no-idle-powerdown
```

For a separate vendor **PI32V2/r3** installation:

```powershell
python firmware/tools/build_br23.py --toolchain C:/JL/pi32/bin
```

This compiles four project C sources and the generated profile against the real SDK headers and
creates `firmware/build/br23/libld2450.a`. Link it into a BR23 SDK application
and invoke `ld2450_app_start()` from that application's task. The SDK supplies
startup, clocks, RTOS, interrupt tables, timer tick, watchdog service, UART
runtime, and linker/flash layout. Their module-specific configuration and a
complete image link are supplied by `tools/build_image.py`. Ordinary ARM GCC or
desktop Clang cannot generate code for this MCU.

Do not run plain `make` in the cached SDK: its stock `all` target runs a device
download script. Our builder invokes only compilation and archive creation.
Review/disable stock audio, charging, keys, SPI1/SPI2/I2C users, and other board
drivers before linking an application for this board. Disable the stock debug
UART before opening our PA9 console; otherwise use the SDK console with
`enable_debug_uart=0` and initialize via `ld2450_peripherals_init()` directly.
The driver's dynamic UART routing supports the schematic's PA1 TX / PA0 RX
despite the reversed fixed UART1C mapping in the datasheet.

The schematic omits the MCU crystal value. The vendor demo's 24 MHz board
setting is an unverified integration default, not a measured LD2450 oscillator.
Confirm it before selecting the final SDK clock configuration.

## Current validation and next evidence

On 2026-10-04 the host build passed five CTest suites and twelve Python tests.
The baseline and customized profiles link with the real JieLi PI32V2/r3
compiler and package into UFW images. Tests include the actual UART adapter
with modeled SDK/device I/O, failure/retry behavior, and byte-identical stock
packaging roundtrips. An independent decoder accepts all four custom flash
variants. **No device flashing, boot test, or bench validation has occurred.**

The [capture plan](docs/CAPTURE_PLAN.md) focuses next on I2C initialization,
both SPI data lanes, CS timing, and power/bias control. Keep new captures as
immutable inputs with hashes and add captured behavior in separate increments.
