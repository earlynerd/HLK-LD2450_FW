#include "system/includes.h"
#include "app_config.h"
#include "asm/power_interface.h"
#include "asm/power/p33.h"
#include "asm/gpio.h"

extern void ld2450_console_write(const char *text);

int eSystemConfirmStopStatus(void)
{
    /* SDK contract: zero keeps periodic wakeups; never request endless sleep. */
    return 0;
}

/* Only MCU power management, without the soundbox's ADC/audio/keys/charger.
 * Keep the boot-time I/O voltage selections instead of borrowing board values. */
static struct low_power_param power_param = {
    .osc_type = OSC_TYPE_LRC,
    .config = 0,
    .btosc_hz = TCFG_CLOCK_OSC_HZ,
    .delay_us = TCFG_CLOCK_SYS_HZ / 1000000,
    .btosc_disable = 0,
    .dcdc_port = (u8)-1, /* SDK NO_CONFIG_PORT: no external DCDC control. */
};

static int ld2450_board_power_init(void)
{
    ld2450_console_write("BOOT: MCU power init\r\n");
    power_param.vddiom_lev = GET_VDDIOM_VOL() & 7;
    power_param.vddiow_lev = GET_VDDIOW_VOL();
    /* This SDK asserts on level zero (2.1 V), even with sleep disabled.
     * Keep supported inherited levels; otherwise use its lowest valid level.
     * power_init itself ensures the strong rail is at least the weak rail. */
    if (power_param.vddiow_lev == VDDIOW_VOL_21V) {
        ld2450_console_write("BOOT: VDDIOW 2.1 V unsupported by SDK; selecting 2.4 V\r\n");
        power_param.vddiow_lev = VDDIOW_VOL_24V;
    }
    power_init(&power_param);
    power_set_mode(TCFG_LOWPOWER_POWER_SEL);
    /* Hold external radar supply and bias off; do not initialize the radar. */
    gpio_set_pull_up(IO_PORTC_02, 0);
    gpio_set_pull_down(IO_PORTC_02, 0);
    gpio_direction_output(IO_PORTC_02, 1);
    gpio_set_pull_up(IO_PORTC_03, 0);
    gpio_set_pull_down(IO_PORTC_03, 0);
    gpio_direction_output(IO_PORTC_03, 0);
    ld2450_console_write("BOOT: MCU power ready; radar held off\r\n");
    return 0;
}
/* Vendor app_init runs board_init after early/platform callbacks. */
__initcall(ld2450_board_power_init);
