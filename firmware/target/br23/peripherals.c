#include "ld2450_peripherals.h"
#include "sdk_bridge.h"
#include <string.h>

#define RADAR_POWER_PIN IO_PORTC_02 /* PW_CTL: low turns Q1 on. */
#define RADAR_BIAS_PIN  IO_PORTC_03 /* REXT_CTL: high turns Q2 on. */
#define UART_BUFFER_SIZE 1024u

#ifdef _MSC_VER
#define ALIGNED4 __declspec(align(4))
#else
#define ALIGNED4 __attribute__((aligned(4)))
#endif

static struct ld2450_status status;
static const uart_bus_t *module_uart;
static const uart_bus_t *debug_uart;
static ALIGNED4 uint8_t uart_rx[UART_BUFFER_SIZE];
static void *dma_buffer[2];
static size_t dma_size[2];
static const uint32_t cs_pin[2] = {IO_PORTB_03, IO_PORTB_11};

static JL_SPI_TypeDef *lane_spi(uint8_t lane)
{
    return lane == 0 ? JL_SPI1 : JL_SPI2;
}

static void input_pin(uint32_t pin, uint8_t pullup)
{
    gpio_set_direction(pin, 1);
    gpio_set_die(pin, 1);
    gpio_set_pull_up(pin, pullup);
    gpio_set_pull_down(pin, 0);
}

static void control_pin(uint32_t pin, uint8_t value)
{
    gpio_set_pull_up(pin, 0);
    gpio_set_pull_down(pin, 0);
    gpio_direction_output(pin, value);
    gpio_set_die(pin, 1);
}

static void spi_receiver_init(JL_SPI_TypeDef *spi)
{
    spi->CON = 0;
    spi->CNT = 0;
    spi->BAUD = 0; /* External slave clock; MCU does not generate SCLK. */
    spi->CON = LD_SPI_SLAVE | LD_SPI_BIDIR | LD_SPI_SHIFT_FALL |
               LD_SPI_CS_IDLE_HIGH | LD_SPI_RECEIVE | LD_SPI_CLEAR_PENDING;
    spi->CON |= LD_SPI_ENABLE;
}

struct ld2450_config ld2450_default_config(void)
{
    struct ld2450_config cfg = {100000, 256000, 115200, 1, 0};
    return cfg;
}

int ld2450_peripherals_init(const struct ld2450_config *cfg)
{
    uint32_t clock, divisor;
    struct uart_platform_data_t uart;
    if (!cfg || !cfg->i2c_hz || !cfg->module_uart_baud ||
        cfg->module_uart_baud > 0xffffffu ||
        (cfg->enable_debug_uart && (!cfg->debug_uart_baud ||
                                   cfg->debug_uart_baud > 0xffffffu))) {
        return LD2450_BAD_ARGUMENT;
    }
    if (status.initialized) { return LD2450_BUSY; }
    clock = clk_get("lsb");
    if (cfg->i2c_hz > clock / 2u) { return LD2450_CLOCK_RANGE; }
    divisor = clock / (2u * cfg->i2c_hz) - 1u;
    if (divisor > 255u) { return LD2450_CLOCK_RANGE; }

    /* Set gates off before enabling communication peripherals. */
    control_pin(RADAR_POWER_PIN, 1);
    control_pin(RADAR_BIAS_PIN, 0);
    input_pin(IO_PORTB_01, 1); /* MCU reset; never route it as SPI DO. */
    input_pin(IO_PORTB_10, 0); /* Unused SPI2 DO. */
    input_pin(IO_PORTB_02, 0);
    input_pin(IO_PORTB_00, 0);
    input_pin(IO_PORTB_08, 0);
    input_pin(IO_PORTB_09, 0);
    input_pin(cs_pin[0], 0);
    input_pin(cs_pin[1], 0);
    JL_IOMAP->CON1 &= ~((1u << 4) | (1u << 16)); /* SPI1/2 group A. */
    spi_receiver_init(JL_SPI1);
    spi_receiver_init(JL_SPI2);

    input_pin(IO_PORTC_04, 0); /* External pulls go to switched 3V3_SOC. */
    input_pin(IO_PORTC_05, 0);
    JL_IOMAP->CON1 = (JL_IOMAP->CON1 & ~(3u << 18)) | (1u << 18);
    JL_IIC->CON0 = 0;
    JL_IIC->CON1 = (uint16_t)(JL_IIC->CON1 & ~(1u << 13)); /* Master. */
    JL_IIC->BAUD = (uint8_t)divisor;
    JL_IIC->CON0 = LD_I2C_FILTER | LD_I2C_CLEAR_PENDING | LD_I2C_CLEAR_END;
    JL_IIC->CON1 |= (1u << 14); /* Clear START pending. */
    JL_IIC->CON0 |= LD_I2C_ENABLE;

    /* SDK UART driver supports arbitrary GPIO remapping. Start with the
     * module schematic's PA1=TX / PA0=RX; the option can swap after probing. */
    memset(&uart, 0, sizeof(uart));
    uart.tx_pin = cfg->swap_module_uart_pins ? IO_PORTA_00 : IO_PORTA_01;
    uart.rx_pin = cfg->swap_module_uart_pins ? IO_PORTA_01 : IO_PORTA_00;
    uart.baud = cfg->module_uart_baud;
    uart.rx_cbuf = uart_rx;
    uart.rx_cbuf_size = UART_BUFFER_SIZE;
    uart.frame_length = 32;
    uart.rx_timeout = 10;
    module_uart = uart_dev_open(&uart);
    if (!module_uart) {
        ld2450_peripherals_deinit();
        return LD2450_UART_UNAVAILABLE;
    }
    if (cfg->enable_debug_uart) {
        memset(&uart, 0, sizeof(uart));
        uart.tx_pin = IO_PORTA_09;
        uart.rx_pin = (uint8_t)-1;
        uart.baud = cfg->debug_uart_baud;
        debug_uart = uart_dev_open(&uart);
        if (!debug_uart) {
            ld2450_peripherals_deinit();
            return LD2450_UART_UNAVAILABLE;
        }
    }
    status.initialized = 1;
    return LD2450_OK;
}

