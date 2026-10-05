#ifndef MOCK_UPDATE_SDK_H
#define MOCK_UPDATE_SDK_H
/* Host-only interface model. Target builds use the real, pinned SDK headers. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef struct { u32 control_io_tx, control_io_rx, control_baud, control_timeout; } UPDATA_UART;
typedef struct {
    u16 parm_crc, parm_type, parm_result, magic;
    u8 file_path[32], parm_priv[32];
    u32 ota_addr;
    u16 ext_arg_len, ext_arg_crc;
} UPDATA_PARM;
typedef struct { int stu; u8 err_code; } update_ret_code_t;
typedef struct {
    void (*ch_init)(void (*)(void *), int (*)(void *));
    u16 (*f_open)(void);
    u16 (*f_read)(void *, u8 *, u16);
    int (*f_seek)(void *, u8, u32);
    u16 (*f_stop)(u8);
    int (*notify_update_content_size)(void *, u32);
    void (*ch_exit)(void *);
} update_op_api_t;
typedef struct {
    int32_t type;
    void (*state_cbk)(int, u32, void *);
    const update_op_api_t *p_op_api;
    u8 task_en;
} update_mode_info_t;
typedef struct { u32 loader_saddr, priv_param; u32 (*update_param_write_hdl)(u32,u8 *,u16); } succ_report_t;
#define UPDATE_PRIV_PARAM_LEN 32
#define UPDATA_NON 0x5a00
#define UPDATA_READY 0x5a01
#define UART_UPDATA 0x5a04
#define UPDATE_PARAM_MAGIC 0x5441
#define IO_PORTA_00 0
#define IO_PORTA_01 1
enum { UPDATE_TASK_INIT, UPDATE_CH_INIT, UPDATE_CH_SUCESS_REPORT, UPDATE_CH_EXIT };
extern u8 mock_update_ram[128];
#define UPDATA_FLAG_ADDR ((UPDATA_PARM *)mock_update_ram)
u32 timer_get_ms(void);
void clr_wdt(void);
void os_time_dly(int);
void local_irq_disable(void);
void cpu_reset(void);
u16 CRC16(const void *, u32);
int app_active_update_task_init(update_mode_info_t *);
#endif
