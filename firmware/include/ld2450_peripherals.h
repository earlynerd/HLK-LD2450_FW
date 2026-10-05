#ifndef LD2450_PERIPHERALS_H
#define LD2450_PERIPHERALS_H

#include <stddef.h>
#include <stdint.h>

enum ld2450_result {
    LD2450_OK = 0,
    LD2450_NOT_READY = -1,
    LD2450_BAD_ARGUMENT = -2,
    LD2450_CLOCK_RANGE = -3,
    LD2450_UART_UNAVAILABLE = -4,
    LD2450_BUSY = -5,
    LD2450_TIMEOUT = -6,
    LD2450_I2C_NACK = -7,
    LD2450_CONFIG_CAPTURE_REQUIRED = -8
};

struct ld2450_config {
    uint32_t i2c_hz;
    uint32_t module_uart_baud;
    uint32_t debug_uart_baud;
    uint8_t enable_debug_uart;
    uint8_t swap_module_uart_pins;
};

struct ld2450_status {
    uint8_t initialized;
    uint8_t radar_powered;
    uint8_t dma_armed_mask;
    uint8_t radar_configuration_known;
};

struct ld2450_spi_completion {
    void *buffer;
    size_t size;
    uint8_t rx_index; /* 0 = RX1 / SPI1, 1 = RX2 / SPI2. */
    uint8_t chip_select_high;
};

struct ld2450_config ld2450_default_config(void);
int ld2450_peripherals_init(const struct ld2450_config *config);
void ld2450_peripherals_deinit(void);
struct ld2450_status ld2450_get_status(void);

/* Power/bias gate control only; does not write radar registers. */
int ld2450_radar_power(uint8_t enabled);

/* One-shot DMA. Arm both lanes BEFORE radar clocking begins. Buffers are
 * borrowed, must be four-byte aligned, and remain owned until completion.
 * CS is an input observed separately; the SDK exposes no slave CS gating. */
int ld2450_spi_arm(uint8_t rx_index, void *buffer, size_t size);
/* Returns 1 on completion, 0 while pending, or a negative error. */
int ld2450_spi_poll(uint8_t rx_index, struct ld2450_spi_completion *completion);

/* Raw I2C transaction, including optional repeated-start read. No register
 * addressing/width is assumed. Address is seven-bit. Stops on every outcome. */
int ld2450_i2c_transfer(uint8_t address, const uint8_t *tx, size_t tx_size,
                       uint8_t *rx, size_t rx_size, uint32_t timeout_ms);
int ld2450_module_uart_write(const uint8_t *data, size_t size);
int ld2450_module_uart_read(uint8_t *data, size_t size, uint32_t timeout_ms);
int ld2450_module_uart_set_baud(uint32_t baud);
int ld2450_debug_write(const char *message);

/* SDK application entry hook. Returns CONFIG_CAPTURE_REQUIRED after
 * successful peripheral setup, because radar register setup is not captured. */
int ld2450_app_start(void);

#endif
