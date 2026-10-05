#include "ld2450_peripherals.h"
#include "ld2450_radar_init.h"
#include "mock_sdk.h"
#include "sdk_bridge.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "line %d: %s\n", __LINE__, #x); exit(1); } } while (0)
#ifdef _MSC_VER
#define ALIGNED4 __declspec(align(4))
#else
#define ALIGNED4 __attribute__((aligned(4)))
#endif
static ALIGNED4 uint8_t buffers[2][2056];
static void reset(void) { ld2450_peripherals_deinit(); mock_sdk_reset(); }
static void init(void)
{
    struct ld2450_config cfg = ld2450_default_config();
    CHECK(ld2450_peripherals_init(&cfg) == LD2450_OK);
}

static void test_initialization(void)
{
    unsigned p;
    struct ld2450_config cfg = ld2450_default_config();
    static const uint8_t input_pins[] = {16, 17, 18, 19, 24, 25, 26, 27, 36, 37};
    reset(); mock_iomap.CON1 = 0xffffffff;
    init();
    CHECK(ld2450_get_status().initialized && !ld2450_get_status().radar_powered);
    CHECK(!ld2450_get_status().radar_bias_enabled);
    CHECK(mock_gpio[34].value == 1 && mock_gpio[35].value == 0);
    CHECK(mock_gpio[34].output_calls == 1 && mock_gpio[35].output_calls == 1);
    for (p = 0; p < sizeof(input_pins); ++p) {
        CHECK(mock_gpio[input_pins[p]].direction == 1);
        CHECK(!mock_gpio[input_pins[p]].output_calls);
        CHECK(mock_gpio[input_pins[p]].die);
    }
    CHECK(mock_gpio[17].pull_up == 1); /* PB1 / RESET remains an input. */
    CHECK(!mock_gpio[36].pull_up && !mock_gpio[37].pull_up);
    CHECK((mock_iomap.CON1 & ((1u << 4) | (1u << 16))) == 0);
    CHECK((mock_iomap.CON1 & (3u << 18)) == (1u << 18));
    CHECK((mock_iomap.CON1 & (1u << 31)) != 0); /* Unrelated mux is preserved. */
    CHECK(!mock_spi[0].CON && !mock_spi[1].CON);
    CHECK(!ld2450_get_status().spi_ready);
    CHECK(ld2450_spi_prepare() == LD2450_OK);
    for (p = 0; p < 2; ++p) {
        uint32_t con = mock_spi[p].CON;
        CHECK(con & LD_SPI_ENABLE); CHECK(con & LD_SPI_SLAVE); CHECK(con & LD_SPI_RECEIVE);
        CHECK(!(con & (LD_SPI_IDLE_HIGH | LD_SPI_SAMPLE_FALL | (1u << 2) | (1u << 13) | (3u << 10))));
        CHECK(mock_spi[p].CNT == 0);
    }
    CHECK(mock_iic.BAUD == 119); CHECK(mock_iic.CON0 & LD_I2C_ENABLE);
    CHECK(mock_uart_config[0].tx_pin == 1 && mock_uart_config[0].rx_pin == 0);
    CHECK(mock_uart_config[0].baud == 256000 && mock_uart_config[0].rx_cbuf_size == 1024);
    CHECK(((uintptr_t)mock_uart_config[0].rx_cbuf & 3) == 0);
    CHECK(mock_uart_config[1].tx_pin == 9 && mock_uart_config[1].rx_pin == 255);
    CHECK(ld2450_peripherals_init(&cfg) == LD2450_BUSY);
    CHECK(ld2450_radar_bias(1) == LD2450_NOT_READY);
    CHECK(ld2450_radar_power(1) == LD2450_OK);
    CHECK(mock_gpio[34].value == 0 && mock_gpio[35].value == 0);
    CHECK(ld2450_radar_bias(1) == LD2450_OK);
    CHECK(mock_gpio[34].value == 0 && mock_gpio[35].value == 1);
    CHECK(ld2450_radar_power(0) == LD2450_OK);
    CHECK(mock_gpio[34].value == 1 && mock_gpio[35].value == 0);
    ld2450_peripherals_deinit();
    CHECK(mock_uart_close_count == 2 && !mock_spi[0].CON && !mock_spi[1].CON && !mock_iic.CON0);
    CHECK(!ld2450_get_status().initialized);

    reset(); cfg.i2c_hz = 1000;
    CHECK(ld2450_peripherals_init(&cfg) == LD2450_CLOCK_RANGE);
    CHECK(mock_uart_open_count == 0 && mock_gpio[34].output_calls == 0);
    cfg.i2c_hz = 13000000;
    CHECK(ld2450_peripherals_init(&cfg) == LD2450_CLOCK_RANGE);
    CHECK(ld2450_peripherals_init(NULL) == LD2450_BAD_ARGUMENT);
    cfg = ld2450_default_config(); cfg.module_uart_baud = 0;
    CHECK(ld2450_peripherals_init(&cfg) == LD2450_BAD_ARGUMENT);
    reset(); mock_uart_fail_on = 2; cfg = ld2450_default_config();
    CHECK(ld2450_peripherals_init(&cfg) == LD2450_UART_UNAVAILABLE);
    CHECK(mock_uart_close_count == 1 && !ld2450_get_status().initialized);
    CHECK(!mock_spi[0].CON && !mock_spi[1].CON && !mock_iic.CON0);
    CHECK(mock_gpio[34].value == 1 && mock_gpio[35].value == 0);
    reset(); cfg.enable_debug_uart = 0; cfg.swap_module_uart_pins = 1;
    CHECK(ld2450_peripherals_init(&cfg) == LD2450_OK);
    CHECK(mock_uart_open_count == 1 && mock_uart_config[0].tx_pin == 0 && mock_uart_config[0].rx_pin == 1);
    CHECK(ld2450_debug_write("test") == LD2450_NOT_READY);
}

