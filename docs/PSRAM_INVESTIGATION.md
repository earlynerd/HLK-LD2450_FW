# PSRAM presence investigation

Date: 2026-10-05. Static evidence only; no device probe or flash performed.

The BR23 supports a PSRAM controller, but there is no affirmative evidence yet
that this module contains usable PSRAM. Stock V2.04 and V2.14 layouts are
consistent with PSRAM being disabled. This does not rule out an unused memory
die in the package. Continue budgeting the demonstrated internal RAM until a
physical memory test or exact package identification establishes more.

## Findings

| Evidence | Observation | Interpretation |
| --- | --- | --- |
| Pinned official SDK `include_lib/driver/cpu/br23/asm/br23.h`, lines 60-68 | Defines `JL_PSRAM` at `0x1f0500`, with CON, BAUD and QUCNT registers. | Controller support, not an attached-memory inventory. |
| SDK `cpu/br23/sdk_ld.c`, lines 37-41 and 62-63 | `CONFIG_PSRAM_ENABLE` reserves the first 16 KiB of RAM; a 2 MiB region at `0x800000` is declared even without it. | The linker region alone proves neither physical capacity nor presence. |
| SDK `cpu/br23/tools/isd_config.ini`, line 76 | `psram=0;` | Default example disables PSRAM; not itself evidence about stock or physical hardware. |
| Both stock application startup sequences | PSRAM destination `0x800000`, copy length zero; initialized data starts at zero. | No startup PSRAM payload; layout lacks the pinned SDK's PSRAM cache reservation. Evidence against the standard PSRAM-enabled configuration. |
| Both extracted stock boot configurations | Eight bounded key/value records; no PSRAM key. | No explicit PSRAM option in these boot configurations. Missing key is not independently proof of the loader's default. |
| Both stock bootloaders | Contain `PSRAM` at byte offset `0x1f75`. | Generic bootloader capability/string; not proof that the branch executes or memory exists. |
| Current capture build | Empty PSRAM sections and zero PSRAM startup copy. | Custom firmware does not currently use PSRAM. |
| AC6956C datasheet V1.1 | Does not advertise PSRAM capacity or an in-package PSRAM option. | No manufacturer confirmation found. Datasheet omission does not prove physical absence; exact module MCU remains a working identification. |

The SDK is pinned by [sdk.lock.json](../firmware/sdk.lock.json). Its local source
cache is generated rather than committed. The manufacturer
[AC6956C datasheet](https://www.yunthinker.net/wp-content/uploads/2024/08/AC6956C-Datasheet-V1.1.pdf)
and [official SDK configuration example](https://gitlab.zh-jieli.com/soundbox/novisualization/ac695n_soundbox_sdk/-/blob/0f08348814fcdf320290418406fccdb4e81504ac/cpu/br23/tools/download/app_ota/isd_config.ini)
are additional references. The online SDK example is a different revision from
the pinned local SDK; the local file was checked directly.

## Reproduce the stock inspection

```powershell
python tools/inspect_psram_evidence.py
```

The script checks startup instruction prefixes against the ABI used by
`firmware/tools/audit_image.py`, extracts immediate operands, parses the known
packed boot configuration records with bounds checks, and records input hashes.
It does not emulate the firmware or establish execution of every possible
PSRAM initialization path.

Results: [static_evidence.json](../output/psram_analysis/static_evidence.json).

## What could establish physical presence

1. Exact MCU ordering-code/package documentation explicitly listing PSRAM.
2. An identified and correctly configured memory interface returning a valid
   memory-device identity, followed by capacity/alias checks.
3. A controlled, uncached read/write memory test after initialization, confirming
   independent storage rather than cached writes or address aliasing.

A read-only controller-register snapshot in a diagnostic build can tell whether
the interface is enabled, but a disabled interface does not establish absence.
The current capture firmware does not expose a register-read command. Any future
diagnostic image must run after the recovery gate and preserve the working image.
Do not simply dereference `0x800000`: an unconfigured mapping can fault or hang,
and apparent cached readback alone cannot prove physical memory. No initialization
or probing sequence has yet been validated for this module's package/pins.