void ld2450_peripherals_deinit(void)
{
    control_pin(RADAR_POWER_PIN, 1);
    control_pin(RADAR_BIAS_PIN, 0);
    JL_SPI1->CON = 0;
    JL_SPI2->CON = 0;
    JL_SPI1->CNT = 0;
    JL_SPI2->CNT = 0;
    JL_IIC->CON0 = 0;
    if (debug_uart) { uart_dev_close((uart_bus_t *)debug_uart); }
    if (module_uart) { uart_dev_close((uart_bus_t *)module_uart); }
    module_uart = NULL;
    debug_uart = NULL;
    memset(&status, 0, sizeof(status));
    memset(dma_buffer, 0, sizeof(dma_buffer));
    memset(dma_size, 0, sizeof(dma_size));
}

struct ld2450_status ld2450_get_status(void)
{
    return status;
}

int ld2450_radar_power(uint8_t enabled)
{
    if (!status.initialized) { return LD2450_NOT_READY; }
    if (enabled) {
        control_pin(RADAR_BIAS_PIN, 1);
        control_pin(RADAR_POWER_PIN, 0);
    } else {
        control_pin(RADAR_POWER_PIN, 1);
        control_pin(RADAR_BIAS_PIN, 0);
        JL_SPI1->CNT = 0;
        JL_SPI2->CNT = 0;
        status.dma_armed_mask = 0;
    }
    status.radar_powered = enabled != 0;
    return LD2450_OK;
}

int ld2450_spi_arm(uint8_t lane, void *buffer, size_t size)
{
    JL_SPI_TypeDef *spi;
    if (!status.initialized) { return LD2450_NOT_READY; }
    if (lane > 1 || !buffer || !size || size > 65535u ||
        ((uintptr_t)buffer & 3u)) { return LD2450_BAD_ARGUMENT; }
    if (status.dma_armed_mask & (1u << lane)) { return LD2450_BUSY; }
    spi = lane_spi(lane);
    ld_spi_clear(spi);
    spi->CON |= LD_SPI_RECEIVE;
    dma_buffer[lane] = buffer;
    dma_size[lane] = size;
    status.dma_armed_mask |= (uint8_t)(1u << lane);
    spi->ADR = (uint32_t)(uintptr_t)buffer;
    ld_sdk_sync(); /* Publish the descriptor before starting DMA. */
    spi->CNT = (uint32_t)size;
    ld_sdk_sync();
    return LD2450_OK;
}

int ld2450_spi_poll(uint8_t lane, struct ld2450_spi_completion *done)
{
    JL_SPI_TypeDef *spi;
    if (!status.initialized) { return LD2450_NOT_READY; }
    if (lane > 1 || !done) { return LD2450_BAD_ARGUMENT; }
    if (!(status.dma_armed_mask & (1u << lane))) { return LD2450_NOT_READY; }
    spi = lane_spi(lane);
    if (!(spi->CON & LD_SPI_PENDING)) { return 0; }
    ld_sdk_sync();
    ld_spi_clear(spi);
    done->buffer = dma_buffer[lane];
    done->size = dma_size[lane];
    done->rx_index = lane;
    done->chip_select_high = gpio_read(cs_pin[lane]) != 0;
    status.dma_armed_mask &= (uint8_t)~(1u << lane);
    return 1;
}

static int i2c_wait(uint16_t pending, uint32_t start, uint32_t timeout)
{
    while (!(JL_IIC->CON0 & pending)) {
        ld_sdk_sync();
        if ((uint32_t)(timer_get_ms() - start) >= timeout) {
            return LD2450_TIMEOUT;
        }
    }
    return LD2450_OK;
}

