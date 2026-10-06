/* Exercise the actual adapter, substituting only device I/O and SDK engine.
 * This does not emulate the closed-source updater or execute the stock loader. */
#include <stdio.h>
#include <stdlib.h>
#include <setjmp.h>
#include "../target/br23/image/uart_loader.c"
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"line %d: %s\n",__LINE__,#x); exit(1); } } while (0)
u8 mock_update_ram[128];
static u8 incoming[2048], saved[112];
static size_t head, tail;
static u32 now, actual_baud, desired_baud;
static unsigned reads, stops, writes, engine_calls, resets, shutdowns;
static int bad_first, drop_reads, drop_stop, writer_failure;
static jmp_buf reboot;
static void (*state_cb)(update_mode_info_t *,u32,void *);

static void queue(const u8 *p, size_t n)
{
    size_t len;
    if (head == tail) head = tail = 0;
    CHECK(tail + n + 6 <= sizeof(incoming));
    len = ld_update_frame(incoming+tail,sizeof(incoming)-tail,p,n);
    CHECK(len); tail += len;
}
u32 timer_get_ms(void) { return now; }
void clr_wdt(void) {}
void os_time_dly(int n) { now += (u32)n * 10; }
void local_irq_disable(void) { CHECK(shutdowns); }
void hwi_all_close(void) { CHECK(shutdowns); }
void cpu_reset(void) { ++resets; longjmp(reboot,1); }
u16 CRC16(const void *p, u32 n) { return ld_update_crc(p,n); }
int ld2450_module_uart_read(uint8_t *p, size_t n, uint32_t timeout)
{
    CHECK(n == 1);
    if (head < tail) { *p = incoming[head++]; return 1; }
    now += timeout; return 0;
}
int ld2450_module_uart_set_baud(uint32_t n) { actual_baud=n; return 0; }
int ld2450_debug_write(const char *p) { CHECK(p); return 0; }
void ld2450_peripherals_deinit(void) { ++shutdowns; }
int ld2450_radar_power(uint8_t enable) { CHECK(!enable); return 0; }
int ld2450_module_uart_write(const uint8_t *wire, size_t n)
{
    const u8 *p=wire+4;
    u8 response[LD_UPDATE_PAYLOAD_MAX];
    CHECK(n >= 7 && ld_update_crc(wire,n-2) == (u16)(wire[n-2] | wire[n-1]<<8));
    if (p[0] == 1) {
        response[0]=1; ld_update_put_u32(response+1,desired_baud); queue(response,5);
    } else if (p[0] == 2) {
        u32 offset=ld_update_u32(p+1), count=ld_update_u32(p+5), i;
        ++reads; CHECK(count && count<=512);
        if (drop_reads) return 0;
        memcpy(response,p,9);
        if (bad_first && reads == 1) ld_update_put_u32(response+1,offset+1);
        for (i=0;i<count;++i) response[9+i]=(u8)(offset+i);
        queue(response,9+count);
    } else if (p[0] == 3) {
        ++stops;
        if (!drop_stop) queue(p,2);
    } else if (p[0] == 4) queue(p,1);
    else CHECK(0);
    return 0;
}
static u32 write_record(u32 priv, u8 *record, u16 len)
{
    CHECK(priv==0x1234 && len==sizeof(saved)); ++writes;
    memcpy(saved,record,len); return (u32)writer_failure;
}
void update_module_init(void (*cb)(update_mode_info_t *,u32,void *)) { state_cb=cb; }
int app_active_update_task_init(update_mode_info_t *mode)
{
    u8 data[700]; size_t i;
    succ_report_t report={0x31000,0x1234,write_record};
    update_ret_code_t result={0,0};
    CHECK(mode->type==UART_UPDATA && !mode->task_en); ++engine_calls;
    state_cb(mode,UPDATE_CH_INIT,NULL);
    mode->p_op_api->ch_init(NULL,NULL);
    CHECK(mode->p_op_api->f_open()==1);
    CHECK(mode->p_op_api->notify_update_content_size(NULL,700)==0);
    CHECK(mode->p_op_api->f_seek(NULL,0,123)==0);
    if (mode->p_op_api->f_read(NULL,data,sizeof(data)) != sizeof(data)) {
        result.stu=-1; result.err_code=7;
    } else {
        for(i=0;i<sizeof(data);++i) CHECK(data[i]==(u8)(123+i));
        state_cb(mode,UPDATE_CH_SUCESS_REPORT,&report);
    }
    state_cb(mode,UPDATE_CH_EXIT,&result);
    return 0;
}
static void fresh(void)
{
    head=tail=0; now=0; actual_baud=desired_baud=ENTRY_BAUD;
    reads=stops=writes=engine_calls=resets=shutdowns=0;
    bad_first=drop_reads=drop_stop=writer_failure=0;
    parser.used=0; baud=ENTRY_BAUD; transport_failed=have_success=0;
    memset(mock_update_ram,0xa5,sizeof(mock_update_ram));
    ld2450_uart_loader_init();
}
static void session(void)
{
    u8 ready=6; queue(&ready,1);
    if (!setjmp(reboot)) ld2450_uart_loader_poll();
}
int main(void)
{
    UPDATA_UART parameters;
    fresh(); CHECK(ld2450_uart_loader_poll() == 0);
    { u8 wrong=7; queue(&wrong,1); CHECK(ld2450_uart_loader_poll() == 0); }
    fresh(); desired_baud=1000001;
    { u8 ready=6; queue(&ready,1); CHECK(ld2450_uart_loader_poll() == 1); }
    CHECK(!engine_calls && !resets);
    fresh(); bad_first=1; desired_baud=1000000; session();
    CHECK(reads==3 && writes==1 && resets==1 && stops==1 && engine_calls==1);
    CHECK(!memcmp(mock_update_ram,saved,sizeof(saved)) && mock_update_ram[112]==0xa5);
    CHECK(UPDATA_FLAG_ADDR->parm_type==UART_UPDATA && UPDATA_FLAG_ADDR->ota_addr==0x31000);
    CHECK(UPDATA_FLAG_ADDR->parm_crc==CRC16(saved+2,78));
    memcpy(&parameters,UPDATA_FLAG_ADDR->parm_priv,sizeof(parameters));
    CHECK(parameters.control_baud==1000000 && parameters.control_io_tx==1 && parameters.control_io_rx==0);
    CHECK(parameters.control_timeout==1000);
    CHECK(update_result_get()==UPDATA_READY && update_result_get()==UPDATA_NON);
    fresh(); drop_reads=1; now=UINT32_MAX-100; session();
    CHECK(reads==4 && !writes && !resets && file_offset==123 && actual_baud==ENTRY_BAUD);
    drop_reads=0; session(); CHECK(engine_calls==2 && writes==1 && resets==1);
    fresh(); drop_stop=1; session(); CHECK(stops==4 && !writes && !resets);
    fresh(); writer_failure=1; session(); CHECK(writes==1 && !resets && !shutdowns);
    CHECK(mock_update_ram[0]==0xa5);
    fresh(); CHECK(file_seek(NULL,0,UINT32_MAX)==0);
    CHECK(file_seek(NULL,1,1)==-1 && file_seek(NULL,2,0)==-1);
    { u8 byte; CHECK(file_read(NULL,&byte,1)==0 && !reads); }
    fresh(); desired_baud=1000001; session(); CHECK(!engine_calls && !writes && !resets);
    puts("Adapter retry, bounds, timeout rollover, baud, repeated sessions and verified handoff passed.");
    return 0;
}
