#include "ld2450_capture.h"
#include "ld2450_peripherals.h"
#include <stdio.h>
#include <string.h>

extern uint32_t timer_get_ms(void);
extern void clr_wdt(void);
/* Sixteen complete 2056-byte records per lane, divisible by dump line size. */
#define CAPTURE_BYTES (2056u * 16u)
#ifdef _MSC_VER
#define CAPTURE_ALIGN __declspec(align(4))
#else
#define CAPTURE_ALIGN __attribute__((aligned(4)))
#endif
static CAPTURE_ALIGN uint8_t samples[2][CAPTURE_BYTES];
static uint32_t started;
static uint8_t active, completed;

int ld2450_capture_arm(void)
{
    int err;
    memset(samples, 0xa5, sizeof(samples));
    completed = 0;
    err = ld2450_spi_arm(0, samples[0], CAPTURE_BYTES);
    if (!err) err = ld2450_spi_arm(1, samples[1], CAPTURE_BYTES);
    if (err) { ld2450_radar_power(0); active = 0; return err; }
    started = timer_get_ms(); active = 1;
    return 0;
}

void ld2450_capture_poll(void)
{
    unsigned lane, offset, j;
    struct ld2450_spi_completion done;
    char line[128];
    static const char hex[] = "0123456789abcdef";
    if (!active) return;
    /* Updater entry and failed radar initialization both cancel acquisition. */
    if (!ld2450_get_status().radar_powered) { active = 0; return; }
    for (lane = 0; lane < 2; ++lane) {
        if (!(completed & (1u << lane)) && ld2450_spi_poll((uint8_t)lane, &done) == 1)
            completed |= (uint8_t)(1u << lane);
    }
    if (completed != 3 && (uint32_t)(timer_get_ms() - started) < 2000u) return;
    /* Stop all DMA before reading even an incomplete buffer. Partial dumps
     * retain their A5 prefill; no inferred received length is claimed. */
    ld2450_radar_power(0); active = 0;
    ld2450_debug_write("CAPTURE: stopped radar; dumping SPI snapshots on module UART\r\n");
    for (lane = 0; lane < 2; ++lane) {
        int n = snprintf(line, sizeof(line), "CAPTURE BEGIN lane=%u size=%u complete=%u\r\n",
                         lane, CAPTURE_BYTES, (completed >> lane) & 1u);
        if (ld2450_module_uart_write((const uint8_t *)line, (size_t)n)) return;
        for (offset = 0; offset < CAPTURE_BYTES; offset += 32) {
            n = snprintf(line, sizeof(line), "DATA %u %04x ", lane, offset);
            for (j = 0; j < 32; ++j) {
                uint8_t b = samples[lane][offset + j];
                line[n++] = hex[b >> 4]; line[n++] = hex[b & 15];
            }
            line[n++] = '\r'; line[n++] = '\n';
            clr_wdt();
            if (ld2450_module_uart_write((const uint8_t *)line, (size_t)n)) return;
        }
        n = snprintf(line, sizeof(line), "CAPTURE END lane=%u\r\n", lane);
        if (ld2450_module_uart_write((const uint8_t *)line, (size_t)n)) return;
    }
    ld2450_debug_write("CAPTURE: dump complete; radar off; updater ready\r\n");
}
