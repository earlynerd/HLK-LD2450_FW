#ifndef LD2450_SDK_BRIDGE_H
#define LD2450_SDK_BRIDGE_H

#ifdef LD2450_HOST_TEST
#include "mock_sdk.h"
#else
#include "asm/cpu.h"
#include "asm/gpio.h"
#include "asm/clock.h"
#include "asm/timer.h"
#include "asm/uart_dev.h"
#endif

/* Driver bits and mux selection verified against the pinned SDK's
 * cpu/br23/{spi,iic_hw}.c. Avoid spi_open(): it drives unused DO pins,
 * including PB1, which this board uses as the MCU reset input. */
#define LD_SPI_ENABLE          (1u << 0)
#define LD_SPI_SLAVE           (1u << 1)
#define LD_SPI_BIDIR           (1u << 3)
#define LD_SPI_SAMPLE_FALL     (1u << 4)
#define LD_SPI_SHIFT_FALL      (1u << 5)
#define LD_SPI_IDLE_HIGH       (1u << 6)
#define LD_SPI_CS_IDLE_HIGH    (1u << 7)
#define LD_SPI_RECEIVE         (1u << 12)
#define LD_SPI_CLEAR_PENDING   (1u << 14)
#define LD_SPI_PENDING         (1u << 15)

#define LD_I2C_ENABLE          (1u << 0)
#define LD_I2C_GO              (1u << 2)
#define LD_I2C_READ            (1u << 3)
#define LD_I2C_STOP            (1u << 4)
#define LD_I2C_START           (1u << 5)
#define LD_I2C_SEND_NACK       (1u << 6)
#define LD_I2C_GOT_NACK        (1u << 7)
#define LD_I2C_FILTER          (1u << 9)
#define LD_I2C_CLEAR_END        (1u << 12)
#define LD_I2C_END             (1u << 13)
#define LD_I2C_CLEAR_PENDING   (1u << 14)
#define LD_I2C_PENDING         (1u << 15)

static inline void ld_sdk_sync(void)
{
#ifdef LD2450_HOST_TEST
    mock_sdk_sync();
#else
    __asm__ volatile("csync" ::: "memory");
#endif
}

static inline void ld_spi_clear(JL_SPI_TypeDef *spi)
{
    spi->CON |= LD_SPI_CLEAR_PENDING;
#ifdef LD2450_HOST_TEST
    spi->CON &= ~LD_SPI_PENDING; /* Simulate hardware write-one-to-clear. */
#endif
}

static inline void ld_i2c_clear(uint16_t mask)
{
    JL_IIC->CON0 |= mask;
#ifdef LD2450_HOST_TEST
    if (mask & LD_I2C_CLEAR_PENDING) { JL_IIC->CON0 &= ~LD_I2C_PENDING; }
    if (mask & LD_I2C_CLEAR_END) { JL_IIC->CON0 &= ~LD_I2C_END; }
#endif
}

#endif
