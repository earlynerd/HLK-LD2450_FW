#include <stdio.h>
#include "../target/br23/image/usb_stream.c"
static u8 received[10000];
static unsigned received_size;
static void complete(void) {
    assert(txcsr&TXCSRP_TxPktRdy);assert(tx_handler && tx_irq_enabled);
    assert(received_size+txcount<=sizeof(received));
    memcpy(received+received_size,dma_in,txcount);received_size+=txcount;
    txcsr=0;local_irq_disable();tx_handler(&device,4);local_irq_enable();
}
static void drain(void) {
    unsigned guard=1000;
    while(txcsr&TXCSRP_TxPktRdy) {assert(guard--);complete();}
    assert(tx_used==0);
}
int main(void) {
    u8 descriptor[128],data[4160];u32 itf=0,n,pos,before;
    struct usb_ctrlrequest r={0x21,0x22,1,0,0};
    struct ld2450_usb_diagnostics diag;
    assert(ld2450_usb_init()==0);reset(&device,0);device.bDeviceStates=USB_CONFIGURED;
    n=cdc_desc_config(0,descriptor,&itf);assert(itf==2);
    for(pos=0;pos<n;pos+=descriptor[pos]) {
        assert(descriptor[pos]>=4 && pos+descriptor[pos]<=n);
        if(descriptor[pos+1]==5)assert((descriptor[pos+2]&15)<5);
    }
    assert(!ld2450_usb_ready());setup(&device,&r);assert(ld2450_usb_ready());
    memset(data,0xa5,100);
    assert(ld2450_usb_write(NULL,data,100)==100 && txcount==64 && submits==1);
    memset(data,0x5a,100);assert(dma_in[0]==0xa5 && tx_used==36);
    ld2450_usb_flush();drain();assert(received_size==100);
    for(pos=0;pos<100;++pos)assert(received[pos]==0xa5);
    assert(submits==2);
    received_size=0;
    for(pos=0;pos<sizeof(data);++pos)data[pos]=(u8)(pos*17);
    assert(ld2450_usb_write(NULL,data,2048)==2048);
    assert(ld2450_usb_write(NULL,data+2048,2048)==2048);
    assert(ld2450_usb_write(NULL,data+4096,64)==64);
    assert(tx_used==4096 && ld2450_usb_write(NULL,data,1)==0);
    before=submits;ld2450_usb_flush();drain();
    assert(received_size==sizeof(data) && !memcmp(received,data,sizeof(data)));
    assert(submits-before==65); /* 64 more data packets plus final ZLP. */
    assert(tx_head!=0);
    received_size=0;
    assert(ld2450_usb_write(NULL,data,sizeof(data))==2048);
    assert(ld2450_usb_write(NULL,data+2048,2048)==2048);
    ld2450_usb_flush();drain();assert(received_size==4096 && !memcmp(received,data,4096));
    before=submits;assert(ld2450_usb_write(NULL,data,7)==7 && submits==before);
    ld2450_usb_flush();assert(txcount==7);drain();assert(submits==before+1);
    /* Bulk OUT: nonblocking packet reads only while open; never truncated. */
    {
        u8 in[LD2450_USB_READ_BYTES];
        /* No packet: the SDK read (which would flush the FIFO) is never entered. */
        assert(ld2450_usb_read(in,sizeof(in))==0 && bulk_reads==0 && rx_polls==1);
        memcpy(out_packet,"LDC1-command-bytes",18);out_size=18;
        assert(ld2450_usb_read(in,64)==0 && out_size==18);
        assert(ld2450_usb_read(in,sizeof(in))==18 && !memcmp(in,"LDC1-command-bytes",18) && out_size==0);
        assert(bulk_reads==1 && ld2450_usb_read(in,sizeof(in))==0 && bulk_reads==1);
        memset(out_packet,0x4c,64);out_size=64;
        assert(ld2450_usb_read(in,sizeof(in))==64 && bulk_reads==2);
    }
    ld2450_usb_snapshot(&diag);
    assert(diag.dtr==1 && diag.resets==1 && diag.suspends==0 && diag.control_requests==1);
    assert(diag.busy==1 && diag.tx_peak==4096 && diag.tx_queued==0 && diag.tx_interrupts>100);
    /* DTR drop discards queued data without reusing in-flight DMA. */
    assert(ld2450_usb_write(NULL,data,100)==100);
    r.wValue=0;setup(&device,&r);assert(!ld2450_usb_ready() && tx_used==0);
    assert(ld2450_usb_write(NULL,data,1)==0);complete();assert(!(txcsr&1));
    {u8 in[LD2450_USB_READ_BYTES];u32 reads=bulk_reads,polls=rx_polls;out_size=5;
     assert(ld2450_usb_read(in,sizeof(in))==0 && bulk_reads==reads && rx_polls==polls);out_size=0;}
    r.wValue=1;setup(&device,&r);now=101;assert(!ld2450_usb_ready());
    ++sof;assert(ld2450_usb_ready());
    assert(ld2450_usb_write(NULL,data,7)==7);ld2450_usb_discard();assert(tx_used==0);
    ld2450_usb_bus_suspend();assert(!ld2450_usb_ready());
    r.bRequest=0x20;r.wLength=65;r.wValue=0;setup(&device,&r);assert(setup_phase==USB_EP0_SET_STALL);
    assert(coding_rx(&device,&r)==USB_EP0_SET_STALL && ep_reads==0);
    r.wLength=7;assert(coding_rx(&device,&r)==0 && ep_reads==1);
    assert(!locked);ld2450_usb_stop();assert(!ld2450_usb_ready());
    puts("CDC owned ring, interrupt drain, wrapping, backpressure, tails, reset and setup bounds passed");return 0;
}
