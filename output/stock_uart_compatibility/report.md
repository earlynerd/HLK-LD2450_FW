# Stock UART update compatibility

Read-only static findings, 2026-10-04. No serial commands or flashing performed.
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
  task's READY message. This establishes a product entry wrapper that our
  uploader currently does not send.
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

Stock-to-custom is version-dependent and not yet implemented end-to-end.
V2.14 now has a recovered entry candidate; V2.04 needs another established
route. Resolve handoff semantics and model the full serial dialogue before
presenting an initial-install command as supported.
