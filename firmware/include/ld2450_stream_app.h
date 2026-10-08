#ifndef LD2450_STREAM_APP_H
#define LD2450_STREAM_APP_H
#include <stddef.h>
#include <stdint.h>
int ld2450_stream_app_init(void);
#ifdef LD2450_FFT_SELFTEST
/* Hardware FFT characterisation on idle scratch memory; prints on PA9. */
void ld2450_fft_selftest(void *scratch, size_t size);
#endif
int ld2450_stream_app_arm(void);
void ld2450_stream_app_poll(void);
void ld2450_stream_app_stop(void);
void ld2450_stream_app_report(void); /* Explicit '?' UART command stops acquisition. */
uint32_t ld2450_stream_clock_us(void);
int ld2450_usb_init(void);
void ld2450_usb_stop(void);
int ld2450_usb_ready(void);
int ld2450_usb_write(void *, const uint8_t *, size_t);
/* Host command bytes received on the CDC bulk OUT endpoint. Nonblocking;
 * returns the count copied (0 when none). capacity must be at least
 * LD2450_USB_READ_BYTES. Main task only. */
#define LD2450_USB_READ_BYTES 256u
int ld2450_usb_read(uint8_t *data, size_t capacity);
void ld2450_usb_flush(void);
void ld2450_usb_discard(void);
uint32_t ld2450_usb_epoch(void);
void ld2450_usb_bus_suspend(void);
void ld2450_usb_irq_elapsed(uint32_t us);
struct ld2450_usb_diagnostics {
    uint32_t initialized, dtr, device_state, epoch, sof, sof_age_ms, txcsr;
    uint32_t resets, suspends, control_requests, control_value;
    uint32_t ready_polls, writes, busy, bytes;
    uint32_t tx_queued,tx_peak,tx_interrupts;
    uint32_t irq_us,irq_max_us,irq_calls;
};
void ld2450_usb_snapshot(struct ld2450_usb_diagnostics *);
#endif
