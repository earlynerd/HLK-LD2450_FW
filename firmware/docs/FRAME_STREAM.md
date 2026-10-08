# Lossless frame stream application

## Installed image: 240 MHz sweep profile (2026-10-08)

The raw 16-chirp stream with live register control (LDC1) now starts the radar
with `firmware/config/radar_sweep240_mode2.json`: 24.005-24.245 GHz, about
0.64 m per FFT bin instead of 0.75 m. Firmware source and wire format are
unchanged; only the radar startup table and the stream configuration identity
differ. Build:

```powershell
python firmware/tools/build_image.py --application stream --stream-chirps 16 --radar-config firmware/config/radar_sweep240_mode2.json --out firmware/build/stream-raw16-sweep240
python firmware/tools/patch_stock_uart_loader.py --input firmware/build/stream-raw16-sweep240/update.ufw --out firmware/build/stream-raw16-sweep240/update-two-wire.ufw
```

Flashed UFW SHA-256 `413aaf0f7c5d76f1e07c041cadf4b1a7e65c557a25e47f1bf0f02540bb1d1b56`;
stream configuration SHA-256
`c8dd4388ad2e37ecc13482b3d5df19322a73a655f963d64823e73b920d5320af`. After the
COM13 update the viewer reconnected on COM30 at register generation 0, and
0x53-0x58 read back the profile values. The x1.18 spectrum stretch was verified
by live writes on a static scene on 2026-10-07; see `DECISIONS.md` and
`docs/S5KM312CL_REGISTER_MAP.md`. Archive:
`firmware/releases/usb-raw16-sweep240-20261008/`. The previously installed
stock-sweep control image is archived in
`firmware/releases/usb-raw16-control-20261006/`.

## Radar record size and FFT self-test build options (2026-10-08)

`--raw-pairs 512|256|128` (stream only) sets the radar record size the firmware
accepts (`LD_RADAR_PAIRS`; records are 8 + 4 x pairs bytes). The build refuses
a radar profile whose register 0x04 size code disagrees. BEGIN carries the pair
count; `frame_stream.py` and the viewer's I/Q unpacking accept 512, 256 and 128.
The other viewer stages still assume 512. The default stays 512, and the 512
build's configuration identity is unchanged. `--fft-selftest` runs the hardware
FFT characterisation at start-up and prints it on PA9 (`firmware/docs/HW_FFT.md`).

Bench 2026-10-08, `radar_sweep240_raw256_step4_diagnostic.json` (256 samples at
step 4, same 410 us window): 337 complete windows in 30 s (11.2/s, every radar
frame), one start-boundary rejection, no protocol errors. Evidence:
`output/raw256_step4/20261008-012401/`. The chip drops samples without filtering
(see the 0x02 entry in `docs/S5KM312CL_REGISTER_MAP.md`). The 240 MHz 512-sample
release image was reinstalled afterwards.

## Current experiment: raw 16-chirp export

The user selected a shorter capture window on 2026-10-06. The installed stream
image now exports chirps 0-15 from both receivers, retaining all 512 complex
samples per chirp in LDF1 raw mode. Acquisition still validates all 64 physical
chirps per receiver. Radar configuration and cadence are unchanged; the export
window is shorter. Frame starts are skipped while earlier output is pending.

A complete window is 67,100 wire bytes, fitting the 90,112-byte producer queue
even with no USB draining. Raw mode removes scene-dependent compression size
and compression work. CPU/DMA guards, radar checksums, message/raw CRCs, sequence
checks and complete paired-window validation remain enabled. BEGIN declares
16 chirps; the host and viewer also retain support for older 64-chirp recordings.
At 1.2 ms/chirp, the shorter window has about 52.1 Hz Doppler bins rather than
13.0 Hz. This intentionally sacrifices slow-time resolution and the later
48 chirps, not samples within the declared window.

Build and prepare the two-wire updater image:

