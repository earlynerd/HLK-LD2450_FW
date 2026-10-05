#ifndef LD_UART_UPDATE_PROTOCOL_H
#define LD_UART_UPDATE_PROTOCOL_H
#include <stdint.h>
#include <stddef.h>
#define LD_UPDATE_DATA_MAX 512u
#define LD_UPDATE_PAYLOAD_MAX (9u + LD_UPDATE_DATA_MAX)
#define LD_UPDATE_FRAME_MAX (LD_UPDATE_PAYLOAD_MAX + 6u)
struct ld_update_parser {
    uint8_t frame[LD_UPDATE_FRAME_MAX];
    size_t used;
};
uint16_t ld_update_crc(const uint8_t *data, size_t size);
uint32_t ld_update_u32(const uint8_t *data);
void ld_update_put_u32(uint8_t *data, uint32_t value);
/* Returns a complete valid frame's payload size, or zero. Consume the frame
 * immediately before feeding more bytes. Reset used on an inter-byte timeout. */
size_t ld_update_feed(struct ld_update_parser *parser, uint8_t byte);
size_t ld_update_frame(uint8_t *out, size_t capacity, const uint8_t *payload, size_t size);
/* A response must exactly match the outstanding read, including its wire size. */
int ld_update_read_reply(const uint8_t *payload, size_t size, uint32_t offset,
                         uint32_t requested, uint8_t *out, size_t capacity);
#endif
