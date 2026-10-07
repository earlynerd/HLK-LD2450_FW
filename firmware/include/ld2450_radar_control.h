#ifndef LD2450_RADAR_CONTROL_H
#define LD2450_RADAR_CONTROL_H
#include <stddef.h>
#include <stdint.h>

/* Live radar register access requested by the host. Portable: no SDK,
 * hardware or allocation. Single task owner; the transport hands received
 * bytes to ld_radar_control_feed from the main task, never from an ISR.
 *
 * Command (20 bytes, little-endian):
 *   0  "LDC1"
 *   4  op: 1 READ, 2 WRITE, 3 REINIT
 *   5  count: READ 1..LD_CONTROL_READ_MAX registers; WRITE 1; REINIT 0
 *   6  register (first register for READ)
 *   7  reserved 0
 *   8  value u16 (WRITE)
 *   10 reserved 0
 *   12 tag u32, echoed in the reply
 *   16 CRC-32 (IEEE, as LDF1) of bytes 0..15
 *
 * Reply payload (LDF1 type 5, little-endian):
 *   0  tag u32, 4 op, 5 status, 6 register, 7 count,
 *   8  register generation u16 after the command, 10 driver error i16,
 *   12 count values u16. READ: values read; WRITE: the value written.
 *
 * No register, value or range restriction is applied: this is a laboratory
 * control path. Every WRITE (successful or not) and REINIT advances the
 * register generation, which BEGIN reports so frames identify their settings. */
#define LD_CONTROL_COMMAND_BYTES 20u
#define LD_CONTROL_QUEUE 16u
#define LD_CONTROL_READ_MAX 32u
#define LD_CONTROL_REPLY_MAX (12u + 2u * LD_CONTROL_READ_MAX)

enum { LD_CONTROL_READ = 1, LD_CONTROL_WRITE = 2, LD_CONTROL_REINIT = 3 };
enum {
    LD_CONTROL_OK = 0,
    LD_CONTROL_BUS_ERROR = 1,
    LD_CONTROL_BAD_COMMAND = 2,
    LD_CONTROL_OVERFLOW = 3,
    LD_CONTROL_REINIT_FAILED = 4
};

struct ld_control_command {
    uint32_t tag, queued_ms;
    uint16_t value;
    uint8_t op, count, reg, status;
};
/* Register transaction to the radar: write tx, then optionally read rx with a
 * repeated start. Returns 0 or a negative driver error. */
typedef int (*ld_control_i2c_fn)(void *context, const uint8_t *tx, size_t tx_size,
                                 uint8_t *rx, size_t rx_size);
/* Stop acquisition, power-cycle the radar and re-apply the build profile. */
typedef int (*ld_control_reinit_fn)(void *context);

struct ld_radar_control {
    uint8_t input[LD_CONTROL_COMMAND_BYTES];
    size_t input_used;
    struct ld_control_command queue[LD_CONTROL_QUEUE];
    unsigned head, count;
    struct ld_control_command overflowed; /* Latest dropped command, answered first. */
    uint8_t overflow_pending;
    /* Command in progress: one bus transaction per execute call. */
    struct ld_control_command current;
    uint8_t has_current, done;
    int16_t error;
    uint16_t values[LD_CONTROL_READ_MAX];
    uint16_t generation;
    uint32_t received, executed, discarded_bytes, overflows;
};

void ld_radar_control_init(struct ld_radar_control *c);
/* Parse any number of bytes; resynchronizes on corrupt input. A full queue
 * still answers: the dropped command's reply reports LD_CONTROL_OVERFLOW. */
void ld_radar_control_feed(struct ld_radar_control *c, const uint8_t *data, size_t size,
                           uint32_t now_ms);
unsigned ld_radar_control_pending(const struct ld_radar_control *c);
/* Milliseconds the oldest pending command has waited (0 when none). */
uint32_t ld_radar_control_waiting_ms(const struct ld_radar_control *c, uint32_t now_ms);
/* Advance the oldest command by at most one bus transaction (one READ
 * register, the WRITE, or REINIT), so the caller can re-check its timing window
 * before every transaction: some radar registers take far longer to read than
 * others. Returns the reply payload length when the command completes, else 0
 * (also when nothing is pending or capacity < LD_CONTROL_REPLY_MAX).
 * No auto-increment is assumed: each READ register is its own transaction. */
size_t ld_radar_control_execute(struct ld_radar_control *c, ld_control_i2c_fn i2c, void *i2c_context,
                                ld_control_reinit_fn reinit, void *reinit_context,
                                uint8_t *reply, size_t capacity);
#endif