```powershell
python firmware/tools/build_image.py --application stream --stream-chirps 16 --out firmware/build/stream-raw16
python firmware/tools/patch_stock_uart_loader.py --input firmware/build/stream-raw16/update.ufw --out firmware/build/stream-raw16/update-two-wire.ufw
```

Flashed UFW SHA-256:
`541c110a9707a110bf3afca69ae46f8ad1e57a406398ce956bf80212fa8506af`.
Configuration SHA-256:
`cdc8522d33c2f58d79aa41877b7922b895f21d554bc8203d4c872c3f34b5b5f5`.
Target build and runtime audits passed; 15 CTest suites, 34 Python firmware tests
and 16 viewer tests passed. The new C test validates whole-window queue capacity
without USB draining, full 64-chirp acquisition tracking, skipping while output
is pending, and recovery after draining. C-to-Python interoperability validates
all samples in two actual raw 16-chirp producer windows.

The user confirmed the plots continued updating during movement. The saved
126,215,608-byte recording contains 1,881 complete windows over 214.55 seconds
(8.76 windows/s), all 60,192 record messages in raw mode, with zero explicit
ABORTs, rejected candidates or protocol errors before EOF. A 64-byte initial
resynchronization prefix and partial EOF tail are recording boundaries. The
device rejection counter remained at one throughout that recording; it was
already nonzero on the first window, so this is not a zero-rejections-since-boot
claim. Timing-outlier observations remain in the viewer diagnostics.

The subsequent stopped UART report covers 174,592 valid records per lane,
with zero corrupt records, sequence errors, timeouts, DMA overruns, CPU
rejections and queue overflows. Peak DMA backlog was one and output queue peak
54,512/90,112 bytes. It reports two cumulative rejected exports after the
USB disconnect/reopen boundary; neither was a CPU or queue overflow, and their
exact cause was not captured. Same-image restart succeeded and the viewer was
reconnected afterward. The motion interval was not precisely time-marked and
this is one office-scene trial, not exhaustive scene/stall qualification.

Image/source archive: `firmware/releases/usb-raw16-20261006/`.
Evidence: `output/live_radar/20261006-175804-capture-a2a17a/validation-raw16.json`,
`output/stream_bench/raw16_motion_report/pa9.txt`, and
`output/firmware_build/raw16_validation_20261006.json`.

## Earlier 64-chirp motion-load qualification

The later live-viewer demonstration on 2026-10-06 exposes a significant limit
of the earlier 64-chirp image: moving scenes can repeatedly abort exports, leaving the
viewer without fresh complete frames until motion subsides. A preserved
50,612,581-byte stream has 305 completed frames and 125 rejected candidates:
71 explicit CPU-backlog aborts (reason 6), 53 explicit output-queue aborts
(reason 3), and one rejection during an interior parser resynchronization.
The extra 869 resynchronization bytes have no established cause; they must not
be silently included in the intentional-abort classification. Host protocol
errors were zero. The first 336 resynchronization bytes are the recording's
mid-message starting prefix.

This exercises the CPU guard that the earlier static trial did not trigger;
it does not establish a motion-robust lossless stream. A full accepted frame
still contains all 128 records. Firmware and sample-retention rules have not
changed. Merely skipping more frame starts cannot guarantee success if one
selected frame exceeds the available within-frame queue/CPU budget.

Host size screening on validated records from aborted prefixes predicts
16.1% fewer bytes with neighboring-sample prediction and 17.1% with a 2-D
gradient, but those predictors increase size on the successful-frame group.
These are estimates, not implemented codecs or measured target timings; they
motivate testing adaptive lossless prediction without reducing chirps/samples.
Evidence and per-frame outcomes:
`output/live_radar/20261006-173642-capture-3fc19b/analysis.json`.
Reproduce with `tools/analyze_stream_health.py`.

## Earlier static-scene baseline

