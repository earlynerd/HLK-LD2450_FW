# Register experiment firmware

The BR23 application now applies the selected radar profile automatically
and reports initialization success or failure on its debug UART.
The logic analyzer can capture I2C and both radar SPI lanes directly, so this
first application does not require implementing tracking or sustained sample
transport to the PC.

## Implemented on 2026-10-04

- Both recovered 80-write profiles are available to the source generator.
- A JSON configuration selects the baseline and occurrence-specific overrides.
- Every override checks its sequence, register, and expected old value. This
  preserves repeated writes: changing sequence 79 at register 0x41 leaves its
  sequence-2 value untouched.
- Generated C, binary table data, inferred I2C transaction bytes, and a
  provenance JSON retain the 75/5 stage boundary, both original firmware
  hashes, configuration hash, table hash, and exact changes.
- `ld2450_radar_apply_init_stage()` writes register/MSB/LSB to seven-bit address
  0x20. It stops on the first bus error and reports the failed source sequence.
- The baseline and example experiment compile and link as **PI32V2/r3 applications
  against the actual pinned SDK**, and package as complete UFW images. See
  [IMAGE_BUILD.md](IMAGE_BUILD.md) for the current five CTest/twelve Python checks.

`libld2450.a` is an SDK component, not a bootable or flashable image.
`ld2450_app_start()` now sequences independent supply/REXT controls, minimum
20 ms supply settling, writes 1..75, SPI receiver setup, REXT assertion,
minimum 3 ms settling, then writes 76..80. A bus error aborts remaining writes
and powers down the radar while preserving UART updating. The timing choices
and evidence boundaries are described in [IMAGE_BUILD.md](IMAGE_BUILD.md).
The stage writer remains separately callable; DMA arming and sustained
acquisition are not part of the boot application.

## Select and build a profile

Run these commands from the project root:

```powershell
# Host checks and a target component using the recovered mode-2 baseline:
python firmware/tools/test_host.py
python firmware/tools/build_br23.py

# Example candidate: only sequence 79 changes, 0x41 = C844 -> C854:
python firmware/tools/test_host.py --radar-config firmware/config/radar_no_idle_powerdown.json --build-dir firmware/build/host-no-idle-powerdown
python firmware/tools/build_br23.py --radar-config firmware/config/radar_no_idle_powerdown.json --out firmware/build/br23-no-idle-powerdown
```

`--plan` generates the selected profile and compile/archive commands without
compiling. Each output directory contains `generated/` and, following a
successful target compile, `libld2450.a` and `build-result.json`. The result
records compiler/archiver provenance, source hashes, and the component hash.

Copy a config file to name another experiment. The schema is:

```json
{
  "name": "example-experiment",
  "base_profile": "mode_2_ram_initial",
  "overrides": [
    {
      "sequence": 79,
      "register": "0x41",
      "expected": "0xC844",
      "value": "0xC854",
      "reason": "Test the inferred automatic idle power-down control."
    }
  ]
}
```

The other baseline is `mode_1_rom`. These are the binary's internal profile
labels; their mapping to user-facing app modes is unconfirmed. The default
mode-2 image values can differ from a stock unit's saved/runtime settings.
The example assumes the register definition from the comparison analysis;
its physical effect has not been tested.

## Project-local compiler

The official JieLi Windows toolchain 2.5.2 was downloaded from the link in
[JieLi's tools index](https://doc.zh-jieli.com/Tools/zh-cn/other_info/index.html).
Its Authenticode signature validated as ZhuHai JieLi Technology Co.,Ltd.
It was unpacked with [innoextract](https://constexpr.org/innoextract/) without
running the installer. Package/tool hashes and the source URLs are in
`firmware/toolchain.lock.json`.

The builder automatically uses the extracted project-local compiler at
`firmware/.cache/toolchain/extracted-2.5.2/C$/JL/pi32/bin`, checking the pinned
compiler, archiver, and linker-wrapper hashes. With that cache absent, it
defaults to the conventional `C:/JL/pi32/bin`; `--toolchain` selects another
installation. The compiler package and extracted files remain local cache
inputs. No system installation or global PATH change was made.

## Bench validation and subsequent acquisition work

The linked application implements the recovered startup ordering and the
captured mode-2 register sequence. Clock/flash assumptions, physical loading,
boot and radar output still need verification on the module. Capture a baseline
first, then change one setting or one coordinated group and compare I2C/SPI
results. Build provenance records the selected profile and table hash.

Continuous acquisition, synchronized SPI lanes, PC sample transport and
runtime profile commands remain subsequent work. External logic-analyzer
capture is sufficient for the first register experiments; rail captures are
not a prerequisite for the implemented startup sequence.

## Loading paths to establish

| Path | Available evidence | Next fact needed |
| --- | --- | --- |
| JieLi forced USB download | Official AC63 documentation identifies AC635N/AC695N as BR23 and specifies the forced-upgrade tool. Working MCU pin map has USB DM/DP at package pins 23/24. | Locate accessible board pads/nets and verify reset-time handshake and loader enumeration on this unit. |
| UART loader | SDK includes `br23loader.uart` and serial-download configuration. JieLi's generic guide names PB05 for pre-AC697x serial upgrade. | Confirm actual part/boot support and accessible upgrade pin; PA9 console output is not evidence of an upgrade input. |
| Existing Hi-Link Bluetooth OTA | APK and stock packages identify an existing update route and retained OTA loaders. | Local modified-image delivery, package acceptance rules, and restoration behavior are not established. |

The stock SDK's `download.bat` performs device writes and can format regions;
our component builder invokes only compile/archive commands. The complete
`build_image.py` pipeline adds linking and offline packaging; device loading
is a separate explicit command with a named serial port.

Changing tables in a copy of the stock application is also a possible first
experiment route. It would preserve its existing boot and acquisition code,
but still needs verification that the device update path accepts the result.
The new packager reconstructs the CRCs/scrambling and updates all four flash
variants; it replaces a complete app.bin rather than editing instructions in
the stock application. The register generator itself remains data-only.

Sources checked on 2026-10-04:

- [Official AC63 family/SDK mapping](https://doc.zh-jieli.com/AC63/zh-cn/master/getting_started/preparation/index.html)
- [Official download-mode entry](https://doc.zh-jieli.com/AC63/zh-cn/master/getting_started/preparation/usb_updater.html)
- [Forced-upgrade handshake and serial-download guide](https://doc.zh-jieli.com/Tools/zh-cn/dev_tools/forced_upgrade/upgrade_and_download.html)
- [Official customizable bootloader](https://github.com/Jieli-Tech/fw-Bootloader)
- [Recovered stock init evidence](../../output/radar_init/report.txt)
- [Register interpretation and confidence notes](../../output/evb1122_analysis/register_write_table.md)
