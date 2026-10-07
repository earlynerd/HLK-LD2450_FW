#include <stdlib.h>
#include "../src/capture.c"
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"line %d: %s\n",__LINE__,#x); exit(1); } } while (0)
static uint32_t now;
static int powered, stopped, ready_mask, fail_arm;
static unsigned arm_calls, tx_bytes;
static char output[200000];
uint32_t timer_get_ms(void) { return now; }
void clr_wdt(void) {}
struct ld2450_status ld2450_get_status(void) { struct ld2450_status s={0}; s.radar_powered=(uint8_t)powered; return s; }
int ld2450_debug_write(const char *s) { CHECK(s); return 0; }
int ld2450_radar_power(uint8_t on) { CHECK(!on); powered=0;stopped=1;return 0; }
int ld2450_spi_arm(uint8_t lane, void *buffer, size_t n) {
    CHECK(lane==arm_calls++ && n==32896 && !((uintptr_t)buffer&3));
    return fail_arm && lane==1 ? LD2450_BUSY : 0;
}
int ld2450_spi_poll(uint8_t lane, struct ld2450_spi_completion *done) { (void)done; return (ready_mask & (1<<lane)) ? 1 : 0; }
int ld2450_module_uart_write(const uint8_t *data, size_t n) {
    CHECK(stopped && !powered && tx_bytes+n<sizeof(output));
    memcpy(output+tx_bytes,data,n);tx_bytes+=(unsigned)n;output[tx_bytes]=0;return 0;
}
static void fresh(void) { powered=1;stopped=ready_mask=fail_arm=0;arm_calls=tx_bytes=0;now=0;output[0]=0;active=0; }
int main(void) {
    fresh();CHECK(ld2450_capture_arm()==0);ld2450_capture_poll();CHECK(!tx_bytes);
    ready_mask=1;ld2450_capture_poll();CHECK(!tx_bytes);
    ready_mask=3;ld2450_capture_poll();CHECK(strstr(output,"lane=0 size=32896 complete=1"));
    CHECK(strstr(output,"lane=1 size=32896 complete=1") && strstr(output,"DATA 1 8060 "));
    {unsigned old=tx_bytes;ld2450_capture_poll();CHECK(tx_bytes==old);}
    fresh();now=UINT32_MAX-500;CHECK(!ld2450_capture_arm());now+=1999;ld2450_capture_poll();CHECK(!tx_bytes);
    now++;ld2450_capture_poll();CHECK(strstr(output,"lane=0 size=32896 complete=0") && strstr(output,"a5a5a5a5"));
    fresh();CHECK(!ld2450_capture_arm());powered=0;ld2450_capture_poll();CHECK(!active && !tx_bytes);
    fresh();fail_arm=1;CHECK(ld2450_capture_arm()==LD2450_BUSY && stopped && !active);
    puts("Capture completion, bounded timeout/rollover, updater cancellation and stop-before-dump passed.");return 0;
}
