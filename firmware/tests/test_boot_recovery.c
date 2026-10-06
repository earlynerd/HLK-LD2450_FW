/* Execute the actual app_main ordering with simulated time and updater I/O. */
#include <stdlib.h>
#include <setjmp.h>
#include <string.h>
#include "../target/br23/image/main.c"
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"line %d: %s\n",__LINE__,#x); exit(1); } } while (0)
static uint32_t now, start_time;
static int uart_ready, loader_ready, app_calls, poll_calls, claim_at, uart_error;
static jmp_buf done;
uint32_t timer_get_ms(void) { return now; }
void clr_wdt(void) {}
void os_time_dly(int ticks) { CHECK(uart_error && !loader_ready && !app_calls); (void)ticks; longjmp(done, 1); }
void ld2450_console_write(const char *s) { CHECK(s); }
int ld2450_debug_write(const char *s) { CHECK(s && uart_ready); return 0; }
struct ld2450_config ld2450_default_config(void) { struct ld2450_config c = {100000,256000,115200,1,0}; return c; }
int ld2450_uart_init(const struct ld2450_config *c) { CHECK(c->module_uart_baud==256000 && !loader_ready && !app_calls); uart_ready=!uart_error; return uart_error; }
struct ld2450_status ld2450_get_status(void) { struct ld2450_status s = {0}; s.initialized=(uint8_t)uart_ready; return s; }
void ld2450_uart_loader_init(void) { CHECK(uart_ready && !app_calls); loader_ready=1; }
int ld2450_app_start(void) {
    CHECK(loader_ready && !claim_at && (uint32_t)(now-start_time)>=3000);
    ++app_calls;
    return LD2450_I2C_NACK; /* A failed radar init must still service updater. */
}
int ld2450_uart_loader_poll(void) {
    CHECK(uart_ready && loader_ready);
    ++poll_calls; now+=20;
    if (claim_at && poll_calls>=250) { CHECK(!app_calls); longjmp(done,1); }
    if (app_calls) { CHECK(app_calls==1); longjmp(done,1); }
    return claim_at==poll_calls;
}
static void run(uint32_t at, int claim, int error) {
    now=start_time=at; uart_ready=loader_ready=app_calls=poll_calls=0;
    claim_at=claim; uart_error=error;
    if (!setjmp(done)) app_main();
}
int main(void) {
    run(0,0,0); CHECK(app_calls==1 && poll_calls==151);
    run(UINT32_MAX-1000u,0,0); CHECK(app_calls==1 && poll_calls==151);
    run(0,1,0); CHECK(!app_calls && poll_calls==250);
    run(0,150,0); CHECK(!app_calls && poll_calls==250);
    run(0,0,LD2450_UART_UNAVAILABLE); CHECK(!app_calls && !poll_calls);
    puts("Boot recovery timing, rollover, early/late failed entry latch and radar failure fallback passed.");
    return 0;
}
