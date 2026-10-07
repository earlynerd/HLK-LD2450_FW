# Live radar viewer

A local browser workspace for the custom firmware's validated LDF1 feed. It
shows both receivers' I/Q waveforms and spectra, spectral history, an exploratory
within-frame Doppler map, and transport/processing health. It does not require a
firmware change or a web service. Dependencies are NumPy and pyserial; the UI
uses browser Canvas with no package build or external assets.

## Start

From the repository root on this computer:

```powershell
.\tools\start_radar_viewer.ps1
```

The launcher reuses an existing viewer, or starts one hidden and opens
http://127.0.0.1:8765. Its logs and PID are in `output/live_radar/`. Closing the
browser does not stop acquisition: use **Disconnect** to release the USB port.
For a foreground server with Ctrl+C shutdown:

```powershell
C:\ProgramData\miniconda3\python.exe tools/live_radar.py --connect
```

On another Python environment, install `tools/radar_viewer/requirements.txt`.
For offline use, omit `--connect` and choose a recording in the UI, or use:

```powershell
python tools/live_radar.py --replay output/stream_bench/usb_budget_guard_capture/stream.ldf
```

Only one process can own native USB COM30. The viewer discovers the matching
VID/PID/serial identity (`4c4a:4155`, `LD2450-STREAM-01`) and asserts DTR. It never
opens debug/updater UART ports or flashes firmware. It sends radar register
commands only when you use the Radar registers panel.
An unplug or serial error stops the source and surfaces the error. Reconnect
explicitly once the device is available. The server binds only to loopback;
mutating requests also require a per-process token and a matching browser origin.
An open page refreshes its token and retries once if the server was restarted.

## Explore

- **Complex waveform:** choose a chirp or the mean of all captured chirps. The
  slider and mean adapt to the declared 16- or 64-chirp export. Both I and Q
  from both receivers are shown. DC removal follows the frame's processing
  setting; background subtraction does not alter this source-data plot.
- **Frame spectrum:** 512-point complex FFT, normalized by the window sum, RMS
  spectral amplitude across chirps, in dB relative to one exported sample count.
  Hann/rectangular and per-chirp complex DC removal are selectable.
- **Spectrum / history span:** defaults to bins -16 through +16 so low-frequency
  detail is visible. Select positive bins 0 through +32 or the full -256 through
  +255 spectrum as needed. This crops the plotted bins only: no samples, FFT
  coefficients, history, or raw recording data are discarded. It does not
  improve FFT resolution or calibrate distance. The fixed outer features remain
  accessible in Full view.
- **Spectrum history:** the last 160 spectra displayed in this browser. Newest
  at the bottom. The default **Change from running average** mode shows the RMS
  deviation of each frame's complex spectrum from an exponential average of
  previous frames (weight 0.1 per processed frame, so about 10 frames of memory).
  Static leakage and clutter dominate the absolute magnitude spectrum while
  motion mostly changes phase, so this mode is where movement is visible.
  The average restarts on configuration, setting or background changes.
  **Absolute spectrum** shows the original magnitude history. Rows are displayed frames, not a uniform time axis: firmware
  intentionally skips export frames, and browser refresh can skip views too.
- **Constellation:** I versus Q on equal axes for both receivers. **FFT bin
  over time** plots the complex value of one signed bin (-64 to +64) for every
  chirp of the last 40 displayed frames, older frames faded; it uses the
  frame's window and DC settings but not background subtraction. A static
  reflector stays a tight cluster; motion at that bin appears as rotation or an
  arc. Changing the bin restarts the trail. **Raw samples** plots the selected
  chirp's (or mean) 512 exported samples, exposing DC offset, I/Q imbalance or
  clipping. The axis range grows immediately to keep every point visible and
  shrinks by 4% per new frame (roughly 3 s to halve), restarting on a mode or
  bin change.
