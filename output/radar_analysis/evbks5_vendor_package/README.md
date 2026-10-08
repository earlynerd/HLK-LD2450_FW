# EVBKS5 vendor GUI package: register evidence

Source: `20230524-EVBKS5-Waveform-Config-and-Demo.zip` (project root, supplied by
the user 2026-10-07), SHA-256
`5aaed93dd90de1bd89cb36077a6c2e9ec4bb39a0b147374f35a71942cb4b4539`.
ICLegend's evaluation-kit GUI for the S5KM312CL ("EVBKS5"), the radar SoC on the
LD2450. Evidence comes from its `Radar_Config.ini` files, English user manual
(Rev 1.1, 2022-11-29) and static disassembly of the root `ICLM_DataProcess.dll`
(x64; addresses below are RVAs). Nothing from the package was executed; the
DLL was read as bytes with pefile/capstone. Vendor dBm/dB figures are the
vendor's own, not measurements.

## Transmit power: stock LD2450 is about 5 dBm

`GetTXGainConfig` (0x8EE10) indexes three tables of 16-byte entries
`{u16 reg6D; u16 reg70; u32 pad; double dBm}` written to registers 0x6D and
0x70 (`GenerateAnalogRegisterItemList`, 0x90F50). 0x6C is a fixed 0x9990.
TXOFF clears 0x70 bits 13 and 9 (AND 0xDDFF).

| Level (ini name) | Code: 0x6D / 0x70 -> dBm |
|---|---|
| Professional (0) | 0: 9DC0/3EA0 12.0, 1: 9FC0/36A0 11.8, 2: 99C0/32A0 11.6, 3: 97C0/2EA0 11.4, 4: 97C0/2AA0 11.2, 5: 93C0/2AA0 11.0, 6: 97C0/26A0 10.8, 7: 9FC0/22A0 10.6, 8: 9BC0/22A0 10.4, 9: 99C0/22A0 10.2, 10: 97C0/22A0 10.0, 11: 9780/2EA0 9.5, 12: 9580/2EA0 9.0 |
| Recommended (1) | 0: 9980/2AA0 8.5, 1: 9780/2AA0 8.0, 2: 9F80/26A0 7.5, 3: 9B80/26A0 7.0, 4: 9380/2AA0 6.5, 5: 9980/26A0 6.0, 6: 9780/26A0 5.5, **7: 9580/26A0 5.0**, 8: 9F80/22A0 4.5, 9: 9D40/2EA0 4.0, 10: 9B40/2EA0 3.5, 11: 9980/22A0 3.0 |
| Special (2) | 0: 9180/26A0 2.5, 1: 9540/2EA0 2.0, 2: 9B40/2AA0 1.5, 3: 9580/22A0 1.0, 4: 9740/2AA0 0.5, 5: 9540/2AA0 0.0, 6: 9D40/26A0 -0.5, 7: 9B40/26A0 -1.0, 8: 9940/26A0 -1.5, 9: 9740/26A0 -2.0 |

The stock LD2450 writes 0x6D=0x9580 and 0x70=0x26A0 (`../../../../radar_i2c.csv`
around line 256-264, and the recovered startup table), which is Recommended
code 7: **5.0 dBm conducted**. The chip maximum in these tables is 12.0 dBm. 0x6D
alone does not identify the power; 9580 appears at 9.0, 5.0 and 1.0 dBm with
different 0x70 values. The manual's older five-level description (LV1..LV5 about
11, 9, 7, 5, 3 dBm) is consistent. Antenna gain, and therefore EIRP, is unknown.

## Receive gain: stock is code 1 (27.4 dB)

`GetRXGainConfig` (0x8EE80), 40-byte entries
`{u16 r61, r62, r63, r64, r6E; pad; double gain_dB; double d18; double sat_dBm}`:

| Code | 0x61-0x64 | 0x6E | Gain dB | +0x18 (likely NF) | Input saturation dBm |
|---|---|---|---|---|---|
| 0 | 02B5 | C3FC | 29.52 | 10.08 | -27.5 |
| **1** | **0021** | **C3FC** | **27.43** | 11.07 | -24.5 |
| 2 | 03EF | C390 | 23.96 | 15.24 | -22.0 |
| 3 | 10EF | EBB4 | 19.82 | 18.98 | -17.0 |

The GUI computes minimum TX-RX isolation as TX dBm - saturation + 2 dB.
RxType masks 0x6E (RX1 &0xBFFF, RX2 &0x7FFF, off &0x3FFF); 0x66 = 0xF00 all,
0xA00 RX1, 0x500 RX2, 0 off.

