# Register experiment firmware

The next deliverable is a minimal bootable BR23 application that applies a
chosen radar profile and reports its identity and initialization result.
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
- The baseline and example experiment pass three CTest suites and seven Python
  tests. Both compile as **PI32V2/r3 components against the actual pinned SDK**.

`libld2450.a` is an SDK component, not a bootable or flashable image.
`ld2450_app_start()` still initializes peripherals with radar power off.
The explicit stage writer does not call itself from startup, sequence power or
bias, insert settling delays, enforce PRE-before-POST, or arm acquisition.
Those operations belong to the application integration below. In particular,
the current convenience power API changes supply and bias together; reproducing
the stock delayed bias operation needs separate control in the boot sequencer.

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

## Remaining application integration

1. Link an LD2450-specific SDK application with startup, clocks, RTOS, timer,
   watchdog service, and the correct flash/boot configuration. Replace stock
   soundbox board initialization so it does not drive radar-owned pins.
2. First boot a console/heartbeat application with radar power off. Establish
   that the image can be loaded, boots, and can be replaced by stock firmware.
3. Incorporate the measured supply/bias order and settling delays. Apply
   sequences 1..75, set up/arm receivers, establish the captured bias/delay
   operation, then apply sequences 76..80. A bus failure aborts startup; do not
   issue the remaining enable writes. The stock delay argument 1000 is a loop
   count, not a measured microsecond delay.
4. Print profile name/table hash and write status. Capture a baseline first,
   then change one setting or one coordinated group and compare the I2C/SPI
   results. Add runtime profile commands after the baseline boot path works.

The MCU oscillator/clock settings and the physical loading path still need
verification on this board. No complete application link, firmware packaging,
device flashing, or bench validation has occurred.

## Loading paths to establish

| Path | Available evidence | Next fact needed |
| --- | --- | --- |
| JieLi forced USB download | Official AC63 documentation identifies AC635N/AC695N as BR23 and specifies the forced-upgrade tool. Working MCU pin map has USB DM/DP at package pins 23/24. | Locate accessible board pads/nets and verify reset-time handshake and loader enumeration on this unit. |
| UART loader | SDK includes `br23loader.uart` and serial-download configuration. JieLi's generic guide names PB05 for pre-AC697x serial upgrade. | Confirm actual part/boot support and accessible upgrade pin; PA9 console output is not evidence of an upgrade input. |
| Existing Hi-Link Bluetooth OTA | APK and stock packages identify an existing update route and retained OTA loaders. | Local modified-image delivery, package acceptance rules, and restoration behavior are not established. |

The stock SDK's `download.bat` performs device writes and can format regions;
our component builder invokes only compile/archive commands. A complete
image pipeline should expose linking, packaging, and device loading as
separate operations with explicit board/flash configuration.

Changing tables in a copy of the stock application is also a possible first
experiment route. It would preserve its existing boot and acquisition code,
but needs reconstruction of inner file CRCs/scrambling and all four UFW flash
variants, plus verification that the update path accepts the result. The
current generator does not patch or repack stock firmware.

Sources checked on 2026-10-04:

- [Official AC63 family/SDK mapping](https://doc.zh-jieli.com/AC63/zh-cn/master/getting_started/preparation/index.html)
- [Official download-mode entry](https://doc.zh-jieli.com/AC63/zh-cn/master/getting_started/preparation/usb_updater.html)
- [Forced-upgrade handshake and serial-download guide](https://doc.zh-jieli.com/Tools/zh-cn/dev_tools/forced_upgrade/upgrade_and_download.html)
- [Official customizable bootloader](https://github.com/Jieli-Tech/fw-Bootloader)
- [Recovered stock init evidence](../../output/radar_init/report.txt)
- [Register interpretation and confidence notes](../../output/evb1122_analysis/register_write_table.md)
