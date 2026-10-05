#include "radar_wire.h"
#include <string.h>

static uint16_t be16(const uint8_t *p)
{
    return (uint16_t)(((uint16_t)p[0] << 8) | p[1]);
}

static uint32_t be32(const uint8_t *p)
{
    return ((uint32_t)be16(p) << 16) | be16(p + 2);
}

enum radar_record_status radar_record_decode(const uint8_t *data, size_t size,
                                             struct radar_record *r)
{
    size_t payload_size, expected, n;
    uint16_t count, tail;
    uint32_t sum = 0;
    if (!r) {
        return RADAR_RECORD_BAD_HEADER;
    }
    memset(r, 0, sizeof(*r));
    if (!data || size < 4) {
        return RADAR_RECORD_INCOMPLETE;
    }
    r->header = be32(data);
    r->rx_index = (uint8_t)((r->header >> 22) & 3);
    r->chirp = (uint16_t)((r->header >> 11) & 0x1ff);
    count = (uint16_t)(r->header & 0x7ff); /* Empirical bit-9 count extension. */
    if (data[0] != 0xaa || r->rx_index > 1 ||
        ((r->header >> 20) & 3) != 2 || count < 2) {
        return RADAR_RECORD_BAD_HEADER;
    }
    r->declared_pairs = (uint16_t)(count - 1);
    r->iq = data + 4;
    expected = 8u + 4u * r->declared_pairs;
    if (size != expected) {
        size_t observed = (size - 4u) / 4u;
        r->observed_pairs = observed > r->declared_pairs ?
                            r->declared_pairs : (uint16_t)observed;
        /* Repeatable observed boot format. No invented checksum/trailer. */
        if (r->chirp == 0 && r->declared_pairs == 256 && size == 996) {
            return RADAR_RECORD_STARTUP_NO_TRAILER;
        }
        return size < expected ? RADAR_RECORD_INCOMPLETE : RADAR_RECORD_BAD_TRAILER;
    }
    r->observed_pairs = r->declared_pairs;
    tail = (uint16_t)(((uint16_t)r->rx_index << 14) | 0x2000 |
                      ((r->chirp & 15u) << 8) | 0x55);
    if (be16(data + size - 2) != tail) {
        return RADAR_RECORD_BAD_TRAILER;
    }
    payload_size = size - 8;
    for (n = 0; n < payload_size; n += 2) {
        sum += be16(r->iq + n);
    }
    r->checksum_calculated = (uint16_t)sum;
    r->checksum_stored = be16(data + size - 4);
    r->checksum_checked = 1;
    if (r->checksum_calculated != r->checksum_stored) {
        return RADAR_RECORD_BAD_CHECKSUM;
    }
    r->packet_valid = 1;
    return RADAR_RECORD_VALID;
}

int radar_record_iq(const struct radar_record *r, size_t sample,
                    int16_t *i, int16_t *q)
{
    uint16_t vi, vq;
    if (!r || !r->iq || !i || !q || sample >= r->observed_pairs) {
        return -1;
    }
    vi = be16(r->iq + 4u * sample);
    vq = be16(r->iq + 4u * sample + 2u);
    *i = (int16_t)(vi & 0x8000 ? (int32_t)vi - 65536 : (int32_t)vi);
    *q = (int16_t)(vq & 0x8000 ? (int32_t)vq - 65536 : (int32_t)vq);
    return 0;
}
