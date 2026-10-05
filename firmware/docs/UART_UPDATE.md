# UART update integration investigation

Status: 2026-10-04. Our application receiver, complete image builder and PC
uploader are implemented and host-tested. Stock-to-custom serial installation
and physical stock restoration are not yet verified. The
[stock compatibility investigation](../../output/stock_uart_compatibility/report.md)
finds a 0xB2 entry wrapper in V2.14 that is absent from the V2.04 command
dispatcher, plus START negotiation and handoff details requiring attention.

## What runs where

The application implements a small update entry/transport service. It exposes
the UFW on the PC as a remotely readable file to JieLi's update library. The
library selects and stages the appropriate loader, verifies it, and supplies a
success report. The application records the handoff parameters and resets.
The staged loader then uses the same UART protocol to obtain and program the
application contents. Every replacement application must include the entry
service for the next update.

The exact mapping in this SDK's `update.a:download_loop.c.o` is:

```text
UART_UPDATA = 0x5a04 -> ota.bin / uart_user.bin
```

This is confirmed by reading the library's LLVM bitcode, not inferred from
filenames. Both extracted stock packages contain an identical 18,212-byte
`uart_user.bin`, SHA-256
`96e6fff47bf911e9a02f7ee62fb398fb37ccf44204a1e77ae782f5d1b3ab294e`.
That establishes availability, not compatibility of an arbitrary repackaged
image with the board's existing boot and flash configuration.

For single-bank updating, reserve enough flash/VM space for the selected loader
plus the updater's records and alignment requirements. Do not budget only the
18,212 bytes. Keep `support_dual_bank_update_en = 0` for this design and build
a matching UFW containing `ota.bin`. Boot metadata, product identity,
flash layout, and encryption settings must agree with the installed image.
The application receiver does not need to contain the full loader as a C array.

## Protocol we can implement

The bundled *JieLi UART upgrade specification*, revision 1.00, 2020-04-29,
pages 5-10 defines the two-stage flow and the packet format:

```text
AA 55 | payload_length:u16le | opcode + arguments | CRC16:u16le
```

CRC is CRC-16/XMODEM over the header, length, and payload; the CRC excludes
its own two bytes. Multi-byte arguments are little-endian. These byte orders
are unrelated to the radar's big-endian sample stream.

| Opcode | Device / host exchange | Application responsibility |
| --- | --- | --- |
| `06` | Host asks application to enter update mode | SDK extension: `CMD_UART_UPDATE_READY`; respond with START after quiescing acquisition |
| `01` | Device START; host replies with a 32-bit baud rate | Negotiate, repeat START after changing baud, then start remote-file reads |
| `02` | Device requests 32-bit UFW offset and length; host echoes both plus data | Validate offset, size, payload length, and CRC before completing a read |
| `03` | Device reports stop/status; host acknowledges | Distinguish loader-stage completion from final application completion |
| `04` | Device reports 32-bit transfer length; host acknowledges | Track progress separately for the two stages |
| `05` | Device keepalive; host acknowledges | Keep the host connected during flash operations |

Opcode `06` is present in the SDK header and both example sources; the PDF
shows an entry notification but does not define its bytes. The master example
also recognizes status `0x80` as loader-download completion; the PDF's status
table omits this value. Our PC peer remains available across the reset between stages; actual loader
behavior still needs a transaction capture.

The stock example and archived UART driver begin at **9600 baud**. The PDF
illustrates 9600 entry, a 10,000-baud loader-staging phase, and a later negotiated
firmware-transfer rate. These are evidence for the vendor implementation,
not proof of the Ai-Thinker tool's exact behavior. Its documented 256000-baud
setting and any product-specific entry wrapper still need a capture or tool
analysis. For our own application/host pair we can choose a documented entry
rate, but must keep the negotiated baud consistent through the loader handoff.

## Implemented integration in our application

See [IMAGE_BUILD.md](IMAGE_BUILD.md) for complete build and transfer commands.
`target/br23/image/uart_loader.c` implements the project-owned receiver over
PA1 TX / PA0 RX. The conflicting vendor examples remain disabled. Our
application calls `update_module_init` before any session and uses
`UART_UPDATA` with the real vendor UFW verification/staging engine. The linked
configuration includes `UPDATE_APP_EN`.

The adapter uses synchronous engine operation (`task_en=0`) in `app_core`.
That task alone reads UART; no queued frame can race a second UART reader.
The SDK resume/sleep hooks are unnecessary because our callback performs its
own bounded blocking reads. RX has a 1024-byte ring and TX has a separate
frame buffer. `f_read` splits requests into 512-byte chunks, verifies CRC,
echoed offset/count and exact length, retries four times and returns zero
without advancing the file offset if a chunk cannot be obtained.

