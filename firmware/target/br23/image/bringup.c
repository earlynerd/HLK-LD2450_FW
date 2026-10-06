#include "asm/clock.h"

/* build_image.py renames only the pinned SDK setup.c entry point. */
extern void ld2450_sdk_setup_arch(void);

void setup_arch(void)
{
    /* The IIC BAUD register is eight bits. At the stock 240 MHz CPU rate,
     * the default 60 MHz LSB would require 299 for our 100 kHz I2C bus.
     * Apply the SDK's limit before its clock-tree initialization. */
    clock_reset_lsb_max_freq(48000000);
    ld2450_sdk_setup_arch();
}
