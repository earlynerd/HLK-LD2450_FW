/* BR23 hardware FFT characterisation (firmware/docs/HW_FFT.md).
 * Runs once at stream start-up, before the radar is armed, on idle scratch
 * memory. Inputs are deterministic pseudo-random values that the host
 * reproduces exactly (firmware/tools/fft_selftest_check.py), so layout,
 * scaling, overflow and in-place behaviour can be inferred from the dumps.
 * Output goes to the PA9 debug UART; nothing is sent over USB. */
#include "system/includes.h"
#include "asm/wdt.h"
#include "ld2450_peripherals.h"
#include "ld2450_stream_app.h"

#define SENTINEL 0x5a5a5a5au
#define POLL_LIMIT 2000000u

struct fft_ctx { uint32_t config; int32_t *in; int32_t *out; };

/* Same packing as the SDK's hw_fft_config() (media.a, recovered IR). */
static uint32_t fft_config(int n, int log2n, int same, int inverse, int real)
{
    uint32_t a, b;
    if (!inverse) {
        a = (uint32_t)(real ? (log2n - 3) << 4 : (log2n - 2) << 4);
        b = (uint32_t)(real ? (log2n - 2) << 8 : (log2n - 1) << 8);
    } else {
        a = real ? 0x24u : 0x34u;
        b = (uint32_t)(real ? (log2n - 2) << 8 : (log2n - 1) << 8);
    }
    return ((uint32_t)n << 16) | a | b | ((uint32_t)real << 1) | (uint32_t)same;
}

/* Same register sequence as hw_fft_wrap(), without the OS mutex (single owner).
 * Returns 0, or -1 if the done flag never appears. */
static int fft_run(struct fft_ctx *ctx)
{
    uint32_t n;
    __asm__ volatile("csync" ::: "memory");
    JL_FFT->CON = 0;
    JL_FFT->CON |= BIT(8);
    JL_FFT->CADR = (uint32_t)ctx;
    JL_FFT->CON |= BIT(0);
    for (n = 0; n < POLL_LIMIT && !(JL_FFT->CON & BIT(7)); ++n) {}
    JL_FFT->CON |= BIT(6);
    __asm__ volatile("csync" ::: "memory");
    return n < POLL_LIMIT ? 0 : -1;
}

static uint32_t lcg_state;
/* Host mirror: firmware/tools/fft_selftest_check.py lcg(). */
static int32_t lcg(int full_scale)
{
    lcg_state = lcg_state * 1103515245u + 12345u;
    return full_scale ? (int32_t)(int16_t)(lcg_state >> 16)
                      : (int32_t)((lcg_state >> 16) & 0x3fffu) - 8192;
}

static void fill(int32_t *p, unsigned count, uint32_t seed, int full_scale)
{
    unsigned j;
    lcg_state = seed;
    for (j = 0; j < count; ++j) p[j] = lcg(full_scale);
}

static void clear(int32_t *p, unsigned count)
{
    unsigned j;
    for (j = 0; j < count; ++j) p[j] = (int32_t)SENTINEL;
}

static void dump(const char *name, const int32_t *p, unsigned count)
{
    char text[112];
    unsigned j, k;
    for (j = 0; j < count; j += 8) {
        int at = snprintf(text, sizeof(text), "FFTD %s %03x", name, j);
        for (k = j; k < j + 8 && k < count; ++k)
            at += snprintf(text + at, sizeof(text) - (size_t)at, " %08x", (unsigned)p[k]);
        snprintf(text + at, sizeof(text) - (size_t)at, "\r\n");
        ld2450_debug_write(text);
        clr_wdt(); /* about 5 s of blocking 115200-baud output in total */
    }
}

static int run_case(const char *name, struct fft_ctx *ctx, uint32_t config, unsigned dump_words)
{
    char text[128];
    uint32_t before = ld2450_stream_clock_us(), elapsed;
    int err;
    ctx->config = config;
    err = fft_run(ctx);
    elapsed = ld2450_stream_clock_us() - before;
    snprintf(text, sizeof(text), "FFTSELF %s cfg=%08x in=%08x out=%08x err=%d us=%u\r\n",
             name, (unsigned)config, (unsigned)ctx->in, (unsigned)ctx->out, err, (unsigned)elapsed);
    ld2450_debug_write(text);
    if (dump_words) dump(name, ctx->out, dump_words);
    return err;
}