2026-10-06: native USB is wired and enumerates as COM30, VID/PID
`4C4A:4155`, serial `LD2450-STREAM-01`. That **64-chirp live radar stream**
uses interrupt-driven CDC, a 4 KiB owned USB staging ring, an 88 KiB output
queue, and the existing independent, lossless LDF1 frame format.

A 30.003-second concurrent acquisition/compression/USB run delivered 20,402,188
wire bytes (~680 kB/s) and **159 complete paired frames**, about 5.3 frames/s.
The host checks every reconstructed record's framing, radar checksum and raw
CRC, plus message CRCs, sequence and all 128 records before publishing a frame.
There were zero DMA overruns, corrupt records, sequence errors, queue overflows
or CPU-budget rejections. Device queue peak was 80,924 of 90,112 bytes; peak DMA
backlog was one record. The device enqueued 160 frames; the capture ended during
the last frame (326-byte tail), so the host published only 159. Acquisition runs
at its original cadence; exports intentionally skip whole frames while output
is pending. This is reduced-cadence lossless retention, not full-rate export.

The three-second reader-pause trial recovered 27 complete frames, with one
explicit queue-overflow ABORT and an EOF tail. Reopening recovered 28 complete
frames after a 64-byte in-flight prefix and an EOF tail. Acquisition stayed
error-free. Physical cable unplug/replug and runtime stack high-water usage
are not qualified. Encoding cost and compression depend on the scene: an
earlier 88 KiB trial overran SPI on less compressible records. A new guard
rejects export at two pending DMA records before the four-slot ring overruns;
that guard did not trigger in the final successful trial, so its loaded
activation remains to be exercised deliberately.

Final live UFW SHA-256:
`25e98a57868261ed3abfe1e7f218eca90a0574452d379be93904c81cce547bd8`.
Preserved image/source: `firmware/releases/usb-optimized-20261006/`.
Evidence: `output/stream_bench/usb_budget_guard*_capture/`, corresponding
`*_decoded/`, and `output/firmware_build/usb_optimized_validation_20261006.json`.

The final radar-off, raw-pattern comparison delivered 7,901,184 wire bytes in
10.004 s (~790 kB/s), versus the prior ~729 kB/s baseline. All 29 complete frames
matched the known pattern exactly: 7,631,872 reconstructed bytes. Its only
parser error is the 611-byte EOF tail. This is an approximately 8.3% raw-rate
gain; it is not a claim of the controller's maximum possible throughput.
Raw image SHA-256:
`9d7d2ba8b88495a85ed8dc24ba3f3dbc3e79d10d6478ced4b708b719b35ff55b`.
Evidence: `output/stream_bench/usb_optimized_raw_final*`.
The original raw baseline remains in `firmware/releases/usb-raw-baseline-20261006/`.

## Earlier acquisition-only reference

The acquisition-only bench run lasted 10.584937 seconds on the local timer:
7,536 valid records per lane, 117 complete paired 64-chirp frames, zero corrupt
records, sequence errors, timeouts or DMA overruns. Peak pending DMA backlog
was one record; maximum record processing time was 264 microseconds. USB was
absent, so all 118 observed frame starts intentionally skipped export. These
timings exclude encoding and USB load and do not qualify sustained export.
Evidence: [quiet-start run](../../output/stream_bench/quiet_start/result.json)
and [PA9 report](../../output/stream_bench/quiet_start/pa9.txt).

Flashed two-wire UFW SHA-256:
`388a98cf4c637a0d8863df2fedb7c248b77d027016525d1f74104075c9e0c8c4`.
The exact image, ELF, manifests and source snapshot are preserved in
`firmware/releases/stream-acquisition-20261006/`. Same-image updater reentry
passed from both stopped and running acquisition; the final run restarted
the application without issuing the stop command. USB had not yet been wired
at that milestone; the current USB results above supersede that limitation.

## Run the checks

From the `HLK-LD2450_FW` project root:

