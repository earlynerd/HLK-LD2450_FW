# Register-derived beat-frequency estimate

This is a candidate absolute scale, not RF calibration. It builds on
`output/evb1122_analysis/register_write_table.md` and the EVB1122 repository
snapshot `86b10850e55f5287a27018768c24b88345463bb3`.

## Reference-project numerical checks

In `Middleware/common/src/banyan_param.c`, `InitRegList_ABD` contains:

- Start-frequency pair 53/54: `0x500CCCCD`.
- Rising duration 47/48, masking the upper mode nibble: 6000 counts.
- Rising step 55/56: 2144.
- Falling duration 49/4A: 5000 counts; signed step 57/58: -2573.

The candidate conversion `q_ICL = 300e6 / 2**24 Hz/code` yields:

- Start: 24.0150000036 GHz.
- Rising excursion: `2144 * 6000 * q_ICL = 230.026245 MHz`.
- Falling excursion: `2573 * 5000 * q_ICL = 230.044127 MHz`.

The manufacturer GUI manual, section 4.1 and parameter table 4-2, gives
24.015 to 24.245 GHz (230 MHz) as its example/default frequencies. These
independent start/excursion matches support this conversion, but the manual
does not explicitly identify that C array as its exported configuration.
The conversion is inferred from matching values, not an exposed PLL formula.

## Transfer to the S5KM312CL profile

The reference MTT profile uses start word `0x50155556`, which under the same
conversion means 24.025 GHz. Our S5 start word `0x0A02AAAB` is approximately
one eighth of that word (rounding differs by two reference-code LSBs).

Hypothesis: S5 uses `q_S5 = 8 * q_ICL = 143.05114746 Hz/code`, and its step
words use that same scale, advancing once per inferred timer count. This
puts the S5 start at 24.025 GHz. The factor of eight and the common scale of
start/step words are NOT directly documented. These are the principal
remaining uncertainties in the absolute range conversion.

Our baseline mode-2 profile has rising step 17 and rising duration 84000
counts. The proposed 200 MHz count clock gives 420 us. Its total 240000
counts predicts 1200 us, independently matching measured SPI chirp spacing
1199.844 us to about 0.013%; the individual RF ramp duration is not measured.

Under these assumptions:

- Sweep bandwidth: 204.277 MHz.
- Sweep slope: 0.486374 MHz/us.
- Nominal effective sample rate: 1.25 MHz; 512-point FFT spacing: 2441.406 Hz.
- Range spacing: 0.7524 m per FFT bin (about 2.47 feet).
- Stationary target at 3 feet: beat magnitude 2966.988 Hz, bin 1.215.
- Stationary target at 6 feet: beat magnitude 5933.976 Hz, bin 2.431.
- Moving the reflector between those resting positions: shift 2966.988 Hz,
  or 1.215 bins. Sign depends on chirp direction and I/Q convention.

Formula: `f_beat = 2 * slope * range / 299792458`.
Calculations are saved in `calculation.json`.

The 16-chirp capture count does not set the range FFT spacing; the 512
samples within each chirp do. The Hann window broadens spectral peaks, and
strong near-zero leakage can obscure these nearby returns. Those effects
could make a one-bin displacement hard to see, but do not prove the cause
of the user's unchanged plot. The prior sweep-step experiment supports the
relative slope interpretation without calibrating the absolute scale.

No firmware or viewer calibration was changed for this estimate. A known
reflector at two measured ranges can validate the predicted 3244.7 Hz/m
beat change and distinguish this candidate from other frequency scalings.
