# Live radar viewer

A local browser workspace for the custom firmware's validated LDF1 feed. It
shows tracked targets in a top view, both receivers' range-bin spectra,
spectral history, a 64-chirp Doppler map, a per-bin constellation, each range
bin's slow-time phase (breathing-scale motion), and transport/processing health. It also controls the radar's registers and sweep
width. It does not require a firmware change or a web service. Dependencies are
NumPy and pyserial; the UI uses browser Canvas with no package build or
external assets.

![The viewer live on 2026-10-08: one confirmed track in the top view, spectra of both receivers, change waterfall, range-Doppler map with detections circled, and the constellation of range bin 4](../resources/Screenshot.png)

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
opens debug/updater UART ports or flashes firmware. On each live connection it
reads the sweep step register (0x56); it writes radar registers only when you
use the Sweep or Radar registers panels.
An unplug or serial error stops the source and surfaces the error. Reconnect
explicitly once the device is available. The server binds only to loopback;
mutating requests also require a per-process token and a matching browser origin.
An open page refreshes its token and retries once if the server was restarted.

## Explore

Since 2026-10-08 the viewer works on **range bins**: the unwindowed, unscaled
512-point FFT bins -40..+40 of each chirp. The installed firmware exports
exactly these (`--fft-bins 40`, LDF1 codec 2, all 64 chirps of every frame).
Older raw recordings are converted to the same bins on the host, so they still
replay. Views that need time samples were removed with the move to range bins:
the complex waveform, the within-chirp spectrogram, linear-trend removal and
the raw-sample constellation. At the 240 MHz sweep a bin is about 0.64 m, so
8 m is about bin 12.

- **Targets (top view):** detections from the range-Doppler map (`targets`
  stage). Cell-averaging CFAR runs on the summed receiver power, with guard and
  training cells, a threshold and a maximum range taken from
  `tools/radar_viewer/calibration.json`. Only positive range bins are searched
  (negative bins hold the I/Q mirror and leakage). The detector keeps local
  maxima, merges cells close in range and Doppler (strongest first, up to
  `max_targets`), and interpolates range and Doppler parabolically.
  - Range: `m_per_bin x bin + offset_m`.
  - Velocity: Doppler Hz x wavelength / 2.
  - Angle: the phase of sum(RX2 x conj(RX1)) over the 3x3 cells around the
    peak, minus `phase_offset_deg`, gives
    sin(theta) = sign x dphi / (2 pi d/lambda). Values beyond +/-1 are clipped
    and marked `?`.
  - Coherence (0-1) is the normalised magnitude of that cross product: low
    values mean the phase is not from one point source.
  - With static removal on, only moving targets appear (Doppler bins
    `|d| < min_doppler_bin` are excluded). Turning it off, after capturing an
    empty-scene background, shows static reflectors too.

- **Clutter map:** a detection must also exceed the long-term average power
  of its range-Doppler cell by `clutter_threshold_db` (10 dB). The average is
  per cell, maximised over +/-1 Doppler bin, with `clutter_tau_s` = 10 s.
  - It removes returns that never go away. Bench case (2026-10-08): with
    nothing moving in view, persistent Doppler lines at multiples of about
    102 Hz sat at 1.2-1.8 m. They were at a fixed range, not locked to the
    chirp timing and not tied to the static return strength, so they come
    from something real but out of view (vibration, an out-of-view fan or
    pickup). Evidence: `output/live_radar/20261008-113257-capture-7cd819`.
  - It starts empty after start-up or a settings change. Persistent returns
    show for the first ~8 s while it learns; the subtitle says so.
  - Range bins near a confirmed, not-in-place track younger than `censor_s`
    (4 s) are not learned, so walkers are not absorbed. The age limit stops a
    track sitting on clutter from protecting its own cells forever.
    Position-based rules failed because clutter tracks jump in angle and
    range.
  - Limits: a person who stays put, or keeps pacing the same path, is
    eventually learned. Walkers whose Doppler lands on a clutter line
    (multiples of about 0.64 m/s at 0.8-2 m here) are hidden there.
  - Check: a simulated walker added to that recording stays tracked in
    94-99% of frames at 0.3 and 1.0 m/s. At 0.6 m/s it falls to about 50%,
    because that speed lands on a clutter line. Once learned, the empty room
    gives no tracks (about 1.2 tracks per frame before).

