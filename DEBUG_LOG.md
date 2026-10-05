# Debug log

## 2026-10-04 — V2.14 entry probe required the actual module UART rate

- **Observation:** After a BLE update, the entry probe at 256000 received only zero bytes and no configuration ACK.
- **Root cause:** `firmware/tools/stock_uart.py:129` defaults to 256000; the connected module was measurably transmitting valid target frames at 9600. The reason the device rate changed is not established.
- **Fix:** Use the existing `--baud 9600` option. First attempt had a corrupt FF ACK header; an unchanged retry obtained FF/A0/B2 acknowledgements and START. No image data was sent, and no parser relaxation was needed.
- **Class:** baud-assumption
- **Recently-touched?** Yes, the probe was newly implemented; its valid-frame filtering correctly rejected the damaged ACK.
