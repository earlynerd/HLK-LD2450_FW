/* Range-bin export (codec 2): acquisition -> validated records -> injected FFT ->
 * bins -K..K. The reference transform here is an exact DFT rounded to int32,
 * standing in for the BR23 engine (measured exact and unscaled, HW_FFT.md). */
#include "ld2450_acquisition.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static struct ld_stream stream;
static struct ld_acquisition acq;
static uint8_t queue[90112],raw[LD_STREAM_RECORD_BYTES],identity[32];
static unsigned transforms;
static int fail_next;
static int output(void *ctx,const uint8_t *p,size_t n) {
    if(n>63)n=63;
    return ctx?(int)fwrite(p,1,n,(FILE *)ctx):(int)n;
}
static int dft(void *ctx,int32_t *data,unsigned n) {
    static double re[LD_RADAR_PAIRS],im[LD_RADAR_PAIRS];
    unsigned j,k;
    (void)ctx;++transforms;
    if(fail_next) {fail_next=0;return -1;}
    assert(n==LD_RADAR_PAIRS);
    for(k=0;k<n;++k) {
        double sr=0,si=0;
        for(j=0;j<n;++j) {
            double a=-2.0*3.14159265358979323846*(double)((j*k)%n)/(double)n,c=cos(a),s=sin(a);
            sr+=data[2*j]*c-data[2*j+1]*s;si+=data[2*j]*s+data[2*j+1]*c;
        }
        re[k]=sr;im[k]=si;
    }
    for(k=0;k<n;++k) {data[2*k]=(int32_t)lround(re[k]);data[2*k+1]=(int32_t)lround(im[k]);}
    return 0;
}
/* Host mirror: stream_bins_interop.py sample(). A tone, an offset and a ramp,
 * scaled so some records need a non-zero shift. */
static int16_t sample(unsigned lane,unsigned chirp,unsigned n,unsigned q) {
    double a=6.283185307179586*(double)((5u+lane)*n)/(double)LD_RADAR_PAIRS+0.1*chirp;
    double v=(q?sin(a):cos(a))*(3000.0+40.0*chirp)+(q?-700.0:1200.0)+(double)n*(lane?3.0:-2.0)+(double)((n*37u+chirp*11u+q)%23u);
    return (int16_t)lround(v);
}
static void feed(unsigned lane,unsigned chirp,uint32_t time) {
    unsigned j;uint32_t h=0xaa200000u|(LD_RADAR_PAIRS+1u)|(lane<<22)|(chirp<<11);uint16_t sum=0;
    raw[0]=(uint8_t)(h>>24);raw[1]=(uint8_t)(h>>16);raw[2]=(uint8_t)(h>>8);raw[3]=(uint8_t)h;
    for(j=0;j<LD_STREAM_VALUES;++j) {
        uint16_t v=(uint16_t)sample(lane,chirp,j/2,j&1u);
        raw[4+2*j]=(uint8_t)(v>>8);raw[5+2*j]=(uint8_t)v;sum=(uint16_t)(sum+v);
    }
    raw[sizeof(raw)-4]=(uint8_t)(sum>>8);raw[sizeof(raw)-3]=(uint8_t)sum;
    raw[sizeof(raw)-2]=(uint8_t)((lane<<6)|0x20|(chirp&15));raw[sizeof(raw)-1]=0x55;
    ld_acquisition_feed(&acq,lane,raw,sizeof(raw),time,1);
}
#define FRAME_BYTES (88u+4u+36u+128u*(36u+LD_STREAM_BIN_PAYLOAD))
int main(int argc,char **argv) {
    unsigned chirp,lane;FILE *file=NULL;
    if(argc==2) {file=fopen(argv[1],"wb");assert(file);}
    assert(LD_STREAM_CHIRPS==64 && LD_STREAM_FFT_BINS==40);
    assert(ld_stream_init(&stream,queue,sizeof(queue),identity)==0);
    ld_stream_set_transform(&stream,dft,NULL);
    ld_acquisition_init(&acq,&stream);
    /* A whole 64-chirp range-bin frame fits the queue with no transport service. */
    for(chirp=0;chirp<64;++chirp)for(lane=0;lane<2;++lane)feed(lane,chirp,1000+chirp*1200);
    assert(transforms==128 && stream.stats.frames_completed==1);
    assert(stream.used==FRAME_BYTES && stream.stats.compressed_records==128);
    while(stream.used)assert(ld_stream_pump(&stream,output,file,511)>0);
    /* A failing transform rejects the frame explicitly instead of exporting garbage. */
    for(chirp=0;chirp<64;++chirp)for(lane=0;lane<2;++lane) {
        if(chirp==9 && lane==1) fail_next=1;
        feed(lane,chirp,91000+chirp*1200);
    }
    assert(stream.stats.frames_completed==1 && stream.stats.frames_rejected==1);
    while(stream.used)assert(ld_stream_pump(&stream,output,file,511)>0);
    /* A missing transform is refused (not a crash). */
    ld_stream_set_transform(&stream,NULL,NULL);
    for(chirp=0;chirp<2;++chirp)for(lane=0;lane<2;++lane)feed(lane,chirp,181000+chirp*1200);
    assert(stream.stats.frames_completed==1 && stream.stats.frames_rejected>=1 && !stream.active);
    while(stream.used)assert(ld_stream_pump(&stream,output,NULL,511)>0);
    if(file)assert(fclose(file)==0);
    return 0;
}
