/* Blocking UART transport: app_core is the only UART reader, including while
 * the SDK engine runs with task_en=0. No parser state crosses tasks or ISRs. */
#ifdef LD2450_LOADER_HOST_TEST
#include "mock_update_sdk.h"
#else
#include "system/includes.h"
#include "asm/includes.h"
#include "update.h"
#include "update_loader_download.h"
#endif
#include "ld2450_peripherals.h"
#include "uart_update_protocol.h"
#ifdef LD2450_USB_STREAM
#include "ld2450_stream_app.h"
#endif

#define ENTRY_BAUD 256000u
#define WAIT_MS 700u
#ifdef _MSC_VER
#define UPDATE_ALIGN4 __declspec(align(4))
#else
#define UPDATE_ALIGN4 __attribute__((aligned(4)))
#endif
typedef char uart_parameter_size_check[sizeof(UPDATA_UART) == 16 ? 1 : -1];
typedef char update_parameter_size_check[sizeof(UPDATA_PARM) == 80 ? 1 : -1];
typedef char update_reserved_ram_check[sizeof(UPDATA_PARM) + UPDATE_PRIV_PARAM_LEN <= 120 ? 1 : -1];
static struct ld_update_parser parser;
static UPDATE_ALIGN4 uint8_t tx[LD_UPDATE_FRAME_MAX];
static uint32_t file_offset, baud = ENTRY_BAUD;
static succ_report_t success;
static uint8_t have_success, transport_failed;
extern void update_module_init(void (*cb)(update_mode_info_t *, u32, void *));
extern void hwi_all_close(void);

static int send_payload(const uint8_t *p, size_t n)
{
    size_t len = ld_update_frame(tx, sizeof(tx), p, n);
    return len ? ld2450_module_uart_write(tx, len) : -1;
}
static size_t receive(uint32_t timeout)
{
    uint32_t start = timer_get_ms(), last = start;
    uint8_t byte;
    while ((uint32_t)(timer_get_ms() - start) < timeout) {
        size_t n;
        int r;
        clr_wdt();
        r = ld2450_module_uart_read(&byte, 1, 10);
        if (r < 0) { transport_failed = 1; return 0; }
        if ((uint32_t)(timer_get_ms() - last) > 100u) parser.used = 0;
        if (r != 1) continue;
        last = timer_get_ms();
        n = ld_update_feed(&parser, byte);
        if (n) return n;
    }
    parser.used = 0;
    return 0;
}
static size_t receive_remaining(uint32_t start)
{
    uint32_t elapsed = (uint32_t)(timer_get_ms() - start);
    return elapsed < WAIT_MS ? receive(WAIT_MS - elapsed) : 0;
}
static int exchange(const uint8_t *p, size_t n, uint8_t opcode)
{
    unsigned attempt;
    for (attempt = 0; attempt < 4; ++attempt) {
        uint32_t start;
        if (send_payload(p, n)) return -1;
        start = timer_get_ms();
        while ((uint32_t)(timer_get_ms() - start) < WAIT_MS) {
            size_t size = receive_remaining(start);
            if (size && parser.frame[4] == opcode &&
                ((opcode == 3 && (size == 1 || (size == 2 && parser.frame[5] == p[1]))) ||
                 (opcode != 3 && size == 1))) return 0;
        }
    }
    return -1;
}
static void channel_init(void (*resume)(void *), int (*sleep)(void *))
{
    /* This transport performs blocking reads itself; SDK wake/sleep callbacks
     * are intentionally unnecessary in task_en=0 mode. */
    (void)resume; (void)sleep;
    file_offset = 0; transport_failed = 0;
}
static u16 file_open(void) { file_offset = 0; return 1; }
static u16 file_read(void *fp, u8 *out, u16 len)
{
    uint32_t done = 0;
    (void)fp;
    if (!len || file_offset > UINT32_MAX - len) return 0;
    while (done < len) {
        uint32_t count = len - done;
        unsigned attempt;
        uint8_t request[9] = {2};
        int accepted = 0;
        if (count > LD_UPDATE_DATA_MAX) count = LD_UPDATE_DATA_MAX;
        ld_update_put_u32(request + 1, file_offset + done);
        ld_update_put_u32(request + 5, count);
        for (attempt = 0; attempt < 4 && !accepted; ++attempt) {
            uint32_t start;
            if (send_payload(request, sizeof(request))) break;
            start = timer_get_ms();
            while ((uint32_t)(timer_get_ms() - start) < WAIT_MS) {
                size_t n = receive_remaining(start);
                if (n && ld_update_read_reply(parser.frame + 4, n, file_offset + done,
                                               count, out + done, len - done) == (int)count) {
                    accepted = 1; break;
                }
            }
        }
        if (!accepted) { transport_failed = 1; return 0; }
        done += count;
    }
    file_offset += done;
    return len;
}
static int file_seek(void *fp, u8 type, u32 offset)
{
    (void)fp;
    if (type == 0) file_offset = offset;
    else if (type == 1 && offset <= UINT32_MAX - file_offset) file_offset += offset;
    else return -1;
    return 0;
}
static u16 file_stop(u8 error)
{
    uint8_t p[2] = {3, error};
    if (exchange(p, sizeof(p), 3)) transport_failed = 1;
    return 0;
}
static int content_size(void *priv, u32 size)
{
    uint8_t p[5] = {4}; (void)priv;
    ld_update_put_u32(p + 1, size);
    if (exchange(p, sizeof(p), 4)) { transport_failed = 1; return -1; }
    return 0;
}
static const update_op_api_t ops = {
    .ch_init = channel_init, .f_open = file_open, .f_read = file_read,
    .f_seek = file_seek, .f_stop = file_stop, .notify_update_content_size = content_size
};

