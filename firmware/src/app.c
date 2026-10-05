#include "ld2450_peripherals.h"
#include "ld2450_radar_init.h"

/* Engineering margins, not recovered stock delay units. The captured
 * 2.424396 ms boundary includes SPI setup, GPIO and the stock delay loop. */
#define RADAR_POWER_SETTLE_MS 20u
#define RADAR_BIAS_SETTLE_MS 3u
#define RADAR_WRITE_TIMEOUT_MS 20u

int ld2450_app_start(void)
{
    struct ld2450_config cfg = ld2450_default_config();
    struct ld2450_radar_init_result progress;
    int err = ld2450_peripherals_init(&cfg);
    if (err) { return err; }
    err = ld2450_radar_power(1);
    if (!err) { err = ld2450_delay_ms(RADAR_POWER_SETTLE_MS); }
    if (!err) {
        err = ld2450_radar_apply_init_stage(&ld2450_build_radar_profile,
                  LD2450_RADAR_PRE_SPI, RADAR_WRITE_TIMEOUT_MS, &progress);
    }
    if (!err) { err = ld2450_spi_prepare(); }
    if (!err) { err = ld2450_radar_bias(1); }
    if (!err) { err = ld2450_delay_ms(RADAR_BIAS_SETTLE_MS); }
    if (!err) {
        err = ld2450_radar_apply_init_stage(&ld2450_build_radar_profile,
                  LD2450_RADAR_POST_SPI, RADAR_WRITE_TIMEOUT_MS, &progress);
    }
    if (err) {
        ld2450_radar_power(0);
        ld2450_debug_write("LD2450: radar init failed; UART updater available\r\n");
        return err;
    }
    ld2450_debug_write("LD2450: radar init writes complete\r\n");
    return LD2450_OK;
}