static void test_dma(void)
{
    struct ld2450_spi_completion done;
    reset(); CHECK(ld2450_spi_arm(0, buffers[0], 2056) == LD2450_NOT_READY); init();
    CHECK(ld2450_spi_arm(2, buffers[0], 2056) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_spi_arm(0, buffers[0] + 1, 100) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_spi_arm(0, buffers[0], 0) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_spi_arm(0, buffers[0], 65536) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_spi_arm(0, buffers[0], 2056) == LD2450_NOT_READY);
    CHECK(ld2450_spi_prepare() == LD2450_OK);
    CHECK(ld2450_spi_arm(0, buffers[0], 2056) == LD2450_OK);
    CHECK(ld2450_spi_prepare() == LD2450_BUSY);
    CHECK(ld2450_spi_arm(1, buffers[1], 2056) == LD2450_OK);
    CHECK(ld2450_get_status().dma_armed_mask == 3);
    CHECK(ld2450_spi_arm(0, buffers[0], 2056) == LD2450_BUSY);
    CHECK(mock_spi[0].CNT == 2056 && mock_spi[1].CNT == 2056);
    CHECK(ld2450_spi_poll(0, &done) == 0);
    mock_spi[1].CON |= LD_SPI_PENDING; mock_gpio[27].value = 1;
    CHECK(ld2450_spi_poll(1, &done) == 1);
    CHECK(done.buffer == buffers[1] && done.size == 2056 && done.rx_index == 1 && done.chip_select_high);
    CHECK(ld2450_get_status().dma_armed_mask == 1);
    CHECK(ld2450_spi_poll(1, &done) == LD2450_NOT_READY);
    mock_spi[0].CON |= LD_SPI_PENDING;
    CHECK(ld2450_spi_poll(0, &done) == 1 && done.buffer == buffers[0] && !done.chip_select_high);
    CHECK(ld2450_spi_arm(0, buffers[0], 2056) == LD2450_OK);
    CHECK(ld2450_radar_power(0) == LD2450_OK);
    CHECK(!mock_spi[0].CNT && !ld2450_get_status().dma_armed_mask);
    CHECK(!mock_gpio[17].output_calls && !mock_gpio[26].output_calls);
}

