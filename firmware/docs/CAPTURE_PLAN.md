# Captures for the next firmware increments

Use the [RD-03D-derived working pin map](../../docs/radar_ic_and_internal_interfaces.md).
The existing captures establish RX2 framing; they do not record the stock
radar configuration sequence or simultaneous RX1 data.
Static firmware analysis has since recovered both ordered 80-write profiles
and the likely wire encoding; see the
[register experiment workflow](REGISTER_EXPERIMENTS.md). The capture now
checks the active profile, saved/runtime changes, ACKs, and physical timing.

## First priority: stock boot configuration

Capture PC4/SCL and PC5/SDA from before power-up through the boot data block
and several steady frames. Decode I2C and retain the raw digital recording as
well as exported transaction bytes, addresses, direction, ACK/NACK, and times.
The stock binary's writer supports seven-bit address `0x20`, an eight-bit
register, and a 16-bit value sent MSB first. Verify these against the capture,
including transaction spacing and the 75-write/SPI-setup/5-write boundary.
Readback behavior has not been established.

Capture PC2/PW_CTL and PC3/REXT_CTL alongside the bus if channels permit.
Their polarity is known from the schematic; the actual ordering and delays
will establish the replacement firmware's automatic startup sequence.

## Second priority: simultaneous radar receivers

| Signal | MCU endpoint |
| --- | --- |
| RX1 data | PB2 |
| RX2 data | PB8 |
| Shared radar SCLK | PB0 and PB9 through separate resistors |
| Shared radar CS | PB3 and PB11 through separate resistors |

Record both data lines against the same clock/CS and retain timestamps across
boot and steady acquisition. Decode mode 0, MSB first. Verify header receiver
IDs, chirp counters, word alignment, whether both lanes share exact boundaries,
and whether the repeatable short boot records occur on both lanes. Headers and
payloads can occupy separate CS intervals; do not discard parser state at CS.

The nominal chip output rate is 16.67 Mbit/s. Use enough analyzer sample rate
to establish edges reliably, and record the acquisition/decoder settings.
Physical validation must check whether SPI1/SPI2 sample correctly with CS as a
separate GPIO and how much time is available to rearm DMA between blocks.

## Later increments

- Record stock debug TX on PA9 and external UART PA1/PA0 to confirm routing,
  baud, startup diagnostics, and output timing.
- Pair simultaneous raw I/Q with stock UART targets and known target motion
  to investigate receiver phase, range/Doppler processing, and bearing.
- Establish MCU oscillator, SDK clock/flash settings, bootloader entry, and a
  recoverable programming method before a complete image is deployed.

For every recording retain the original file, SHA-256, hardware/firmware
revision if readable, analyzer settings, channel-to-pin mapping, and any power
or reset events. Exported bytes complement the raw recording. New findings
belong in the hardware reference and DECISIONS.md when they change the map or
firmware behavior.