```powershell
python firmware/tools/test_host.py
python firmware/tools/build_br23.py --out firmware/build/stream-component
python firmware/tools/build_image.py --application stream
python firmware/tools/build_image.py --application usb-bench
python firmware/tools/build_image.py --application usb-bench --raw-usb-bench --out firmware/build/usb-raw-next
python firmware/tools/patch_stock_uart_loader.py --input firmware/build/stream/update.ufw --out firmware/build/stream/update-two-wire.ufw
```

CTest runs thirteen suites, including raw-only encoding, acquisition, the actual USB adapter with
mocked registers, nonblocking updater polling, and twelve C-to-Python
interoperability cases. Another 34 Python tests cover existing tools. The real
16-chirp startup fixtures reconstruct byte-for-byte and retain
their source hashes in `firmware/tests/fixtures/dual_lane_startup/manifest.json`.
Their codec payloads total 35,332 bytes from 65,792 bytes (53.7%), including
original record framing and codec overhead, excluding LDF1 transfer envelopes.
These are not complete frames or a worst-case compression guarantee. Separate
synthetic paired 64-chirp frames test completion. The 16-chirp stream test ends
with ABORT and must publish no complete frame.

Checks cover int16 extremes and 17-bit deltas, raw fallback, zero-width blocks,
USB-sized and arbitrary byte splits, queue wrapping, partial writes, stalls,
overflow, disconnect, missing/duplicate/reordered chirps, truncation, bad
lengths, header/payload/raw CRCs, radar checksums and recovery at a new BEGIN.

For the installed raw diagnostic, open COM30 with DTR asserted:

```powershell
python firmware/tools/frame_stream.py --port COM30 --seconds 10 --out output/usb-raw-next
python firmware/tools/verify_usb_bench.py output/usb-raw-next
```

`--raw-usb-bench` is accepted only with `--application usb-bench`. Its
configuration identity explicitly labels synthetic, paced, raw-only encoding.
The LDF1 wire format is unchanged. Every sample value is `17*index+chirp+lane`;
the independent verifier compares both full reconstructed lane files.

The speed fixes preserve the format: slicing-by-four IEEE CRC, byte-oriented packing,
one residual calculation per sample using a 32-value scratch block, and `-O2`
for stream/acquisition/radar parsing, the USB adapter and generated dispatcher.
Stream images place the CRC routine and 4 KiB lookup table in startup-copied internal RAM. CPU configuration and live
registers agree: `CLK_CON0=0x1c3`, `CLK_CON2=0xc53`, `SYS_DIV=0x400` select the
480 MHz PLL divided by two, HSB divide one and LSB divide five. Runtime
`clk_get("sys")` reports 240 MHz. These are configuration/readback evidence,
not an independently measured clock waveform.

## Producer integration

`include/ld2450_stream.h` and `src/stream.c` have no SDK or hardware dependencies.
All operations have one task owner; DMA/USB interrupt handlers must hand off
buffer ownership instead of calling these APIs concurrently.

1. Allocate the state and a caller-owned queue statically. Unit tests use an
   8 KiB queue plus an 88 KiB boundary/wrap test; the target uses 88 KiB.
   The x64 host state is 6,312 bytes, including 4,096 bytes of prediction
   history and a 2,093-byte message scratch buffer. Target ABI size and total
   application RAM/stack/heap must be measured separately. No complete raw
   frame is buffered by the producer and it performs no heap allocation.
2. Initialize with a 32-byte SHA-256 identifying the actual ordered radar
   configuration and acquisition settings. Define and retain that identity's
   input manifest in the acquisition adapter; test streams use an all-zero
   identity explicitly as synthetic data.
3. At an observed paired frame boundary call `ld_stream_begin` once, with an
   observed-frame counter (including skipped frames) and local microseconds.
   Select only when the previous output queue is empty; otherwise count an
   intentional whole-frame skip. Calling BEGIN while a frame is active rejects
   the old frame as incomplete. No inference of physical frame boundaries is
   implemented by this module.