static void test_i2c(void)
{
    uint8_t tx[] = {0x12, 0x34}, rx[2];
    reset(); init();
    CHECK(ld2450_i2c_transfer(0x20, tx, 2, rx, 2, 100) == LD2450_NOT_READY);
    CHECK(ld2450_radar_power(1) == LD2450_OK);
    mock_i2c_read_data[0] = 0xab; mock_i2c_read_data[1] = 0xcd; mock_i2c_read_size = 2;
    CHECK(ld2450_i2c_transfer(0x20, tx, 2, rx, 2, 100) == LD2450_OK);
    CHECK(rx[0] == 0xab && rx[1] == 0xcd && mock_i2c_event_count == 7);
    CHECK(mock_i2c_events[0].byte == 0x40 && mock_i2c_events[0].start);
    CHECK(mock_i2c_events[1].byte == 0x12 && mock_i2c_events[2].byte == 0x34);
    CHECK(mock_i2c_events[3].byte == 0x41 && mock_i2c_events[3].start);
    CHECK(mock_i2c_events[4].read && !mock_i2c_events[4].nack);
    CHECK(mock_i2c_events[5].read && mock_i2c_events[5].nack);
    CHECK(mock_i2c_events[6].stop);
    CHECK(ld2450_i2c_transfer(0x80, tx, 2, NULL, 0, 10) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_i2c_transfer(0x20, NULL, 0, NULL, 0, 10) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_i2c_transfer(0x20, tx, 2, NULL, 0, 0) == LD2450_BAD_ARGUMENT);
    reset(); init(); ld2450_radar_power(1); mock_i2c_nack_on = 1;
    CHECK(ld2450_i2c_transfer(0x20, tx, 2, NULL, 0, 100) == LD2450_I2C_NACK);
    CHECK(mock_i2c_event_count == 2 && mock_i2c_events[1].stop);
    reset(); init(); ld2450_radar_power(1); mock_i2c_nack_on = 2;
    CHECK(ld2450_i2c_transfer(0x20, tx, 2, NULL, 0, 100) == LD2450_I2C_NACK);
    CHECK(mock_i2c_event_count == 3 && mock_i2c_events[2].stop);
    reset(); init(); ld2450_radar_power(1); mock_i2c_stall = 1; mock_time = UINT32_MAX - 2;
    CHECK(ld2450_i2c_transfer(0x20, tx, 2, NULL, 0, 5) == LD2450_TIMEOUT);
    CHECK(mock_time < 30 && !(mock_iic.CON0 & (LD_I2C_GO | LD_I2C_START | LD_I2C_STOP)));
    mock_i2c_stall = 0;
    CHECK(ld2450_i2c_transfer(0x20, tx, 2, NULL, 0, 100) == LD2450_OK); /* Recovered. */
    CHECK(mock_i2c_events[mock_i2c_event_count - 1].stop);
    reset(); init(); ld2450_radar_power(1);
    CHECK(ld2450_i2c_transfer(0x20, tx, 2, NULL, 0, 2) == LD2450_TIMEOUT); /* Total deadline. */
    CHECK(mock_i2c_events[mock_i2c_event_count - 1].stop);
}

static void test_uart_and_startup(void)
{
    uint8_t tx[] = {0x01, 0xff}, rx[4];
    reset();
    CHECK(ld2450_app_start() == LD2450_OK);
    CHECK(ld2450_get_status().initialized && ld2450_get_status().radar_powered);
    CHECK(mock_i2c_event_count == 400 && mock_uart_tx_size[1] > 0);
    CHECK(ld2450_module_uart_write(tx, 2) == LD2450_OK);
    CHECK(mock_uart_tx_size[0] == 2 && !memcmp(tx, mock_uart_tx[0], 2));
    mock_uart_rx[0] = 0xaa; mock_uart_rx[1] = 0x55; mock_uart_rx_size = 2;
    CHECK(ld2450_module_uart_read(rx, 4, 10) == 2 && rx[0] == 0xaa && rx[1] == 0x55);
    CHECK(ld2450_module_uart_write(NULL, 1) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_module_uart_read(rx, 513, 10) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_module_uart_set_baud(1000000) == LD2450_OK);
    CHECK(mock_uart_config[0].baud == 1000000);
    CHECK(ld2450_module_uart_set_baud(9599) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_module_uart_set_baud(1000001) == LD2450_BAD_ARGUMENT);
    CHECK(mock_uart_config[0].baud == 1000000);
    ld2450_peripherals_deinit();
    CHECK(ld2450_module_uart_set_baud(256000) == LD2450_NOT_READY);
    CHECK(ld2450_module_uart_write(tx, 2) == LD2450_NOT_READY);
}

