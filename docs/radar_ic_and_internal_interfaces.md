# Radar IC identification and internal interfaces

This is the reference for the radar-chip identification, documented interface
pins, and evidence from the internal SPI captures. The original capture files
remain unchanged. Decoder setup and display details are in the
[Saleae extension README](../saleae_ld2450/README.md).

## Identification and confidence

**Working identification for this HLK-LD2450: ICLegend S5KM312CL radar IC;
JieLi AC695N-family MCU, with AC6956C the strongest specific candidate.** Ai-Thinker's
[RD-03D Specification V1.0.0](datasheets/Ai-Thinker_RD-03D_Specification_V1.0.0.pdf)
explicitly identifies the **S5KM312CL** on printed p. 4 and supplies the RD-03D
schematic on p. 10, Figure 6. Its revision history gives 2023-08-31 as the
first-edition date (p. 2).

The user reports that **RD-03D and LD2450 are visually identical devices**, that
the radar IC on their LD2450 carries Hi-Link markings, and that RD-03D board
photos show a large **JL logo on the MCU**. They identify **AC695N** as the
likely MCU family. These visual observations, the matching radar protocol,
and the manufacturer's schematic support using the RD-03D circuit as the
**likely LD2450 wiring reference** for this investigation. A shared circuit
is the working assumption; no continuity audit has been performed, and the
manufacturing/white-label relationship is not documented.

Ai-Thinker's PDF is direct manufacturer documentation for the **RD-03D**.
It labels the MCU **U2** without a part number. A separate JieLi AC6956C
datasheet supplies a matching package pinout, as detailed below.

