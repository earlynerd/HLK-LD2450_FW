#include "ld2450_peripherals.h"
#include "ld2450_radar_init.h"
#include <stdio.h>
#ifdef LD2450_USB_STREAM
#include "ld2450_stream_app.h"
#endif
#ifdef LD2450_CAPTURE
#include "ld2450_capture.h"
#endif

/* Engineering margins, not recovered stock delay units. The captured
 * 2.424396 ms boundary includes SPI setup, GPIO and the stock delay loop. */
#define RADAR_POWER_SETTLE_MS 20u
#define RADAR_BIAS_SETTLE_MS 3u
#define RADAR_WRITE_TIMEOUT_MS 20u

int ld2450_app_start(void)
{
    struct ld2450_config cfg = ld2450_default_config();
    struct ld2450_radar_init_result progress = {0, 0};
    const char *stage = "peripherals";
    unsigned acknowledged = 0;
    char message[192];
    int err;
    snprintf(message, sizeof(message), "RADAR: profile=%s; I2C=0x20; starting init\r\n",
             ld2450_build_radar_profile.name);
    ld2450_debug_write(message);
    /* A live REINIT re-enters here with radar I/O already configured. */
    err = ld2450_get_status().radar_io_ready ? LD2450_OK : ld2450_peripherals_init(&cfg);
    if (err) { goto failed; }
    stage = "power-settle";
    err = ld2450_radar_power(1);
    if (!err) { err = ld2450_delay_ms(RADAR_POWER_SETTLE_MS); }
    if (!err) {
        stage = "writes-1-75";
        err = ld2450_radar_apply_init_stage(&ld2450_build_radar_profile,
                  LD2450_RADAR_PRE_SPI, RADAR_WRITE_TIMEOUT_MS, &progress);
        acknowledged = (unsigned)progress.completed;
    }
    /* No diagnostic UART traffic inside the SPI/REXT/table boundary. */
    if (!err) { stage = "spi-prepare"; err = ld2450_spi_prepare(); }
#ifdef LD2450_USB_STREAM
    if (!err) { stage = "stream-arm"; err = ld2450_stream_app_arm(); }
#endif
#ifdef LD2450_CAPTURE
    if (!err) { stage = "capture-arm"; err = ld2450_capture_arm(); }
#endif
    if (!err) { stage = "bias-enable"; err = ld2450_radar_bias(1); }
    if (!err) { stage = "bias-settle"; err = ld2450_delay_ms(RADAR_BIAS_SETTLE_MS); }
    if (!err) {
        stage = "writes-76-80";
        err = ld2450_radar_apply_init_stage(&ld2450_build_radar_profile,
                  LD2450_RADAR_POST_SPI, RADAR_WRITE_TIMEOUT_MS, &progress);
        acknowledged += (unsigned)progress.completed;
    }
failed:
    if (err) {
        ld2450_radar_power(0);
        snprintf(message, sizeof(message), "RADAR: failed stage=%s error=%d acked=%u/80\r\n",
                 stage, err, acknowledged);
        ld2450_debug_write(message);
        if (progress.failed_sequence && progress.failed_sequence <= ld2450_build_radar_profile.count) {
            const struct ld2450_radar_write *w = &ld2450_build_radar_profile.writes[progress.failed_sequence - 1];
            snprintf(message, sizeof(message), "RADAR: failed write=%u reg=0x%02x value=0x%04x\r\n",
                     (unsigned)progress.failed_sequence, (unsigned)w->reg, (unsigned)w->value);
            ld2450_debug_write(message);
        }
        ld2450_debug_write("LD2450: radar init failed; UART updater available\r\n");
        return err;
    }
#ifndef LD2450_USB_STREAM
    ld2450_debug_write("LD2450: radar init writes complete\r\n");
#ifdef LD2450_CAPTURE
    ld2450_debug_write("RADAR: 80/80 writes ACKed; both SPI DMA captures armed\r\n");
#else
    ld2450_debug_write("RADAR: 80/80 writes ACKed; SPI configured; bias enabled; DMA not armed\r\n");
#endif
#endif /* Never block on debug UART after continuous DMA is armed. */
    return LD2450_OK;
}
