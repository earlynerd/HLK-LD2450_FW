#include <stdint.h>
#include <stdio.h>
struct task_info { const char *name; int priority, stack, queue; };
uint32_t timer_get_ms(void);
void clr_wdt(void);
void os_time_dly(int ticks);