static int i2c_send(uint8_t byte, uint32_t start, uint32_t timeout)
{
    int err;
    if ((uint32_t)(timer_get_ms() - start) >= timeout) { return LD2450_TIMEOUT; }
    JL_IIC->CON0 &= (uint16_t)(0xffffu ^ LD_I2C_READ);
    JL_IIC->BUF = byte;
    JL_IIC->CON0 |= LD_I2C_GO;
    ld_sdk_sync();
    err = i2c_wait(LD_I2C_PENDING, start, timeout);
    if (err) { return err; }
    err = (JL_IIC->CON0 & LD_I2C_GOT_NACK) ? LD2450_I2C_NACK : LD2450_OK;
    ld_i2c_clear(LD_I2C_CLEAR_PENDING);
    return err;
}

int ld2450_i2c_transfer(uint8_t address, const uint8_t *tx, size_t tx_size,
                       uint8_t *rx, size_t rx_size, uint32_t timeout)
{
    size_t n;
    uint32_t start;
    int err = LD2450_OK, stop_err;
    if (!status.initialized || !status.radar_powered) { return LD2450_NOT_READY; }
    if (address > 0x7f || (!tx_size && !rx_size) || (tx_size && !tx) ||
        (rx_size && !rx) || !timeout || timeout > 1000) {
        return LD2450_BAD_ARGUMENT;
    }
    start = timer_get_ms();
    ld_i2c_clear(LD_I2C_CLEAR_PENDING | LD_I2C_CLEAR_END);
    if (tx_size) {
        JL_IIC->CON0 |= LD_I2C_START;
        err = i2c_send((uint8_t)(address << 1), start, timeout);
        for (n = 0; !err && n < tx_size; ++n) { err = i2c_send(tx[n], start, timeout); }
    }
    if (!err && rx_size) {
        JL_IIC->CON0 |= LD_I2C_START;
        err = i2c_send((uint8_t)((address << 1) | 1u), start, timeout);
        for (n = 0; !err && n < rx_size; ++n) {
            if ((uint32_t)(timer_get_ms() - start) >= timeout) {
                err = LD2450_TIMEOUT;
                break;
            }
            JL_IIC->CON0 |= LD_I2C_READ;
            if (n + 1 == rx_size) { JL_IIC->CON0 |= LD_I2C_SEND_NACK; }
            else { JL_IIC->CON0 &= (uint16_t)(0xffffu ^ LD_I2C_SEND_NACK); }
            JL_IIC->BUF = 0xff;
            JL_IIC->CON0 |= LD_I2C_GO;
            ld_sdk_sync();
            err = i2c_wait(LD_I2C_PENDING, start, timeout);
            if (!err) { rx[n] = JL_IIC->BUF; ld_i2c_clear(LD_I2C_CLEAR_PENDING); }
        }
    }
    /* STOP gets its own bounded wait even after a transfer timeout. */
    JL_IIC->CON0 |= LD_I2C_STOP | LD_I2C_GO;
    ld_sdk_sync();
    stop_err = i2c_wait(LD_I2C_END, timer_get_ms(), timeout);
    ld_i2c_clear(LD_I2C_CLEAR_PENDING | LD_I2C_CLEAR_END);
    if (err == LD2450_TIMEOUT || stop_err) {
        /* Drop the pending transaction; preserve mode and clock settings. */
        JL_IIC->CON0 = 0;
        JL_IIC->CON1 |= (1u << 14);
        JL_IIC->CON0 = LD_I2C_FILTER | LD_I2C_ENABLE;
    }
    return err ? err : stop_err;
}

int ld2450_module_uart_write(const uint8_t *data, size_t size)
{
    if (!status.initialized || !module_uart) { return LD2450_NOT_READY; }
    if (!data || !size || size > UINT32_MAX) { return LD2450_BAD_ARGUMENT; }
    module_uart->write(data, (uint32_t)size);
    return LD2450_OK;
}

int ld2450_module_uart_read(uint8_t *data, size_t size, uint32_t timeout)
{
    if (!status.initialized || !module_uart) { return LD2450_NOT_READY; }
    if (!data || !size || size > 512u || !timeout || timeout > 1000) {
        return LD2450_BAD_ARGUMENT;
    }
    return (int)module_uart->read(data, (uint32_t)size, timeout);
}

int ld2450_module_uart_set_baud(uint32_t baud)
{
    if (!status.initialized || !module_uart) return LD2450_NOT_READY;
    if (baud < 9600u || baud > 1000000u) return LD2450_BAD_ARGUMENT;
    module_uart->set_baud(baud);
    return LD2450_OK;
}

int ld2450_debug_write(const char *message)
{
    size_t size;
    if (!status.initialized || !debug_uart) { return LD2450_NOT_READY; }
    if (!message) { return LD2450_BAD_ARGUMENT; }
    size = strlen(message);
    if (size > UINT32_MAX) { return LD2450_BAD_ARGUMENT; }
    debug_uart->write((const uint8_t *)message, (uint32_t)size);
    return LD2450_OK;
}
