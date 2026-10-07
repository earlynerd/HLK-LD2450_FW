#ifndef LD2450_ACQUISITION_H
#define LD2450_ACQUISITION_H
#include "ld2450_stream.h"
struct ld_acquisition {
    struct ld_stream *stream;
    uint8_t candidate[2][2056], first[2][2056];
    size_t used[2];
    uint32_t first_time[2], last_record, frame_id;
    uint32_t valid[2], corrupt, sync_bytes, unpaired, timeouts;
    uint32_t complete_pairs,sequence_errors;
    uint16_t next[2];
    uint8_t tracking;
    uint8_t bad_snapshot[2056];
    uint32_t bad_status;
    uint8_t first_mask;
};
void ld_acquisition_init(struct ld_acquisition *,struct ld_stream *);
void ld_acquisition_feed(struct ld_acquisition *,unsigned lane,const uint8_t *,size_t,
                         uint32_t time_us,int export_enabled);
void ld_acquisition_gap(struct ld_acquisition *,uint32_t time_us);
void ld_acquisition_tick(struct ld_acquisition *,uint32_t time_us);
#endif
