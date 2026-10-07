#include "ld2450_acquisition.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static struct ld_stream stream;
static struct ld_acquisition acq;
static uint8_t queue[8192],raw[2056],identity[32];
static int discard(void *c,const uint8_t *p,size_t n) {(void)c;(void)p;return (int)n;}
static void feed(unsigned lane,unsigned chirp,uint32_t time,int enabled) {
    uint32_t h=0xaa200201u|(lane<<22)|(chirp<<11);
    memset(raw,0,sizeof(raw));
    raw[0]=(uint8_t)(h>>24);raw[1]=(uint8_t)(h>>16);raw[2]=(uint8_t)(h>>8);raw[3]=(uint8_t)h;
    raw[2054]=(uint8_t)((lane<<6)|0x20|(chirp&15));raw[2055]=0x55;
    ld_acquisition_feed(&acq,lane,raw,19,time,enabled);
    ld_acquisition_feed(&acq,lane,raw+19,sizeof(raw)-19,time,enabled);
    while(stream.used) assert(ld_stream_pump(&stream,discard,NULL,64)>0);
}
int main(void) {
    unsigned c,lane;
    assert(ld_stream_init(&stream,queue,sizeof(queue),identity)==0);
    ld_acquisition_init(&acq,&stream);
    /* Split records, prefix noise, alternating lanes, timestamps wrapping. */
    ld_acquisition_feed(&acq,0,(const uint8_t *)"noise",5,0,1);
    for(c=0;c<64;++c) for(lane=0;lane<2;++lane) feed(lane,c,0xffffff00u+c*1200u+lane*10,1);
    assert(stream.stats.frames_completed==1 && acq.valid[0]==64 && acq.valid[1]==64);
    assert(acq.sync_bytes==5);
    assert(acq.complete_pairs==1 && acq.sequence_errors==0);
    feed(0,0,90000,1);feed(1,0,89990,1);
    assert(stream.active); /* DMA lane service order need not match timestamp order. */
    ld_acquisition_gap(&acq,90001);
    stream.stats.frames_rejected=0;
    for(c=0;c<64;++c) for(lane=0;lane<2;++lane) feed(lane,c,100000+c*1200,0);
    assert(stream.stats.frames_skipped==1 && stream.stats.frames_completed==1);
    assert(acq.complete_pairs==2 && acq.sequence_errors==0);
    feed(0,0,200000,1);feed(1,0,289000,1);
    assert(acq.unpaired==1 && !stream.active); /* Never pair adjacent frames. */
    ld_acquisition_gap(&acq,300000);
    feed(0,0,400000,1);feed(1,0,400010,1);feed(0,2,402400,1);
    assert(!stream.active && stream.stats.frames_rejected==1);
    assert(acq.complete_pairs==2 && acq.sequence_errors==1);
    feed(0,0,500000,1);feed(1,0,500010,1);
    ld_acquisition_tick(&acq,700011);assert(!stream.active && acq.timeouts==1);
    feed(0,0,800000,1);feed(1,0,800010,1);
    raw[10]^=1;ld_acquisition_feed(&acq,1,raw,sizeof(raw),801200,1);
    assert(acq.corrupt==1 && !stream.active);
    puts("Acquisition synchronization, complete frames, skips, gaps, corruption and timeouts passed");return 0;
}
