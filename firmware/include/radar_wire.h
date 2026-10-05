#ifndef LD2450_RADAR_WIRE_H
#define LD2450_RADAR_WIRE_H

#include <stddef.h>
#include <stdint.h>

enum radar_record_status {
    RADAR_RECORD_VALID = 0,
    RADAR_RECORD_STARTUP_NO_TRAILER,
    RADAR_RECORD_INCOMPLETE,
    RADAR_RECORD_BAD_HEADER,
    RADAR_RECORD_BAD_TRAILER,
    RADAR_RECORD_BAD_CHECKSUM
};

struct radar_record {
    uint32_t header;
    uint16_t chirp;
    uint16_t declared_pairs;
    uint16_t observed_pairs;
    uint16_t checksum_stored;
    uint16_t checksum_calculated;
    uint8_t rx_index;
    uint8_t checksum_checked;
    uint8_t packet_valid;
    const uint8_t *iq; /* Borrowed payload; keep the input buffer alive. */
};

/* Accepts one assembled logical record, not one CS transaction. */
enum radar_record_status radar_record_decode(const uint8_t *data, size_t size,
                                             struct radar_record *record);
int radar_record_iq(const struct radar_record *record, size_t sample,
                    int16_t *i, int16_t *q);

#endif
