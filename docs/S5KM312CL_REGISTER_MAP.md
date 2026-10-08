# S5KM312CL register map (HLK-LD2450)

Reverse-engineered register map of the ICLegend S5KM312CL 24 GHz FMCW radar SoC
(1 TX, 2 RX) as used on the Hi-Link HLK-LD2450. No register documentation for
this chip is public; everything here comes from the evidence listed below.
It covers addresses 0x00-0x7F. Status 2026-10-08: reverse engineering is
considered complete for the raw-data (DS RAW) use of the chip.

## Evidence tags

- **V** - vendor EVBKS5 GUI (ICLegend's evaluation-kit software for this chip):
  its register generator and parser, decoded statically from
  `ICLM_DataProcess.dll`, plus its `Radar_Config.ini` and user manual. Details,
  tables and function addresses: [vendor package notes](../output/radar_analysis/evbks5_vendor_package/README.md).
- **S** - the stock LD2450 startup sequence, captured on I2C and recovered from
  firmware: [startup table](../output/evb1122_analysis/register_write_table.md).
- **B** - bench measurement on an LD2450 running this project's firmware, using
  live register writes and the raw sample stream. Sweeps:
  - 2026-10-06: 4 masks per register, written live
    ([sweep](../output/live_radar/register_sweep_20261006.jsonl)).
  - 2026-10-07: all 16 bits of 0x00-0x36 with the sweep generator held and
    restarted ([sweep](../output/live_radar/register_sweep_relatch_20261007.jsonl)).
  - Targeted tests: [tuning log](../output/live_radar/register_tuning_20261007.jsonl),
    [experiments](../output/live_radar/register_experiments_20261006.json).
- **I** - inference from value patterns or neighbouring fields; not confirmed.

"No effect" means a bit flip changed none of the measured raw-stream metrics:
DC offset, AC level, I/Q mirror image, level near bins 4-5, noise floor, and
(2026-10-07 sweep only) near-range chirp-to-chirp noise and frame period. A
register may still matter for an output mode this project does not use.

## Bus and access

- I2C, 7-bit address 0x20. 8-bit register address, 16-bit big-endian data.
- Write: address, register, MSB, LSB.
- Read: register byte, repeated start, two bytes.
- Some registers (the 0x20-0x2F block) read noticeably slower than others.
- The LD2450 writes 80 registers at startup in two stages: 75 writes, then SPI
  receiver setup and the radar's REXT pin, then 5 final writes.

## Operating rules learned on the bench

1. **Waveform and timing registers latch only when the sweep generator
   restarts.** Write 0x40 = 0x4207 (hold), make the changes, then 0x40 = 0x0207
   (run). This applies to 0x02 step bits, 0x42-0x58 and the 0x45/0x46 timing.
   Written while running, these read back the new value but change nothing.
   Analog registers (gain, TX power, trims) and the 0x02 offset apply live.
2. **0x76 must stay 0x0021.** Any +/-1 change silences both receivers.
3. **Out-of-band risk:** 0x47-0x4A (ramp durations), 0x53-0x58 (frequency and
   steps) and 0x59/0x5A directly set the transmitted frequency span. Blind bit
   flips there can sweep outside 24.0-24.25 GHz. 0x6D/0x70 set transmit power.
4. A failed write during the startup sequence (I2C NACK) has been seen once on a
   re-init after an interrupted command; an immediate retry succeeded.

## Key formulas (V, confirmed against S and B)

- **RF frequency:** the synthesizer runs at f_RF / 3.
  - 0x53[15:8] = integer part of f_VCO / 800 MHz; 0x53[7:0]:0x54 = 24-bit fraction.
  - One LSB = 2400 MHz / 2^24 = **143.05 Hz at RF**.
  - Stock 0x0A02AAAB = 24.025 GHz.
- **Sweep steps:** 0x55:0x56 (rise) and 0x57:0x58 (fall) are signed 32-bit, in
  the same 143.05 Hz units per 5 ns tick. Sweep span = step x ramp ticks x 143.05 Hz.
  Stock 17 x 84,000 ticks = 204.3 MHz. Bench range calibration measured
  0.75 m/bin (+/-10%), i.e. about 200 MHz.
- **Times:** 200 counts per us.
  - Each pair's high word = phase-flag nibble << 12 | count[27:16]; the low word = count[15:0].
  - Stock: chirp 1200 us = T0 20 + T1 420 up + T2 420 down + T3 340 stop.
  - Frame = pre 2.2 ms + 64 x 1.2 ms + NOP 10 ms = 89.0 ms, matching the
    measured 88.99 ms.
- **Sampling:** the ADC runs at a fixed 2.5 MS/s.
  - Raw step 1/2/4/8 and raw size 64-1024; the window starts at "offset"
    2.5 MHz counts after the chirp start.
  - The vendor rules are T1 x 2.5 MHz > step x size and T0 x 2.5 MHz < offset.
  - Stock: 512 samples at step 2 = 410 us from 24 us, on the 20-440 us up-ramp.
- **SPI output clock** = 50 MHz / div, div 3..31. Stock div 3 = 16.7 MHz, the
  documented maximum: one 2,056-byte record takes about 985 us.

## Map

The value column gives the LD2450 stock final write. For registers the stock
startup never writes, it gives the readback (marked r). Changes in this
project's current 240 MHz profile are marked †.

| Reg | Stock | Function | Evidence |
|---|---|---|---|
| 0x00 | r 0x1207 | Unknown, possibly an ID or revision word. A write with bit 15 set returned an error. | B, I |
| 0x01 | 0x8222 | Output data type. Bit 1 = DS RAW, bit 2 = range FFT, bit 12 = Doppler FFT, bit 4 = peak list. The vendor writes 0x8222 for raw and 0x8E24 for 1D-FFT; it is 0 while stopped. Bits 0-4 and 15 stop the raw stream. | V, S, B |
| 0x02 | 0x103C | [13:12] raw sample step 1/2/4/8 (codes 0-3); [9:0] sample offset in 2.5 MHz counts from chirp start (stock 60 = 24 us). The offset applies live; the step needs a hold and restart. | V, B |
| 0x03 | r 0x101F | Not written by stock or the vendor. Bits 6-11 corrupt or mute individual paths (mirror image +35 to +38 dB): bit 6 RX2, 7 RX1, 8 RX2-Q, 9 RX2-I, 10 RX1-Q, 11 RX1-I. Other bits: no effect. | B |
| 0x04 | 0x030C | [10:8] raw sample size 64/128/256/512/1024 (codes 0-4); low byte 0x0C (0x1B for 2D peak output). Other sizes change the record length. | V, B |
| 0x05 | 0x0010 | On-chip 1D-FFT output size (1..256). No effect on raw. | V, B |
| 0x06 | 0x0122 | SPI output: with d = div - 1, value = 0x100 \| SPIMerged<<13 \| (d&0x10)<<8 \| max(2, d>>1)<<4 \| (d&0xF). Stock div 3 = 16.7 MHz. Almost any bit flip stops the stream. | V, B |
| 0x07 | 0x01B2 | Written by stock; absent from the vendor configuration file. Unknown. No effect. | S, B |
| 0x08 | 0x001C | Written by stock; absent from the vendor configuration file. Unknown. No effect. | S, B |
| 0x09 | 0x6901 | [11:10] on-chip 1D-FFT size 64/128/256 (0x6101/0x6501/0x6901); bit 15 held during configuration (0xE901 while stopped). | V, S |
| 0x0A | 0x4200 | [15:14] FFT output rate - 1 (1..4); base 0x0200. | V |
| 0x0B | 0xC03C | 0xC000 \| sample offset (copy of 0x02[9:0]). | V |
| 0x0C | r 0xEA5F | Unknown. No effect. | B |
| 0x0D | 0x1000 | On-chip 2D-FFT size << 8. No effect on raw. | V, B |
| 0x0E | 0x4000 | On-chip 2D-FFT rows << 8. Bits 8 and 12 stop the raw stream. | V, B |
| 0x0F | r 0x0000 | Bit 0: about +0.5 dB on RX1-I and RX2-Q. Otherwise unknown. | B |
| 0x10 | r 0x1001 | Reads like 0x47 (up-ramp high word). Probably a status or shadow. No effect. | B, I |
| 0x11 | r 0x0003 | Reads like 0x42 (total-time high word). Probably a status or shadow. No effect. | B, I |
| 0x12-0x13 | r 0x0000 | Unknown. No effect. | B |
| 0x14 | 0x5A03 | 2D peak-detect gate bytes. No effect on raw. | V, B |
| 0x15 | 0x1708 | 2D peak-detect velocity bytes. No effect on raw. | V, B |
| 0x16 | r 0x0300 | Unknown. No effect. | B |
| 0x17 | 0x0210 | 2D peak-detect setting. No effect on raw. | V, B |
| 0x18-0x1F | r 0x0000 | Unknown. No effect. | B |
| 0x20-0x2F | 0x0000 ... 0x15DC | 2D peak thresholds, mantissa11 \| exponent << 11. Slow to read. | V, S, B |
| 0x30-0x3F | r 0x0000 | Unknown. 0x30-0x36: no effect. The vendor SDK names 0x31 bit 10 (header format) and 0x33/0x34 (Doppler ROI counts). | B, I |
| 0x40 | 0x0207 | Run control. Bit 14 = hold the sweep generator (0x4207 = configure or stop, 0x0207 = run). Waveform and timing registers latch on release. | V, S, B |
| 0x41 | 0xC844 | Power control: 0xC844 = automatic low power during frame NOP, 0xC874 = off; 0x0004 while stopped. | V, S |
| 0x42/0x43 | 0x0003/0xA980 | Total chirp time, 240,000 counts = 1200 us. | V, S, B |
| 0x44 | 0x0040 | Chirps per frame, [9:0] (64). | V |
| 0x45/0x46 | 0x0000/0x0FA0 | T0, chirp start-up: 4,000 counts = 20 us (vendor minimum 10 us). Lengthening it moves the sample window (offset counts from T0 start). | V, S, B |
| 0x47/0x48 | 0x1001/0x4820 | T1 up-ramp, flag nibble 1: 84,000 counts = 420 us (vendor minimum 128 us). Sets the sweep span with 0x56. | V, S |
| 0x49/0x4A | 0x2001/0x4820 | T2 down-ramp, flag nibble 2: 420 us (vendor minimum T1/4). | V, S |
| 0x4B/0x4C | 0x0001/0x09A0 | T3 stop: 68,000 counts = 340 us (vendor minimum 60 us). | V, S |
| 0x4D/0x4E | 0x0000/0x0001 | One tick (constant in sawtooth mode). | V |
| 0x4F/0x50 | 0x0006/0xB6C0 | Frame pre-delay: 440,000 counts = 2.2 ms. | V, S |
| 0x51/0x52 | 0x001E/0x8480 | Frame NOP: 2,000,000 counts = 10 ms. | V, S |
| 0x53/0x54 | 0x0A02/0xAAAB † 0x0A00/0x8889 | Start frequency: 24.025 GHz stock, 24.005 GHz in the 240 MHz profile. | V, B |
| 0x55/0x56 | 0x0000/0x0011 † 0x0014 | Rise step: +17 stock (204 MHz), +20 in the profile (240 MHz). Bench: spectrum x1.18. Spans up to 2 GHz verified (needs out-of-band transmission). | V, B |
| 0x57/0x58 | 0xFFFF/0xFFEF † 0xFFEC | Fall step: -17 stock, -20 in the profile. | V, S |
| 0x59/0x5A | 0x0000 | Vendor constant 0 (an additional step word). Excluded from blind tests (frequency risk). | V, I |
| 0x5B/0x5C | 0x0022 | Frame-to-power-down time / 0.64 us (22 us). | V, B |
| 0x5D | 0x1919 | Vendor constant. +1 in either byte: no effect. | V, B |
| 0x5E | 0xFF00 | Vendor constant (cascade related). No effect. | V, B |
| 0x5F | r 0x1005 | Unknown. No effect. | B |
| 0x60 | r 0x019C | Unknown. No effect. | B |
| 0x61-0x64 | 0x0021 | RX baseband common-mode trims ("IVCM" in vendor code), set together per RX gain code: 0x02B5 / 0x0021 / 0x03EF / 0x10EF for codes 0-3. Bench: the low field shifts RX2 I/Q DC by about 450 counts per step (0x61/0x63 I, 0x62/0x64 Q, opposite senses). | V, B |
| 0x65 | r 0x0000 | Per-channel baseband gain, one nibble each: bits 12/8/4/0 = RX1-I / RX2-I / RX1-Q / RX2-Q; +2.6 dB per step. SNR unchanged (noise enters earlier). | B |
| 0x66 | 0x0F00 | RX path enables: 0x0F00 both, 0x0A00 RX1, 0x0500 RX2, 0 off. | V, B |
| 0x67 | 0x1E40 | ADC enables: 0x1E40 both, 0x1840 RX1, 0x0640 RX2, 0x0040 off; 0 while stopped. | V, S, B |
| 0x68 | r 0x0000 | Unknown. No effect. | B |
| 0x69 | r 0x0000 | Bit 12: noise floor +5 to +7 dB. | B |
| 0x6A | r 0x3C41 | Bit 4 or 8: noise floor +5 to +10 dB. | B |
| 0x6B | r 0x6D00 | Unknown. No effect. | B |
| 0x6C | 0x9990 | TX-related constant, fixed for every gain setting. | V, S |
| 0x6D | 0x9580 | TX power, paired with 0x70 (see the TX table below). | V, S, B |
| 0x6E | 0xC3FC | LNA: bit 15 = RX1 enable, bit 14 = RX2 enable. RX gain codes 0/1 = 0xC3FC, 2 = 0xC390, 3 = 0xEBB4 (29.5 / 27.4 / 24.0 / 19.8 dB; stock code 1). | V, S, B |
| 0x6F | r 0x5500 | Unknown. No effect. | B |
| 0x70 | 0x26A0 | TX power, paired with 0x6D. TX off clears bits 13 and 9. | V, S, B |
| 0x71 | r 0x20A1 | Clearing bit 0 stops the stream. | B |
| 0x72 | 0x0653 | TX state: 0x0650 stopped; 0x0653 running (legacy gain path, as the LD2450 uses); 0x0793 running (vendor new gain path). | V, S |
| 0x73-0x75 | r 0x8000/0x0001/0x0004 | Unknown. No effect. | B |
| 0x76 | 0x0021 | Vendor constant. Any +/-1 change silences both receivers. | V, S, B |
| 0x77-0x7F | r 0x0000 | Unknown. No effect. | B |

## Transmit power (0x6D, 0x70)

Vendor table, nominal conducted dBm. The stock LD2450 uses **0x9580/0x26A0 =
5.0 dBm**. Selected entries:

| 0x6D | 0x70 | dBm |
|---|---|---|
| 0x9DC0 | 0x3EA0 | 12.0 (maximum) |
| 0x9580 | 0x2EA0 | 9.0 |
| 0x9B80 | 0x26A0 | 7.0 |
| 0x9580 | 0x26A0 | **5.0 (stock)** |
| 0x9980 | 0x22A0 | 3.0 |
| 0x9580 | 0x22A0 | 1.0 |
| 0x9740 | 0x26A0 | -2.0 (minimum) |

The full 35-entry table is in the vendor package notes.

On the bench, the 1 to 12 dBm settings changed received levels by only about
4.5 dB. Near-range chirp-to-chirp noise rose almost one-for-one with them, so
SNR at maximum improved by only +1.6 / +0.3 dB (RX1 / RX2) over stock. Radiated
power depends on the unmeasured antenna gain. In the US, Part 15.249 limits this
band to 250 mV/m at 3 m (about +12.7 dBm EIRP, average).

## Receive gain

The vendor RX gain code sets 0x61-0x64 and 0x6E together:

| Code | Gain | 0x61-0x64 | 0x6E | Input saturation |
|---|---|---|---|---|
| 0 | 29.5 dB | 0x02B5 | 0xC3FC | -27.5 dBm |
| 1 | 27.4 dB | 0x0021 | 0xC3FC | -24.5 dBm |
| 2 | 24.0 dB | 0x03EF | 0xC390 | -22.0 dBm |
| 3 | 19.8 dB | 0x10EF | 0xEBB4 | -17.0 dBm |

The stock LD2450 uses code 1.

## Start and stop sequences (V, consistent with S)

- **Stop:** 0x40=0x4207, 0x41=0x0004, 0x09=0xE901, 0x01=0x0000, 0x67=0x0000, 0x72=0x0650.
- **Start** (after configuration): 0x72 = TX on, 0x67 = ADC enables, 0x01 = output
  type, 0x41 = power mode, 0x40 = 0x0207.
- The LD2450 places SPI receiver setup and the REXT pin between its 75th and
  76th writes.
