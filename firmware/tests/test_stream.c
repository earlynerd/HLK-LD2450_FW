#ifdef _MSC_VER
#define _CRT_SECURE_NO_WARNINGS
#endif
#include "ld2450_stream.h"
#include "radar_wire.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static struct ld_stream stream;
static uint8_t queue[8192], record[2056], encoded[2057], config[32];
static void make_record(unsigned lane, unsigned chirp)
{
    uint32_t h=0xaa200201u|(lane<<22)|(chirp<<11);
    uint16_t sum=0, tail=(uint16_t)((lane<<14)|0x2000|((chirp&15)<<8)|0x55);
    unsigned n;
    record[0]=(uint8_t)(h>>24); record[1]=(uint8_t)(h>>16);
    record[2]=(uint8_t)(h>>8); record[3]=(uint8_t)h;
    for (n=0;n<1024;++n) {
        uint16_t value=(uint16_t)(n+chirp+lane);
        record[4+2*n]=(uint8_t)(value>>8); record[5+2*n]=(uint8_t)value;
        sum=(uint16_t)(sum+value);
    }
    record[2052]=(uint8_t)(sum>>8); record[2053]=(uint8_t)sum;
    record[2054]=(uint8_t)(tail>>8); record[2055]=(uint8_t)tail;
}
static int discard(void *ctx, const uint8_t *data, size_t size)
{ (void)ctx; (void)data; return (int)size; }
static int stall(void *ctx, const uint8_t *data, size_t size)
{ (void)ctx; (void)data; (void)size; return 0; }
static int fail(void *ctx, const uint8_t *data, size_t size)
{ (void)ctx; (void)data; (void)size; return -1; }
static int file_write(void *ctx, const uint8_t *data, size_t size)
{
    /* Force short acceptance independently of the pump's 37-byte budget. */
    if (size>13) size=13;
    return (int)fwrite(data,1,size,(FILE *)ctx);
}
static void drain(ld_stream_write_fn fn, void *ctx)
{
    while (stream.used) assert(ld_stream_pump(&stream,fn,ctx,37)>0);
}
static void init(size_t capacity)
{ assert(ld_stream_init(&stream,queue,capacity,config)==0); }
static void checks(void)
{
    unsigned chirp, lane;
    assert(ld_stream_crc32((const uint8_t *)"123456789",9)==0xcbf43926u);
    /* Independent bitwise reference, all four alignments and tail lengths. */
    {
        uint8_t bytes[260]; unsigned off,n,j,k; uint32_t ref;
        for(n=0;n<sizeof(bytes);++n)bytes[n]=(uint8_t)(n*71u+n/7u);
        for(off=0;off<4;++off) for(n=0;n<=256;++n) {
            ref=0xffffffffu;
            for(j=0;j<n;++j) {
                ref^=bytes[off+j];
                for(k=0;k<8;++k)ref=(ref>>1)^((ref&1)?0xedb88320u:0);
            }
            assert(ld_stream_crc32(bytes+off,n)==(ref^0xffffffffu));
        }
    }
    assert(ld_stream_init(&stream,queue,100,config)==-1);
    {
        static uint8_t large_queue[90112];
        unsigned n;
        assert(ld_stream_init(&stream,large_queue,sizeof(large_queue),config)==0);
        /* Cross the old 16-bit boundary, then the actual ring boundary. */
        stream.head=65520;
        for(n=0;n<200;++n) {
            assert(ld_stream_begin(&stream,n,0)==1);
            ld_stream_abort(&stream,5,0);drain(discard,NULL);
        }
        assert(stream.head==(65520u+200u*128u)%sizeof(large_queue));
    }
    {
        struct radar_record decoded;unsigned bad;
        /* Trusted fast path still rejects mismatched validation metadata. */
        for(bad=0;bad<4;++bad) {
            init(sizeof(queue));assert(ld_stream_begin(&stream,1,0)==1);
            make_record(0,0);
            assert(radar_record_decode(record,sizeof(record),&decoded)==RADAR_RECORD_VALID);
            if(bad==0)decoded.rx_index=2;
            if(bad==1)decoded.iq=record;
            if(bad==2)decoded.packet_valid=0;
            if(bad==3)decoded.checksum_calculated^=1;
            assert(ld_stream_record_validated(&stream,record,sizeof(record),&decoded,0)==-1);
            assert(!stream.active && stream.stats.invalid_records==1);
        }
    }
    init(sizeof(queue));
    stream.sequence=0xfffffffeu;
    assert(ld_stream_begin(&stream,42,0xfffffff0u)==1);
    for (chirp=0;chirp<64;++chirp) for (lane=0;lane<2;++lane) {
        make_record(lane,chirp);
        assert(ld_stream_record(&stream,record,sizeof(record),chirp*1200)==1);
        drain(discard,NULL);
    }
    assert(stream.stats.frames_completed==1 && !stream.active);
    assert(stream.stats.raw_records==2 && stream.stats.compressed_records==126);
    assert(stream.stats.queue_peak<=sizeof(queue));
    /* A new frame resets both references. */
    assert(ld_stream_begin(&stream,44,100000)==1);
    make_record(0,0); assert(ld_stream_record(&stream,record,sizeof(record),0)==1);
    assert(stream.stats.raw_records==3);
    /* Duplicate, missing chirp, checksum failure and timeout abort. */
    assert(ld_stream_record(&stream,record,sizeof(record),0)==-1);
    assert(stream.stats.invalid_records==1 && stream.stats.frames_rejected==1);
    drain(discard,NULL);
    assert(ld_stream_begin(&stream,45,0)==1);
    make_record(0,1); assert(ld_stream_record(&stream,record,sizeof(record),0)==-1);
    drain(discard,NULL);
    assert(ld_stream_begin(&stream,46,0)==1);
    make_record(0,0); record[5]^=1;
    assert(ld_stream_record(&stream,record,sizeof(record),0)==-1);
    drain(discard,NULL);
    assert(ld_stream_begin(&stream,47,0)==1);
    ld_stream_abort(&stream,4,200000);
    assert(stream.stats.frames_rejected==4);
    drain(discard,NULL);
    /* Minimum queue, stalled host: reject atomically, reserve ABORT, skip. */
    init(LD_STREAM_MESSAGE_MAX+40);
    assert(ld_stream_begin(&stream,0,0)==1);
    assert(ld_stream_pump(&stream,stall,NULL,64)==0);
    make_record(0,0);
    assert(ld_stream_record(&stream,record,sizeof(record),0)==-1);
    assert(stream.stats.queue_overflows==1 && stream.used==128);
    assert(ld_stream_begin(&stream,1,0)==0 && stream.stats.frames_skipped==1);
    drain(discard,NULL);
    assert(ld_stream_begin(&stream,2,0)==1);
    assert(ld_stream_pump(&stream,fail,NULL,64)==-1);
    assert(stream.used==0 && !stream.active && stream.stats.transport_errors==1);
    assert(ld_stream_begin(&stream,3,0)==1);
    assert(ld_stream_begin(&stream,4,0)==0); /* Frame boundary before completion. */
    assert(stream.stats.frames_rejected==3);
    /* Disconnect after END is enqueued also records the lost frame. */
    init(sizeof(queue));
    assert(ld_stream_begin(&stream,5,0)==1);
    for (chirp=0;chirp<64;++chirp) for (lane=0;lane<2;++lane) {
        make_record(lane,chirp);
        assert(ld_stream_record(&stream,record,sizeof(record),0)==1);
        if (chirp!=63 || lane!=1) drain(discard,NULL);
    }
    assert(stream.pending_complete && !stream.active);
    assert(ld_stream_pump(&stream,fail,NULL,64)==-1);
    assert(stream.stats.frames_rejected==1 && !stream.pending_complete);
    printf("stream checks passed; state=%u bytes; queue=%u bytes\n",
           (unsigned)sizeof(stream),(unsigned)sizeof(queue));
}
/* Cross-language harness: actual C codec and stream producer, no hardware. */
int main(int argc, char **argv)
{
    FILE *input[2], *output;
    unsigned chirp, lane;
    if (argc==4 && strcmp(argv[1],"--codec")==0) {
        uint8_t previous[2048], length[2];
        size_t got, size;
        input[0]=fopen(argv[2],"rb"); output=fopen(argv[3],"wb");
        if (!input[0] || !output) return 2;
        chirp=0;
        while ((got=fread(record,1,2056,input[0]))!=0) {
            if (got!=2056) return 3;
            size=ld_stream_encode(record,chirp ? previous : NULL,encoded,sizeof(encoded));
            memcpy(previous,record+4,2048); ++chirp;
            length[0]=(uint8_t)size; length[1]=(uint8_t)(size>>8);
            if (fwrite(length,1,2,output)!=2 || fwrite(encoded,1,size,output)!=size) return 4;
        }
        fclose(input[0]); return fclose(output)!=0;
    }
    if (argc==5 && strcmp(argv[1],"--replay")==0) {
        input[0]=fopen(argv[2],"rb"); input[1]=fopen(argv[3],"rb"); output=fopen(argv[4],"wb");
        if (!input[0] || !input[1] || !output) return 2;
        init(sizeof(queue));
        if (ld_stream_begin(&stream,7,1000)!=1) return 3;
        for (chirp=0;chirp<64;++chirp) for (lane=0;lane<2;++lane) {
            if (fread(record,1,2056,input[lane])!=2056) {
                ld_stream_abort(&stream,4,chirp*1200); drain(file_write,output);
                fclose(input[0]); fclose(input[1]); fclose(output); return 0;
            }
            if (ld_stream_record(&stream,record,2056,1000+chirp*1200)!=1) return 4;
            drain(file_write,output);
        }
        drain(file_write,output);
        fclose(input[0]); fclose(input[1]); return fclose(output)!=0;
    }
    checks(); return 0;
}