- **I/Q correction:** **Calibrate I/Q** fits each receiver's Q-versus-I gain
  and phase error from the latest frame, assuming a static scene with a strong
  reflector: a mismatch puts a conjugated copy of each positive-frequency
  component at the matching negative frequency, X(-k) = alpha * conj(X(k)), and
  alpha = (1 - u) / (1 + u) with u = g * exp(-j*phi). It then applies
  Q_ideal = (Q/g - I*sin(phi)) / cos(phi) to every frame before DC/trend removal
  and all FFTs. The raw waveform and constellation stay uncorrected. Cleared
  when the settings identity changes (gain registers alter the mismatch).
  Session-local, like the background. The `iq_balance` product reports the
  mirror the model still finds (bins 2-12 of the coherent mean chirp) and how
  much negative-bin energy it fails to explain (fit residual near 1 means what
  remains is not a mirror). Bench 2026-10-06, corner reflector: Q gain
  -2.19 / -0.83 dB and phase -18.2 / -15.1 deg (RX1 / RX2); negative-to-positive
  energy over bins 2-12 fell from -13.7 / -16.9 dB to -28.3 / -33.1 dB. RX1's -4
  bin (-8 dB relative to +4) is unchanged: genuine negative-frequency content
  or drift leakage, not mirror.
- **Linear trend removal:** optional (off by default). Subtracts a least-squares
  straight line from each chirp's complex record before every FFT, and from the
  browser-side waveform and constellation. It removes the large slow drift
  whose leakage otherwise dominates the central bins. It also removes any
  genuine content that is linear across the record.
- **Within-chirp spectrogram:** short-time spectrum along each chirp to test
  whether the 512-sample record is one ramp. 128-sample Hann segments every 16
  samples, zero-padded to 512 points so bins share the frame spectrum's axis
  (true resolution 4 bins), RMS over chirps, signed bins -64 through +64. Rows
  are segment centres, chirp start at the top. A reflector on a single linear
  ramp is a vertical line; segment joins, fold-over or settling appear as
  jumps or slopes. Uses `ctx.signal`, so DC, trend and background settings apply.
  A white trace marks the strongest bin in each row (ignoring |bin| < 2,
  parabolic sub-bin estimate); the legend gives its mean bin, start-to-end
  tilt and scatter. Auto colour shows only the top 40 dB below the 99.9th
  percentile. The trace follows whatever is strongest: with the drift present
  that may be leakage, not a reflector.
  First bench result (2026-10-06 capture `20261006-182335-capture-16da54`):
  each chirp carries a large slow trend; a straight-line fit removes about 96%
  (RX1) / 98% (RX2) of the DC-removed power. Its leakage dominates the central
  bins and gives the near-DC energy a U shape along the record. It is not
  evidence of ramp segmentation.
- **Scaling:** by default the spectrum axis and both heatmaps auto-scale to
  the visible bins (spectrum: range of the displayed history; heatmaps: 2nd to
  99.5th percentile, at least 10 dB). In a fully static scene this stretches
  noise across the palette. Untick auto-scale for separate manual waterfall
  and Doppler colour ranges.
- **Doppler:** 16- or 64-chirp Hann FFT across fast-time bins -64 through +64. Optional
  static removal subtracts the within-frame mean complex spectrum before the
  slow-time FFT. Frequency uses the median reported chirp interval (typically
  1200 us: about 52.1 Hz/bin for 16 chirps, or 13.0 Hz/bin for 64).
  Timing outliers are reported, not silently repaired.
- **Background:** capture the mean complex waveform of the latest acquired
  frame for each receiver, then subtract it before spectrum/Doppler processing.
  Source changes, configuration changes and replay loops clear the reference.
  The capture is session-local. It is not saved as a calibration.
- **Freeze display:** continues reading, decoding and optional recording while
  holding the displayed frame. Chirp/receiver/heatmap controls still work.
  Resume starts a fresh history. Processing changes apply to newly processed
  frames, not the frozen view. **Save latest acquired frame** and **Capture
  background** always act on the current acquisition, even when display is frozen.
