# HLK-LD2450 custom firmware

Reverse engineering and experimental JieLi BR23/AC695N firmware for the
HLK-LD2450 radar module. This project starts with the recovered radar init
profiles, dual SPI acquisition support, and a documented UART update path.

Start with the [image build and loading guide](firmware/docs/IMAGE_BUILD.md),
[firmware/README.md](firmware/README.md), the
[UART update investigation](firmware/docs/UART_UPDATE.md), and the
[hardware evidence](docs/radar_ic_and_internal_interfaces.md).

## Current state

The project links a minimal BR23 UART recovery application and packages it
into `.ufw` images using either pinned stock firmware as a layout template.
The application contains our UART receiver and register profile, and uses the
vendor update engine and preserved `uart_user.bin` for the flash-writing stage.
Startup applies the selected radar profile with the recovered 75-write / SPI /
REXT / five-write ordering. Images are target-built and host-verified, but have
not been flashed or boot-tested on a module.

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
