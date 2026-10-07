#ifndef MOCK_USB_SDK_H
#define MOCK_USB_SDK_H
#include <assert.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
typedef uint8_t u8,usb_dev;
typedef uint16_t u16;
typedef uint32_t u32;
#ifdef _MSC_VER
#define __attribute__(x)
#endif
#define ASSERT(x,...) assert(x)
#define USB_ENDPOINT_XFER_BULK 2
#define USB_ENDPOINT_XFER_INT 3
#define USB_EP0_SET_STALL 3
#define USB_EP0_STAGE_SETUP 0
#define USB_CONFIGURED 4
#define CDC_CLASS 16
#define TXCSRP_TxPktRdy 1
#define TXCSRP_FIFONotEmpty 2
#define TXCSRP_SendStall 16
#define RXCSRP_RxPktRdy 1
struct usb_device_t {u8 bDeviceStates;};
struct usb_ctrlrequest {u8 bRequestType,bRequest;u16 wValue,wIndex,wLength;};
static struct usb_device_t device;
static u32 now,txcsr,txcount,setup_phase;
static u16 sof;
static unsigned locked,submits,ep_reads,bulk_reads;
static u8 out_packet[256];
static u32 out_size;
static u8 *dma_in;
static void (*tx_handler)(struct usb_device_t *,u32);
static unsigned tx_irq_enabled;
static void local_irq_disable(void) {++locked;}
static void local_irq_enable(void) {assert(locked);--locked;}
static u32 timer_get_ms(void) {return now;}
static u16 usb_read_sofframe(usb_dev id) {(void)id;return sof;}
static struct usb_device_t *usb_id2device(usb_dev id) {(void)id;return &device;}
static u32 usb_read_txcsr(usb_dev id,u32 ep) {(void)id;assert(ep==4);return txcsr;}
static void usb_write_txcsr(usb_dev id,u32 ep,u32 value) {(void)id;assert(ep==4 && locked);txcsr=value;++submits;}
static void usb_write_ep_cnt(usb_dev id,u32 ep,u32 n) {(void)id;assert(ep==4 && n<=64 && locked);txcount=n;}
static int usb_device_mode(usb_dev id,u32 mode) {(void)id;(void)mode;return 0;}
static void usb_g_ep_config(usb_dev id,u32 ep,u32 type,u32 irq,u8 *buffer,u32 size) {
    (void)id;(void)type;assert((ep&15)<5 && size<=64);if(ep==0x84) {dma_in=buffer;tx_irq_enabled=irq;}
}
static void usb_g_set_intr_hander(usb_dev id,u32 ep,void (*fn)(struct usb_device_t *,u32)) {
    (void)id;assert(ep==0x84);tx_handler=fn;
}
static void usb_enable_ep(usb_dev id,u32 ep) {(void)id;assert(ep<5);}
static unsigned rx_polls;
static u32 usb_read_rxcsr(usb_dev id,u32 ep) {(void)id;assert(ep==4);++rx_polls;return out_size?RXCSRP_RxPktRdy:0;}
static u32 usb_read_rxcount(usb_dev id,u32 ep) {(void)id;assert(ep==4);return out_size;}
static u32 usb_g_bulk_read(usb_dev id,u32 ep,u8 *p,u32 n,u32 block) {
    /* The SDK flushes the FIFO when entered without a packet: never allowed. */
    u32 size=out_size;(void)id;assert(ep==4 && !block && size && n==size);++bulk_reads;
    memcpy(p,out_packet,size);out_size=0;return size;
}
static void usb_read_ep0(usb_dev id,u8 *p,u32 n) {(void)id;assert(n==7);memset(p,0,n);++ep_reads;}
static void usb_set_setup_recv(struct usb_device_t *d,u32 (*f)(struct usb_device_t *,struct usb_ctrlrequest *)) {(void)d;(void)f;}
static void usb_set_data_payload(struct usb_device_t *d,struct usb_ctrlrequest *r,const void *p,u32 n) {(void)d;(void)r;(void)p;assert(n<=7);}
static void usb_set_setup_phase(struct usb_device_t *d,u32 p) {(void)d;setup_phase=p;}
static void usb_set_interface_hander(usb_dev id,u32 itf,u32 (*f)(struct usb_device_t *,struct usb_ctrlrequest *)) {(void)id;(void)f;assert(itf==0);}
static void usb_set_reset_hander(usb_dev id,u32 itf,void (*f)(struct usb_device_t *,u32)) {(void)id;(void)f;assert(itf==0);}
#endif
