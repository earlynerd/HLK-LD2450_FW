#ifndef LD_IMAGE_APP_CONFIG_H
#define LD_IMAGE_APP_CONFIG_H
#include "asm/clock_define.h"
#define CONFIG_FLASH_SIZE (256 * 1024)
#define LIB_DEBUG 1
/* The linked full logger requires setup.c's log_early_init(), including its
 * RTOS mutex. Lite mode omits that initialization. */
#define CONFIG_DEBUG_ENABLE
#define CONFIG_DEBUG_LIB(x) (x)
#define TCFG_CLOCK_SYS_SRC SYS_CLOCK_INPUT_PLL_BT_OSC
#define TCFG_CLOCK_OSC_HZ 24000000
/* Stock V2.14 reports sys=240 MHz; the PLL reference remains 24 MHz. */
#define TCFG_CLOCK_SYS_HZ 240000000
#define TCFG_CLOCK_MODE CLOCK_MODE_ADAPTIVE
#define TCFG_LOWPOWER_POWER_SEL PWR_LDO15
#define AUDIO_OUTPUT_WAY 0
#define AUDIO_OUTPUT_WAY_FM 1
#define CONFIG_DOUBLE_BANK_ENABLE 0
#define CONFIG_UPDATE_ENABLE 1
#define CONFIG_SDFILE_ENABLE 1
#define CONFIG_FATFS_ENABLE 0
#define SDFILE_DEV "sdfile"
#define SDFILE_MOUNT_PATH "mnt/sdfile"
#define USER_UART_UPDATE_ENABLE 0
#define MUTIL_CPU_UART_UPDATE_ENABLE 0
#define TCFG_USER_TWS_ENABLE 0
#define TCFG_USER_BLE_ENABLE 0
#define TCFG_USER_EMITTER_ENABLE 0
#define TCFG_UART0_ENABLE 0
#define TCFG_UART1_ENABLE 0
#define TCFG_UART2_ENABLE 0
#ifdef LD2450_USB_STREAM
#define TCFG_PC_ENABLE 1
#define USB_DEVICE_CLASS_CONFIG CDC_CLASS
#include "usb_common_def.h"
#include "usb_std_class_def.h"
#endif
#ifndef __LD__
void save_spi_port(void);
#endif
#endif
