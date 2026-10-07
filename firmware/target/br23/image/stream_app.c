#include "system/includes.h"
#include "asm/timer.h"
#include "asm/hwi.h"
#include "malloc.h"
#include "sdk_bridge.h"
#include "ld2450_peripherals.h"
#include "ld2450_stream_app.h"
#include "ld2450_acquisition.h"
#include "radar_wire.h"
#include "ld2450_radar_control.h"
#include "ld2450_radar_init.h"
#include "stream_config_generated.h"

#define SLOTS 4u
#define DMA_BYTES 2056u
static uint8_t dma[2][SLOTS][DMA_BYTES] __attribute__((aligned(4)));
static volatile uint32_t produced[2],consumed[2],overruns,stopped;
static volatile uint32_t stamp[2][SLOTS],clock_base,last_dma_us;
static uint32_t ticks_us,seen_overruns,seen_epoch,was_ready,max_process_us;
static struct ld_stream stream;
static struct ld_acquisition acquisition;
static uint8_t output_queue[LD_STREAM_QUEUE_BYTES];
static uint8_t enabled;
static uint32_t max_backlog,cpu_rejections;
/* Live register control. Commands run between physical frames: once no SPI
 * record has completed for CONTROL_GAP_US (chirps arrive every ~1.2 ms), new
 * commands may start for CONTROL_START_US. Baseline frames leave ~11 ms of
 * NOP. Each register is a separate step and every step re-checks the window,
 * because some registers (the 0x20-0x2F table) read far slower than others:
 * four in one gap overran DMA on the bench. A command therefore spans as many
 * gaps as it needs. A stuck bus takes up to 20 ms per transaction and can
 * still overrun DMA; REINIT recovers. With
 * no records for CONTROL_IDLE_US the radar is idle and commands run freely.
 * After CONTROL_STARVE_MS without a usable gap, a command runs anyway; that
 * can overrun DMA if chirps continue, which stops acquisition until REINIT. */
#define CONTROL_GAP_US 2000u
#define CONTROL_START_US 3000u
#define CONTROL_IDLE_US 250000u
#define CONTROL_STARVE_MS 2000u
/* timer_get_ms() advances in 10 ms steps (IMAGE_BUILD.md): a shorter timeout
 * can expire mid-transaction and reset the bus mid-byte. A register takes
 * ~0.5 ms at 100 kHz, so 20 ms (as for startup writes) only ends a stuck bus. */
#define CONTROL_I2C_TIMEOUT_MS 20u
static struct ld_radar_control control;
static uint8_t control_reply[LD_CONTROL_REPLY_MAX];
static uint32_t gap_seen_dma,gap_start_us;
static uint8_t gap_open;

___interrupt static void clock_irq(void) {JL_TIMER3->CON|=BIT(14);clock_base+=1000;}
uint32_t ld2450_stream_clock_us(void) {
    uint32_t base,count;
    local_irq_disable();base=clock_base;count=JL_TIMER3->CNT;
    if(JL_TIMER3->CON&BIT(15)) {base+=1000;count=JL_TIMER3->CNT;}
    local_irq_enable();return base+count/ticks_us;
}
static void dma_irq(unsigned lane) {
    JL_SPI_TypeDef *spi=lane?JL_SPI2:JL_SPI1;
    uint32_t next;
    if(!(spi->CON&LD_SPI_PENDING)) return;
    ld_spi_clear(spi);
    if(stopped) return;
    stamp[lane][produced[lane]%SLOTS]=last_dma_us=clock_base+
        ((JL_TIMER3->CON&BIT(15))?1000u:0u)+JL_TIMER3->CNT/ticks_us;
    __asm__ volatile("csync" ::: "memory");
    next=++produced[lane];
    if(next-consumed[lane]>=SLOTS) {
        ++overruns;stopped=1;
        JL_SPI1->CON&=~BIT(13);JL_SPI2->CON&=~BIT(13);
        JL_SPI1->CNT=0;JL_SPI2->CNT=0;return;
    }
    spi->ADR=(uint32_t)dma[lane][next%SLOTS];spi->CNT=DMA_BYTES;
    __asm__ volatile("csync" ::: "memory");
}
___interrupt static void spi1_irq(void) {dma_irq(0);}
___interrupt static void spi2_irq(void) {dma_irq(1);}
int ld2450_stream_app_init(void) {
    uint32_t hz=clk_get("timer");
    /* Timer3 has no owner in the minimal application. Refuse an unexpected
     * enabled timer or unsupported clock rather than borrowing its state. */
    if((JL_TIMER3->CON&3) || !hz || hz%4000000u || hz/4000u>65535u) return -1;
    ticks_us=hz/4000000u;clock_base=0;
    JL_TIMER3->CON=0;JL_TIMER3->CNT=0;JL_TIMER3->PRD=ticks_us*1000u-1;
    request_irq(IRQ_TIME3_IDX,4,clock_irq,0);
    JL_TIMER3->CON=(1u<<4)|BIT(3)|BIT(0); /* timer clock /4, counting */
    if(ld_stream_init(&stream,output_queue,sizeof(output_queue),ld_stream_config_hash)) return -2;
    ld_acquisition_init(&acquisition,&stream);
    ld_radar_control_init(&control);
    return ld2450_usb_init();
}
int ld2450_stream_app_arm(void) {
    produced[0]=produced[1]=consumed[0]=consumed[1]=0;stopped=0;enabled=1;
    request_irq(IRQ_SPI1_IDX,5,spi1_irq,0);request_irq(IRQ_SPI2_IDX,5,spi2_irq,0);
    JL_SPI1->ADR=(uint32_t)dma[0][0];JL_SPI2->ADR=(uint32_t)dma[1][0];
    ld_spi_clear(JL_SPI1);ld_spi_clear(JL_SPI2);
    JL_SPI1->CON|=BIT(13);JL_SPI2->CON|=BIT(13);
    JL_SPI1->CNT=DMA_BYTES;JL_SPI2->CNT=DMA_BYTES;return 0;
}
static int disconnected(void *ctx,const uint8_t *p,size_t n) {(void)ctx;(void)p;(void)n;return -1;}
static int control_i2c(void *ctx,const uint8_t *tx,size_t tx_size,uint8_t *rx,size_t rx_size) {
    (void)ctx;
    return ld2450_i2c_transfer(LD2450_RADAR_I2C_ADDRESS,tx,tx_size,rx,rx_size,CONTROL_I2C_TIMEOUT_MS);
}
/* Stop acquisition cleanly, power-cycle the radar and re-run the full build
 * profile. DMA is disarmed first, so the restart never begins mid-record. */
