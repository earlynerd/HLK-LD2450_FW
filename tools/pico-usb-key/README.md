# Pico USB_KEY entry helper

Arduino-Pico / PlatformIO project for a **Raspberry Pi Pico W (RP2040)**.
It sends the JieLi entry key, detects an ACK-shaped low interval, supplies
calibration edges, then releases the data lines for a manual USB cable swap.
No flash commands or firmware images are sent to the radar.

The revised project is target-built and software-tested. The previous version
produced one apparent ACK on the bench, but **BR23 USB enumeration remains unverified**.
A solid LED reports completion of this sequence, not successful enumeration.

## Wiring

| Pico signal | Physical pin | Connection |
| --- | --- | --- |
| GP10 | 14 | Radar USB D+ |
| GP11 | 15 | Radar USB D- |
| GND | 13 or 23 | Radar GND |
| GP12 | 16 | Supply ends of the two **1 kOhm** resistors; other ends go to GP10 and GP11 |
| GP15 (optional) | 20 | Momentary button to GND; internal pull-up enabled |

**Move both resistor supply ends from 3V3 OUT to GP12.** GP10, GP11 and GP12
use 12 mA drive strength. GP12 drives low at startup, idle, stop, error and
completion; it drives high only during an entry attempt, including calibration.
With GP12 low these resistors pull the data lines down; the whole connection
is therefore not high-impedance, even though GP10/11 are inputs. With both
lines low during an attempt, the two 1 kOhm resistors draw about 6.6 mA total.
This GPIO supplies only the resistors, never the radar power input.

Keep the pull-ups on the **Pico side of the removable connection**. Unplugging
the injector must remove both pull-ups as well as its GPIO wires before the
PC USB data connection takes over. Both lines are open-drain: the Pico only
drives low, otherwise releasing the pin. Internal data-line pulls are disabled.
Use short wires and 3.3 V pull-ups, not 5 V.

Power the radar independently so it stays powered during the swap. The Pico's
own USB connector powers the Pico and provides its serial console; it does not
pass USB through to GP10/GP11. This wiring does not join Pico VBUS/VSYS to the
radar supply. Keep the target disconnected from the PC's USB data lines while
the injector operates. Preserve the target's power arrangement when connecting
the PC cable; do not inadvertently parallel two power supplies through VBUS.

## Load and run

1. Hold the Pico's BOOTSEL button while plugging its USB connector into the PC.
2. Copy `build/pico-w-usb-key.uf2` to the `RPI-RP2` drive. This programs the Pico
   only. The board automatically reboots after the copy.
3. Open the Pico's new USB serial port at 115200. Send `?` to see commands.
   This is a different port from the radar's COM11/COM13 adapters.
4. Connect the injector. Send **`x`**, then switch the radar power **off** and
   allow its supply to discharge. GP12 stays low throughout this off interval.
5. Send **`g`** (or press the GP15 button) as you restore radar power. This
   enables the resistor supply and allows up to three seconds for both lines
   to read high continuously for 500 us before sending any key. The key then
   repeats for up to 30 seconds, alternating clock/data roles every 500 ms.
   There is no target-power sense wire: high data lines do not prove the radar
   is powered, and enabling GP12 while the radar is off can back-power it again.
   Coordinate `g` with power-on; do not leave it armed throughout a long off
   interval. If a separate target reset is available, reset while sending.
6. On ACK, it stops transmitting the key. Once D+ rises, it sends 1 kHz
   calibration edges for two seconds. Wait for **solid LED / SWAP TO PC USB NOW**.
7. Unplug the injector (including its pull-ups) and promptly connect the
   target to the PC's USB data connection, keeping target power applied.

The search times out after 30 seconds, with signal pins released, GP12 low and
fast LED blink. The separate startup high-level wait times out after three seconds.
Send `g` to retry. USB enumeration and any subsequent use of `jl-uboot-tool`
are separate steps. A powered but unresponsive application will generally need
a reset during key transmission or a fresh coordinated power-on attempt.

| Command | Action |
| --- | --- |
| `g` | Arm key search, automatic pin reversal, ACK detection and calibration (default) |
| `m` | Same key/ACK search, but release immediately for manual host calibration |
| `x` | Stop immediately, release GP10/11 and drive resistor supply GP12 low |
| `s` | Stop and reverse the starting clock/data mapping; automatic alternation still applies |
| `?` / `h` | Print state, frame count, current mapping and pin levels |

