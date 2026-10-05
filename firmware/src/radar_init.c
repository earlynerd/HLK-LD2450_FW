#include "ld2450_radar_init.h"
#include "ld2450_peripherals.h"

int ld2450_radar_apply_init_stage(const struct ld2450_radar_profile *profile,
                                enum ld2450_radar_init_stage stage,
                                uint32_t timeout_ms,
                                struct ld2450_radar_init_result *result)
{
    size_t first, last, i;
    uint8_t tx[3];
    int err;
    if (!result) { return LD2450_BAD_ARGUMENT; }
    result->completed = 0;
    result->failed_sequence = 0;
    if (!profile || !profile->writes || profile->count != LD2450_RADAR_INIT_COUNT ||
        (stage != LD2450_RADAR_PRE_SPI && stage != LD2450_RADAR_POST_SPI) ||
        !timeout_ms || timeout_ms > 1000) {
        return LD2450_BAD_ARGUMENT;
    }
    /* Validate the whole table before issuing any write. Register zero is
     * the recovered sentinel and cannot be part of these 80-entry profiles. */
    for (i = 0; i < profile->count; ++i) {
        if (!profile->writes[i].reg) { return LD2450_BAD_ARGUMENT; }
    }
    first = stage == LD2450_RADAR_PRE_SPI ? 0 : LD2450_RADAR_PRE_SPI_COUNT;
    last = stage == LD2450_RADAR_PRE_SPI ? LD2450_RADAR_PRE_SPI_COUNT : profile->count;
    for (i = first; i < last; ++i) {
        tx[0] = profile->writes[i].reg;
        tx[1] = (uint8_t)(profile->writes[i].value >> 8);
        tx[2] = (uint8_t)profile->writes[i].value;
        err = ld2450_i2c_transfer(LD2450_RADAR_I2C_ADDRESS, tx, sizeof(tx),
                                NULL, 0, timeout_ms);
        if (err) {
            result->failed_sequence = i + 1;
            return err;
        }
        ++result->completed;
    }
    return LD2450_OK;
}