static void test_radar_startup_order_and_failures(void)
{
    size_t n;
    uint8_t byte = 0x55;
    reset();
    CHECK(ld2450_app_start() == LD2450_OK);
    CHECK(mock_i2c_event_count == 400);
    CHECK(mock_i2c_events[0].time - mock_gpio[34].changed_at >= 20);
    CHECK(mock_gpio[35].spi_enabled == 3); /* Both configured BEFORE REXT high. */
    CHECK(mock_i2c_events[375].time - mock_gpio[35].changed_at >= 3);
    for (n = 0; n < 80; ++n) {
        const struct mock_i2c_event *e = &mock_i2c_events[5 * n];
        const struct ld2450_radar_write *w = &ld2450_build_radar_profile.writes[n];
        CHECK(e[0].start && e[0].byte == 0x40 && e[4].stop);
        CHECK(e[1].byte == w->reg && e[2].byte == (w->value >> 8) &&
              e[3].byte == (w->value & 255));
        CHECK(e[0].power && e[4].power);
        CHECK(e[0].bias == (n >= 75) && e[4].bias == (n >= 75));
        CHECK(e[0].spi_enabled == (n >= 75 ? 3 : 0));
    }
    CHECK(ld2450_get_status().radar_bias_enabled && ld2450_get_status().spi_ready);
    CHECK(!ld2450_get_status().dma_armed_mask); /* Acquisition is a separate step. */
    CHECK(!mock_gpio[17].output_calls);
    for (n = 0; n < 320; ++n) {
        reset(); mock_i2c_nack_on = (unsigned)n + 1;
        CHECK(ld2450_app_start() == LD2450_I2C_NACK);
        CHECK(mock_i2c_tx_count == n + 1); /* No subsequent writes after any NACK. */
        CHECK(ld2450_get_status().initialized && !ld2450_get_status().radar_powered);
        CHECK(mock_gpio[34].value == 1 && mock_gpio[35].value == 0);
        CHECK(!mock_spi[0].CON && !mock_spi[1].CON);
        CHECK(!mock_uart_close_count);
        CHECK(ld2450_module_uart_write(&byte, 1) == LD2450_OK);
    }
    reset(); mock_i2c_stall = 1;
    CHECK(ld2450_app_start() == LD2450_TIMEOUT);
    CHECK(!ld2450_get_status().radar_powered);
    CHECK(ld2450_module_uart_write(&byte, 1) == LD2450_OK);
    reset(); mock_uart_fail_on = 1;
    CHECK(ld2450_app_start() == LD2450_UART_UNAVAILABLE);
    CHECK(!ld2450_get_status().initialized && !mock_i2c_event_count);
    reset(); mock_time = UINT32_MAX - 5;
    CHECK(ld2450_delay_ms(20) == LD2450_OK && mock_time < 40);
    for (n = 0; n < 10; ++n) {
        uint32_t start;
        reset(); mock_timer_quantum = 10; mock_time = (uint32_t)n;
        start = mock_time;
        CHECK(ld2450_delay_ms(3) == LD2450_OK);
        CHECK(mock_time - start >= 3 && mock_time - start <= 21);
        start = mock_time;
        CHECK(ld2450_delay_ms(20) == LD2450_OK);
        CHECK(mock_time - start >= 20 && mock_time - start <= 31);
    }
    CHECK(ld2450_delay_ms(0) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_delay_ms(1001) == LD2450_BAD_ARGUMENT);
}

int main(void)
{
    test_initialization(); test_dma(); test_i2c(); test_uart_and_startup(); test_radar_startup_order_and_failures();
    puts("Validated pin ownership, mode/baud setup, rollback, dual DMA, I2C deadlines/recovery, UART, and startup status.");
    return 0;
}