void ld2450_fft_selftest(void *scratch, size_t size)
{
    char text[128];
    int32_t *in = (int32_t *)scratch, *out = in + 1024;
    struct fft_ctx *ctx = (struct fft_ctx *)(out + 1024);
    uint32_t before, total;
    unsigned j, mismatches;
    if (size < 2 * 4096u + sizeof(*ctx)) {
        ld2450_debug_write("FFTSELF skipped: scratch too small\r\n");
        return;
    }
    ld2450_debug_write("FFTSELF begin v1 lcg=1103515245/12345 sentinel=5a5a5a5a\r\n");
    ctx->in = in; ctx->out = out;

    /* C512: complex forward, 512 points, interleaved re/im, values +/-8192. */
    fill(in, 1024, 1, 0); clear(out, 1024);
    run_case("C512", ctx, fft_config(512, 9, 0, 0, 0), 1024);
    /* Timing over 16 runs of the same transform (input unchanged by a separate-buffer run). */
    before = ld2450_stream_clock_us();
    for (j = 0; j < 16; ++j) fft_run(ctx);
    total = ld2450_stream_clock_us() - before;
    snprintf(text, sizeof(text), "FFTSELF C512 runs=16 total_us=%u\r\n", (unsigned)total);
    ld2450_debug_write(text);
    /* Did 17 separate-buffer runs leave the input intact? */
    lcg_state = 1;
    for (j = 0, mismatches = 0; j < 1024; ++j) mismatches += in[j] != lcg(0);
    snprintf(text, sizeof(text), "FFTSELF C512 input_changed=%u\r\n", mismatches);
    ld2450_debug_write(text);
    /* INPLACE: same input in one buffer; compare with the C512 output. */
    fill(in, 1024, 1, 0);
    ctx->out = in;
    run_case("INPLACE", ctx, fft_config(512, 9, 1, 0, 0), 0);
    for (j = 0, mismatches = 0; j < 1024; ++j) mismatches += in[j] != out[j];
    snprintf(text, sizeof(text), "FFTSELF INPLACE mismatches=%u\r\n", mismatches);
    ld2450_debug_write(text);
    ctx->out = out;
    /* C512F: full-scale int16 inputs, for overflow/saturation behaviour. */
    fill(in, 1024, 7, 1); clear(out, 1024);
    run_case("C512F", ctx, fft_config(512, 9, 0, 0, 0), 1024);
    /* IMP: impulse of 16384 at sample 0 (flat spectrum shows the gain). */
    for (j = 0; j < 1024; ++j) in[j] = 0;
    in[0] = 16384; clear(out, 1024);
    run_case("IMP", ctx, fft_config(512, 9, 0, 0, 0), 16);
    /* C256: complex forward, 256 points. */
    fill(in, 512, 3, 0); clear(out, 1024);
    run_case("C256", ctx, fft_config(256, 8, 0, 0, 0), 520);
    /* R512: real forward, 512 real inputs; dump past N to see the output extent. */
    fill(in, 512, 5, 0); clear(out, 1024);
    run_case("R512", ctx, fft_config(512, 9, 0, 0, 1), 1024);
    /* I512: complex inverse of a regenerated C512 input's transform. */
    fill(in, 1024, 1, 0); clear(out, 1024);
    run_case("I512A", ctx, fft_config(512, 9, 0, 0, 0), 0);
    for (j = 0; j < 1024; ++j) in[j] = out[j];
    clear(out, 1024);
    run_case("I512", ctx, fft_config(512, 9, 0, 1, 0), 1024);
    JL_FFT->CON = BIT(1); /* force the engine off, as the SDK audio code does */
    ld2450_debug_write("FFTSELF end\r\n");
}
