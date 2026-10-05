/* Data recovered from LD2450 V2.04 and V2.14; both versions match.
 * Analysis artifact only. Contains no bus driver or hardware actions.
 * Apply indices 0..74 BEFORE SPI receive setup, 75..79 AFTER it.
 * Mode 2 is the initial RAM image, which runtime commands may change.
 * Register semantics and physical startup timing remain unvalidated.
 * I2C 7-bit address: 0x20; inferred data: register, value MSB, value LSB.
 */
#ifndef LD2450_EXTRACTED_RADAR_INIT_DATA_H
#define LD2450_EXTRACTED_RADAR_INIT_DATA_H
#include <stdint.h>
typedef struct { uint8_t reg; uint16_t value; } ld2450_init_write_t;
enum { LD2450_INIT_COUNT = 80, LD2450_INIT_PRE_SPI_COUNT = 75 };

static const ld2450_init_write_t ld2450_mode_1_rom[LD2450_INIT_COUNT] = {
    {0x40, 0x4207}, /*  1: pre_spi */
    {0x41, 0x0004}, /*  2: pre_spi */
    {0x09, 0xE901}, /*  3: pre_spi */
    {0x01, 0x0000}, /*  4: pre_spi */
    {0x67, 0x0000}, /*  5: pre_spi */
    {0x72, 0x0650}, /*  6: pre_spi */
    {0x42, 0x0003}, /*  7: pre_spi */
    {0x43, 0x72D0}, /*  8: pre_spi */
    {0x44, 0x0020}, /*  9: pre_spi */
    {0x45, 0x0000}, /* 10: pre_spi */
    {0x46, 0x0FA0}, /* 11: pre_spi */
    {0x47, 0x1000}, /* 12: pre_spi */
    {0x48, 0xA410}, /* 13: pre_spi */
    {0x49, 0x2000}, /* 14: pre_spi */
    {0x4A, 0x2AF8}, /* 15: pre_spi */
    {0x4B, 0x0002}, /* 16: pre_spi */
    {0x4C, 0x9428}, /* 17: pre_spi */
    {0x4D, 0x0000}, /* 18: pre_spi */
    {0x4E, 0x0001}, /* 19: pre_spi */
    {0x4F, 0x0000}, /* 20: pre_spi */
    {0x50, 0x4E20}, /* 21: pre_spi */
    {0x51, 0x0030}, /* 22: pre_spi */
    {0x52, 0xD400}, /* 23: pre_spi */
    {0x53, 0x0A02}, /* 24: pre_spi */
    {0x54, 0xAAAB}, /* 25: pre_spi */
    {0x55, 0x0000}, /* 26: pre_spi */
    {0x56, 0x0023}, /* 27: pre_spi */
    {0x57, 0xFFFF}, /* 28: pre_spi */
    {0x58, 0xFF78}, /* 29: pre_spi */
    {0x59, 0x0000}, /* 30: pre_spi */
    {0x5A, 0x0000}, /* 31: pre_spi */
    {0x5B, 0x0022}, /* 32: pre_spi */
    {0x5C, 0x0022}, /* 33: pre_spi */
    {0x5D, 0x1919}, /* 34: pre_spi */
    {0x5E, 0xFF00}, /* 35: pre_spi */
    {0x61, 0x0021}, /* 36: pre_spi */
    {0x62, 0x0021}, /* 37: pre_spi */
    {0x63, 0x0021}, /* 38: pre_spi */
    {0x64, 0x0021}, /* 39: pre_spi */
    {0x6E, 0xC3FC}, /* 40: pre_spi */
    {0x66, 0x0F00}, /* 41: pre_spi */
    {0x6C, 0x9990}, /* 42: pre_spi */
    {0x6D, 0x9580}, /* 43: pre_spi */
    {0x70, 0x26A0}, /* 44: pre_spi */
    {0x76, 0x0021}, /* 45: pre_spi */
    {0x02, 0x003C}, /* 46: pre_spi */
    {0x04, 0x030C}, /* 47: pre_spi */
    {0x09, 0x6901}, /* 48: pre_spi */
    {0x0A, 0x0200}, /* 49: pre_spi */
    {0x0B, 0xC03C}, /* 50: pre_spi */
    {0x05, 0x0010}, /* 51: pre_spi */
    {0x06, 0x0122}, /* 52: pre_spi */
    {0x07, 0x01B2}, /* 53: pre_spi */
    {0x08, 0x001C}, /* 54: pre_spi */
    {0x0D, 0x2000}, /* 55: pre_spi */
    {0x0E, 0x2000}, /* 56: pre_spi */
    {0x14, 0x5A03}, /* 57: pre_spi */
    {0x15, 0x1708}, /* 58: pre_spi */
    {0x17, 0x0210}, /* 59: pre_spi */
    {0x20, 0x0000}, /* 60: pre_spi */
    {0x21, 0x0000}, /* 61: pre_spi */
    {0x22, 0x0000}, /* 62: pre_spi */
    {0x23, 0x1DDC}, /* 63: pre_spi */
    {0x24, 0x1D5E}, /* 64: pre_spi */
    {0x25, 0x1CE2}, /* 65: pre_spi */
    {0x26, 0x1C64}, /* 66: pre_spi */
    {0x27, 0x17D0}, /* 67: pre_spi */
    {0x28, 0x16D4}, /* 68: pre_spi */
    {0x29, 0x15DC}, /* 69: pre_spi */
    {0x2A, 0x15DC}, /* 70: pre_spi */
    {0x2B, 0x15DC}, /* 71: pre_spi */
    {0x2C, 0x15DC}, /* 72: pre_spi */
    {0x2D, 0x15DC}, /* 73: pre_spi */
    {0x2E, 0x15DC}, /* 74: pre_spi */
    {0x2F, 0x15DC}, /* 75: pre_spi */
    /* SPI RECEIVE SETUP OCCURS BEFORE THESE LAST FIVE WRITES. */
    {0x72, 0x0653}, /* 76: post_spi */
    {0x67, 0x1E40}, /* 77: post_spi */
    {0x01, 0x8222}, /* 78: post_spi */
    {0x41, 0xC844}, /* 79: post_spi */
    {0x40, 0x0207}, /* 80: post_spi */
};

