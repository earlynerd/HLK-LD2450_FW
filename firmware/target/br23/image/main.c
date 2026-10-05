#include "system/includes.h"
#include "asm/wdt.h"
#include "ld2450_peripherals.h"
const struct task_info task_info_table[] = {
    {"app_core", 1, 2048, 512},
    {"sys_event", 6, 256, 0},
    {"systimer", 6, 256, 0},
    {"update", 1, 1024, 0},
    {0, 0, 0, 0}
};
void app_main(void)
{
    extern void ld2450_uart_loader_init(void);
    extern void ld2450_uart_loader_poll(void);
    ld2450_app_start();
    if (!ld2450_get_status().initialized) {
        /* Setup failure must not proceed into an updater with no UART. */
        cpu_reset();
        for (;;) os_time_dly(1);
    }
    ld2450_debug_write("HLK-LD2450_FW radar experiment application 0.2\r\n");
    ld2450_uart_loader_init();
    for (;;) { clr_wdt(); ld2450_uart_loader_poll(); }
}
