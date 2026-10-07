#define _CRT_SECURE_NO_WARNINGS
#include "ld2450_acquisition.h"
#include "ld2450_radar_control.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static struct ld_stream stream;
static struct ld_acquisition acq;
static struct ld_radar_control control;
static uint8_t queue[90112],raw[2056],identity[32],reply[LD_CONTROL_REPLY_MAX];
static uint16_t registers[256];
static unsigned transactions,reinits,fail_at;
static int output(void *ctx,const uint8_t *p,size_t n) {
    if(n>63)n=63;
    return ctx?(int)fwrite(p,1,n,(FILE *)ctx):(int)n;
}
/* Register-file model: 16-bit big-endian registers, one per transaction. */
static int i2c(void *ctx,const uint8_t *tx,size_t tx_size,uint8_t *rx,size_t rx_size) {
    (void)ctx;
    if(++transactions==fail_at) {fail_at=0;return -7;}
    assert(tx && tx_size>=1);
    if(tx_size==3) {assert(!rx_size);registers[tx[0]]=(uint16_t)((tx[1]<<8)|tx[2]);return 0;}
    assert(tx_size==1 && rx_size==2);
    rx[0]=(uint8_t)(registers[tx[0]]>>8);rx[1]=(uint8_t)registers[tx[0]];return 0;
}
static int reinit(void *ctx) {(void)ctx;++reinits;return 0;}
static void command(uint8_t *out,uint8_t op,uint8_t count,uint8_t reg,uint16_t value,uint32_t tag) {
    uint32_t crc;
    memset(out,0,20);memcpy(out,"LDC1",4);
    out[4]=op;out[5]=count;out[6]=reg;out[8]=(uint8_t)value;out[9]=(uint8_t)(value>>8);
    out[12]=(uint8_t)tag;out[13]=(uint8_t)(tag>>8);out[14]=(uint8_t)(tag>>16);out[15]=(uint8_t)(tag>>24);
    crc=ld_stream_crc32(out,16);
    out[16]=(uint8_t)crc;out[17]=(uint8_t)(crc>>8);out[18]=(uint8_t)(crc>>16);out[19]=(uint8_t)(crc>>24);
}
static unsigned steps;
/* One bus transaction per call: step until the command completes (or nothing is pending). */
static size_t run(void) {
    size_t size=0;steps=0;
    while(ld_radar_control_pending(&control) && !size) {
        unsigned before=transactions;
        size=ld_radar_control_execute(&control,i2c,NULL,reinit,NULL,reply,sizeof(reply));
        assert(transactions-before<=1);++steps;
    }
    return size;
}
static unsigned value(unsigned n) {return reply[12+2*n]|(reply[13+2*n]<<8);}
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
static void frame(uint32_t start) {
    unsigned chirp,lane;
    for(chirp=0;chirp<64;++chirp)for(lane=0;lane<2;++lane)feed(lane,chirp,start+chirp*1200);
}
int main(int argc,char **argv) {
    uint8_t cmd[20],noisy[64];unsigned n;size_t size;FILE *file=NULL;
    if(argc==2) {file=fopen(argv[1],"wb");assert(file);}
    ld_radar_control_init(&control);
    for(n=0;n<256;++n)registers[n]=(uint16_t)(0x1000+n);

    /* Parsing: split delivery, leading noise, a corrupt command, then a good one. */
    command(cmd,LD_CONTROL_READ,3,0x61,0,0x11223344u);
    memset(noisy,'L',5);memcpy(noisy+5,cmd,20);noisy[5+16]^=1; /* Bad CRC. */
    memcpy(noisy+25,cmd,20);
    for(n=0;n<45;++n)ld_radar_control_feed(&control,noisy+n,1,100);
    assert(ld_radar_control_pending(&control)==1 && control.received==1 && control.discarded_bytes==25);
    assert(ld_radar_control_waiting_ms(&control,350)==250);
    size=run();
    assert(size==18 && reply[4]==LD_CONTROL_READ && reply[5]==LD_CONTROL_OK && reply[6]==0x61 && reply[7]==3);
    assert(reply[0]==0x44 && reply[3]==0x11 && value(0)==0x1061 && value(2)==0x1063);
    assert(transactions==3 && steps==3 && reply[8]==0 && reply[9]==0 && !ld_radar_control_pending(&control));

    /* WRITE: any register and value, generation advances, value read back. */
    command(cmd,LD_CONTROL_WRITE,1,0x53,0xbeef,7);ld_radar_control_feed(&control,cmd,20,0);
    assert(run()==14 && reply[5]==LD_CONTROL_OK && value(0)==0xbeef && registers[0x53]==0xbeef);
    assert(reply[8]==1 && control.generation==1);
    /* A failed write still advances generation: the radar state is unknown. */
    command(cmd,LD_CONTROL_WRITE,1,0x61,0x0022,8);ld_radar_control_feed(&control,cmd,20,0);
    transactions=0;fail_at=1;
    assert(run()==14 && reply[5]==LD_CONTROL_BUS_ERROR && reply[8]==2);
    assert((int16_t)(reply[10]|(reply[11]<<8))==-7);
    /* A failed READ stops and reports only the registers actually read. */
    command(cmd,LD_CONTROL_READ,4,0x10,0,9);ld_radar_control_feed(&control,cmd,20,0);
    transactions=0;fail_at=3;
    assert(run()==16 && reply[5]==LD_CONTROL_BUS_ERROR && reply[7]==2 && value(1)==0x1011);
    assert(transactions==3 && control.generation==2);
    /* Malformed fields are answered without bus traffic. */
    command(cmd,LD_CONTROL_READ,LD_CONTROL_READ_MAX+1,0,0,11);ld_radar_control_feed(&control,cmd,20,0);
    command(cmd,LD_CONTROL_READ,2,0xff,0,12);ld_radar_control_feed(&control,cmd,20,0);
    command(cmd,9,0,0,0,13);ld_radar_control_feed(&control,cmd,20,0);
    transactions=0;
    for(n=0;n<3;++n) {assert(run()==12 && reply[5]==LD_CONTROL_BAD_COMMAND && reply[7]==0);}
    assert(transactions==0);
    /* REINIT advances generation and calls the application hook. */
    command(cmd,LD_CONTROL_REINIT,0,0,0,14);ld_radar_control_feed(&control,cmd,20,0);
    assert(run()==12 && reply[5]==LD_CONTROL_OK && reinits==1 && control.generation==3);
    /* Overflow: the dropped command is answered first, nothing is lost silently. */
    for(n=0;n<LD_CONTROL_QUEUE+1;++n) {command(cmd,LD_CONTROL_READ,1,(uint8_t)n,0,100+n);ld_radar_control_feed(&control,cmd,20,0);}
    assert(ld_radar_control_pending(&control)==LD_CONTROL_QUEUE+1 && control.overflows==1);
    assert(run()==12 && reply[5]==LD_CONTROL_OVERFLOW && reply[0]==100+LD_CONTROL_QUEUE);
    for(n=0;n<LD_CONTROL_QUEUE;++n) {assert(run()==14 && reply[0]==100+n && value(0)==registers[n]);}
    assert(run()==0 && ld_radar_control_execute(&control,i2c,NULL,reinit,NULL,reply,12)==0);

    /* Stream: replies only between frames; BEGIN carries the generation. */
    assert(LD_STREAM_CHIRPS==16);
    assert(ld_stream_init(&stream,queue,sizeof(queue),identity)==0);
    ld_acquisition_init(&acq,&stream);
    frame(1000);
    assert(stream.stats.frames_completed==1 && !stream.active);
    while(stream.used)assert(ld_stream_pump(&stream,output,file,511)>0);
    command(cmd,LD_CONTROL_WRITE,1,0x61,0x0023,0xabcd);ld_radar_control_feed(&control,cmd,20,0);
    size=run();assert(size==14);
    stream.register_generation=control.generation;
    feed(0,0,91000);feed(1,0,91000); /* BEGIN: no reply may enter mid-frame. */
    assert(stream.active && !ld_stream_control_reply(&stream,reply,size,91100));
    for(n=1;n<64;++n){feed(0,n,91000+n*1200);feed(1,n,91000+n*1200);}
    assert(!stream.active && stream.stats.frames_completed==2);
    assert(ld_stream_control_reply(&stream,reply,size,170000)==1);
    frame(181000); /* Skipped: BEGIN still requires an empty queue. */
    assert(stream.stats.frames_skipped==1);
    while(stream.used)assert(ld_stream_pump(&stream,output,file,511)>0);
    frame(271000);
    assert(stream.stats.frames_completed==3 && control.generation==4);
    while(stream.used)assert(ld_stream_pump(&stream,output,file,511)>0);
    if(file)fclose(file);
    puts("radar control: parsing, execution, overflow and stream replies passed");
    return 0;
}