4. Submit validated, assembled 2,056-byte DS RAW records. Each receiver must
   independently progress from chirp 0 through 63. Lanes may interleave in any
   order. The first chirp of each lane is raw, so each frame is independent.
   Startup records, missing chirps, identity/sequence errors or bad checksums
   reject the frame. Call `ld_stream_abort` on acquisition timeout, DMA overrun
   or updater entry, including when no further record arrives.
   Acquisition may pass a VALID decoder result for the exact unchanged,
   caller-owned bytes to `ld_stream_record_validated`, avoiding a redundant
   radar-checksum pass. The ordinary API always validates; all transport CRCs
   remain enabled in both paths.
5. Pump a bounded byte budget between acquisition work. The transport callback
   must return promptly and **copy** accepted bytes before returning their
   count. Zero means temporary backpressure; a negative result means disconnect
   or transfer failure. An asynchronous DMA adapter needs its own owned buffer
   and must not retain a pointer into this queue after accepting bytes.

Messages enter the queue atomically. Every data insertion reserves 40 bytes for
ABORT, so overflow has an explicit terminal record even with a stalled host.
Previously queued bytes remain ordered and drain before another frame begins.
A transport error clears the queue, resets active state and counts loss; the
host discards any incomplete prefix and resynchronizes on a subsequent valid
BEGIN. It also invalidates unfinished frames at EOF/capture end.

Stats include completed encoding, rejected/skipped frames, invalid records,
overflows, transport errors, raw/compressed record counts and queue peak.
`frames_completed` counts complete frames **enqueued**, not host acknowledgments.
A disconnect before draining END also increments rejection. Only the host's
accepted complete-frame count establishes receipt; this protocol has no ACK or
retransmission. Counters/frame IDs/sequence/timestamps are uint32, wrapping
modulo 2^32. Timestamps are caller-provided observation times, not proven radar
sample timestamps, and are not compared as ordinary monotonic integers.

## Target integration and USB bench handoff

`stream_app.c` owns four 2,056-byte DMA slots per lane. SPI completion IRQs
rearm the next slot immediately; the main loop validates and encodes owned
records. `acquisition.c` pairs lane chirp-zero records within 5 ms and requires
ordered chirps 0..63 independently on both lanes. TIMER3 supplies microsecond
observation timestamps, wrapping as uint32; it is not a radar sampling clock.
A 200 ms missing-record timeout aborts an unfinished frame. A DMA ownership
overrun stops acquisition and powers down the radar until restart, avoiding
rearming in the middle of a physical record. Output backpressure instead
rejects/skips whole frames while continuing acquisition.

`usb_stream.c` uses the SDK EP0/device stack with project-owned CDC descriptors:
bulk IN/OUT endpoint 4, notification IN endpoint 2, 64-byte packets. The write
callback copies at most 2 KiB into a bounded 4 KiB ring. The endpoint-completion
interrupt copies and submits the next 64-byte packet from that ring while
the main task encodes records. DMA has a separate owned buffer. Full rings
return zero promptly. Final partial packets/ZLP are flushed only at an output
boundary; the adapter does not call vendor blocking `cdc_write_data`.
Register accessors retain bounded SDK polling loops; stopped reports include
total/max USB ISR time (including boot/reset handling and timing overhead). Reset, suspend, DTR loss and missing SOFs invalidate the
transport epoch. A new host receives a new independent frame after recovery.
The generated SDK configuration keeps USB buffers in ordinary BSS and leaves
EP0 available across suspend; the pinned SDK checkout is unchanged.

The laboratory descriptor currently inherits SDK VID/PID `4C4A:4155`, product
`LD2450 frame stream`, serial `LD2450-STREAM-01`. These are not an allocated
production identity. Windows enumeration and serial-driver binding are verified.