static const ld2450_init_write_t ld2450_mode_2_ram_initial[LD2450_INIT_COUNT] = {
    {0x40, 0x4207}, /*  1: pre_spi */
    {0x41, 0x0004}, /*  2: pre_spi */
    {0x09, 0xE901}, /*  3: pre_spi */
    {0x01, 0x0000}, /*  4: pre_spi */
    {0x67, 0x0000}, /*  5: pre_spi */
    {0x72, 0x0650}, /*  6: pre_spi */
    {0x42, 0x0003}, /*  7: pre_spi */
    {0x43, 0xA980}, /*  8: pre_spi */
    {0x44, 0x0040}, /*  9: pre_spi */
    {0x45, 0x0000}, /* 10: pre_spi */
    {0x46, 0x0FA0}, /* 11: pre_spi */
    {0x47, 0x1001}, /* 12: pre_spi */
    {0x48, 0x4820}, /* 13: pre_spi */
    {0x49, 0x2001}, /* 14: pre_spi */
    {0x4A, 0x4820}, /* 15: pre_spi */
    {0x4B, 0x0001}, /* 16: pre_spi */
    {0x4C, 0x09A0}, /* 17: pre_spi */
    {0x4D, 0x0000}, /* 18: pre_spi */
    {0x4E, 0x0001}, /* 19: pre_spi */
    {0x4F, 0x0006}, /* 20: pre_spi */
    {0x50, 0xB6C0}, /* 21: pre_spi */
    {0x51, 0x001E}, /* 22: pre_spi */
    {0x52, 0x8480}, /* 23: pre_spi */
    {0x53, 0x0A02}, /* 24: pre_spi */
    {0x54, 0xAAAB}, /* 25: pre_spi */
    {0x55, 0x0000}, /* 26: pre_spi */
    {0x56, 0x0011}, /* 27: pre_spi */
    {0x57, 0xFFFF}, /* 28: pre_spi */
    {0x58, 0xFFEF}, /* 29: pre_spi */
    {0x59, 0x0000}, /* 30: pre_spi */
    {0x5A, 0x0000}, /* 31: pre_spi */
    {0x5B, 0x0022}, /* 32: pre_spi */
    {0x5C, 0x0022}, /* 33: pre_spi */
    {0x5D, 0x1919}, /* 34: pre_spi */
    {0x5E, 0xFF00}, /* 35: pre_spi */
    {0x61, 0x0021}, /* 36: pre_spi */
    {0x62, 0x0021}, /* 37: pre_spi */
    {0x63, 0x0021}, /* 38: pre_spi */
    {0x64, 0x0021}, /* 39: pre_spi */
    {0x6E, 0xC3FC}, /* 40: pre_spi */
    {0x66, 0x0F00}, /* 41: pre_spi */
    {0x6C, 0x9990}, /* 42: pre_spi */
    {0x6D, 0x9580}, /* 43: pre_spi */
    {0x70, 0x26A0}, /* 44: pre_spi */
    {0x76, 0x0021}, /* 45: pre_spi */
    {0x02, 0x103C}, /* 46: pre_spi */
    {0x04, 0x030C}, /* 47: pre_spi */
    {0x09, 0x6901}, /* 48: pre_spi */
    {0x0A, 0x4200}, /* 49: pre_spi */
    {0x0B, 0xC03C}, /* 50: pre_spi */
    {0x05, 0x0010}, /* 51: pre_spi */
    {0x06, 0x0122}, /* 52: pre_spi */
    {0x07, 0x01B2}, /* 53: pre_spi */
    {0x08, 0x001C}, /* 54: pre_spi */
    {0x0D, 0x1000}, /* 55: pre_spi */
    {0x0E, 0x4000}, /* 56: pre_spi */
    {0x14, 0x5A03}, /* 57: pre_spi */
    {0x15, 0x1708}, /* 58: pre_spi */
    {0x17, 0x0210}, /* 59: pre_spi */
    {0x20, 0x0000}, /* 60: pre_spi */
    {0x21, 0x0000}, /* 61: pre_spi */
    {0x22, 0x0000}, /* 62: pre_spi */
    {0x23, 0x1DDC}, /* 63: pre_spi */
    {0x24, 0x1D5E}, /* 64: pre_spi */
    {0x25, 0x1CE2}, /* 65: pre_spi */
    {0x26, 0x1C64}, /* 66: pre_spi */
    {0x27, 0x17D0}, /* 67: pre_spi */
    {0x28, 0x16D4}, /* 68: pre_spi */
    {0x29, 0x15DC}, /* 69: pre_spi */
    {0x2A, 0x15DC}, /* 70: pre_spi */
    {0x2B, 0x15DC}, /* 71: pre_spi */
    {0x2C, 0x15DC}, /* 72: pre_spi */
    {0x2D, 0x15DC}, /* 73: pre_spi */
    {0x2E, 0x15DC}, /* 74: pre_spi */
    {0x2F, 0x15DC}, /* 75: pre_spi */
    /* SPI RECEIVE SETUP OCCURS BEFORE THESE LAST FIVE WRITES. */
    {0x72, 0x0653}, /* 76: post_spi */
    {0x67, 0x1E40}, /* 77: post_spi */
    {0x01, 0x8222}, /* 78: post_spi */
    {0x41, 0xC844}, /* 79: post_spi */
    {0x40, 0x0207}, /* 80: post_spi */
};

#endif