## Data, timing and frequency fields (generator and parser agree)

- **0x06 SPI clock:** SPI clock = 50 MHz / SPIClockDiv, div 3..31 (ini). With
  d = div - 1: `0x06 = 0x100 | SPIMerged<<13 | (d&0x10)<<8 | max(2, d>>1)<<4 | (d&0xF)`;
  parser div = (v&0xF) + ((v>>8)&0x10) + 1. Stock 0x0122 = div 3 = 16.7 MHz, the
  fastest documented setting and the rate measured on the logic analyzer.
- **0x02:** bits 13:12 raw sample step (1, 2, 4, 8 -> 0..3); bits 9:0 sample
  offset (2.5 MHz counts from chirp start). **0x0B** = 0xC000 | offset.
- **0x04:** bits 10:8 raw sample size (64, 128, 256, 512, 1024 -> 0..4); low byte 0x0C.
  The vendor example uses 256 samples at step 4: the same 410 us window as
  the LD2450's 512 at step 2, with half the data.
- **0x44:** chirps per frame (low 10 bits).
- **Timing** (200 counts/us; high word = phase-flag nibble<<12 | count[27:16]):
  0x42/43 total chirp, 0x45/46 start T0, 0x47/48 up-ramp (flag 1), 0x49/4A
  down-ramp (flag 2), 0x4B/4C stop T3, 0x4D/4E one tick, 0x4F/50 frame pre,
  0x51/52 frame NOP; 0x5B/0x5C = frame-to-power-down / 0.64 us.
- **Frequency:** f_RF / 3 synthesized. 0x53[15:8] integer of f_VCO/800 MHz,
  0x53[7:0]:0x54 24-bit fraction; LSB 143.05 Hz at RF (0x0A02AAAB = 24.025 GHz).
  0x55/56 rise and 0x57/58 fall steps are signed 32-bit in the same units per 5 ns tick.
- **Start sequence:** 0x72=0x0793 (new gain path; the LD2450 uses the legacy
  0x0653), 0x67 RX ADC enables, 0x01 data type (0x8222 raw), 0x41 = 0xC844
  low-power or 0xC874, 0x40 = 0x0207. **Stop:** 0x40=0x4207, 0x41=0x0004,
  0x09=0xE901, 0x01=0, 0x67=0, 0x72=0x0650.

The manual recommends 24005-24245 MHz for a 240 MHz sweep, the setting the
bench adopted on 2026-10-07, and gives the chip's chirp range as 22.5-27.5 GHz.
It requires T1 x 2.5 MHz > sample step x sample size and T0 x 2.5 MHz < offset.

Unresolved: individual bit meanings of 0x6D, 0x70 and 0x72; the +0x18 RX field.
Disassembly helper scripts were scratch work and are not retained here.

## Bench check of the TX table (2026-10-08)

Live writes of 0x6D then 0x70 (no sweep-generator hold needed), static office
scene, 20 frames each, stock references before and after agreeing within 0.2 dB.
Evidence: `output/live_radar/register_tuning_20261007.jsonl` (kind `tx_power`).

| Table dBm | Scene bins 2-12, RX1/RX2 dB | Chirp-to-chirp noise bins 8-40 | SNR vs far floor |
|---|---|---|---|
| 1.0 | 37.5 / 42.6 | 48.2 / 49.2 | 39.9 / 45.9 |
| 3.0 | 38.2 / 43.3 | 48.3 / 49.9 | 40.0 / 46.5 |
| 5.0 (stock) | 39.6 / 44.7 | 49.8 / 51.1 | 40.9 / 46.7 |
| 7.0 | 40.0 / 45.1 | 50.4 / 51.7 | 41.6 / 46.7 |
| 9.0 | 40.7 / 45.9 | 51.3 / 52.4 | 41.9 / 47.0 |
| 11.0 | 41.4 / 46.6 | 51.3 / 52.7 | 42.2 / 46.7 |
| 12.0 | 42.0 / 47.2 | 52.4 / 53.9 | 42.5 / 47.0 |

Returns span about 4.5 dB, not the table's 11 dB. Near-range chirp-to-chirp
noise rises almost one-for-one with the return level, so it is transmitter-
correlated (phase noise on leakage/clutter is the likely mechanism, not proven).
Maximum power improves SNR by about 1.6 dB (RX1) and 0.3 dB (RX2) over stock
against far-bin noise, and by roughly nothing against near-range noise. The
radar was restored to stock 5 dBm.
