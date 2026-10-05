#include "uart_update_protocol.h"
#include <string.h>
uint16_t ld_update_crc(const uint8_t *data, size_t size)
{
    uint16_t crc = 0;
    size_t i; unsigned bit;
    for (i = 0; i < size; ++i) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (bit = 0; bit < 8; ++bit)
            crc = (uint16_t)((crc << 1) ^ ((crc & 0x8000u) ? 0x1021u : 0u));
    }
    return crc;
}
uint32_t ld_update_u32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
void ld_update_put_u32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8);
    p[2] = (uint8_t)(v >> 16); p[3] = (uint8_t)(v >> 24);
}
size_t ld_update_frame(uint8_t *out, size_t capacity, const uint8_t *p, size_t n)
{
    uint16_t crc;
    if (!out || !p || !n || n > LD_UPDATE_PAYLOAD_MAX || capacity < n + 6u) return 0;
    out[0] = 0xaa; out[1] = 0x55;
    out[2] = (uint8_t)n; out[3] = (uint8_t)(n >> 8);
    memcpy(out + 4, p, n); crc = ld_update_crc(out, n + 4);
    out[n + 4] = (uint8_t)crc; out[n + 5] = (uint8_t)(crc >> 8);
    return n + 6;
}
size_t ld_update_feed(struct ld_update_parser *p, uint8_t b)
{
    size_t n; uint16_t crc;
    if (!p) return 0;
    if (p->used == 0) { if (b == 0xaa) p->frame[p->used++] = b; return 0; }
    if (p->used == 1 && b != 0x55) { p->used = b == 0xaa ? 1u : 0u; return 0; }
    if (p->used >= sizeof(p->frame)) { p->used = 0; return 0; }
    p->frame[p->used++] = b;
    if (p->used < 4) return 0;
    n = (size_t)p->frame[2] | ((size_t)p->frame[3] << 8);
    if (!n || n > LD_UPDATE_PAYLOAD_MAX) { p->used = b == 0xaa ? 1u : 0u; return 0; }
    if (p->used != n + 6) return 0;
    p->used = 0;
    crc = (uint16_t)((uint16_t)p->frame[n + 4] | ((uint16_t)p->frame[n + 5] << 8));
    return crc == ld_update_crc(p->frame, n + 4) ? n : 0;
}
int ld_update_read_reply(const uint8_t *p, size_t n, uint32_t offset,
                         uint32_t requested, uint8_t *out, size_t capacity)
{
    if (!p || !out || !requested || requested > LD_UPDATE_DATA_MAX ||
        requested > capacity || n != requested + 9u || p[0] != 2 ||
        ld_update_u32(p + 1) != offset || ld_update_u32(p + 5) != requested) return -1;
    memcpy(out, p + 9, requested);
    return (int)requested;
}