static int control_reinit(void *ctx) {
    int err;
    (void)ctx;
    enabled=0;stopped=1;
    JL_SPI1->CON&=~BIT(13);JL_SPI2->CON&=~BIT(13);JL_SPI1->CNT=JL_SPI2->CNT=0;
    ld_acquisition_gap(&acquisition,ld2450_stream_clock_us());
    ld2450_radar_power(0);
    ld2450_delay_ms(50);
    err=ld2450_app_start();
    /* Chirps restart now: treat the radar as active so later commands wait for a real gap. */
    last_dma_us=ld2450_stream_clock_us();gap_open=0;
    return err;
}
static void control_service(void) {
    uint8_t input[LD2450_USB_READ_BYTES];
    int n;
    uint32_t now,since_dma;
    while((n=ld2450_usb_read(input,sizeof(input)))>0)
        ld_radar_control_feed(&control,input,(size_t)n,timer_get_ms());
    while(ld_radar_control_pending(&control) && !stream.active &&
          stream.capacity-stream.used>=36u+LD_CONTROL_REPLY_MAX) {
        size_t size;
        int idle,starving,in_gap;
        now=ld2450_stream_clock_us();since_dma=now-last_dma_us;
        idle=!enabled || since_dma>=CONTROL_IDLE_US;
        if(since_dma<CONTROL_GAP_US) gap_open=0;
        else if(!gap_open || gap_seen_dma!=last_dma_us) {gap_open=1;gap_seen_dma=last_dma_us;gap_start_us=now;}
        in_gap=gap_open && produced[0]==consumed[0] && produced[1]==consumed[1] &&
               now-gap_start_us<CONTROL_START_US;
        starving=ld_radar_control_waiting_ms(&control,timer_get_ms())>=CONTROL_STARVE_MS;
        if(!idle && !in_gap && !starving) break;
        size=ld_radar_control_execute(&control,control_i2c,NULL,control_reinit,NULL,
                                      control_reply,sizeof(control_reply));
        stream.register_generation=control.generation;
        if(size) ld_stream_control_reply(&stream,control_reply,size,ld2450_stream_clock_us());
        if(!idle && !in_gap) break; /* Starving: one command per poll. */
    }
}
static void usb_pump(void) {
    ld_stream_pump(&stream,ld2450_usb_write,NULL,2048);
    if(!stream.used && !stream.active)ld2450_usb_flush();
}
void ld2450_stream_app_poll(void) {
    unsigned lane;
    uint32_t time=ld2450_stream_clock_us(),epoch=ld2450_usb_epoch();
    int ready=ld2450_usb_ready();
    if((was_ready && !ready) || epoch!=seen_epoch) {
        ld2450_usb_discard();
        ld_acquisition_gap(&acquisition,time);
        if(stream.used) ld_stream_pump(&stream,disconnected,NULL,1);
    }
    seen_epoch=epoch;was_ready=(uint32_t)ready;
#ifndef LD2450_USB_BENCH
    /* Preserve acquisition when an expensive frame consumes the CPU budget.
     * Two pending slots leave two slots of DMA headroom. Abort export only;
     * the validated input sequence continues until the next paired boundary. */
    if(enabled && stream.active &&
       (produced[0]-consumed[0]>=2 || produced[1]-consumed[1]>=2)) {
        ld_stream_abort(&stream,6,time);++cpu_rejections;
    }
#endif
    if(ready) {control_service();usb_pump();}
#ifdef LD2450_USB_BENCH
    /* Deterministic LDF1 frames: benchmark codec + USB without powering radar. */
    {
        static uint8_t raw[2056];static unsigned chirp,lane_id;static uint32_t frame;
        uint32_t h,sum=0;unsigned j;
        if(ready && !stream.active && !stream.used) {ld_stream_begin(&stream,++frame,time);chirp=lane_id=0;}
        if(stream.active && stream.capacity-stream.used>4200) {
            h=0xaa200201u|(lane_id<<22)|(chirp<<11);
            raw[0]=(uint8_t)(h>>24);raw[1]=(uint8_t)(h>>16);raw[2]=(uint8_t)(h>>8);raw[3]=(uint8_t)h;
            for(j=0;j<1024;++j) {uint16_t v=(uint16_t)(j*17+chirp+lane_id);raw[4+2*j]=(uint8_t)(v>>8);raw[5+2*j]=(uint8_t)v;sum+=v;}
            raw[2052]=(uint8_t)(sum>>8);raw[2053]=(uint8_t)sum;
            raw[2054]=(uint8_t)((lane_id<<6)|0x20|(chirp&15));raw[2055]=0x55;
            ld_stream_record(&stream,raw,sizeof(raw),time);
            if(++lane_id==2) {lane_id=0;++chirp;}
        }
    }
#else
    if(enabled && !ld2450_get_status().radar_powered) {enabled=0;stopped=1;ld_acquisition_gap(&acquisition,time);}
    if(enabled && stopped) {
        seen_overruns=overruns;ld_acquisition_gap(&acquisition,time);
        /* Never rearm mid-record. A DMA ownership overrun requires restart;
         * output backpressure alone still skips whole frames while running. */
        enabled=0;ld2450_radar_power(0);
    }
    if(enabled) for(lane=0;lane<2;++lane) {
        uint32_t count=consumed[lane],pending=produced[lane]-count;
        if(pending) {
            uint32_t before=ld2450_stream_clock_us(),elapsed;
            if(pending>max_backlog) max_backlog=pending;
            ld_acquisition_feed(&acquisition,lane,dma[lane][count%SLOTS],DMA_BYTES,
                                stamp[lane][count%SLOTS],ready);
            __asm__ volatile("csync" ::: "memory");consumed[lane]=count+1;
            elapsed=ld2450_stream_clock_us()-before;if(elapsed>max_process_us) max_process_us=elapsed;
            if(ready)usb_pump();
        }
    }
    ld_acquisition_tick(&acquisition,ld2450_stream_clock_us());
#endif
    if(ready)usb_pump();
}
void ld2450_stream_app_stop(void) {
    enabled=0;stopped=1;
    JL_SPI1->CON&=~BIT(13);JL_SPI2->CON&=~BIT(13);
    JL_SPI1->CNT=JL_SPI2->CNT=0;
    if(ticks_us) ld_acquisition_gap(&acquisition,ld2450_stream_clock_us());
    ld2450_radar_power(0);ld2450_usb_stop();
}
void ld2450_stream_app_report(void) {
    char text[256];
    struct ld2450_usb_diagnostics usb;
    unsigned running=enabled, halted=stopped;
    if(!ticks_us) return; /* Recovery window precedes timer/USB setup. */
    uint32_t runtime=ld2450_stream_clock_us();
    ld2450_usb_snapshot(&usb);
    ld2450_stream_app_stop();
    snprintf(text,sizeof(text),"CLOCK sys=%u lsb=%u timer=%u timer_ticks_us=%u timer_prd=%u sdk_ms=%u local_us=%u\r\n",
        clk_get("sys"),clk_get("lsb"),clk_get("timer"),ticks_us,(unsigned)JL_TIMER3->PRD,timer_get_ms(),runtime);
    ld2450_debug_write(text);
    snprintf(text,sizeof(text),"USB stage_queued=%u stage_peak=%u tx_interrupts=%u\r\n",
        usb.tx_queued,usb.tx_peak,usb.tx_interrupts);
    ld2450_debug_write(text);
    snprintf(text,sizeof(text),"CLOCK registers con0=%x con1=%x con2=%x sys_div=%x\r\n",
        (unsigned)JL_CLOCK->CLK_CON0,(unsigned)JL_CLOCK->CLK_CON1,(unsigned)JL_CLOCK->CLK_CON2,(unsigned)JL_CLOCK->SYS_DIV);
    ld2450_debug_write(text);
    snprintf(text,sizeof(text),"USB before_stop init=%u dtr=%u state=%u epoch=%u sof=%u age_ms=%u txcsr=%x running=%u halted=%u\r\n",
        usb.initialized,usb.dtr,usb.device_state,usb.epoch,usb.sof,usb.sof_age_ms,usb.txcsr,running,halted);
    ld2450_debug_write(text);
    snprintf(text,sizeof(text),"USB resets=%u suspends=%u controls=%u control_value=%u ready_polls=%u writes=%u busy=%u bytes=%u\r\n",
        usb.resets,usb.suspends,usb.control_requests,usb.control_value,usb.ready_polls,usb.writes,usb.busy,usb.bytes);
    ld2450_debug_write(text);
    snprintf(text,sizeof(text),"STREAM stopped us=%u valid=%u/%u frames=%u skip=%u bad=%u sync=%u unpaired=%u timeout=%u\r\n",
        runtime,acquisition.valid[0],acquisition.valid[1],acquisition.frame_id,stream.stats.frames_skipped,
        acquisition.corrupt,acquisition.sync_bytes,acquisition.unpaired,acquisition.timeouts);
    ld2450_debug_write(text);
    snprintf(text,sizeof(text),"STREAM dma_overrun=%u backlog=%u process_max_us=%u queue_peak=%u encoded=%u rejected=%u raw=%u compressed=%u usb_epoch=%u\r\n",
        seen_overruns,max_backlog,max_process_us,stream.stats.queue_peak,stream.stats.frames_completed,
        stream.stats.frames_rejected,stream.stats.raw_records,stream.stats.compressed_records,seen_epoch);
    ld2450_debug_write(text);
    snprintf(text,sizeof(text),"STREAM heap_free=%u heap_min=%u state_bytes=%u dma_bytes=%u queue_bytes=%u\r\n",
        (unsigned)xPortGetFreeHeapSize(),(unsigned)xPortGetMinimumEverFreeHeapSize(),
        (unsigned)(sizeof(stream)+sizeof(acquisition)),(unsigned)sizeof(dma),(unsigned)sizeof(output_queue));
    ld2450_debug_write(text);
    snprintf(text,sizeof(text),"STREAM complete_pairs=%u sequence_errors=%u bad_status=%u\r\n",
        acquisition.complete_pairs,acquisition.sequence_errors,acquisition.bad_status);
    ld2450_debug_write(text);
    snprintf(text,sizeof(text),"STREAM cpu_rejections=%u queue_overflows=%u\r\n",cpu_rejections,stream.stats.queue_overflows);
    ld2450_debug_write(text);
    snprintf(text,sizeof(text),"USB irq_calls=%u irq_us=%u irq_max_us=%u\r\n",usb.irq_calls,usb.irq_us,usb.irq_max_us);
    ld2450_debug_write(text);
    if(acquisition.corrupt) {
        unsigned offset,j;
        static const char hex[]="0123456789abcdef";
        for(offset=0;offset<2056;offset+=32) {
            int at=snprintf(text,sizeof(text),"BAD %04x ",offset);
            for(j=offset;j<offset+32 && j<2056;++j) {uint8_t b=acquisition.bad_snapshot[j];text[at++]=hex[b>>4];text[at++]=hex[b&15];}
            text[at++]='\r';text[at++]='\n';text[at]=0;ld2450_debug_write(text);
        }
    }
    /* Bounded kernel measurements after stopping acquisition; no UART output
     * inside timed work. Retain the captured input and exercise real samples. */
    if(acquisition.valid[0] && stream.stats.raw_records) {
        uint32_t before,crc_us,encode_us,validate_us,value=0;unsigned n;size_t size=0;
        struct radar_record decoded;
        before=ld2450_stream_clock_us();
        for(n=0;n<16;++n)value+=(uint32_t)radar_record_decode(acquisition.first[0],2056,&decoded);
        validate_us=ld2450_stream_clock_us()-before;
        before=ld2450_stream_clock_us();
        for(n=0;n<16;++n) value^=ld_stream_crc32(acquisition.first[0],2056);
        crc_us=ld2450_stream_clock_us()-before;
        before=ld2450_stream_clock_us();
        for(n=0;n<16;++n) size+=ld_stream_encode(acquisition.first[0],stream.previous[0],stream.scratch,LD_STREAM_PAYLOAD_MAX);
        encode_us=ld2450_stream_clock_us()-before;
        snprintf(text,sizeof(text),"KERNEL runs=16 crc_us=%u encode_us=%u validate_us=%u encoded_bytes=%u check=%u\r\n",crc_us,encode_us,validate_us,(unsigned)size,value);
        ld2450_debug_write(text);
    }
}
