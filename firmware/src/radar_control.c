#include "ld2450_radar_control.h"
#include "ld2450_stream.h"
#include <string.h>

static uint16_t le16_get(const uint8_t *p) { return (uint16_t)(p[0] | (p[1] << 8)); }
static uint32_t le32_get(const uint8_t *p) { return (uint32_t)le16_get(p) | ((uint32_t)le16_get(p + 2) << 16); }
static void le16_put(uint8_t *p, uint16_t v) { p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8); }

void ld_radar_control_init(struct ld_radar_control *c)
{
    memset(c, 0, sizeof(*c));
}

static void enqueue(struct ld_radar_control *c, const uint8_t *p, uint32_t now_ms)
{
    struct ld_control_command cmd;
    cmd.tag = le32_get(p + 12);
    cmd.op = p[4];
    cmd.count = p[5];
    cmd.reg = p[6];
    cmd.value = le16_get(p + 8);
    cmd.status = LD_CONTROL_OK;
    cmd.queued_ms = now_ms;
    if (p[7] || le16_get(p + 10) ||
        (cmd.op == LD_CONTROL_READ && (!cmd.count || cmd.count > LD_CONTROL_READ_MAX ||
                                       cmd.reg + cmd.count > 256)) ||
        (cmd.op == LD_CONTROL_WRITE && cmd.count != 1) ||
        (cmd.op == LD_CONTROL_REINIT && cmd.count) ||
        cmd.op < LD_CONTROL_READ || cmd.op > LD_CONTROL_REINIT) {
        cmd.status = LD_CONTROL_BAD_COMMAND; /* Answered without touching the radar. */
    }
    ++c->received;
    if (c->count == LD_CONTROL_QUEUE) {
        ++c->overflows;
        cmd.status = LD_CONTROL_OVERFLOW;
        c->overflowed = cmd;
        c->overflow_pending = 1;
        return;
    }
    c->queue[(c->head + c->count) % LD_CONTROL_QUEUE] = cmd;
    ++c->count;
}

void ld_radar_control_feed(struct ld_radar_control *c, const uint8_t *data, size_t size, uint32_t now_ms)
{
    while (size) {
        size_t take = LD_CONTROL_COMMAND_BYTES - c->input_used;
        if (take > size) take = size;
        memcpy(c->input + c->input_used, data, take);
        c->input_used += take;
        data += take;
        size -= take;
        while (c->input_used) {
            size_t skip = 1, valid = c->input_used >= 4 ? 4 : c->input_used;
            if (!memcmp(c->input, "LDC1", valid)) {
                if (c->input_used < LD_CONTROL_COMMAND_BYTES) break; /* Await the rest. */
                if (ld_stream_crc32(c->input, 16) == le32_get(c->input + 16)) {
                    enqueue(c, c->input, now_ms);
                    c->input_used = 0;
                    break;
                }
            }
            /* Resynchronize: drop up to the next possible "LDC1" start. */
            while (skip < c->input_used && c->input[skip] != 'L') ++skip;
            c->discarded_bytes += (uint32_t)skip;
            c->input_used -= skip;
            memmove(c->input, c->input + skip, c->input_used);
        }
    }
}

unsigned ld_radar_control_pending(const struct ld_radar_control *c)
{
    return c->count + c->overflow_pending + c->has_current;
}

uint32_t ld_radar_control_waiting_ms(const struct ld_radar_control *c, uint32_t now_ms)
{
    if (c->has_current) return now_ms - c->current.queued_ms;
    if (c->overflow_pending) return now_ms - c->overflowed.queued_ms;
    return c->count ? now_ms - c->queue[c->head].queued_ms : 0;
}

size_t ld_radar_control_execute(struct ld_radar_control *c, ld_control_i2c_fn i2c, void *i2c_context,
                                ld_control_reinit_fn reinit, void *reinit_context,
                                uint8_t *reply, size_t capacity)
{
    struct ld_control_command *cmd = &c->current;
    unsigned n, values;
    int err = 0, finished = 1;
    if (!ld_radar_control_pending(c) || !reply || capacity < LD_CONTROL_REPLY_MAX) return 0;
    if (!c->has_current) {
        if (c->overflow_pending) {
            *cmd = c->overflowed;
            c->overflow_pending = 0;
        } else {
            *cmd = c->queue[c->head];
            c->head = (c->head + 1) % LD_CONTROL_QUEUE;
            --c->count;
        }
        c->has_current = 1;
        c->done = 0;
        c->error = 0;
    }
    if (cmd->status == LD_CONTROL_OK && cmd->op == LD_CONTROL_READ) {
        uint8_t tx = (uint8_t)(cmd->reg + c->done), rx[2];
        err = i2c ? i2c(i2c_context, &tx, 1, rx, 2) : -1;
        if (err) {
            cmd->status = LD_CONTROL_BUS_ERROR;
        } else {
            c->values[c->done++] = (uint16_t)((rx[0] << 8) | rx[1]); /* Radar is big-endian. */
            finished = c->done == cmd->count;
        }
    } else if (cmd->status == LD_CONTROL_OK && cmd->op == LD_CONTROL_WRITE) {
        uint8_t tx[3];
        tx[0] = cmd->reg;
        tx[1] = (uint8_t)(cmd->value >> 8);
        tx[2] = (uint8_t)cmd->value;
        /* A NACK may still have latched part of the write: settings are unknown either way. */
        ++c->generation;
        err = i2c ? i2c(i2c_context, tx, 3, NULL, 0) : -1;
        if (err) cmd->status = LD_CONTROL_BUS_ERROR;
        c->values[0] = cmd->value;
        c->done = 1;
    } else if (cmd->status == LD_CONTROL_OK && cmd->op == LD_CONTROL_REINIT) {
        ++c->generation;
        err = reinit ? reinit(reinit_context) : -1;
        if (err) cmd->status = LD_CONTROL_REINIT_FAILED;
    }
    if (err) c->error = (int16_t)err;
    if (!finished) return 0;
    c->has_current = 0;
    ++c->executed;
    values = c->done;
    reply[0] = (uint8_t)cmd->tag;
    reply[1] = (uint8_t)(cmd->tag >> 8);
    reply[2] = (uint8_t)(cmd->tag >> 16);
    reply[3] = (uint8_t)(cmd->tag >> 24);
    reply[4] = cmd->op;
    reply[5] = cmd->status;
    reply[6] = cmd->reg;
    reply[7] = (uint8_t)values;
    le16_put(reply + 8, c->generation);
    le16_put(reply + 10, (uint16_t)c->error);
    for (n = 0; n < values; ++n) le16_put(reply + 12 + 2 * n, c->values[n]);
    return 12u + 2u * values;
}
