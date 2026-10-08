#include "ld2450_acquisition.h"
#include "radar_wire.h"
#include <string.h>
void ld_acquisition_init(struct ld_acquisition *a,struct ld_stream *s) {
    memset(a,0,sizeof(*a));a->stream=s;
}
void ld_acquisition_gap(struct ld_acquisition *a,uint32_t time) {
    ld_stream_abort(a->stream,5,time);a->first_mask=0;a->tracking=0;a->used[0]=a->used[1]=0;
}
void ld_acquisition_tick(struct ld_acquisition *a,uint32_t time) {
    if((a->tracking || a->stream->active || a->first_mask) && (uint32_t)(time-a->last_record)>200000) {
        ++a->timeouts;ld_acquisition_gap(a,time);
    }
}
static void record(struct ld_acquisition *a,unsigned lane,uint32_t time,int enabled,
                   const struct radar_record *r) {
    uint8_t *p=a->candidate[lane];
    ++a->valid[lane];a->last_record=time;
    if(!r->chirp) {
        if(a->tracking) {++a->sequence_errors;a->tracking=0;}
        if(a->stream->active) ld_stream_abort(a->stream,1,time);
        if(a->first_mask&(1u<<lane)) ++a->unpaired;
        memcpy(a->first[lane],p,LD_STREAM_RECORD_BYTES);a->first_time[lane]=time;
        a->first_mask|=(uint8_t)(1u<<lane);
        if(a->first_mask==3) {
            uint32_t delta=time-a->first_time[1-lane];
            if(delta>5000u && (uint32_t)(0u-delta)>5000u) {
                a->first_mask=(uint8_t)(1u<<lane);++a->unpaired;return;
            }
            a->first_mask=0;++a->frame_id;
            a->tracking=1;a->next[0]=a->next[1]=1;
            if(!enabled) {++a->stream->stats.frames_skipped;return;}
            if(ld_stream_begin(a->stream,a->frame_id,time)==1) {
                ld_stream_record(a->stream,a->first[0],LD_STREAM_RECORD_BYTES,a->first_time[0]);
                ld_stream_record(a->stream,a->first[1],LD_STREAM_RECORD_BYTES,a->first_time[1]);
            }
        }
    } else {
        if(a->tracking) {
            if(a->next[lane]!=r->chirp) {++a->sequence_errors;a->tracking=0;}
            else {++a->next[lane];if(a->next[0]==64 && a->next[1]==64) {++a->complete_pairs;a->tracking=0;}}
        }
        if(a->first_mask&(1u<<lane)) {a->first_mask=0;++a->unpaired;}
        /* Acquisition still validates all 64 physical chirps. An export may
         * retain only the first 16; never feed later chirps into that window. */
        if(a->stream->active && r->chirp<LD_STREAM_CHIRPS)
            ld_stream_record_validated(a->stream,p,LD_STREAM_RECORD_BYTES,r,time);
    }
}
void ld_acquisition_feed(struct ld_acquisition *a,unsigned lane,const uint8_t *p,size_t n,
                         uint32_t time,int enabled) {
    if(lane>1 || (!p && n)) return;
    while(n) {
        uint8_t *b=a->candidate[lane];
        size_t *used=&a->used[lane];
        size_t take=(*used<4 ? 4 : LD_STREAM_RECORD_BYTES)-*used;
        if(take>n) take=n;
        memcpy(b+*used,p,take);*used+=take;p+=take;n-=take;
        while(*used>=4) {
            uint32_t h=((uint32_t)b[0]<<24)|((uint32_t)b[1]<<16)|((uint32_t)b[2]<<8)|b[3];
            int header=(h>>24)==0xaa && ((h>>22)&3)==lane && ((h>>20)&3)==2 &&
                       (h&2047)==LD_RADAR_PAIRS+1u && ((h>>11)&511)<64;
            if(header && *used<LD_STREAM_RECORD_BYTES) break;
            if(header) {
                struct radar_record r;
                enum radar_record_status status=radar_record_decode(b,LD_STREAM_RECORD_BYTES,&r);
                if(status==RADAR_RECORD_VALID) {
                    record(a,lane,time,enabled,&r);*used=0;break;
                }
                if(!a->corrupt) {memcpy(a->bad_snapshot,b,LD_STREAM_RECORD_BYTES);a->bad_status=(uint32_t)status;}
                ++a->corrupt;ld_stream_abort(a->stream,2,time);a->first_mask=0;a->tracking=0;
            }
            /* Search without repeatedly moving a whole corrupt candidate.
             * Keep at most the final three bytes if no next header is found. */
            {
                size_t skip=1;
                while(skip+3<*used) {
                    uint32_t next=((uint32_t)b[skip]<<24)|((uint32_t)b[skip+1]<<16)|
                                  ((uint32_t)b[skip+2]<<8)|b[skip+3];
                    if((next>>24)==0xaa && ((next>>22)&3)==lane && ((next>>20)&3)==2 &&
                       (next&2047)==LD_RADAR_PAIRS+1u && ((next>>11)&511)<64) break;
                    ++skip;
                }
                *used-=skip;memmove(b,b+skip,*used);a->sync_bytes+=(uint32_t)skip;
            }
        }
    }
}
