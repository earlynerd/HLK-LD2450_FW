#include "ld2450_stream.h"
#include <assert.h>
#include <string.h>
/* Identical chirps normally compress to zero-width blocks. The bench must
 * emit exact raw payloads even with a valid previous-chirp reference. */
int main(void) {
    unsigned n;
    uint8_t record[2056]={0},previous[2048],payload[2057];
    for(n=0;n<2048;++n) previous[n]=record[n+4]=(uint8_t)n;
    record[0]=0xaa;record[1]=0x20;record[2]=2;record[3]=1;
    record[2054]=0x20;record[2055]=0x55;
    assert(ld_stream_encode(record,previous,payload,sizeof(payload))==2057);
    assert(payload[0]==0 && !memcmp(payload+9,record+4,2048));
    assert(!memcmp(payload+1,record,4) && !memcmp(payload+5,record+2052,4));
    return 0;
}
