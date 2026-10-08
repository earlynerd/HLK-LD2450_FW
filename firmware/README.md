# LD2450 firmware foundation

The new [stream application and bench handoff](docs/FRAME_STREAM.md) connects
continuous dual-SPI acquisition to lossless LDF1 encoding and native USB CDC.
The optimized image is flashed and has delivered 159 complete host-validated
frames in a 30-second concurrent acquisition/compression/USB trial, with zero
DMA overruns or radar errors. Native CDC is COM30; UART recovery remains on
COM13 and PA9 diagnostics on COM11. Use `--application stream` for radar data
or `--application usb-bench --raw-usb-bench` for paced synthetic raw records
with the radar off. See the linked report for skips, pause/reopen and limits.

An incremental C firmware component for the likely **JieLi AC695N / AC6956C
(BR23)** MCU, using the RD-03D schematic as the working LD2450 pin map. The
[hardware reference](../docs/radar_ic_and_internal_interfaces.md) records the
evidence and unresolved details. This first version initializes the known
peripherals and provides APIs for the recovered radar register profiles and
data handling. It now links a minimal PI32V2/r3 application and packages UFW
images. The [image guide](docs/IMAGE_BUILD.md) gives reproducible commands and
the [register experiment workflow](docs/REGISTER_EXPERIMENTS.md) describes
customizable profiles and automatic radar startup.
The [UART update investigation](docs/UART_UPDATE.md) establishes the SDK's
`UART_UPDATA` -> `uart_user.bin` path, protocol, integration points, and vendor
example defects. Its ABI probe compiles for BR23; the application update
receiver and complete image builder are implemented. Stock V2.14 to custom hello,
power-cycle boot, and custom-to-custom replacement are bench-verified with two
[loader patches](docs/UART_LOADER_BENCH.md). The boot recovery window, failed
handshake latch and subsequent update retry are also bench-verified in hello.
The radar image now reports 80/80 initialization writes ACKed and retains working
updater entry. Bounded SPI DMA capture now yields checksum-valid, distinct
RX0/RX1 records. Continuous acquisition and stock restoration have since been verified (see the
repository README); RF calibration remains open; see [the image guide](docs/IMAGE_BUILD.md) for exact artifacts.

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
It initializes UART and I2C, holds REXT low, enables the radar supply, and
waits at least 20 ms. It then writes entries 1..75 of the selected profile,
configures both SPI receivers, asserts PC3/REXT, waits at least 3 ms, and
writes entries 76..80. REXT remains asserted after successful initialization.
The default profile is the mode-2 table confirmed by the 80-write I2C capture.

`LD2450_OK` means all writes were acknowledged; it does not establish RF or
sample-stream correctness. A radar error stops the sequence, powers the radar
down, and preserves UART updating. A basic peripheral setup failure rolls
back setup; the image resets if no initialized UART service remains. A second
initialization returns `LD2450_BUSY`.

`ld2450_radar_power(1)` enables only the supply; `ld2450_radar_bias(1)` controls
REXT independently. Power-off cancels DMA and disables SPI and REXT.
`ld2450_spi_prepare()` configures both SPI controllers after the first stage.
The application does not arm DMA or process samples yet; use external capture
for register experiments. Supply settling and the initial low REXT state are
engineering choices. The 3 ms delay is a conservative starting value based on
the captured 2.424396 ms gap, which also includes stock SPI/GPIO setup. The
stock delay argument 1000 is a loop count, not a known time unit. Delays use
the SDK timer, whose 10 ms resolution makes these waits roughly 20..30 ms
and 10..20 ms respectively. A full tick of margin prevents early completion. See [IMAGE_BUILD.md](docs/IMAGE_BUILD.md).

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
continuous radar acquisition remain future application integration work.

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

The five CTest suites compile the decoder, peripherals, init and UART sources with
warnings treated as errors. Peripheral tests use a host model of the SDK:
pin ownership, SPI/I2C configuration, UART failure rollback, independent DMA
completion, I2C repeated starts/NACK/deadline recovery, and startup status.
The packet suite checks 34 byte-exact captured records, all 7,944 boot pairs,
and checksum corruption, trailer corruption, and bounds handling.
Twelve Python tests additionally check recovered table/source hashes, guarded
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
both SPI data lanes and CS timing; the initial I2C capture now matches mode 2
exactly (see [comparison](../output/i2c_init_comparison/report.txt)). Further
power/bias captures are optional timing validation. Keep new captures as
immutable inputs with hashes and add captured behavior in separate increments.