- **Raw recording:** retains original wire bytes plus a SHA-256 manifest in a
  new `output/live_radar/*-capture-*` folder. Stops at 1 GiB or disconnect. Starts
  and ends can be mid-frame; replay resynchronizes and only publishes complete
  frames. Refresh the recording list after creating captures in another client.
- **Save latest acquired frame:** exports two exact validated lane binaries and
  their hash manifest, source and processing settings, to a new snapshot folder.
  It does not modify the frame in memory. The raw data is retained unchanged.

Recordings loop at approximately their original timestamp spacing, with very
long gaps capped at two seconds. Known capture directories are listed; an
arbitrary file can be supplied on the trusted command line with `--replay`.
Older diagnostic captures named `raw` may contain synthetic benchmark data;
their configuration identities and source names remain visible.

## Radar registers

Live I2C access to the radar chip's registers through the native USB port
(LDC1 commands, see `firmware/docs/FRAME_STREAM.md`). It needs register-control
firmware; with older images commands go unanswered and the panel says so.

- Commands are sent one at a time (the SDK's USB receive routine cannot take
  bursts) and each register is read in a separate inter-frame gap, because some
  registers read slowly. A full 0x00-0x7F dump takes about 4 s. READ/WRITE are
  retried if a reply is missing; the log shows attempts (normally 1).
- **Read 0x00–0x7F** dumps the first 128 addresses in 8-register READs.
  **Read stock-written** reads only the registers the startup table writes.
  Any address and value can be read or written from the row editors or the
  Reg/Value fields. Nothing is blocked or range-limited.
- **Stock** is the final value the recovered mode-2 startup table writes
  (`*` marks registers written more than once; hover for all writes).
  **Working interpretation** is the analysis label from
  `output/evb1122_analysis/register_write_table.json`, not documentation.
  **Bench:** lines come from `tools/radar_viewer/register_findings.json`,
  a hand-edited file of measured effects (evidence files in `output/live_radar/`);
  it also adds rows for registers the stock table never writes. Restart the
  viewer server after editing it.
  Current values differing from stock are highlighted.
- **Re-init radar** stops acquisition, power-cycles the radar and re-applies the
  build profile. Use it to return to stock or recover a radar a write has
  stopped.
- Writes are applied between radar frames. Each WRITE and REINIT advances the
  register generation carried in every frame's BEGIN. The viewer treats build
  configuration plus generation as the settings identity, so history, the
  change average and any background reference restart after a write. Raw
  recordings contain every REPLY, so the register operations behind a
  recording can be reconstructed from it.

## Interpretation limits

FFT bin is not distance. Full-record FFTs may combine multiple ramp segments;
sample rate, chirp slope and sample-to-ramp alignment still need calibration.
The Doppler map is exploratory, not a calibrated range/velocity map. Neither
receiver phase nor an amplitude peak is reported as bearing or an identified
target. The spectra are not dBm measurements.

The 2026-10-06 sampling/slope experiment confirms that the prominent outer
features must not be treated as range peaks. Changing only inferred RAW
sampling interval 2 to 1 moved the largest pair from about +/-219 to +/-110;
restoring sampling and reducing sweep step 17 to 8 left it near +/-219. The
central spectral structure contracted under both changes. All four comparison
captures (including return to baseline) decoded without explicit ABORTs or
protocol errors. Original stock-firmware logic-analyzer captures also contain
mirrored outer features. Their electrical origin is not proven; the roughly
535 kHz estimate, assuming the datasheet's 2.5 MHz ADC rate and 2:1 sampling,
is consistent with the specified 400-650 kHz internal converter range.
The baseline firmware was restored after both diagnostic images. Data and
plots: `output/radar_analysis/spur_four_way_comparison/`; experiment profiles
are explicitly named diagnostics under `firmware/config/`. Exact sweep/sample
alignment, calibrated distance, and identification of individual range peaks
remain separate validation work.

Within-frame variation is RMS residual after subtracting the frame's mean
DC-centered waveform, divided by the DC-centered RMS amplitude. It includes
noise, drift and motion; it is not target SNR. ADC saturation cannot be ruled
out just because the exported int16 samples do not reach the numerical rails.

