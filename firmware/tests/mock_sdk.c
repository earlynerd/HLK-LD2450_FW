#include "mock_sdk.h"
#include "sdk_bridge.h"
#include <string.h>

JL_SPI_TypeDef mock_spi[2];
JL_IIC_TypeDef mock_iic;
JL_IOMAP_TypeDef mock_iomap;
struct mock_gpio mock_gpio[64];
struct uart_platform_data_t mock_uart_config[2];
struct mock_i2c_event mock_i2c_events[64];
size_t mock_i2c_event_count;
uint32_t mock_clock, mock_time;
unsigned mock_uart_open_count, mock_uart_close_count, mock_uart_fail_on;
unsigned mock_i2c_tx_count, mock_i2c_nack_on;
uint8_t mock_i2c_stall, mock_i2c_read_data[32];
size_t mock_i2c_read_size, mock_i2c_read_index;
uint8_t mock_uart_tx[2][512], mock_uart_rx[512];
size_t mock_uart_tx_size[2], mock_uart_rx_size;

void mock_sdk_reset(void)
{
    memset(mock_spi, 0, sizeof(mock_spi));
    memset(&mock_iic, 0, sizeof(mock_iic));
    memset(&mock_iomap, 0, sizeof(mock_iomap));
    memset(mock_gpio, 0, sizeof(mock_gpio));
    memset(mock_uart_config, 0, sizeof(mock_uart_config));
    memset(mock_i2c_events, 0, sizeof(mock_i2c_events));
    mock_clock = 24000000;
    mock_time = 0;
    mock_uart_open_count = mock_uart_close_count = mock_uart_fail_on = 0;
    mock_i2c_tx_count = mock_i2c_nack_on = 0;
    mock_i2c_event_count = mock_i2c_read_size = mock_i2c_read_index = 0;
    mock_i2c_stall = 0;
    mock_uart_tx_size[0] = mock_uart_tx_size[1] = mock_uart_rx_size = 0;
}

int gpio_set_direction(uint32_t p, uint32_t v) { mock_gpio[p].direction = (uint8_t)v; return 0; }
int gpio_set_die(uint32_t p, uint32_t v) { mock_gpio[p].die = (uint8_t)v; return 0; }
int gpio_set_pull_up(uint32_t p, uint32_t v) { mock_gpio[p].pull_up = (uint8_t)v; return 0; }
int gpio_set_pull_down(uint32_t p, uint32_t v) { mock_gpio[p].pull_down = (uint8_t)v; return 0; }
int gpio_direction_output(uint32_t p, int v)
{
    mock_gpio[p].direction = 0;
    mock_gpio[p].value = (uint8_t)v;
    ++mock_gpio[p].output_calls;
    return 0;
}
uint32_t gpio_read(uint32_t p) { return mock_gpio[p].value; }
uint32_t clk_get(const char *name) { return strcmp(name, "lsb") ? 0 : mock_clock; }
uint32_t timer_get_ms(void) { return mock_time++; }

void mock_sdk_sync(void)
{
    struct mock_i2c_event *e;
    uint16_t con = mock_iic.CON0;
    if (!(con & LD_I2C_GO) || mock_i2c_stall) { return; }
    if (mock_i2c_event_count >= 64) { return; }
    e = &mock_i2c_events[mock_i2c_event_count++];
    e->byte = mock_iic.BUF;
    e->start = (con & LD_I2C_START) != 0;
    e->stop = (con & LD_I2C_STOP) != 0;
    e->read = (con & LD_I2C_READ) != 0;
    e->nack = (con & LD_I2C_SEND_NACK) != 0;
    mock_iic.CON0 &= (uint16_t)(0xffffu ^ (LD_I2C_GO | LD_I2C_START | LD_I2C_STOP | LD_I2C_GOT_NACK));
    if (e->stop) { mock_iic.CON0 |= LD_I2C_END; return; }
    if (e->read) {
        mock_iic.BUF = mock_i2c_read_index < mock_i2c_read_size ?
                      mock_i2c_read_data[mock_i2c_read_index++] : 0xff;
    } else {
        ++mock_i2c_tx_count;
        if (mock_i2c_nack_on == mock_i2c_tx_count) { mock_iic.CON0 |= LD_I2C_GOT_NACK; }
    }
    mock_iic.CON0 |= LD_I2C_PENDING;
}

static void uart_write0(const uint8_t *p, uint32_t n)
{
    if (n > 512) { n = 512; }
    memcpy(mock_uart_tx[0], p, n); mock_uart_tx_size[0] = n;
}
static void uart_write1(const uint8_t *p, uint32_t n)
{
    if (n > 512) { n = 512; }
    memcpy(mock_uart_tx[1], p, n); mock_uart_tx_size[1] = n;
}
static uint32_t uart_read(uint8_t *p, uint32_t n, uint32_t timeout)
{
    (void)timeout;
    if (n > mock_uart_rx_size) { n = (uint32_t)mock_uart_rx_size; }
    memcpy(p, mock_uart_rx, n); mock_uart_rx_size = 0; return n;
}
static void set_module_baud(uint32_t baud) { mock_uart_config[0].baud = baud; }
static void set_debug_baud(uint32_t baud) { mock_uart_config[1].baud = baud; }
static uart_bus_t uart_bus[2] = {{uart_write0, uart_read, set_module_baud}, {uart_write1, uart_read, set_debug_baud}};
const uart_bus_t *uart_dev_open(const struct uart_platform_data_t *cfg)
{
    unsigned i = mock_uart_open_count++;
    if (mock_uart_open_count == mock_uart_fail_on || i >= 2) { return NULL; }
    mock_uart_config[i] = *cfg;
    return &uart_bus[i];
}
uint32_t uart_dev_close(uart_bus_t *bus) { (void)bus; ++mock_uart_close_count; return 0; }
