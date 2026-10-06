#ifdef LD2450_BOOT_HOST_TEST
#include "mock_boot_sdk.h"
#else
#include "system/includes.h"
#include "asm/wdt.h"
#include "asm/timer.h"
#endif
#include "ld2450_peripherals.h"
extern void ld2450_console_write(const char *text);
extern void ld2450_uart_loader_init(void);
extern int ld2450_uart_loader_poll(void);

/* Keep experimental application work below this gate. A valid READY latches
 * recovery until reset; failed transfers must not release a broken app. */
static void boot_recovery_window(void)
{
    uint32_t start = timer_get_ms();
    int claimed = 0;
    ld2450_debug_write("UPDATE: boot recovery window 3000 ms; radar held off\r\n");
    while (claimed || (uint32_t)(timer_get_ms() - start) < 3000u) {
        clr_wdt();
        if (ld2450_uart_loader_poll()) {
            if (!claimed) ld2450_debug_write("UPDATE: recovery latched until reset\r\n");
            claimed = 1;
        }
    }
}
const struct task_info task_info_table[] = {
    {"app_core", 1, 2048, 512},
    {"sys_event", 6, 256, 0},
    {"systimer", 6, 256, 0},
    {"update", 1, 1024, 0},
    {0, 0, 0, 0}
};
void app_main(void)
{
    struct ld2450_config cfg = ld2450_default_config();
    int result;
#ifdef LD2450_HELLO_WORLD
    uint32_t last_hello;
    static const char heartbeat[] = "HLK-LD2450_FW: hello; UART updater ready\r\n";
#endif
    ld2450_console_write("BOOT: app_main reached\r\n");
    result = ld2450_uart_init(&cfg);
    if (!ld2450_get_status().initialized) {
        for (;;) {
            printf("BOOT ERROR: UART/peripheral init=%d; updater unavailable\n", result);
            clr_wdt();
            os_time_dly(100);
        }
    }
    ld2450_uart_loader_init();
    boot_recovery_window();
#ifdef LD2450_HELLO_WORLD
    ld2450_debug_write("Hello world! Starting UART updater\r\n");
#else
    ld2450_debug_write("HLK-LD2450_FW radar experiment application 0.2\r\n");
    result = ld2450_app_start();
    if (result) printf("BOOT: radar init=%d; updater remains available\n", result);
#endif
#ifdef LD2450_HELLO_WORLD
    ld2450_debug_write("UPDATE: ready on PA1/PA0 at 256000 baud\r\n");
    ld2450_module_uart_write((const uint8_t *)heartbeat, sizeof(heartbeat) - 1);
    last_hello = timer_get_ms();
#endif
    for (;;) {
        clr_wdt();
        ld2450_uart_loader_poll();
#ifdef LD2450_HELLO_WORLD
        if ((uint32_t)(timer_get_ms() - last_hello) >= 1000u) {
            ld2450_debug_write("Hello world!\r\n");
            /* Same task as the blocking updater (task_en=0): this cannot
             * run during its handshake, transfer or loader handoff. */
            ld2450_module_uart_write((const uint8_t *)heartbeat, sizeof(heartbeat) - 1);
            last_hello = timer_get_ms();
        }
#endif
    }
}
