#include "uart_update_protocol.h"
#include <stdio.h>
#include <string.h>
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"line %d: %s\n",__LINE__,#x); return 1; } } while (0)
int main(void)
{
    struct ld_update_parser p = {{0},0};
    uint8_t payload[LD_UPDATE_PAYLOAD_MAX], frame[LD_UPDATE_FRAME_MAX], out[514];
    size_t n,i,result=0;
    CHECK(ld_update_crc((const uint8_t *)"123456789",9)==0x31c3);
    payload[0]=2; ld_update_put_u32(payload+1,0x12345678); ld_update_put_u32(payload+5,512);
    for(i=9;i<sizeof(payload);++i) payload[i]=(uint8_t)i;
    n=ld_update_frame(frame,sizeof(frame),payload,sizeof(payload)); CHECK(n==527);
    ld_update_feed(&p,0x21);ld_update_feed(&p,0xaa);
    for(i=0;i<n;++i) { result=ld_update_feed(&p,frame[i]); if(i+1<n) CHECK(!result); }
    CHECK(result==sizeof(payload));
    memset(out,0x5a,sizeof(out));
    CHECK(ld_update_read_reply(p.frame+4,result,0x12345678,512,out+1,512)==512);
    CHECK(out[0]==0x5a && out[513]==0x5a && !memcmp(out+1,payload+9,512));
    CHECK(ld_update_read_reply(payload,sizeof(payload),0x12345679,512,out,512)==-1);
    CHECK(ld_update_read_reply(payload,sizeof(payload)-1,0x12345678,512,out,512)==-1);
    CHECK(ld_update_read_reply(payload,sizeof(payload),0x12345678,512,out,511)==-1);
    payload[5]=1;CHECK(ld_update_read_reply(payload,sizeof(payload),0x12345678,512,out,512)==-1);
    frame[50]^=1;
    for(i=0;i<n;++i) CHECK(ld_update_feed(&p,frame[i])==0);
    for(i=0;i<65536;++i) {
        p.used=0;ld_update_feed(&p,0xaa);ld_update_feed(&p,0x55);
        ld_update_feed(&p,(uint8_t)i);ld_update_feed(&p,(uint8_t)(i>>8));
        if(!i || i>LD_UPDATE_PAYLOAD_MAX) CHECK(p.used<=1);
    }
    p.used=0;payload[0]=6;n=ld_update_frame(frame,sizeof(frame),payload,1);
    for(i=0;i<n;++i) result=ld_update_feed(&p,frame[i]);
    CHECK(result==1 && p.frame[4]==6);
    CHECK(!ld_update_frame(frame,6,payload,1));
    CHECK(!ld_update_frame(frame,sizeof(frame),payload,0));
    puts("UART CRC, resynchronization, all length fields, corruption and reply bounds passed.");
    return 0;
}
