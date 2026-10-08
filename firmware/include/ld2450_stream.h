#ifndef LD2450_STREAM_H
#define LD2450_STREAM_H
#include <stddef.h>
#include <stdint.h>

/* Complex samples per radar DS RAW record (radar register 0x04 bits 10:8).
 * The stock profile uses 512; builds may select 256 or 128 with a matching
 * radar profile. Records are header(4) + 4*pairs I/Q bytes + trailer(4). */
#ifndef LD_RADAR_PAIRS
#define LD_RADAR_PAIRS 512u
#endif
#if LD_RADAR_PAIRS != 512 && LD_RADAR_PAIRS != 256 && LD_RADAR_PAIRS != 128
#error Unsupported radar record size
#endif
#define LD_STREAM_IQ_BYTES (4u * LD_RADAR_PAIRS)
#define LD_STREAM_RECORD_BYTES (LD_STREAM_IQ_BYTES + 8u)
#define LD_STREAM_VALUES (2u * LD_RADAR_PAIRS)
#define LD_STREAM_BLOCKS (LD_STREAM_VALUES / 32u)
#ifndef LD_STREAM_CHIRPS
#define LD_STREAM_CHIRPS 64u
#endif
#if LD_STREAM_CHIRPS != 16 && LD_STREAM_CHIRPS != 64
#error Unsupported export window
#endif
#define LD_STREAM_PAYLOAD_MAX (LD_STREAM_IQ_BYTES + 9u)
/* Range-bin export (codec 2), selected by LD_STREAM_FFT_BINS = K. Each validated
 * record is converted to interleaved int32 I/Q, transformed in place by an
 * injected LD_RADAR_PAIRS-point complex FFT (unscaled, natural bin order, as the
 * BR23 engine computes it), and bins -K..K are exported:
 *   mode(2) | radar header(4) | radar trailer(4) | shift (u8) |
 *   bin 0 re, im (int32 LE) | bins -K..-1, 1..K: re, im (int16 LE, value >> shift)
 * shift is the smallest right shift that fits every non-DC kept bin in int16
 * (rounded half up, saturated). BEGIN declares codec version 2. */
#ifdef LD_STREAM_FFT_BINS
#if LD_STREAM_FFT_BINS < 1 || LD_STREAM_FFT_BINS >= LD_RADAR_PAIRS / 2
#error Unsupported range-bin count
#endif
#define LD_STREAM_BIN_PAYLOAD (18u + 8u * LD_STREAM_FFT_BINS)
typedef int (*ld_stream_transform_fn)(void *context, int32_t *data, unsigned points);
#endif
#define LD_STREAM_HEADER_BYTES 32u
#define LD_STREAM_MESSAGE_MAX (32u + LD_STREAM_PAYLOAD_MAX + 4u)

/* Single task owner. No allocation, hardware access, or blocking calls.
 * A USB adapter must COPY accepted bytes before returning their count;
 * zero means would-block, negative means disconnect/error. */
typedef int (*ld_stream_write_fn)(void *, const uint8_t *, size_t);
struct ld_stream_stats {
    uint32_t frames_completed, frames_rejected, frames_skipped;
    uint32_t invalid_records, queue_overflows, transport_errors;
    uint32_t raw_records, compressed_records, queue_peak;
};
struct ld_stream {
    uint8_t *queue;
    size_t capacity, head, used;
    uint8_t config_sha256[32];
#ifdef LD_STREAM_FFT_BINS
    int32_t work[2u * LD_RADAR_PAIRS];        /* interleaved I/Q, FFT in place */
    ld_stream_transform_fn transform;
    void *transform_context;
#else
    uint8_t previous[2][LD_STREAM_IQ_BYTES];
#endif
    uint8_t scratch[LD_STREAM_MESSAGE_MAX];
    uint32_t sequence, frame;
    uint16_t next_chirp[2];
    uint8_t active, pending_complete;
    /* Live radar register generation reported by BEGIN (formerly reserved 0). */
    uint16_t register_generation;
    struct ld_stream_stats stats;
};
uint32_t ld_stream_crc32(const uint8_t *data, size_t size);
/* Codec output: mode, original header, original trailer, then raw IQ or
 * previous-chirp zigzag residuals in 32-value, MSB-first packed blocks. */
size_t ld_stream_encode(const uint8_t record[LD_STREAM_RECORD_BYTES],
                        const uint8_t *previous_iq, uint8_t *out, size_t capacity);
int ld_stream_init(struct ld_stream *s, uint8_t *queue, size_t capacity,
                   const uint8_t config_sha256[32]);
#ifdef LD_STREAM_FFT_BINS
/* Required before the first frame in range-bin builds (after ld_stream_init). */
void ld_stream_set_transform(struct ld_stream *s, ld_stream_transform_fn fn, void *context);
/* Codec 2 payload for one validated record; 0 if the transform fails. */
size_t ld_stream_encode_bins(const uint8_t record[LD_STREAM_RECORD_BYTES], int32_t *work,
                             ld_stream_transform_fn fn, void *context,
                             uint8_t *out, size_t capacity);
#endif
/* Call once at an observed paired frame boundary. Returns 1 when selected,
 * 0 when intentionally skipped (backlog), -1 on API misuse. Frame IDs must
 * count observed radar frames, including skips; timestamp is local us. */
int ld_stream_begin(struct ld_stream *s, uint32_t frame, uint32_t timestamp_us);
/* Only complete, checksum-valid LD_RADAR_PAIRS-pair records, chirps 0..LD_STREAM_CHIRPS-1 per RX.
 * Any invalid/missing/reordered record rejects the entire active frame. */
int ld_stream_record(struct ld_stream *s, const uint8_t *record, size_t size,
                     uint32_t timestamp_us);
struct radar_record;
/* Acquisition-only fast path: decoded must be a VALID radar_record_decode
 * result for these exact, unchanged bytes. The caller retains sole ownership
 * until return. Skips only the redundant radar checksum pass, not wire CRCs. */
int ld_stream_record_validated(struct ld_stream *s,const uint8_t *record,size_t size,
                               const struct radar_record *decoded,uint32_t timestamp_us);
void ld_stream_abort(struct ld_stream *s, uint32_t reason, uint32_t timestamp_us);
/* Out-of-frame control REPLY (type 5). Only between frames: returns 0 while a
 * frame is active or the queue lacks space (retry later), 1 when enqueued.
 * A queued reply delays the next export: BEGIN still requires an empty queue. */
int ld_stream_control_reply(struct ld_stream *s, const uint8_t *payload, size_t size,
                            uint32_t timestamp_us);
/* One bounded write attempt, at most budget bytes (also bounded by queue wrap).
 * Call between acquisition work. This does not make a blocking adapter safe. */
int ld_stream_pump(struct ld_stream *s, ld_stream_write_fn write, void *context,
                   size_t budget);
#endif
