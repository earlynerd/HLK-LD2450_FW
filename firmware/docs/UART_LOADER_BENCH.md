# LD2450 UART loader bench result

**Current result (2026-10-05):** The corrected hello application boots, survives
a power cycle, and accepts a different custom build through its UART updater at
256000 baud. See [the current image and bench evidence](IMAGE_BUILD.md).
Stock restoration was verified later (2026-10-08, [UART_UPDATE.md](UART_UPDATE.md#restoring-stock-firmware)). The observations below
retain the history of the earlier failed applications.

On 2026-10-04, stock V2.14 on COM13 at 256000 baud accepted the custom
baseline image and its second-stage loader reported final success (`03 00`)
after 419 file-read requests. **Application boot is not yet verified:** PA9
on COM11 produced no custom banner at 115200, and a subsequent READY probe
received no reply. The user subsequently reported continued silence, including no RX LED activity
during a power cycle. The COM11 power-cycle capture file contains zero bytes.

## Reproduce the loader fixes

After building the application as described in [IMAGE_BUILD.md](IMAGE_BUILD.md):

```powershell
python -m pip install lz4 pyserial
python firmware/tools/patch_stock_uart_loader.py --input firmware/build/image/update.ufw --out firmware/build/image/update-two-wire.ufw
```

The patcher performs no device operation. It requires the exact SHA-pinned
vendor `uart_user.bin`, checks/decompresses its LZ4 stream using preceding
blocks as the dictionary, modifies exactly two four-byte instruction slots,
recompresses it, and rebuilds the nested CRCs. All application and non-OTA
components remain byte-identical. The compressed result fits the original
loader slot. Unknown loaders are rejected.

| Loader VMA | Original | Replacement | Evidence |
| --- | --- | --- | --- |
| `0xa40e` | `r1 = [r4+128]`, handoff TX pin | `r1 = 1; nop`, PA1 TX | Stock V2.14 passes PA0 for both TX/RX at `0x1e19552`; the loader selects one-wire mode when they match. PA1-only patch made the loader emit START on the ordinary module UART. RX remains PA0. |
| `0xa482` | `r2 &= 0x30`, then writes UART1 CON1 | `r2 = 0; nop` | At 256000 the original computation writes `0x30`. START retries received no accepted reply, including with a 10 ms host delay. A temporary diagnostic found an empty receive DMA buffer. Clearing CON1 allowed both START exchanges and the complete programming transaction. |

The SDK's normal `uart_dev.c` baud setter does not install this CON1 value;
its single-wire path toggles bit 4 around transmission. The bench establishes
the failure and successful workaround at **256000**, not a complete register
specification or validation of every baud rate. The PA1 override applies to
the valid nonzero-baud handoff path. No diagnostic payload changes are included
in the final two-wire image.

For a stock V2.14 module whose current UART rate is 256000, the writing command
is:

```powershell
python firmware/tools/uart_upload.py firmware/build/image/update-two-wire.ufw --port COM13 --entry stock-b2 --initial-baud 256000 --baud 256000
```

This writes firmware. Substitute the actual port. V2.04 needs the previously
documented BLE update to V2.14 first. Use the currently verified hello image
from IMAGE_BUILD.md rather than the historical build/image artifact above.
Custom-to-custom application replacement is now verified for hello;
custom-to-stock restoration was verified on 2026-10-08.

## Exact artifacts and observations

- Original custom UFW: `eacb4d81bfe249967c159b94150689de7e71769d8d9d13b199317c12e6aabd6b`.
- Programmed two-wire UFW: `689d37b86a26be8d209dfcdda033b530c08f2e27d949528784fc1e65cc98ed4f`.
- Application: 75052 bytes, `50c02943717d6fa9afd414e9d2eba39af409f46c6ff5246ee3ee4414e23dbcf2`.
- Patched compressed loader: 17953 bytes, `c2f79a161743879655ea4d42f2588e66ef93783a5de419766a393b3c289bc9f7`.
- [Successful programming trace](../../output/stock_uart_compatibility/tenth_custom_flash_con1_clear/events.jsonl)
  and [result](../../output/stock_uart_compatibility/tenth_custom_flash_con1_clear/result.json).

The first 45 reads stage the loader. Successful staging is not application
programming: the unmodified loader returned to stock with `UPDATA_DEV_ERR`
(`0x5a04`); the PA1-only patch reached four START retries but still returned
to stock. The final trace continues through a content-size notification and
374 additional reads before `03 00`. Stock did not send staging STOP `03 80`,
so `loader_staged: false` in the host report means that status packet was
absent, not that the loader failed to run.

COM11 was captured at 1 Mbaud during stock staging, then changed to 115200
before acknowledging final success. The file named `debug-com11-1mbaud.bin`
in the final attempt therefore spans both rates; the baud change is timestamped
in `events.jsonl`. It ends at the stock staging reset message. The separate
postflash captures on COM11 and COM13 were empty. No custom boot, radar init,
or repeat-update claim follows from loader success alone.

## 2026-10-05 - Second module, audited hello with module-UART heartbeat

Stock V2.14 responded on COM13 at 256000 before flashing. Programmed
`firmware/build/hello-heartbeat/update-two-wire.ufw`, SHA256
`1b215c1abf083cb50897cc8a53241ea85dbc8d2d5bc7bef58496e78def57cbee`.
The loader reported final success after 419 read requests, with no error.
A subsequent 12-second COM13 capture contained zero bytes. Four READY-only
requests over four seconds also received zero bytes; no second image was sent.
PA9 connection was not confirmed and was not captured. Cold power-cycle
behavior is pending. This verifies the programming transaction again, not
custom application boot or repeat updating. Root cause remains unresolved.
Evidence: `output/stock_uart_compatibility/hello_heartbeat_flash_20261005T165015Z/`.
