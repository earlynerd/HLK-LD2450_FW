# HLK-LD2450 custom firmware

Reverse engineering and experimental JieLi BR23/AC695N firmware for the
HLK-LD2450 radar module. This project starts with the recovered radar init
profiles, dual SPI acquisition support, and a documented UART update path.

Start with the [image build and loading guide](firmware/docs/IMAGE_BUILD.md),
[firmware/README.md](firmware/README.md), the
[UART update investigation](firmware/docs/UART_UPDATE.md), and the
[hardware evidence](docs/radar_ic_and_internal_interfaces.md).

The [radar processing and data export plan](DSP_plan.md) tracks the next
milestones, acceptance evidence, resource budgets, and session handoff.
The [lossless frame stream application](firmware/docs/FRAME_STREAM.md) integrates
continuous dual-SPI acquisition, a bounded lossless codec, native USB CDC, and
a Python receiver. The current experiment exports raw 16-chirp windows from both
receivers through native CDC on COM30, avoiding the scene-dependent compression
cost that limited the earlier 64-chirp stream during movement. Whole-frame skips
bound the export rate. See the stream guide for the exact image, validation,
capture tradeoffs, and earlier 64-chirp/USB benchmark evidence.

## Current state

The project links a minimal BR23 UART recovery application and packages it
into `.ufw` images using either pinned stock firmware as a layout template.
The application uses our UART receiver, the vendor update engine and a patched
`uart_user.bin` for the flash-writing stage. Stock V2.14 to custom hello,
power-cycle boot, and replacement with a different custom hello build are
bench-verified at 256000 baud. The exact working image is preserved in
[`firmware/releases/hello-verified-20261005`](firmware/releases/hello-verified-20261005/README.md).

The three-second boot recovery window is bench-verified: failed handshake entry
holds off the application, and retrying from recovery replaces it successfully.
The radar profile uses the recovered 75-write / SPI / REXT / five-write ordering.
The MCU reports all 80 writes ACKed on hardware, and updater entry after radar
initialization is verified. A bounded on-device SPI capture has now recovered
distinct RX0/RX1 streams with checksum-valid 512-pair I/Q records on both lanes.
Continuous acquisition now has an initial bench pass; RF calibration and
restoration to stock remain unverified.

## Initial snapshot

The initial commit contains the existing host-tested firmware foundation,
PI32V2 component build scripts, register customization tools, and analysis
artifacts before the complete image builder was added.
`INITIAL_SNAPSHOT.json` records the exact imported file hashes.

The two stock `.ufw` files are immutable vendor reference inputs, downloaded
from `https://h.hlktech.com/Uploads/otagujian/` under their original filenames.
They and extracted vendor code remain third-party materials; no ownership or
license over them is claimed. SDK and compiler downloads are pinned separately
in `firmware/sdk.lock.json` and `firmware/toolchain.lock.json`; their caches and
installers are excluded. The EVB1122 register interpretation is an explicitly
labelled cross-chip hypothesis, not a manufacturer register specification.

Phone Bluetooth archives, unrelated upstream application files, large raw
logic-analyzer captures, and personal attachments are not part of this repo.
Captured binary test fixtures retain their source hashes and sample provenance.

## Live radar viewer

Run `./tools/start_radar_viewer.ps1` to open the local live I/Q, spectrum,
waterfall and exploratory Doppler workspace. It supports native USB with DTR,
saved-stream replay, background subtraction and raw recording. See
[the viewer guide](docs/LIVE_RADAR_VIEWER.md) for controls, calibration limits,
and the processing-stage extension interface.

## Checks

```powershell
python firmware/tools/test_host.py
python firmware/tools/setup_sdk.py --download
python firmware/tools/setup_toolchain.py --download
python firmware/tools/build_image.py
```

The image builder writes `firmware/build/image/update.ufw`, the ELF/map,
application binary, commands and hash manifests. It never accesses a device.
Build caches and generated images are ignored by Git. See the image guide for
custom profiles, the experimental PC uploader and first-boot checks.

## Pico USB recovery entry helper

[`tools/pico-usb-key`](tools/pico-usb-key/README.md) is an Arduino-Pico / PlatformIO
project that sends the USB entry key, tries both clock/data mappings, detects
an ACK-shaped response and supplies calibration edges before a manual cable
swap. It uses GP10/D+ and GP11/D- with removable external pull-ups supplied by GP12. A Pico W UF2
has been built and software-tested; BR23 boot entry remains unverified. This
helper does not flash the radar or forward USB traffic.