- **Tracks:** the `tracks` stage follows objects across frames with a
  constant-velocity Kalman filter in x, y (`processing.Tracker`, parameters in
  the `tracking` block of `calibration.json`).
  - Detections within about 0.9 m and 20 deg are one measurement; a person or a
    fan gives several Doppler peaks at one place.
  - A track is confirmed after 3 detections in 5 frames and coasts through
    missed frames for up to 1 s, with its velocity decaying.
  - It is flagged *in place* when its Doppler speed is at least 0.25 m/s but
    its range hardly changes (fans, fidgeting).
  - Comparing Doppler speed with the fitted range rate also checks the
    velocity sign: for a walker they should agree. Measured 2026-10-09
    (four passes towards and away): positive velocity means moving away.
  - Synthetic check: a walker detected in about 60% of frames stays one track
    in every frame after confirmation, and the tracked angle spread is 3.5 deg
    against 5.9 deg per detection.

  Why tracking rather than requiring both receivers to agree (2026-10-08,
  recorded noise from `output/live_radar/20261008-030525-capture-51fbe3` with
  injected targets, equal false-alarm rate):
  - The summed power |RX1|^2 + |RX2|^2 already uses both receivers. It needs
    about 3 dB less signal than RX1 alone.
  - Coherent combining at the best angle, (|RX1| + |RX2|)^2, gives the same
    detection probability.
  - Gating on 3x3 RX1/RX2 coherence lowers detection probability at equal
    false-alarm rate. The Hann windows correlate neighbouring cells, so noise
    already shows coherence about 0.5.
  - Receiver noise is mostly independent (complex correlation 0.26).
  - Noise false alarms are rare in this scene even at 8 dB. Detections there
    come from real reflectors, which both receivers see. So the threshold is
    10 dB (was 13), and tracking supplies the consistency check.

  The top view draws the radar at the bottom centre, 1 m rings and the
  +/-60 deg field of view.
  - Confirmed tracks: 3 s trail, id and a 1 s velocity arrow. Hollow means in
    place; faded means coasting.
  - This frame's detections: small grey dots.
  - Table: per track, range, angle, Doppler speed, range rate, age and state.
  - Quantities whose calibration is marked false are labelled uncalibrated. Initial values (2026-10-08): range scaled from the 204 MHz
  three-point fit; d/lambda = 0.5, offset 0 and both signs assumed. The
  Range-Doppler panel circles the same detections.

  First live use: detections at about 1.3-1.6 m with symmetric Doppler lines at
  +/-104, +/-208 and +/-417 Hz. The same lines are the strongest in the earlier
  raw-firmware recordings, so they come from the room, not the range-bin
  firmware; the pattern is typical of a rotating fan.
- **Frame spectrum:** RMS range-bin amplitude across chirps, normalized by the
  window sum, in dB relative to one exported sample count. Hann/rectangular
  window and per-chirp DC removal are selectable. The Hann window is applied in
  the bin domain (0.5 X[k] - 0.25 X[k-1] - 0.25 X[k+1]), so the displayed bins
  are -39..+39.
- **Spectrum / history span:** defaults to bins -16 through +16. Positive bins
  0 through +32 or all exported bins are selectable. This crops the plotted bins
  only.
