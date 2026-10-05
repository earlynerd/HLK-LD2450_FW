#ifndef LD2450_RADAR_INIT_H
#define LD2450_RADAR_INIT_H

#include <stddef.h>
#include <stdint.h>

enum {
    LD2450_RADAR_I2C_ADDRESS = 0x20,
    LD2450_RADAR_INIT_COUNT = 80,
    LD2450_RADAR_PRE_SPI_COUNT = 75
};

struct ld2450_radar_write {
    uint8_t reg;
    uint16_t value;
};

struct ld2450_radar_profile {
    const char *name;
    const char *table_sha256;
    const struct ld2450_radar_write *writes;
    size_t count;
};

/* Generated from the recovered stock table plus explicit sequence overrides. */
extern const struct ld2450_radar_profile ld2450_build_radar_profile;

enum ld2450_radar_init_stage {
    LD2450_RADAR_PRE_SPI,
    LD2450_RADAR_POST_SPI
};

struct ld2450_radar_init_result {
    size_t completed;       /* Successful writes in this call. */
    size_t failed_sequence; /* One-based source sequence, or zero if none. */
};

/* Explicit stage writer, not an automatic boot sequencer. Caller owns power,
 * bias, settling delays, SPI setup/arming, and PRE -> POST ordering. Power
 * must already be enabled for the underlying I2C API. No delay units or
 * readback protocol are assumed. Stop on the first bus error; the caller
 * must abort startup rather than issuing the remaining enable writes.
 * timeout_ms is per transaction (1..1000). Single task owner, no ISR calls.
 */
int ld2450_radar_apply_init_stage(const struct ld2450_radar_profile *profile,
                                enum ld2450_radar_init_stage stage,
                                uint32_t timeout_ms,
                                struct ld2450_radar_init_result *result);

#endif
