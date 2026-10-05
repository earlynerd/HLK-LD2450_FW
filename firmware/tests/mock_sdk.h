#ifndef LD2450_MOCK_SDK_H
#define LD2450_MOCK_SDK_H
#include <stdint.h>
#include <stddef.h>

/* Host model of only the vendor interfaces used by this project. This does
 * not replace compilation against the real SDK or hardware validation. */
#define IO_PORTA_00 0u
#define IO_PORTA_01 1u
#define IO_PORTA_09 9u
#define IO_PORTB_00 16u
#define IO_PORTB_01 17u
#define IO_PORTB_02 18u
#define IO_PORTB_03 19u
#define IO_PORTB_08 24u
#define IO_PORTB_09 25u
#define IO_PORTB_10 26u
#define IO_PORTB_11 27u
#define IO_PORTC_02 34u
#define IO_PORTC_03 35u
#define IO_PORTC_04 36u
#define IO_PORTC_05 37u
typedef struct { volatile uint32_t CON, BAUD, BUF, ADR, CNT; } JL_SPI_TypeDef;
typedef struct { volatile uint16_t CON0; volatile uint8_t BUF, BAUD; volatile uint16_t CON1; } JL_IIC_TypeDef;
typedef struct { volatile uint32_t CON0, CON1, CON2, CON3, CON4, CON5; } JL_IOMAP_TypeDef;
extern JL_SPI_TypeDef mock_spi[2];
extern JL_IIC_TypeDef mock_iic;
extern JL_IOMAP_TypeDef mock_iomap;
#define JL_SPI1 (&mock_spi[0])
#define JL_SPI2 (&mock_spi[1])
#define JL_IIC (&mock_iic)
#define JL_IOMAP (&mock_iomap)

typedef void (*ut_isr_cbfun)(void *, uint32_t);
struct uart_platform_data_t {
    uint8_t tx_pin, rx_pin;
    void *rx_cbuf;
    uint32_t rx_cbuf_size, frame_length, rx_timeout;
    ut_isr_cbfun isr_cbfun;
    void *argv;
    uint32_t is_9bit:1;
    uint32_t baud:24;
};
typedef struct {
    void (*write)(const uint8_t *, uint32_t);
    uint32_t (*read)(uint8_t *, uint32_t, uint32_t);
} uart_bus_t;
const uart_bus_t *uart_dev_open(const struct uart_platform_data_t *);
uint32_t uart_dev_close(uart_bus_t *);
int gpio_set_direction(uint32_t, uint32_t);
int gpio_set_die(uint32_t, uint32_t);
int gpio_set_pull_up(uint32_t, uint32_t);
int gpio_set_pull_down(uint32_t, uint32_t);
int gpio_direction_output(uint32_t, int);
uint32_t gpio_read(uint32_t);
uint32_t clk_get(const char *);
uint32_t timer_get_ms(void);
void mock_sdk_sync(void);

struct mock_gpio { uint8_t direction, value, die, pull_up, pull_down, output_calls; };
struct mock_i2c_event { uint8_t byte, start, stop, read, nack; };
extern struct mock_gpio mock_gpio[64];
extern struct uart_platform_data_t mock_uart_config[2];
extern struct mock_i2c_event mock_i2c_events[64];
extern size_t mock_i2c_event_count;
extern uint32_t mock_clock, mock_time;
extern unsigned mock_uart_open_count, mock_uart_close_count, mock_uart_fail_on;
extern unsigned mock_i2c_tx_count, mock_i2c_nack_on;
extern uint8_t mock_i2c_stall, mock_i2c_read_data[32];
extern size_t mock_i2c_read_size, mock_i2c_read_index;
extern uint8_t mock_uart_tx[2][512], mock_uart_rx[512];
extern size_t mock_uart_tx_size[2], mock_uart_rx_size;
void mock_sdk_reset(void);
#endif
