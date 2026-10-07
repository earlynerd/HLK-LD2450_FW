/* CDC ACM with a bounded owned staging ring. The completion interrupt feeds
 * bulk IN while the main task processes radar records. No waits or allocation. */
#ifdef LD2450_USB_HOST_TEST
#include "mock_usb_sdk.h"
#else
#include "system/includes.h"
#include "app_config.h"
#include "usb/device/usb_stack.h"
#include "usb/usb_config.h"
#endif
#include "ld2450_stream_app.h"

static u8 bulk_in[68] __attribute__((aligned(4)));
#define TX_CAPACITY 4096u
static u8 tx_queue[TX_CAPACITY];
static volatile u32 tx_head,tx_used,tx_peak,tx_interrupts;
static u8 bulk_out[136] __attribute__((aligned(4)));
static u8 notification[12] __attribute__((aligned(4)));
static u8 line_coding[7]={0x00,0xc2,0x01,0,0,0,8};
static volatile u8 dtr, initialized;
static volatile u32 epoch;
static u8 need_zlp,flush_requested;
static u16 last_sof;
static u32 sof_time;
static volatile u32 resets,suspends,control_requests,control_value;
static u32 ready_polls,busy;
static volatile u32 writes,bytes;
static volatile u32 irq_us,irq_max_us,irq_calls;
void ld2450_usb_irq_elapsed(uint32_t us) {
    irq_us+=us;++irq_calls;if(us>irq_max_us)irq_max_us=us;
}
static void tx_kick(void);
static void tx_complete(struct usb_device_t *d,u32 ep) {
    (void)d;(void)ep;++tx_interrupts;tx_kick();
}
static void tx_clear(void) {tx_head=tx_used=0;need_zlp=flush_requested=0;}

/* Laboratory identity inherited from the pinned SDK, not an allocated PID. */
static const u8 device_desc[]={18,1,0x10,1,0xef,2,1,64, 'J','L','U','A',0,2,1,2,3,1};
static const u8 config_desc[]={9,2,0,0,0,1,0,0x80,50};
static const u8 language[]={4,3,9,4};
static void string_desc(u8 *out,const char *s) {
    unsigned n=0; while(s[n] && n<60) {out[2+2*n]=(u8)s[n];out[3+2*n]=0;++n;}
    out[0]=(u8)(2+2*n);out[1]=3;
}
void get_device_descriptor(u8 *p) {memcpy(p,device_desc,sizeof(device_desc));}
void get_language_str(u8 *p) {memcpy(p,language,sizeof(language));}
void get_manufacture_str(u8 *p) {string_desc(p,"LD2450 laboratory");}
void get_product_str(u8 *p) {string_desc(p,"LD2450 frame stream");}
void get_iserialnumber_str(u8 *p) {string_desc(p,"LD2450-STREAM-01");}
const u8 *usb_get_config_desc(void) {return config_desc;}
const u8 *usb_get_string_desc(u32 id) {(void)id;return NULL;}
void user_setup_filter_install(struct usb_device_t *d) {(void)d;}
u32 usb_root2_testing(void) {return 0;}