Startup keeps the three-second UART recovery window before USB/radar setup.
The running application's UART poll is bounded and retains split update
handshakes; a valid updater request first stops acquisition and USB. Module
UART remains PA1/PA0 at 256000 baud; PA9 diagnostics remain at 115200. Avoid
printing during acquisition: blocking startup prints previously filled the
DMA ring before the main loop could service it.

Sending ASCII `?` on the module UART snapshots DTR, configuration state, SOF age,
endpoint status and transfer counters, then **stops radar and USB** and prints
the report on PA9. It also reports clocks/registers and, if radar records were
encoded, bounded stopped-state CRC/encoder timing. Restart or use the UART updater to resume. This is a one-off diagnostic,
not a command for the native USB data port. The checked bench runner is
`firmware/tools/bench_stream.py`; it requires explicit ports and an image hash.

Measured static sizes: producer plus acquisition state 16,648 bytes, DMA
16,448 bytes, output queue 90,112 bytes, plus a 4,096-byte USB staging ring
and a 4,096-byte CRC table. The final linker map reserves 24,320 bytes of main
heap and 11,648 bytes of secondary heap (35,968 total), after static layout.
These are link-time reservations, not measured runtime free space. SDK heap
counters report 230,640 bytes, inconsistent with physical RAM; do not use that
figure. Runtime stack usage and allocator accounting remain unqualified.

When native USB is connected, verify its COM port identity and run the capture
command below. Require accepted complete frames and preserved source hashes.
Then exercise reader stalls and reconnect, obtain the stopped PA9 report, and
compare acquisition errors, encoding time and queue peaks. If enumeration or
transport needs isolation, use the separately built `usb-bench` image first.

## Wire format v1

All envelope integers are little-endian; original radar bytes remain big-endian.
Each message is a 32-byte header, payload, then IEEE CRC-32 of the payload
(polynomial 0xEDB88320, initial/final xor 0xFFFFFFFF). Header CRC covers bytes
0..27. Header CRC and the 2,057-byte payload bound are checked before using
lengths. Maximum message size is 2,093 bytes. Empty payload CRC is zero.

| Offset | Bytes | Meaning |
| --- | --- | --- |
| 0 | 4 | ASCII `LDF1` |
| 4 | 1 | Protocol version 1 |
| 5 | 1 | Type: 1 BEGIN, 2 RECORD, 3 END, 4 ABORT |
| 6 | 1 | Codec: 1 for RECORD, 0 otherwise |
| 7 | 1 | Receiver 0/1; 255 for control messages |
| 8 | 2 | Payload length |
| 10 | 2 | Chirp 0..63; 65535 for control messages |
| 12 | 4 | Message sequence, consecutive within a frame |
| 16 | 4 | Observed radar frame ID |
| 20 | 4 | Local timestamp in microseconds |
| 24 | 4 | CRC-32 of reconstructed 2,056-byte record; zero for control |
| 28 | 4 | Header CRC-32 |

BEGIN has 52 payload bytes: configuration SHA-256 (32), cumulative skipped
frames (u32), rejected frames (u32), prior queue peak (u32), pairs=512 (u16),
chirps=64 (u16), receivers=2 (u8), codec version=1 (u8), register generation
(u16). The last field was reserved zero before live register control; images
without control still send zero. The generation counts every live WRITE and
REINIT since boot (mod 65536), so frames with different live register
settings never share an identity. The build configuration hash is unchanged
by live writes.
END has no payload and is valid only after all 128 records. ABORT has a u32
reason: 1 next boundary before completion, 2 invalid record, 3 queue overflow;
4 is the replay harness's incomplete-input reason; 5 is an acquisition gap,
timeout, stop or transport reset; 6 is CPU backlog (two pending DMA records).
Host rejection does not require parsing a reason.

### Live radar register control (LDC1)