- **Spectrum history:** the last 160 spectra displayed in this browser, newest
  at the bottom: about 15 s when the browser draws every frame. The default **Change from running average** mode shows the RMS
  deviation of each frame's complex spectrum from an exponential average of
  previous frames (weight 0.1 per processed frame, about 10 frames of memory).
  Static leakage and clutter dominate the absolute magnitude spectrum while
  motion mostly changes phase, so this mode is where movement is visible.
  The average restarts on configuration, setting or background changes.
  **Absolute spectrum** shows the magnitude history. Rows are displayed frames,
  not a uniform time axis. A change of bin range (for example after reflashing)
  restarts the history.
- **Constellation:** the complex value of one signed range bin for every chirp
  of the last 40 displayed frames, older frames faded. Background, I/Q
  correction, DC and window settings apply. A static reflector stays a tight
  cluster; motion at that bin appears as rotation or an arc. Changing the bin
  restarts the trail. The axis range grows immediately to keep every point
  visible and shrinks by 4% per new frame.
- **Slow-time phase:** each range bin's value, averaged over the frame's
  chirps, followed from frame to frame over the last 20 s (stage `phase`, range
  bins 1 to `max_range_m`). A displacement d turns a bin's phase by
  4 pi d / wavelength, about 58 deg per mm, long before the object moves
  far enough to leave Doppler bin 0. So breathing and heartbeat are visible here
  while the range-Doppler map, static removal and the clutter map discard them.
  The history is a strip chart. Each frame's sample is computed once, when the
  frame arrives, and never revised, so the past does not change on screen. The
  two receivers are added after turning RX2 onto RX1 by a running average
  (5 s) of their cross product. Spectra resample the window to 10 Hz, since
  frames arrive at about 11/s with gaps. Three views:
  - **Slow-time spectrum of each bin** (range bin across, -3 to +3 Hz up): the
    FFT over the 20 s window of the deviation from the bin's mean. Breathing is
    a pair of lines near +/-0.2-0.5 Hz in the bin of a person holding still.
  - **I/Q path** of the selected bin. Motion turns the phasor about the bin's
    static part (walls, leakage, the still parts of the body), not about the
    origin. A circle is refitted to the path every frame and smoothed (2 s);
    its centre (+) is the static part.
  - **Displacement**: each frame adds the phase step from the previous frame,
    measured about the current centre and converted to mm, so unwrapping never
    revisits old samples. Drift is removed by subtracting a 10 s running
    average. The sign is uncalibrated. A short arc gives the right waveform
    shape, but its scale is then uncertain. Steps over 180 deg between frames
    (above about 35 mm/s) alias, so this view is for slow motion.

  The running averages start as plain means, so they settle within seconds of
  a restart. The I/Q and displacement axes stay fixed until the data leaves
  them or fills less than 40% of them. An earlier version recomputed the whole
  window every frame, so the receiver rotation, circle centre, unwrapping and
  trend fit all moved the displayed past.

  **Auto** selects the bin with the most slow-time motion (0.1-3 Hz). It moves
  only when another bin is 3 dB stronger. The text below the plots gives each
  bin's strongest breathing-band (0.1-0.6 Hz) and heart-band (0.8-2.5 Hz) line,
  with its ratio to the band median. These rates mean something only while
  someone holds still in that bin, and a breathing harmonic can fall in the
  heart band. History restarts on configuration, setting or background changes
  and on a gap over 1 s.

  Frame-to-frame phase coherence was checked live on 2026-10-09 (30 s, still
  scene beyond 3 m): the phase of static bins steps 2-3 deg between frames
  (40-50 um), with slower wander of 5-20 deg over seconds. Live, the bin at
  0.78 m in front of the user showed a breathing waveform of about 15/min and
  4.6 mm peak to peak. Heartbeat, 2026-10-09
  (`output/live_radar/20261009-233900-capture-80c03c`, bin at 0.78 m): during
  a breath hold, each beat moves the displacement by about 50 um peak to peak,
  visible live and in the recorded trace without filtering. 24 beats in 16.5 s
  at a steady 0.60-0.70 s interval (about 92/min), with a second harmonic near
  184/min; the next range bin gives the same rate.
  `python tools/readme_figures.py --still <capture> --still-hold START END`
  draws it.
