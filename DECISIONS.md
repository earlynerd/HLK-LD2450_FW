# Decision Log

Forward-facing, append-only record of architectural and behavioral decisions for this project. Search this file when structural history can affect the task; newer applicable decisions supersede conflicting older statements.

When a decision is reversed or superseded, append a new entry rather than rewriting the old one.

## 2026-10-03 — Start a BR23 firmware component from the observed interfaces

- **Decision:** Target the likely AC695N/AC6956C using the pinned JieLi BR23 SDK and the RD-03D-derived pin map. Initialize dual receive-only SPI, I2C, module/debug UARTs, and power/bias GPIOs; keep radar power off at startup until configuration traffic is captured. Use direct SPI initialization because the stock driver configures PB1/RESET as an output. CS remains a separately observed input. Provide one-shot DMA and a portable DS RAW record decoder, retaining short boot I/Q as unvalidated.
- **Why:** The schematic and captures support peripheral setup now, while register initialization, continuous acquisition, and tracking require further evidence. Separate the host-tested component from the SDK image-link and hardware validation stages.
- **Supersedes:** (initial)
- **Affects:** `firmware/`, internal interface reference, future radar boot/acquisition implementation.

## 2026-10-04 — Build configurable radar initialization components

- **Decision:** Generate firmware register profiles from the recovered stock tables plus guarded, one-based write-occurrence overrides. Preserve the 75/5 split and provide an explicit fail-fast I2C stage writer. Use the signed official toolchain unpacked into the project cache for target compilation; keep automatic radar startup disabled pending measured power/bias timing and application integration.
- **Why:** Register experiments need reproducible custom builds, and repeated register addresses must retain their startup roles. The first bootable test application can use the logic analyzer for sample observation while application linking and a board-specific loading method are established.
- **Supersedes:** The initial 2026-10-03 component scope now includes recovered/customizable register data and actual target component compilation; its power-off startup contract remains.
- **Affects:** `firmware/` profile generation, init API, component builder, and register experiment workflow.

## 2026-10-04 — Plan UART updates around the existing module UART

- **Decision:** Use a project-owned, bounded UART update receiver over PA1 TX / PA0 RX and the vendor UFW staging engine, with `UART_UPDATA` selecting `uart_user.bin`. Keep the entry service in every replacement application and preserve it when radar startup fails. This records the integration design; the receiver is not yet implemented.
- **Why:** The bundled protocol and library establish the route, while the example receiver has compile-guard, buffer, retry, and baud-state defects. Its separate low-level driver also directly claims UART1, conflicting with dynamic UART ownership.
- **Supersedes:** (initial UART update design)
- **Affects:** `firmware/docs/UART_UPDATE.md`, future application startup, UART ownership, and UFW packaging.

## 2026-10-04 — Link a UART recovery application and package stock-layout UFWs

- **Decision:** Run a bounded custom UART receiver synchronously in `app_core`, using the vendor update engine and preserved `uart_user.bin`. Require successful staging, STOP acknowledgement and verified handoff-record persistence before reset. Link the minimal SDK startup at the stock `0x1E00120` entry, retain the selected register table, and keep radar supply/bias off. Package all four flash variants using a SHA-pinned stock UFW and fixed application slots; keep building separate from the explicit-port PC uploader.
- **Why:** This supplies reproducible complete images and a repeatable-update entry service without importing conflicting soundbox UART or board initializers. One UART owner avoids queued-frame races. Stock-template packaging preserves the known bootloader/layout while byte-identical no-op roundtrips and an independent decoder check its transforms. The clock default and all physical loader/boot behavior still require bench verification.
- **Supersedes:** The UART implementation-pending status above and the earlier component-only build scope. Automatic radar startup remains pending captured supply/bias timing.
- **Affects:** `firmware/target/br23/image/`, UART protocol/PC peer, compiler setup, image builder/packager, and `firmware/docs/IMAGE_BUILD.md`.

## 2026-10-04 — Apply the captured radar profile at boot in recovered stock order

- **Decision:** Enable supply with REXT low, wait at least 20 ms, apply the selected profile's first 75 writes, configure both SPI receivers, assert REXT, wait at least 3 ms, and apply the final five writes. Leave REXT asserted. The SDK timer has 10 ms resolution, so waits round up with a full tick of margin. A radar failure powers it down but preserves UART updating. Acquisition remains separate.
- **Why:** The capture matches all 80 mode-2 writes, and stock code establishes late REXT assertion. Initial REXT low and the settling margins are engineering choices; the captured 2.424396 ms boundary includes SPI/GPIO work, and the stock 1000-loop argument has no established time unit. The user authorized using this evidence without requiring rail captures.
- **Supersedes:** Earlier automatic-startup-disabled and capture-prerequisite decisions.
- **Affects:** Startup, independent supply/bias control, SPI preparation, host failure tests, and image/experiment documentation. Target builds are not bench validation.

## 2026-10-04 — Require explicit stock-to-custom and restoration compatibility

- **Decision:** Treat installing over stock and restoring stock as required compatibility directions, not implied consequences of SDK protocol support. Accept both SDK START payload forms in the PC uploader. Keep stock entry unsupported until the version-specific wrapper and handoff are integrated and validated.
- **Why:** The user expected both directions. V2.14 has a recovered configuration-command 0xB2 wrapper; V2.04 lacks that handler. Stock STOP/baud and zero-valued handoff pin fields need further interpretation. Restoring V2.04 also removes our application's UART entry service.
- **Supersedes:** Any implication that the custom application/host pair alone establishes stock firmware interoperability.
- **Affects:** UART updater, compatibility report and UART integration documentation. No device update was performed.