/* Startup.S calls this before application startup. Match the SDK's result
 * validation/clear behavior without importing soundbox UI and audio code. */
u16 update_result_get(void)
{
    UPDATA_PARM *p = UPDATA_FLAG_ADDR;
    u16 crc = CRC16((u8 *)p + 2, sizeof(*p) - 2);
    u16 result = crc && crc == p->parm_crc ? p->parm_result : UPDATA_NON;
    memset(p, 0, sizeof(*p));
    return result;
}
static void state_changed(update_mode_info_t *info, u32 state, void *priv)
{
    (void)info;
    if (state == UPDATE_CH_INIT) { have_success = 0; memset(&success, 0, sizeof(success)); }
    if (state == UPDATE_CH_SUCESS_REPORT && priv) {
        memcpy(&success, priv, sizeof(success));
        have_success = success.loader_saddr && success.update_param_write_hdl;
    }
    if (state == UPDATE_CH_EXIT && priv) {
        update_ret_code_t *ret = priv;
        if (ret->stu == 0 && ret->err_code == 0 && have_success && !transport_failed) {
            UPDATE_ALIGN4 uint8_t record[sizeof(UPDATA_PARM) + UPDATE_PRIV_PARAM_LEN] = {0};
            UPDATA_PARM *p = (UPDATA_PARM *)record;
            UPDATA_UART uart = {IO_PORTA_01, IO_PORTA_00, baud, 1000};
            uint8_t stop[2] = {3, 0x80};
            /* The library's UART single-bank success path does not send STOP.
             * Acknowledge loader-stage completion before committing the handoff. */
            if (exchange(stop, sizeof(stop), 3)) return;
            p->parm_type = UART_UPDATA; p->parm_result = UPDATA_READY;
            p->magic = UPDATE_PARAM_MAGIC; p->ota_addr = success.loader_saddr;
            memcpy(p->parm_priv, &uart, sizeof(uart));
            p->parm_crc = CRC16(record + 2, sizeof(*p) - 2);
            /* Archived writer returns a byte status: zero means verified write. */
            if ((u8)success.update_param_write_hdl(success.priv_param, record, sizeof(record)) != 0) {
                ld2450_debug_write("UPDATE: handoff record verification failed\r\n"); return;
            }
            ld2450_debug_write("UPDATE: entering uart_user loader\r\n");
            ld2450_peripherals_deinit();
            local_irq_disable(); hwi_all_close();
            memcpy(UPDATA_FLAG_ADDR, record, sizeof(record));
            cpu_reset();
        }
    }
}
void ld2450_uart_loader_init(void) { update_module_init(state_changed); }
int ld2450_uart_loader_poll(void)
{
#ifdef LD2450_USB_STREAM
    static uint32_t last_byte;
    size_t n=0;
    unsigned budget;
    if ((uint32_t)(timer_get_ms()-last_byte)>100u) parser.used=0;
    for (budget=0;budget<64 && !n;++budget) {
        uint8_t byte;
        int got=ld2450_module_uart_read_nowait(&byte,1);
        if(got!=1) break;
        last_byte=timer_get_ms();
        if(byte=='?' && !parser.used) {ld2450_stream_app_report();continue;}
        n=ld_update_feed(&parser,byte);
    }
#else
    size_t n = receive(20);
#endif
    unsigned attempt;
    uint8_t start[1] = {1};
    if (n != 1 || parser.frame[4] != 6) return 0;
#ifdef LD2450_USB_STREAM
    ld2450_stream_app_stop();
#endif
    ld2450_radar_power(0);
    for (attempt = 0; attempt < 6; ++attempt) {
        uint32_t proposed;
        send_payload(start, sizeof(start));
        n = receive(WAIT_MS);
        if (n != 5 || parser.frame[4] != 1) continue;
        proposed = ld_update_u32(parser.frame + 5);
        if (proposed < 9600 || proposed > 1000000) continue;
        if (proposed != baud) {
            if (ld2450_module_uart_set_baud(proposed)) break;
            baud = proposed; os_time_dly(2); continue;
        }
        {
            update_mode_info_t mode = {.type=UART_UPDATA, .p_op_api=&ops, .task_en=0};
            int result = app_active_update_task_init(&mode);
            if (result) ld2450_debug_write("UPDATE: engine busy\r\n");
        }
        break;
    }
    baud = ENTRY_BAUD;
    ld2450_module_uart_set_baud(baud);
    parser.used = 0;
    return 1; /* Valid READY, including an aborted or failed transaction. */
}