- **I/Q correction:** **Calibrate I/Q** fits each receiver's Q-versus-I gain
  and phase error from the latest frame, assuming a static scene with a strong
  reflector: a mismatch puts a conjugated copy of each positive-frequency
  component at the matching negative frequency, X(-k) = alpha * conj(X(k)), and
  alpha = (1 - u) / (1 + u) with u = g * exp(-j*phi). The correction
  Q_ideal = (Q/g - I*sin(phi)) / cos(phi) is applied in the bin domain as
  X'(k) = A X(k) + B conj(X(-k)), before DC removal and windowing. It is
  cleared when the settings identity changes (gain registers alter the
  mismatch), and is session-local like the background. The `iq_balance` product
  reports the mirror the model still finds (bins 2-12 of the coherent mean) and
  how much negative-bin energy it fails to explain. Bench 2026-10-06, corner
  reflector: Q gain -2.19 / -0.83 dB and phase -18.2 / -15.1 deg (RX1 / RX2);
  negative-to-positive energy over bins 2-12 fell from -13.7 / -16.9 dB to
  -28.3 / -33.1 dB.
- **Scaling:** by default the spectrum axis and both heatmaps auto-scale to the
  visible bins (spectrum: range of the displayed history; heatmaps: 2nd to
  99.5th percentile, at least 10 dB). Untick auto-scale for manual waterfall and
  Doppler colour ranges.
- **Doppler:** Hann FFT across the frame's chirps for every displayed range bin.
  Optional static removal subtracts the within-frame mean before the slow-time
  FFT. Frequency uses the median reported chirp interval: 1200 us gives
  13.0 Hz/bin with 64 chirps (52.1 Hz/bin for older 16-chirp recordings).
  Timing outliers are reported, not silently repaired.
- **Background:** capture the mean complex range bins of the latest acquired
  frame for each receiver, then subtract them before spectrum/Doppler
  processing. Source changes, configuration changes and replay loops clear the
  reference. Session-local; not saved as a calibration.
- **Freeze display:** continues reading, decoding and optional recording while
  holding the displayed frame. Receiver/heatmap controls still work. Resume
  starts a fresh history. **Save latest acquired frame** and **Capture
  background** always act on the current acquisition, even when frozen.
- **Raw recording:** retains original wire bytes plus a SHA-256 manifest in a
  new `output/live_radar/*-capture-*` folder. Stops at 1 GiB or disconnect.
  Starts and ends can be mid-frame; replay resynchronizes and only publishes
  complete frames.
- **Save latest acquired frame:** exports the frame's validated lane data
  (range bins as int32 re/im, `lane*.bins.bin`, or raw records, `lane*.bin`)
  with a hash manifest, source and processing settings, to a new snapshot folder.

## Sweep width

The **02 / Sweep** section chooses the sweep width while live. The start stays
at 24.005 GHz; the rise step (0x56, falling step 0x58 = -step) sets the width.
The range axis follows the live step (`range.sweep_step` in `calibration.json`).

| Sweep | Top | Band | Bin | Exported range |
|---|---|---|---|---|
| 240 MHz | 24.245 GHz | inside 24.0-24.25 GHz (build profile) | ~0.64 m | ~25 m |
| 480 MHz | 24.49 GHz | out of band | ~0.32 m | ~12 m |
| 1 GHz | 25.00 GHz | out of band | ~0.15 m | ~6 m |
| 2 GHz | 26.00 GHz | out of band | ~0.08 m | ~3 m |

Out-of-band sweeps are the user's decision and need the acknowledgement box
ticked for each run. The server enforces the rest:
- Minimum vendor TX setting (0x6D 0x9740 / 0x70 0x26A0, nominal -2.0 dBm
  against 5.0 dBm stock), written before the sweep widens.
- A revert timer of 1-30 minutes, then a re-init to the in-band build profile.
  The same happens if a sweep write fails, on **Restore in band now**, and on
  disconnect or server shutdown. A failed re-init is retried up to 3 times.
