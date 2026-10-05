# UART update integration investigation

Status: 2026-10-04. The application-to-loader route is established from the
pinned SDK source, its compiled library, and its bundled protocol specification.
The BR23 ABI checks compile with the actual target compiler. No UART receiver
has been added to our application, no complete application has been linked,
and no device has been updated in this investigation.

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
table omits this value. A future PC host must accommodate the actual loader
behavior and remain available across the reset between stages.

The stock example and archived UART driver begin at **9600 baud**. The PDF
illustrates 9600 entry, a 10,000-baud loader-staging phase, and a later negotiated
firmware-transfer rate. These are evidence for the vendor implementation,
not proof of the Ai-Thinker tool's exact behavior. Its documented 256000-baud
setting and any product-specific entry wrapper still need a capture or tool
analysis. For our own application/host pair we can choose a documented entry
rate, but must keep the negotiated baud consistent through the loader handoff.

## Proposed integration in our application

Use a project-owned receiver over the existing module UART, with the vendor
update engine handling UFW verification and loader staging. Keep the cached
SDK unmodified. Implement the receiver under our own feature flag; leave the
two conflicting vendor UART example sources disabled. The protocol is known
well enough to implement without depending on the Ai-Thinker executable.

1. **Initialize the update runtime.** Retain the `app_update_init` initcall and
   common state handler from `apps/common/update/update.c`, or an explicitly
   audited board adaptation of them. This calls `update_module_init` and
   retains `UPDATE_CH_SUCESS_REPORT` for the subsequent handoff. Calling
   `app_active_update_task_init` before this initialization dereferences an
   uninitialized library control pointer. Retain the RTOS `update` task entry.
   Remove unrelated audio/UI/test-box dependencies in the board adaptation.
   Include `UPDATE_APP_EN` in `config_update_mode`: the header explicitly
   includes user UART updating under this bit. `UPDATE_UART_EN` alone is not
   the documented configuration for this route.
2. **Give the transport one owner.** Use PA1 TX / PA0 RX through our existing
   `module_uart`. Pause normal reports and radar acquisition on accepted entry;
   disable both SPI DMA engines and turn off radar power/bias. Keep PA9 debug
   output separate. Add a baud-change operation to our peripheral API and use
   a bounded stream parser; a 1024-byte RX ring is a practical first size
   because a reply containing 512 data bytes occupies 527 wire bytes, larger
   than our current 512-byte ring. Define task ownership explicitly: a UART
   service task receives and validates responses while the update task waits
   on a semaphore. Do not let both tasks read the same UART stream.
3. **Implement `update_op_api_t`.** `ch_init` stores the library's resume/sleep
   callbacks; `f_open` resets the UFW offset; `f_read` requests bytes at that
   offset with bounded retries; `f_seek` changes it; `f_stop` sends status;
   `notify_update_content_size` supplies progress; `ch_exit` releases session
   state. Validate data into a separate response buffer before waking the
   waiting reader. Chunk reads to a supported size and never report bytes
   that were not received. Verify the library's failure/short-read contract
   while implementing the adapter.
4. **Start the engine after negotiation.** Pass a persistent callback table in
   `update_mode_info_t` with `.type = UART_UPDATA`, `.task_en = 1`, and the
   application state callback to `app_active_update_task_init`. Check its
   return value and reject duplicate sessions. The library copies the mode
   structure, but the callback table and transport state must remain alive.
5. **Handoff after verified success.** Require a valid success report and
   successful `UPDATE_CH_EXIT` status. Fill `UPDATA_UART` with TX, RX, the
   actual handoff baud and timeout; copy it into `UPDATA_PARM.parm_priv`.
   Call `update_mode_api_v2(UART_UPDATA, fill_parameters, reset_callback)`.
   Keep the vendor's common success-report handling, which supplies the
   loader address and flash-record writer. Complete UART acknowledgments
   and peripheral shutdown before the v2 call: its common handler disables
   interrupts before invoking the reset callback. The v2 path does not call
   `update_close_hw`, so merely registering a driver-close hook is insufficient.
6. **Keep entry available on subsequent boots.** Initialize the UART update
   service even if radar initialization fails. Include it in every custom
   firmware build. Test the full cycle twice: stock/custom entry -> custom A
   -> custom B, with a version banner proving each application booted.

The target-compiled ABI assertions confirm `UPDATA_UART` is **16 bytes**,
despite its stale “12 bytes” source comment; `UPDATA_PARM` is 80 bytes with
`USE_SDFILE_NEW=1`. Use the SDK types and `sizeof`, not a hand-written packed
record derived from comments. The SDK linker also reserves the update RAM
region; preserve that reservation and its startup behavior in the full image.

## Why the shipped example needs repair

| Finding in pinned SDK | Consequence / required handling |
| --- | --- |
| `uart_update.c:10` and `uart_update_master.c:2` both select MASTER | Selecting SLAVE excludes both; selecting MASTER includes conflicting implementations. The bundled guide explicitly calls `uart_update.c` the slave. |
| `update.c:513-514` references `sava_uart_update_param` for SLAVE | Declaration exists, but no definition was found in SDK source or `update.a`. Resolve this legacy path if adopting the vendor macro; the proposed custom adapter uses the v2 route with vendor examples disabled. |
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