void ld2450_usb_bus_suspend(void) {dtr=0;tx_clear();++epoch;++suspends;}
static void reset(struct usb_device_t *d,u32 itf) {
    (void)d;(void)itf;
    ld2450_usb_bus_suspend();
    ++resets;--suspends;
    usb_g_set_intr_hander(0,0x84,tx_complete);
    usb_g_ep_config(0,0x84,USB_ENDPOINT_XFER_BULK,1,bulk_in,64);
    usb_g_ep_config(0,0x04,USB_ENDPOINT_XFER_BULK,0,bulk_out,64);
    usb_g_ep_config(0,0x82,USB_ENDPOINT_XFER_INT,0,notification,8);
    usb_enable_ep(0,4);usb_enable_ep(0,2);
}
static u32 coding_rx(struct usb_device_t *d,struct usb_ctrlrequest *r) {
    if(r->wLength!=7) return USB_EP0_SET_STALL;
    usb_read_ep0(0,line_coding,7);
    (void)d;return USB_EP0_STAGE_SETUP;
}
static u32 setup(struct usb_device_t *d,struct usb_ctrlrequest *r) {
    if(r->wIndex!=0) goto stall;
    if(r->bRequestType==0x21 && r->bRequest==0x20 && r->wLength==7 && !r->wValue) {
        usb_set_setup_recv(d,coding_rx);return 0;
    }
    if(r->bRequestType==0xa1 && r->bRequest==0x21 && !r->wValue) {
        usb_set_data_payload(d,r,line_coding,r->wLength<7?r->wLength:7);return 0;
    }
    if(r->bRequestType==0x21 && r->bRequest==0x22 && !r->wLength) {
        u8 opened=(u8)(r->wValue&1);
        ++control_requests;control_value=r->wValue;
        if(opened!=dtr) {++epoch;tx_clear();}
        dtr=opened;
        usb_set_setup_phase(d,USB_EP0_STAGE_SETUP);return 0;
    }
stall: usb_set_setup_phase(d,USB_EP0_SET_STALL);return 0;
}
u32 cdc_desc_config(const usb_dev id,u8 *p,u32 *itf) {
    static const u8 desc[]={
        8,11,0,2,2,2,1,0,
        9,4,0,0,1,2,2,1,0,
        5,0x24,0,0x10,1, 5,0x24,1,0,1, 4,0x24,2,2, 5,0x24,6,0,1,
        7,5,0x82,3,8,0,16,
        9,4,1,0,2,10,0,0,0,
        7,5,4,2,64,0,0, 7,5,0x84,2,64,0,0};
    ASSERT(*itf==0,"CDC-only application");
    memcpy(p,desc,sizeof(desc));
    usb_set_interface_hander(id,0,setup);usb_set_reset_hander(id,0,reset);
    *itf+=2;return sizeof(desc);
}
void cdc_register(const usb_dev id) {(void)id;dtr=0;}
void cdc_release(const usb_dev id) {(void)id;ld2450_usb_bus_suspend();}
int ld2450_usb_init(void) {
    int result=usb_device_mode(0,CDC_CLASS);
    initialized=(result==0);last_sof=0;sof_time=timer_get_ms();return result;
}
void ld2450_usb_stop(void) {
    if(initialized) {
        local_irq_disable();initialized=0;ld2450_usb_bus_suspend();local_irq_enable();
        usb_device_mode(0,0);
    }
}
void ld2450_usb_discard(void) {local_irq_disable();tx_clear();local_irq_enable();}
uint32_t ld2450_usb_epoch(void) {return epoch;}
int ld2450_usb_ready(void) {
    u16 frame_number;
    if(!initialized) return 0;
    frame_number=usb_read_sofframe(0);
    if(frame_number!=last_sof) {last_sof=frame_number;sof_time=timer_get_ms();}
    if(dtr && usb_id2device(0)->bDeviceStates==USB_CONFIGURED &&
           (u32)(timer_get_ms()-sof_time)<100) {++ready_polls;return 1;}
    return 0;
}
void ld2450_usb_snapshot(struct ld2450_usb_diagnostics *s) {
    local_irq_disable();
    s->initialized=initialized;s->dtr=dtr;
    s->device_state=usb_id2device(0)->bDeviceStates;s->epoch=epoch;
    s->sof=last_sof;s->sof_age_ms=timer_get_ms()-sof_time;
    s->txcsr=initialized?usb_read_txcsr(0,4):0;
    s->resets=resets;s->suspends=suspends;
    s->control_requests=control_requests;s->control_value=control_value;
    s->ready_polls=ready_polls;s->writes=writes;s->busy=busy;s->bytes=bytes;
    s->tx_queued=tx_used;s->tx_peak=tx_peak;s->tx_interrupts=tx_interrupts;
    s->irq_us=irq_us;s->irq_max_us=irq_max_us;s->irq_calls=irq_calls;
    local_irq_enable();
}
static void submit(size_t n) {
#ifndef LD2450_USB_HOST_TEST
    __asm__ volatile("csync" ::: "memory");
#endif
    usb_write_ep_cnt(0,4,(u32)n);
    usb_write_txcsr(0,4,TXCSRP_TxPktRdy);
    ++writes;bytes+=(u32)n;
}
/* Called with IRQs masked, or from the USB ISR. DMA always reads bulk_in,
 * never the staging ring; consuming the ring therefore cannot free DMA data. */