- A red header badge counts down while out of band.
- Each live connection reads 0x56. A radar left out of band by an earlier
  session shows **RADAR NOT IN BAND**.
- A killed server process cannot restore anything. Power-cycling the module
  re-applies the in-band profile.

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

Spectrum and heatmap axes stay in FFT bins; only the targets view uses metres.
A three-point corner-reflector fit gave about 0.75 m per bin (+/-10%) at the
stock 204 MHz sweep, so about 0.64 m per bin at the installed 240 MHz sweep,
scaled again for wider sweeps. The sample window covers about 98% of the
up-ramp (register map, 0x02). Target range, angle and velocity are marked
uncalibrated until `calibration.json` says otherwise: the 240 MHz range scale,
the receiver phase offset, antenna spacing and angle sign have not been
measured. The velocity sign has (2026-10-09): positive is moving away. Live angles still jump for one object. The
spectra are not dBm measurements.

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

Within-frame variation is the RMS chirp-to-chirp residual within the exported
bins (DC excluded) after subtracting the frame mean, divided by the in-band RMS
amplitude. It includes noise, drift and motion; it is not target SNR. Range
bins carry no time samples, so the viewer cannot report ADC rail hits.

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

The installed range-bin firmware exports all 64 chirps of every radar frame
(about 48 KB/frame, 11 frames/s); export skips occur only while no host reads
the port. See `firmware/docs/FRAME_STREAM.md` for the image and bench evidence.

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
3. `processing.Pipeline` obtains complex range bins `(receiver, chirp, bin)`
   (device codec-2 bins, or a host FFT of raw records) and constructs
   `FrameContext`. Its named `stages` mapping publishes JSON-compatible products.
   Stage exceptions appear as named errors; other stages can still render.
4. The browser long-polls `/api/state`: the server answers as soon as a newer
   frame is processed (or after 0.5 s), and the page asks again straight after
   drawing. Every frame is drawn (about 11/s, ~180 kB of JSON each) while the
   browser keeps up; a slower browser draws the newest frame and skips the
   rest. Slow/frozen/closed browsers never block acquisition. It retains only one frame plus 160 displayed spectra. Settings
   and configuration generations prevent combining different processing modes
   in the same waterfall history.

To add a range estimator, phase/coherence stage, motion detector or angle solver:
implement a function taking `FrameContext`, add it to `Pipeline.stages`, and add
a corresponding plot in `web/app.js` / `web/index.html`. Retain units and
calibration identity with each new product. Use `ctx.raw` for the unchanged
bins -K..K (unscaled DFT units), `ctx.signal` after background, I/Q correction
and DC removal, or `ctx.spectra` for the windowed, normalized bins
`ctx.bin_range()`. Stage execution must stay bounded; heavy work can
drop display frames but must not alter the acquisition integrity contract.

Tests from the repository root:

```powershell
python -m unittest discover -s tools -p test_viewer.py -v
```

Tests cover complex FFT sign/amplitude, Doppler frequency, timestamp rollover,
background/config changes, static rejection, stage-failure isolation, device
codec-2 bins matching the host conversion of raw frames (with I/Q correction),
endianness, corruption recovery, bounded display backlog, port identity,
recording hashes, replay/snapshot lifecycle, and local HTTP control protection.
Detection, angle and tracking tests use synthetic scenes (two targets, a
fluctuating walker, a fan, noise alone). Phase tests: a 4 mm, 0.3 Hz breathing
reflector beside a 17 dB stronger static one is selected automatically, with the
rate and displacement recovered. A 1.2 Hz, 0.3 mm heartbeat under breathing is
found, a time gap restarts the history, and consecutive products give
bit-identical values for every instant they share. Sweep tests use a simulated device:
the acknowledgement and timer checks, the order of the writes (minimum power
first), range scaling to the live step, and the return to in band on the
timer, a failed write, Restore and disconnect. 41 tests pass (2026-10-09).
