# BR23 hardware FFT engine

The BR23 (AC695N) has an FFT accelerator. The pinned SDK
(`firmware/sdk.lock.json`, commit 641e45d) exposes it without any header:
`media.a` member `hw_fft.c.o` and `libFFT_pi32v2_OnChip.a`. Both are LLVM
bitcode with debug information. The project toolchain's clang turns them back
into readable IR with the original parameter names:

```powershell
$B = "firmware/.cache/toolchain/extracted-2.5.2/C$/JL/pi32/bin"
& "$B/llvm-ar.exe" x firmware/.cache/sdk/include_lib/liba/br23/media.a hw_fft.c.o
& "$B/clang.exe" -target pi32v2 -x ir -S -emit-llvm hw_fft.c.o -o hw_fft.ll
```

An `ac695n_soundbox_sdk-master.zip` supplied on 2026-10-08 is byte-identical to
the pinned checkout (1,698 of 1,698 files) and adds nothing. Everything below
comes from the IR; the hardware behaviour was measured on 2026-10-08 (below).

## Driver API (source `.../cpu/br23/hw_fft.c`)

```c
typedef struct {
    unsigned int fft_config;   /* from hw_fft_config() */
    int *in;                   /* 32-bit samples */
    int *out;
} pi32v2_hw_fft_ctx;

unsigned int hw_fft_config(int N, int log2N, int is_same_addr, int is_ifft, int is_real);
void hw_fft_run(unsigned int fft_config, const int *in, int *out); /* builds ctx, calls wrap */
void hw_fft_wrap(pi32v2_hw_fft_ctx *ctx);                          /* OS mutex around the engine */
```

`libFFT_pi32v2_OnChip.a` adds fixed-point `firfft`/`firifft` (real FFT/IFFT via
`struct fifft_config {N, log2N, ...}`) on top of the same `hw_fft_wrap`. It
also has float variants (`flrfft`, `flcfft`, ...). The `fCos_Tab` and `Get_FFT_Base`
symbols suggest those float variants are software implementations.

## Configuration word (`hw_fft_config`)

```
cfg = (N << 16) | A | B | (is_real << 1) | is_same_addr
forward, real:     A = (log2N - 3) << 4   B = (log2N - 2) << 8
forward, complex:  A = (log2N - 2) << 4   B = (log2N - 1) << 8
inverse, real:     A = 0x24               B = (log2N - 2) << 8
inverse, complex:  A = 0x34               B = (log2N - 1) << 8
```

`is_same_addr` is set when `in == out` (in-place). The meanings of the A and B
fields are not established. A plausible reading is a per-transform scaling
shift plus a stage count, with bit 2 marking an inverse, but that is inference.
Use `hw_fft_config()` values rather than hand-building the word.

## Register sequence (`hw_fft_wrap`)

`JL_FFT` lives at 0x102000 (`csfr.h`: CON, CADR, TEST0, TEST1). The engine reads the
ctx structure itself (the address of the struct, not the data, goes to CADR):

```c
JL_FFT->CON = 0;
JL_FFT->CON |= BIT(8);              /* enable */
JL_FFT->CADR = (u32)ctx;            /* {fft_config, in, out} */
JL_FFT->CON |= BIT(0);              /* start */
while (!(JL_FFT->CON & BIT(7)));    /* done flag */
JL_FFT->CON |= BIT(6);              /* clear pending */
```

The SDK wraps this in an OS mutex created on first use. The audio code also
uses `JL_FFT->CON = BIT(1)` to force the engine off (`cpu/br23/audio_common/app_audio.c`).
`IRQ_FFT_IDX` = 32 exists, but the SDK driver polls.

## Measured on hardware (2026-10-08)

Self-test build: `--fft-selftest` (`target/br23/image/fft_selftest.c`), image
`firmware/build/stream-raw16-p256-fftself`, SHA-256
`c4d88f5bf49b561801268b47500fe562026aff01c39ae514ca95335fe2b640ee`. It ran at start-up
with buffers in ordinary internal RAM (4-byte aligned, 0x1EB44/0x1FB44). The PA9 log
`output/fft_selftest/pa9_20261008-012401.txt` was checked by
`firmware/tools/fft_selftest_check.py` (report `check_20261008-012401.json`):

| Case | Result |
|---|---|
| 512-point complex forward | Matches `numpy.fft.fft` to -105 dB: natural bin order, interleaved int32 re/im, **unscaled** (gain 1.000). 58 us first call; 16 calls 845 us (53 us each). |
| Full-scale int16 inputs | Exact (-118 dB), no overflow; largest output 1.39e6. |
| In place (`is_same_addr`) | Identical to the separate-buffer result. A separate input buffer is not modified. |
| 256-point complex | Exact, unscaled, 21 us. |
| 512-point real | Exact; writes N/2+1 complex bins (514 words), unscaled, 28 us. |
| 512-point inverse | Exact; output = `numpy.fft.ifft` (scaled by 1/N), 94 us. |
| Impulse 16384 | Flat 16384 + 0j in every bin. |

A per-chirp 512-point range FFT therefore costs about 53 us of engine time, of
the 600 us available per record. The CPU polls during that time (an interrupt,
IRQ 32, could free it). Outputs need up to about 23 bits for 16-bit inputs, so
an int16 export requires a shift or block exponent.

## Relevance

A 512-point complex range FFT per chirp would let the firmware keep only the
retained range bins. With 128 records per frame that is the "bin selection"
reduction in `DSP_plan.md`. An FFT, zeroing of out-of-band bins and a short
inverse FFT would instead give brick-wall decimated time samples. The project
owns the engine, so a polled, mutex-free call is enough.

The measurements above settle the size, layout, scaling, overflow, timing and
buffer questions for these cases.
