#include "ld2450_acquisition.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static struct ld_stream stream;
static struct ld_acquisition acq;
static uint8_t queue[90112],raw[2056],identity[32];
static int output(void *ctx,const uint8_t *p,size_t n) {
    if(n>63)n=63;
    return ctx?(int)fwrite(p,1,n,(FILE *)ctx):(int)n;
}
static void feed(unsigned lane,unsigned chirp,uint32_t time) {
    unsigned j;uint32_t h=0xaa200201u|(lane<<22)|(chirp<<11);uint16_t sum=0;
    raw[0]=(uint8_t)(h>>24);raw[1]=(uint8_t)(h>>16);raw[2]=(uint8_t)(h>>8);raw[3]=(uint8_t)h;
    for(j=0;j<1024;++j) {
        uint16_t v=(uint16_t)(chirp*7919u+j*71u+lane*12345u);
        raw[4+2*j]=(uint8_t)(v>>8);raw[5+2*j]=(uint8_t)v;sum=(uint16_t)(sum+v);
    }
    raw[2052]=(uint8_t)(sum>>8);raw[2053]=(uint8_t)sum;
    raw[2054]=(uint8_t)((lane<<6)|0x20|(chirp&15));raw[2055]=0x55;
    ld_acquisition_feed(&acq,lane,raw,2056,time,1);
}
int main(int argc,char **argv) {
    unsigned chirp,lane;FILE *file=NULL;
    if(argc==2) {file=fopen(argv[1],"wb");assert(file);}
    assert(LD_STREAM_CHIRPS==16);
    assert(ld_stream_init(&stream,queue,sizeof(queue),identity)==0);
    ld_acquisition_init(&acq,&stream);
    /* A whole raw window fits with NO transport service. Later physical
     * chirps are validated but never appended to the completed export. */
    for(chirp=0;chirp<64;++chirp)for(lane=0;lane<2;++lane)feed(lane,chirp,1000+chirp*1200);
    assert(stream.stats.frames_completed==1 && stream.used==67100);
    assert(stream.stats.raw_records==32 && stream.stats.compressed_records==0);
    assert(acq.complete_pairs==1 && acq.valid[0]==64 && acq.valid[1]==64);
    for(chirp=0;chirp<64;++chirp)for(lane=0;lane<2;++lane)feed(lane,chirp,91000+chirp*1200);
    assert(stream.stats.frames_skipped==1 && stream.stats.frames_completed==1);
    assert(stream.used==67100 && acq.complete_pairs==2);
    while(stream.used)assert(ld_stream_pump(&stream,output,file,511)>0);
    for(chirp=0;chirp<64;++chirp)for(lane=0;lane<2;++lane)feed(lane,chirp,181000+chirp*1200);
    assert(stream.stats.frames_completed==2 && acq.complete_pairs==3);
    assert(stream.stats.frames_rejected==0 && stream.stats.queue_overflows==0);
    while(stream.used)assert(ld_stream_pump(&stream,output,file,511)>0);
    if(file)assert(fclose(file)==0);
    /* Missing retained chirps still cannot become a completed window. */
    for(chirp=0;chirp<15;++chirp)for(lane=0;lane<2;++lane)feed(lane,chirp,271000+chirp*1200);
    assert(stream.active && stream.stats.frames_completed==2);
    ld_acquisition_tick(&acq,600000);
    assert(!stream.active && stream.stats.frames_rejected==1);
    return 0;
}
