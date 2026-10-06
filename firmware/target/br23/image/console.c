#include "system/includes.h"
#include "asm/uart.h"
#include "asm/uart_dev.h"
#include "asm/gpio.h"
#include "asm/cpu.h"
#include "asm/clock.h"

/* UART0 stays reserved for SDK diagnostics for the entire application.
 * uart_dev_open therefore allocates another UART for PA1/PA0 updates. */
static const struct uart_platform_data console = {
    .irq = IRQ_UART0_IDX,
    .tx_pin = IO_PORTA_09,
    .rx_pin = (u8)-1,
    .baudrate = 115200,
    .flags = UART_DEBUG,
};

void ld2450_console_write(const char *text)
{
    while (*text) putbyte(*text++);
}

void debug_uart_init(const struct uart_platform_data *unused)
{
    (void)unused;
    /* The SDK debug allocator picks the first idle UART. Own UART0 before
     * it runs, including after a bootloader handoff with stale UART state. */
    JL_UART0->CON0 = BIT(13) | BIT(12) | BIT(10);
    JL_UART0->CON1 = 0;
    uart_init(&console);
    ld2450_console_write("\r\nBOOT: clocks ready; PA9 console ready\r\n");
    printf("BOOT: sys=%u lsb=%u uart=%u UART0_BAUD=%u\n",
           clk_get("sys"), clk_get("lsb"), clk_get("uart"),
           (unsigned)JL_UART0->BAUD);
}

static void console_write(const u8 *data, u32 size)
{
    while (size--) putbyte((char)*data++);
}

const uart_bus_t *ld2450_console_bus(u32 baud)
{
    static const uart_bus_t bus = {.write = console_write};
    return baud == 115200 ? &bus : NULL;
}
