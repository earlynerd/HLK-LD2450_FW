#include "ld2450_peripherals.h"

int ld2450_app_start(void)
{
    struct ld2450_config cfg = ld2450_default_config();
    int err = ld2450_peripherals_init(&cfg);
    if (err) { return err; }
    err = ld2450_debug_write("LD2450: peripherals ready; radar configuration capture required\r\n");
    if (err) { return err; }
    /* The known pins/controllers are initialized. Register writes, RF
     * startup timing, and streaming acquisition await additional captures. */
    return LD2450_CONFIG_CAPTURE_REQUIRED;
}