The radar is a 24 GHz, one-transmitter/two-receiver FMCW SoC in a
32-pin QFN package. [Manufacturer product page](https://www.iclegend.com/en/product/S5KM312CL/).
The internal stream matches its published DS RAW framing, RX encoding, I/Q
layout, and checksum. The three captures contain 19,619 complete packets
passing the checksum and trailer checks. This establishes protocol compatibility;
it does not by itself prove a white-label manufacturing arrangement.

The pin numbers below are **datasheet package pins**. The RD-03D schematic
connections are recorded separately below. The LD2450 PCB connections,
test-point names, and actual reset-strap levels have not been traced or verified.
These package pins are distinct from the module's four-pin power/UART connector.

## Radar data-output SPI

| Chip pin | Signal in SPI output mode | Function |
| --- | --- | --- |
| 26 | `SPI_CSN` | Shared chip-select output |
| 27 | `SPI_MOSI_0` | RX1 data output |
| 28 | `SPI_MOSI_1` | RX2 data output |
| 29 | `SPI_SCLK` | Shared clock output |

Pin reference: [Rev. 1.3 PDF](datasheets/S5KM312CL_Rev.1.3_20221109.pdf),
printed pp. 5–6, Table 5-1.

The radar is the **master** on this interface. It has two output data lanes;
there is no MCU-to-radar data input on this data-output bus. The documented
SPI mode is 0 (`CPOL=0`, `CPHA=0`), MSB first, up to 16.67 Mbit/s.
[Rev. 1.6, section 8.2.1](https://www.scribd.com/document/932226790/ICLegend-S5KM312CL-24Ghz-mmWave-Sensor-for-RD-03-Radar-Module-Datasheet).

The current CSVs contain **RX2 packets only**. Their useful lane is named
`miso`, while the exported `mosi` lane is zero. These are analyzer labels,
not evidence of the physical master/slave direction. A zero captured lane
does not establish that RX1 is absent from its own output pin.

The datasheet also documents optional RX1/RX2 interleaving on one output lane;
that format has not been observed in these three captures. To examine the
second receiver, use the pin map above as a tracing reference. I and Q in one
packet are components of **one receiver**, not the two receivers.

## Separate MCU configuration interface

| Selected configuration mode | Chip pins |
| --- | --- |
| I2C | 20 = SDA; 21 = SCL |
| SPI | 20 = MOSI into radar; 21 = clock into radar; 22 = CS; 23 = MISO out of radar |
| UART | 20 = RX into radar; 21 = TX out of radar |

These multiplexed functions are documented in
[Rev. 1.3, Table 5-1](datasheets/S5KM312CL_Rev.1.3_20221109.pdf).
Thus MCU-to-radar configuration traffic can exist on **different pins** from
the captured data-output bus. The RD-03D schematic explicitly connects I2C
between the MCU and radar. The LD2450's selected control interface remains
unmeasured; I2C is the likely interface under the shared-circuit assumption.

The documented reset selection uses pins 23 and 24 for configuration mode:

| Pin 23 | Pin 24 | Configuration mode |
| --- | --- | --- |
| Low | Low | UART |
| Low | High | I2C |
| High | Either | SPI |

Pin 25 selects raw GPIO data when low and SPI/UART data when high. These
are reset/settling-time states, not necessarily normal operating levels.
[Rev. 1.3, printed p. 6, Tables 5-2 and 5-3](datasheets/S5KM312CL_Rev.1.3_20221109.pdf).

## Ai-Thinker RD-03D schematic connections

Source: [RD-03D Specification V1.0.0](datasheets/Ai-Thinker_RD-03D_Specification_V1.0.0.pdf),
printed p. 10, Figure 6. The embedded schematic was inspected visually because
its signal labels are an image and are absent from extracted PDF text.
**Confidence: high for the drawn connections; likely shared with the user's
LD2450 based on their reported visual match, pending a physical check.**
U3 is the radar, identified as S5KM312CL by the product overview on p. 4;
U2 is the external MCU, whose exact part number is omitted.

| Radar U3 pin / function | Schematic net and components | MCU U2 endpoint |
| --- | --- | --- |
| 27 / RX1 SPI data output | `SPI0_MOSI0` | PB2, pin 13 |
| 28 / RX2 SPI data output | `SPI1_MOSI1` | PB8, pin 8 |
| 29 / shared SPI clock | `SPI_SCLK` -> R8 -> `SPI0_SCLK` | PB0, pin 15 |
| 29 / shared SPI clock | `SPI_SCLK` -> R9 -> `SPI1_SCLK` | PB9, pin 7 |
| 26 / shared SPI chip select | `SPI_CSN` -> R10 -> `SPI0_CSN` | PB3, pin 12 |
| 26 / shared SPI chip select | `SPI_CSN` -> R13 -> `SPI1_CSN` | PB11, pin 5 |
| 20 / configuration I2C data | `I2C_SDA`, R4 pull-up to `3V3_SOC` | PC5, pin 19 |
| 21 / configuration I2C clock | `I2C_SCL`, R3 pull-up to `3V3_SOC` | PC4, pin 20 |

Thus the reference design brings **both radar data lanes** to two MCU SPI
ports, sharing the radar's clock and chip select through separate series
resistors. It draws **no MCU-to-radar data wire on that SPI output interface**.
MCU-to-radar configuration uses the separate I2C bus; SDA can carry data in
both directions. This supplies a concrete explanation for why the present
SPI capture could miss both RX1 and configuration traffic. These connections
are the working map for the LD2450; tracing or additional captures can verify it.

The diagram draws R17 from radar pin 23 to ground and R37 from pin 24 to
`3V3_SOC`, consistent with the chip datasheet's I2C configuration selection.
It also draws R15/R14 pull-downs on pins 27/28. If those establish low/low
during settling, Rev. 1.3 Table 5-4 gives the **7-bit I2C address 0x20**;
that address has not been measured here. Resistor values and population
options are not specified in the diagram.

**Unresolved data-mode detail:** R38 is drawn from pin 25 to ground, while
Rev. 1.3 Table 5-3 associates a low pin 25 with raw GPIO output and a high
pin 25 with SPI/UART output. The figure still labels pins 26-29 as SPI.
The supplied documentation does not reconcile this strap/mode discrepancy;
do not assume R38 is populated or that the drawn circuit establishes the
actual boot level. The schematic does not document DS RAW packets or explain
the repeatable startup records in the existing capture.

The RD-03D's external UART connects to MCU PA1/pin 27 (`UART_TX`) and
PA0/pin 28 (`UART_RX`); it is separate from these internal interfaces.
Printed p. 9, Table 5 gives the external four-pin connector order as
5V, GND, TX, RX. The page 8 board illustration is explicitly a rendering
for reference, rather than physical proof of a particular board revision.

## MCU identification: AC695N / likely AC6956C

**High-confidence candidate from the pinout: JieLi AC6956C (QFN32).** The
[cached JieLi datasheet V1.1](datasheets/JieLi_AC6956C_Datasheet_V1.1.pdf),
dated 2020-03-19, matches U2's pin names and numbers across all 32 package
pins. See PDF p. 4, Figure 1-1, and PDF pp. 5-7, Table 1-1. In particular:

| Connection | Matching MCU pins |
| --- | --- |
| First radar data / clock | PB2/13 and PB0/15 |
| Second radar data / clock | PB8/8 and PB9/7 |
| Radar I2C SDA / SCL | PC5/19 and PC4/20 |
| USB DM / DP | 23 / 24 |
| UART-connected GPIOs | PA1/27 and PA0/28 |

The datasheet calls the SPI alternate functions **SPI1/SPI2**; the RD-03D
net labels call the two paths **SPI0/SPI1**. Keep package pins and net names
as the reference rather than equating those interface numbers.
Its UART1C function table assigns PA1 to RX and PA0 to TX, opposite the
RD-03D's `UART_TX`/`UART_RX` net names. The official BR23 SDK's `uart_dev_open`
supports arbitrary GPIO remapping, so the schematic routing is implementable.
The stock LD2450 firmware's routing has not been captured; the firmware project
defaults to PA1 TX / PA0 RX and permits swapping after probing.

JieLi's [official bootloader repository](https://github.com/Jieli-Tech/fw-Bootloader)
groups **AC695N / AC695X / AC635N** under **br23**. AC695N is the working
family identification; AC6956C is the likely concrete part, pending readable
device markings. The JL logo alone identifies a vendor, not an exact model.

### SDK mapping and firmware foundation

The [firmware project](../firmware/README.md) pins the official
[AC695N SDK](https://gitlab.zh-jieli.com/soundbox/novisualization/ac695n_soundbox_sdk)
at commit `641e45dff1a8dc455fc6ccd688236fa59688b9ee` (release 3.1.2).
Its BR23 drivers confirm SPI1 group A on PB2/PB0 and SPI2 group A on PB8/PB9;
hardware I2C group B is PC4 SCL / PC5 SDA. The stock SPI driver samples on the
falling edge and configures unused output pins including PB1, so the firmware
uses direct register initialization for mode 0 and keeps PB1/RESET as input.
SPI1/SPI2 expose no slave CS GPIO mapping in that driver. CS is observed
separately; hardware acquisition and alignment still need bench validation.

The startup hook initializes known peripherals while leaving radar power off
and reports that a configuration capture is required. The MCU crystal value
is absent from the schematic; the vendor demo's 24 MHz setting is unverified
for this board. See the [next capture plan](../firmware/docs/CAPTURE_PLAN.md)
and [SDK provenance](../firmware/sdk.lock.json).

The recovered register profiles now feed a configurable staged I2C writer.
Both the baseline and a single-bit experiment compiled as PI32V2/r3 SDK
components using the official project-local toolchain on 2026-10-04. A
complete bootable application and board loading path remain to be integrated;
see the [register experiment workflow](../firmware/docs/REGISTER_EXPERIMENTS.md).

## Observed DS RAW format

The applicable packet reference is **Rev. 1.6, Table 8-8**. The older Rev. 1.3
PDF provides the pinout and interface topology but does not contain this DS RAW
packet table. [Rev. 1.6 datasheet](https://www.scribd.com/document/932226790/ICLegend-S5KM312CL-24Ghz-mmWave-Sensor-for-RD-03-Radar-Module-Datasheet).

Steady output uses a four-byte header followed by 512 complex pairs and a
four-byte trailer: 2,056 bytes total. Header and body/trailer occupy separate
chip-select transactions in these captures. Words are big-endian; each pair
is signed int16 I followed by signed int16 Q.

For header word `h`, the decoder uses:

```python
marker = h >> 24                   # 0xAA
rx_index = (h >> 22) & 3           # 0 = RX1, 1 = RX2
data_type = (h >> 20) & 3          # 2 = DS RAW
chirp = (h >> 11) & 0x1FF
raw_count = h & 0x7FF              # empirical count mask
complex_pairs = raw_count - 1
```

The printed count field is nine bits, inconsistent with the observed
`0x201 = 513` body words. The captures establish use of bit 9. The low-11-bit
mask is an empirical implementation choice; use of bit 10 is unconfirmed.

The verified checksum is `sum(unsigned 16-bit payload words) & 0xFFFF`, excluding
header and trailer. It occupies the trailer's upper half. The lower half is
`(rx_index << 14) | 0x2000 | ((chirp & 0xF) << 8) | 0x55`.

Example from the first steady power-up packet: `AA600201` identifies RX2,
chirp 0, 512 pairs. `F7FA0B61` decodes to I = -2054, Q = 2913.
The trailer is `07E66055`, with validated checksum `0x07E6`.

## Repeatable startup records

The power-up capture has 31 `AA600101` records containing 248 pairs each,
without a matching normal DS RAW trailer; the header count indicates 256
pairs. The final record has 256 pairs and valid trailer `F1DA6055`.
The user reports the same sequence on every boot. Its purpose and the reason
for the count difference are unconfirmed; capture loss has not been established.

The extension decodes all 7,944 captured pairs. It labels the first 7,688
**STARTUP / NO TRAILER**, with checksum validation unavailable. The final
256 pass validation. This preserves the measured data without treating the
startup records as verified normal packets. The datasheet's configuration-time
output caveat does not explain this particular sequence.

## Datasheets and further references

- [Cached JieLi AC6956C Datasheet V1.1](datasheets/JieLi_AC6956C_Datasheet_V1.1.pdf),
  dated 2020-03-19. Package pinout: PDF p. 4; pin functions: PDF pp. 5-7.
  Manufacturer-authored document hosted by Yunthinker; its hash and URL are
  recorded in the provenance manifest.
- [Cached Ai-Thinker RD-03D Specification V1.0.0](datasheets/Ai-Thinker_RD-03D_Specification_V1.0.0.pdf),
  first-edition date 2023-08-31. Chip identification: printed p. 4;
  module connector: p. 9; internal schematic: p. 10, Figure 6.
  Supplied by the user as `20231016032622_13559.pdf`; the cached copy preserves
  the attachment bytes. This describes the RD-03D, not an explicitly named
  HLK-LD2450 board.
- [Cached S5KM312CL Rev. 1.3 PDF](datasheets/S5KM312CL_Rev.1.3_20221109.pdf),
  dated 2022-11-09. Pinout: printed pp. 4–6; configuration: section 8.1;
  data-output SPI: section 8.2.1.
  [Original distributor-hosted PDF](https://www.edworks.co.kr/wp-content/uploads/2023/10/S5KM312CL_Rev.1.3_20221109.pdf).
- [S5KM312CL Rev. 1.6](https://www.scribd.com/document/932226790/ICLegend-S5KM312CL-24Ghz-mmWave-Sensor-for-RD-03-Radar-Module-Datasheet),
  cover dated 2025-02-14, manufacturer-authored copy hosted on Scribd.
  DS RAW format: Table 8-8. **External link only; no local Rev. 1.6 PDF saved.**
- [EVBKS5 reference schematic](https://edworks.co.kr/wp-content/uploads/2023/12/EVBKS5_Schematics_20220705.pdf),
  particularly sheets 2–3 for the separate control and data paths.
- [EVBKS5 user manual](https://edworks.co.kr/wp-content/uploads/2023/12/EVBKS5-User-Manual_Rev.1.0_20231207.pdf).
- [Manufacturer EVBKS5 resources](https://www.iclegend.com/en/product/EVBKS5/).
  Resource availability and download permissions can change.
- Further documentation lead: **RM10003, S5KM312CL Technical Reference Manual**.
  No public copy was found during the original investigation. A complete
  register map and driver/example firmware remain useful missing references.

The cached PDFs' source provenance, revisions, file sizes, and SHA-256 hashes are recorded in
[datasheet provenance](datasheets/sources.json). The existing
[HLK-LD2450 module datasheet](hlk_ld2450_datasheet.pdf) and
[module serial-protocol document](hlk_ld2450_serial_communication.pdf) describe
the module, rather than serving as the radar-chip datasheet.

## Local evidence and tools

- Original inputs: `radar_powerup.csv`, `radar_moving_reflector.csv`, and
  `radar_moving_reflector_side.csv` at the project root.
- [Detailed SPI findings](../output/spi_analysis/decoding_notes.txt) and
  [analysis summary with input hashes](../output/spi_analysis/summary.json).
- [Saleae extension and setup](../saleae_ld2450/README.md).
- [Offline HLA validation](../output/saleae_ld2450/validation.json),
  [boot validation](../output/saleae_ld2450/boot_validation.json), and
  [decoded boot I/Q](../output/saleae_ld2450/boot_iq.csv).

Recorded validation is offline decoding/replay. The user has loaded the local
extension; automated loading/rendering inside Logic 2 and a physical PCB
pin-to-net audit have not been performed.