Images whose stream identity includes `radar_control: ldc1-v1` accept 20-byte
LDC1 commands on the CDC bulk OUT endpoint: READ (1..32 consecutive registers,
one I2C transaction each, no auto-increment assumed), WRITE (one register),
REINIT (stop acquisition, power-cycle the radar, re-apply the build profile).
The exact layout is in `firmware/include/ld2450_radar_control.h`; the host
encoder is `encode_command` in `firmware/tools/frame_stream.py`. No register,
value or range is restricted: this is a laboratory control path.

Commands execute between physical frames: once no SPI record has completed
for 2 ms, new commands may start for 3 ms (baseline frames leave about 11 ms of
NOP). With no records for 250 ms the radar is treated as idle and commands run
freely. After 1 s without a usable gap a command runs anyway; if chirps are
still arriving that can overrun DMA and stop acquisition until REINIT.

Every command is answered by a type-5 REPLY control message (lane 255, chirp
65535, codec 0, raw CRC 0), only between export frames: tag (u32), op (u8),
status (u8: 0 ok, 1 bus error, 2 bad command, 3 queue overflow, 4 reinit
failed), register (u8), value count (u8), register generation after the
command (u16), driver error (i16), then the values (u16 each). A queued reply
delays the next export because BEGIN still requires an empty queue. Older
hosts ignore REPLY between frames; a REPLY inside a frame is a protocol error.

RECORD payload starts with mode (u8), original header (4 bytes), original
trailer (4 bytes), then encoded I/Q. Mode 0 is 2,048 verbatim I/Q bytes.
Mode 1 subtracts the previous chirp from signed int16 samples independently
at each I/Q position. Encode d as z=2*d for d>=0, or -2*d-1 otherwise. For each
32-value block emit a one-byte bit width (0..17) then 32 z values MSB-first at
that width. Blocks are naturally byte aligned (4*width bytes). Width zero has
no value bytes. Use raw mode unless packed I/Q plus width bytes is strictly
smaller than 2,048 bytes. Never wrap residual arithmetic into int16. The host
rejects reconstructed samples outside int16 and validates original framing,
radar checksum and raw CRC before accepting a chirp.

## Host capture

Offline decoding needs only Python's standard library:

```powershell
python firmware/tools/frame_stream.py --input saved-stream.ldf --out output/decoded-new
```

Once the flashed streaming USB CDC firmware enumerates, the receiver
can read its explicit port (requires `pyserial`):

```powershell
python firmware/tools/frame_stream.py --port COMXX --seconds 30 --out output/usb-new
```

COMXX is a placeholder for that new CDC device, not the module's UART updater.
The existing capture image emits ASCII and cannot supply this protocol. The
CDC line-coding value is 115200; it is not a measured USB data-rate limit.
The capture tool sends no application commands. The serial library opens the port and
may assert control lines as part of CDC setup; hardware use requires a known
USB connection. Native USB capture is validated with both the exact synthetic raw profile
and complete live radar frames; see the measured scope above.

Each new output directory retains `stream.ldf`, its SHA-256 in `report.json`,
and separate accepted-frame directories with both original lane binaries,
hashes, configuration identity, per-chirp observation timestamps and device
counters. Incomplete/rejected data remains in the original stream. Existing
output directories are refused. A capture with no complete frame exits 1.

## Preserved baseline

Before source edits, 148 source/build/evidence files were archived locally in
`firmware/build/baseline-before-stream-20261006/baseline.zip`, with per-file
hashes in `manifest.json`. Archive SHA-256:
`c6877225654e608a018543b15066b098796cce3d20cf3859ec58a8680bafc411`.
The preserved `spi-capture16/update-two-wire.ufw` matches the prior reference:
`16381b9302ccceaa48af63f7459c293fccbeb042064be85432480fbb575f6fb5`.
This archive is in ignored build storage, not a committed release or a claim
that the entire working tree is clean. Existing uncommitted work was retained.
