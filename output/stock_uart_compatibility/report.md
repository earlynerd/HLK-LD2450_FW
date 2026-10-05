# Stock UART update compatibility

Static findings and entry-only bench results, 2026-10-04. No firmware data sent or flashing performed.
The accompanying manifest pins both stock application hashes; selected vendor
disassembly is retained in v214.asm and v204.asm.

## V2.14 transparent firmware

- Configuration command dispatch subtracts 0xA0 and admits 37 entries at
  VMA 0x1e11e0e. Command 0xB2 selects index 18 in the halfword table at
  0x1e11e82. Entry 0x1D9 targets 0x1e12234, which sets RAM byte 0x7390 to 1
  and returns a command-0xB2 response. The normal configuration gate applies:
  the dispatcher admits 0xFF before configuration is enabled, other commands
  require it. Candidate entry is configuration-enable then 0xB2.
- VMA 0x1e15602 tests that same byte before parsing AA 55, little-endian length,
  payload and CRC. Its opcode table includes READY 6, which posts the updater
  task's READY message. The host now implements this product entry wrapper
  under explicit `--entry stock-b2` and in the no-image `stock_uart.py` probe.
- VMA 0x1e19648 changes the negotiated baud and emits START with four baud
  bytes. Our original PC peer rejected this valid five-byte payload. The peer
  now accepts opcode-only START and START+baud, with baud range validation.
- VMA 0x1e19532 sends STOP and sets the saved baud to 9600. Whether successful
  loader staging invokes this callback before handoff is not established;
  do not assume successful handoff necessarily changes to 9600.
- VMA 0x1e19552 writes zeros at handoff-private offsets 0 and 4 and saved baud
  at offset 8. Under the pinned SDK UPDATA_UART ABI these are TX, RX and baud.
  Stock loader/default-pin semantics remain unresolved. This is a concrete
  compatibility question, not proof that stock serial updating is broken.

## V2.04 normal firmware

- Its configuration dispatcher at VMA 0x1e11634 admits 0xA0..0xB1 in this
  command group, then tests other explicit commands. 0xB2 has no handler in
  this dispatcher. The UART_UPDATE strings and corresponding task seen in
  V2.14 are absent. A stock V2.14 entry sequence must not be advertised as
  working with V2.04. Other boot/download routes are not excluded by this.
- Both UFWs contain uart_user.bin. A loader being bundled in the update
  container does not establish an application entry service in both images.

## Compatibility directions

Our running application can serve either pinned stock UFW through the same
host remote-file protocol: the uploader does not require a custom image and
our application supplies its own handoff parameters. Actual stock restoration
still requires loader acceptance and a bench test. Once V2.04 is restored,
its application entry capabilities return too; our updater service is gone.

Stock-to-custom is version-dependent. V2.14's recovered entry sequence is now
implemented and host-tested, but no complete physical transfer is established.
The user accepts a BLE update from V2.04 to the stock V2.14 image as the bridge
before the first UART custom installation. The separate entry probe sends no
START response or file data; even a successful result does not validate the
staged loader, handoff, or firmware programming.

## Official Ai-Thinker PC updater

The [official Rd-03D_V2 page](https://docs.aithinker.com/Rd-03D_V2/index.html)
links an English serial burning tool archive. Its executable and archive are
pinned in `vendor_tool_manifest.json`. The program was not executed; selected
x64 disassembly and resolved import names are in `vendor_tool.asm`.

- VMA 0x140007cdc supplies argument 0x66 to the imported
  `ICLM_Interface_RadarDevice_Protocol_SendCommand_NoCheckAck`, with no data.
  The DLL's wire encoding has not been reconstructed here, so this is not a
  claim that the transmitted LD2450 command is 0x66.
- VMA 0x140007d27 supplies baud 9600 to serial reopen after that call.
- VMA 0x140007dab builds READY opcode 6; 0x140007f7d / 0x140007fcd build START
  opcode 1 with baud 9600. Its receive loop recognizes read/stop/size/keepalive
  opcodes 2..5. The read handler extracts offset and count as 32-bit values.

This independently supports the remote-file protocol already recovered from
the SDK. It does not establish the Ai-Thinker product wrapper as compatible
with Hi-Link firmware. We use the Hi-Link application's own recovered B2 path.

## Entry-only bench test: stock V2.04, COM13

On 2026-10-04 the user identified COM13 and authorized testing loader entry.
At 256000 baud, the probe received successful acknowledgements for configuration
entry (FF), firmware version (A0), and subsequent configuration exit (FE).
The version bytes were `00 01 04 02 15 19 10 23`, consistent with V2.04.
Command B2 received no acknowledgement during its two-second deadline. Three
CRC-framed READY requests over the following three seconds produced no updater
START frame. This confirms the tested B2 entry path did not work on this unit;
it does not exclude every possible stock serial boot/download route.

The final FE acknowledgement confirms configuration mode was exited. No START
acknowledgement, image data, reset command, or baud change was sent. DTR/RTS
were configured deasserted. Raw byte traffic and timings are preserved in
`bench_com13_v204.json`. The next test is the same probe after the user installs
stock V2.14 using the existing BLE updater.

## Entry-only bench test: stock V2.14, COM13

After the user updated through BLE, the module's UART output was readable at
**9600 baud**, not the previous 256000. This establishes the rate on this unit
at this time, not a universal V2.14 default. A passive scan received valid
`AA FF 03 00 ... 55 CC` target frames at 9600; other tested rates yielded zeros.
The 256000 entry probe received no valid acknowledgements.

At 9600, the first attempt received a damaged configuration-ACK header
(`E0 FC FB FA`, where `FD FC FB FA` was expected). The parser correctly rejected
it, and subsequent FE was acknowledged. Repeating the unchanged probe at 9600
succeeded: FF, A0 and B2 were acknowledged; READY produced CRC-valid START
payload `01`. The reported version bytes were `00 01 14 02 12 24 11 25` (V2.14).
The exact exchanges are retained in `bench_com13_v214_9600_success.json`, with
separate first-attempt and passive-check logs.

**Confirmed:** stock V2.14's B2 UART application-update entry is accessible on
the normal module serial interface. **Not tested:** START/baud negotiation,
loader staging, reset/handoff, flash programming, custom boot or restoration.
No START acknowledgement or image data was sent. The successful probe left the
application in its update service; power-cycle before another fresh-entry test.
For this unit, use `--baud 9600` on the probe and `--initial-baud 9600` on the
uploader; the uploader's separate `--baud` controls subsequent negotiation.

The earlier configuration-only control captured 23 target-frame headers in
2 seconds before FF, zero bytes during 3 seconds in configuration, and 21
headers in 2 seconds after FE. Its firmware version was not queried, and the
user subsequently reported an overlapping BLE update, so the control's
`v204` filename must not be treated as verified firmware identity.