static void tx_kick(void) {
    u32 n,first;
    if(!initialized || !dtr || usb_id2device(0)->bDeviceStates!=USB_CONFIGURED ||
       (usb_read_txcsr(0,4)&(TXCSRP_TxPktRdy|TXCSRP_FIFONotEmpty|TXCSRP_SendStall))) return;
    n=tx_used;
    if(n>=64 || (n && flush_requested)) {
        if(n>64)n=64;
        first=TX_CAPACITY-tx_head;if(first>n)first=n;
        memcpy(bulk_in,tx_queue+tx_head,first);memcpy(bulk_in+first,tx_queue,n-first);
        tx_head=(tx_head+n)%TX_CAPACITY;tx_used-=n;
        need_zlp=(n==64);submit(n);
    } else if(!n && flush_requested && need_zlp) {
        need_zlp=flush_requested=0;submit(0);
    }
}
int ld2450_usb_write(void *ctx,const uint8_t *p,size_t n) {
    int accepted=0;(void)ctx;
    if(!n) return 0;
    /* Main-task producer, serialized with reset and the completion consumer.
     * Bounded copy; return zero only when the owned staging ring is full. */
    local_irq_disable();
    if(initialized && dtr && usb_id2device(0)->bDeviceStates==USB_CONFIGURED) {
        u32 tail=(tx_head+tx_used)%TX_CAPACITY,first=TX_CAPACITY-tail;
        if(n>2048)n=2048;
        if(n>TX_CAPACITY-tx_used)n=TX_CAPACITY-tx_used;
        if(first>n)first=(u32)n;
        memcpy(tx_queue+tail,p,first);memcpy(tx_queue,p+first,n-first);
        tx_used+=(u32)n;if(tx_used>tx_peak)tx_peak=tx_used;
        if(n)flush_requested=0;
        accepted=(int)n;tx_kick();
    }
    if(!accepted)++busy;
    local_irq_enable();return accepted;
}
/* Host commands on bulk OUT, polled from task context (no RX IRQ).
 * The SDK's usb_g_bulk_read (linked from cpu.a, inlined into app_main) must
 * only be entered with a packet already waiting, asking for exactly its length:
 * - with no packet ready it re-reads RXCSR and writes it back with
 *   RXCSRP_FlushFIFO, so a packet arriving in that window is discarded (this
 *   lost about a third of commands while the main loop polled);
 * - it keeps reading while packets are ready and copies whole packets without
 *   bounding them by the remaining length, and after a short packet it falls
 *   into the same flushing path.
 * With RxPktRdy set and len == RXCOUNT it copies that one packet and returns.
 * A zero-length packet still goes through the SDK flush, which then discards it. */
#define RX_PACKET 64u
static u8 rx_packet[4*RX_PACKET] __attribute__((aligned(4)));
int ld2450_usb_read(uint8_t *data,size_t capacity) {
    u32 n,count;
    if(!data || capacity<sizeof(rx_packet)) return 0; /* Never truncate a packet. */
    if(!initialized || !dtr || usb_id2device(0)->bDeviceStates!=USB_CONFIGURED) return 0;
    if(!(usb_read_rxcsr(0,4)&RXCSRP_RxPktRdy)) return 0;
    count=usb_read_rxcount(0,4);
    if(count>RX_PACKET) count=RX_PACKET;
    n=usb_g_bulk_read(0,4,rx_packet,count?count:RX_PACKET,0);
    if(n>sizeof(rx_packet)) n=sizeof(rx_packet);
    memcpy(data,rx_packet,n);
    return (int)n;
}
void ld2450_usb_flush(void) {
    local_irq_disable();
    flush_requested=1;tx_kick();
    local_irq_enable();
}