The optional button starts the default sequence when idle/finished/error and
stops an active sequence. The firmware never automatically rearms after ACK:
after a cable swap it cannot determine whether the PC enumerated the target.

## Timing and detection

PIO supplies a nominal 50 kHz clock: 10 us low / 10 us high, MSB-first `0x16EF`.
Both lines release after each word for at least 40 us. If both read low, sending
pauses until the low breaks or qualifies as an ACK. Qualification requires
500 us of observed low: the reported 1-2 ms ACK may already be partway through
when the preceding roughly 320 us word completes. Three microseconds of pull-up
settling are excluded from detection. Startup waits for high levels instead of
aborting on the first low sample, but rejects a bus still stuck low at timeout; a later short or target power loss can still imitate an ACK. Enumeration
is the definitive result. CPU polling can miss a response if delayed long enough.

Calibration always acts on physical **D+**, regardless of which key mapping
succeeded. PIO generates a 10 us low every 1000 us for two seconds. These are
clock-reference edges, **not encoded USB SOF packets**. The ROM behavior and
prior Pico implementation motivate this experiment; it is not USB emulation.
All ends, aborts and timeouts leave GP10/11 as inputs with internal pulls off
and GP12 driven low. This cannot remove back-power supplied by other adapters.
Pico W LED writes occur only when the LED changes, avoiding repeated CYW43
transactions in the polling loop.

## Build and checks

Open this folder as the PlatformIO project, or from here run:

```powershell
pio run
```

Output: `.pio/build/pico/firmware.uf2`. Pins are build flags in `platformio.ini`.
The committed configuration pins the platform and Arduino-Pico revisions.
The supplied build used `platformio.local.ini` with symlinks to locally installed
checkouts at those same revisions, avoiding another framework download. That
machine-specific file is ignored; `validation.json` records the exact inputs.

```powershell
python tests/check_waveform.py
cmake -S tests -B build/tests
cmake --build build/tests --config Debug
ctest --test-dir build/tests -C Debug --output-on-failure
```

The waveform check reads the actual ELF PIO instruction arrays and simulates
their bit order, clock period and calibration pulse period. Native tests cover
startup high qualification, settling/timeout, ACK qualification, broken intervals
and timer wrap. Neither tests electrical
rise times, USB enumeration, nor actual target ROM acceptance.

## Existing implementations and sources

- [czietz's working Pico/MicroPython dongle](https://gist.github.com/czietz/9a94cf3c3e68f2ceb45fab682e1cbbd5),
  reviewed revision `7c846aca65db47adbaad9e4e81dc1b9de1eb1f9d`:
  GP10 D+ clock, GP11 D- data, 50 kHz hardware SPI key, followed by two seconds
  of 1 kHz PWM. It has reported FM-1/WL80 success but no ACK gating; the author
  describes roughly a 50:50 entry chance. [Another user's success report](https://github.com/ip2k/lunar-modulator/issues/2#issuecomment-5890460122).
- [USB_KEY research](https://kagaimiq.github.io/jielie/isp/usb/usb-key.html):
  D+ clock, rising-edge sampling, ACK, external pull-up requirement, and
  calibration using 1 ms falling-edge spacing. This page agrees with the
  working examples; the older `jl-uboot-tool/docs/how-to-enter-uboot.md` text
  reverses clock/data labels. Hence default D+ clock and automatic reversal.
- [Original Arduino capture and successful experiment](https://github.com/christian-kramer/JieLi-AC690X-Familiarization):
  useful waveform evidence; AVR delay values cannot simply be reused on Pico.
- [ElectronicCats Pico prototype](https://github.com/ElectronicCats/jieli-ble-badge-research/tree/main/tools/pi-pico-jl-dongle):
  BR35 project with incomplete validation, not a ready BR23 recovery guarantee.
- [Arduino-Pico PlatformIO instructions](https://arduino-pico.readthedocs.io/en/latest/platformio.html).

This is a project-owned implementation of the published signal protocol, not
a copy of the MicroPython or Arduino sketches. No hardware was flashed while
creating it, and no change to the radar firmware was required.