Health counters distinguish host parser/protocol failures, rejected complete
frame candidates, firmware skips/rejections (cumulative since boot), and dropped
display-processing work. **Rejected exports** includes deliberate firmware
ABORT messages; **Buffer-full aborts** (reason 3) and **CPU-guard aborts** (reason
6) identify their causes. **Invalid / incomplete** excludes explicit ABORTs.
Device totals update from validated BEGIN messages even when candidates abort;
wire throughput remains visible when there are no completed frames. The badge
shows **EXPORT LIMITED** when recent firmware aborts prevent fresh frames.
Parser counters include initial resynchronization:
the previously observed 64-byte USB prefix on reconnect can increment them
without invalidating a subsequently accepted frame. Export skips are expected.
Timing outliers count intervals more than 10% from the frame median, separately
for both lanes; these are timestamp observations, not proven physical jitter.
During looping replay, parser/protocol/rejected-candidate counters describe the
current pass; byte/frame totals span all passes. Connecting a source resets the
host counters.

The 2026-10-06 motion demonstration confirmed a firmware export limitation:
305 completed frames, 71 CPU-guard aborts, 53 output-buffer aborts, and one
additional resynchronization rejection in the recorded interval. Clear reason
counters diagnose this; they do not resolve the firmware's motion-dependent
compression/queue/CPU limits of that 64-chirp image. Evidence is in
`output/live_radar/20261006-173642-capture-3fc19b/analysis.json`.

The subsequent raw 16-chirp firmware exports chirps 0-15 from both receivers,
with all 512 complex samples per chirp. Its complete 67,100-byte wire export fits
the existing producer queue without compression or concurrent USB draining.
The radar still produces 64 physical chirps; exports deliberately cover only the
first 16, and whole physical frames can be skipped while USB output drains.
See `firmware/docs/FRAME_STREAM.md` for the installed image and bench evidence.

## Extend processing

The integrity boundary is the existing `firmware/tools/frame_stream.py` decoder.
Only its complete, checksum/CRC-validated, paired 16- or 64-chirp export is published.
The viewer neither weakens checks nor introduces another wire decoder.

`tools/radar_viewer/server.py` separates USB reading, frame decoding, and DSP:

1. USB reader feeds a bounded 4 MiB byte queue; recording keeps the original
   bytes. Overflow stops with a visible error instead of dropping hidden bytes.
2. Decoder produces verified frames. The one-frame processing queue replaces an
   older pending display frame if necessary; the drop is counted independently
   of device export loss. Recording remains independent of display work.
3. `processing.Pipeline` unpacks `(receiver, chirp, sample, I/Q)` and constructs
   `FrameContext`. Its named `stages` mapping publishes JSON-compatible products.
   Stage exceptions appear as named errors; other stages can still render.
4. The browser polls the latest result. Slow/frozen/closed browsers never block
   acquisition. It retains only one frame plus 160 displayed spectra. Settings
   and configuration generations prevent combining different processing modes
   in the same waterfall history.

To add a range estimator, phase/coherence stage, motion detector or angle solver:
implement a function taking `FrameContext`, add it to `Pipeline.stages`, and add
a corresponding plot in `web/app.js` / `web/index.html`. Retain units and
calibration identity with each new product. Use `ctx.raw` for unchanged complex
samples, `ctx.signal` for optional DC/background removal, or `ctx.spectra` for
the normalized fast-time FFT. Stage execution must stay bounded; heavy work can
drop display frames but must not alter the acquisition integrity contract.

Tests from the repository root:

```powershell
python -m unittest discover -s tools -p test_viewer.py -v
```

Tests cover complex FFT sign/amplitude, Doppler frequency, timestamp rollover,
background/config changes, static rejection, stage-failure isolation, endian
roundtrip, corruption recovery, bounded display backlog, port identity,
recording hashes, replay/snapshot lifecycle, and local HTTP control protection.