The receiver accepts READY at 256000 baud, negotiates START, and retains that
actual baud through the handoff. After the success report and a successful
EXIT, it sends/acknowledges STOP `0x80`. The adapter implements the audited
record construction used by `update_mode_api_v2`: type, magic, loader address,
UART parameters and CRC. It additionally zeroes the whole 112-byte record
and checks the library writer's byte status (zero success) before resetting.
The vendor v2 helper itself ignores that writer result.

The target compiler checks `UPDATA_UART == 16` and `UPDATA_PARM == 80` bytes.
The reserved 128-byte update RAM begins at `0x2ff80`, with the record at
`+8`, leaving 120 available bytes. The application preserves the SDK linker
reservation, copies 112 bytes, and resets only after peripheral shutdown.
Entry is included in every image built here. Aborted sessions return to
256000 baud. Radar startup runs first with bounded I2C deadlines; any radar
failure powers it down and preserves UART entry. Accepting READY powers the
radar down, and aborted update sessions leave it off until reboot. A failure
to initialize the basic MCU peripherals currently resets the MCU.

A Python PC peer implements our entry protocol and serves both stages. Its
behavior, the adapter, framing and failure paths are host-tested. The vendor
engine and stock `uart_user.bin` have not been run in these tests, and actual
boot, loader acceptance and repeated device updates remain bench work.

## Why the shipped example needs repair

| Finding in pinned SDK | Consequence / required handling |
| --- | --- |
| `uart_update.c:10` and `uart_update_master.c:2` both select MASTER | Selecting SLAVE excludes both; selecting MASTER includes conflicting implementations. The bundled guide explicitly calls `uart_update.c` the slave. |
| `update.c:513-514` references `sava_uart_update_param` for SLAVE | Declaration exists, but no definition was found in SDK source or `update.a`. Resolve this legacy path if adopting the vendor macro; our adapter constructs the v2-format record with vendor examples disabled. |
| `uart_data_decode` accepts unchecked packet lengths | It can write beyond its frame buffer or read missing arguments. Enforce frame and per-command bounds before copying or dispatching. |
| `uart_dev_receive_data` returns requested length after all retries fail | It can falsely advance the UFW offset. Return a real failure and preserve offset instead. |
| Read response copy uses received frame length without bounding it to the requested length | Validate echoed offset, echoed count, actual payload size, and destination capacity together. |
| RX, TX, and task messages share `protocal_frame` | Later UART activity can overwrite queued commands or an unread response. Separate owned buffers and synchronization. |
| `uart_f_stop` changes `update_baudrate` back to 9600 | Handoff subsequently reads this variable. Preserve the actual negotiated baud for successful handoff; restore entry baud only on a deliberate aborted-session transition. |
| Archived driver directly owns UART1, IRQ 19, and a 544-byte DMA buffer | It bypasses `uart_dev_open` ownership. Adding it alongside our dynamic UARTs could overwrite the PA9 debug UART or another allocated UART1 user. |
| Master source and PDF differ on START/STOP payload details | Use the specification plus a real transaction trace to establish compatibility; do not copy either example as a proven end-to-end implementation. |

## Evidence and reproduction

Run the read/compile-only investigation:

```powershell
python firmware/tools/analyze_uart_update_sdk.py
```

It extracts three library members into `firmware/build/uart-investigation`,
converts their bitcode to readable LLVM IR, saves the archive symbol inventory,
checks the UART loader mapping, and compiles ABI assertions for PI32V2/r3.
It does not link an application or run SDK download tools.

The [analysis manifest](../../output/uart_update_analysis/manifest.json)
records inspected source/PDF hashes, SDK commit, compiler provenance, and
the commands used. The source paths are relative to the project root.

Primary references in the pinned SDK:

- `doc/功能模块说明文档/串口升级相关说明文档/杰理串口升级规范.pdf`, pages 5-10.
- `doc/功能模块说明文档/串口升级相关说明文档/AC695x串口升级说明.pdf`, pages 1-2;
  its internal title says AC693x, so source/library verification is important.
- `apps/common/update/uart_update.c`, `uart_update_master.c`, `update.c`.
- `include_lib/update/update.h`, `update_loader_download.h`, `uart_update.h`.
- `include_lib/liba/br23/update.a`, especially `download_loop.c.o`,
  `uart_update_driver.c.o`, and `update_main.c.o`.

JieLi's public [OTA architecture description](https://doc.zh-jieli.com/AC63/zh-cn/master/module_demo/ota/ota_introduce.html)
corroborates loader staging in VM space for single-bank updating. Its
[UART integration instructions](https://doc.zh-jieli.com/AC63/zh-cn/master/module_demo/ota/ota_use.html)
describe role and pin selection, but concern the AC63 documentation family;
the pinned BR23 sources and library are the concrete implementation evidence.
