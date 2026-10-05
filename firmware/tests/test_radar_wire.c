#define _CRT_SECURE_NO_WARNINGS
#include "radar_wire.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(x) do { if (!(x)) { fprintf(stderr, "line %d: %s\n", __LINE__, #x); exit(1); } } while (0)
static uint8_t data[40000];
static size_t load(const char *dir, const char *name)
{
    char path[1024];
    FILE *f;
    size_t n;
    CHECK(snprintf(path, sizeof(path), "%s/%s", dir, name) > 0);
    f = fopen(path, "rb"); CHECK(f != NULL);
    n = fread(data, 1, sizeof(data), f); CHECK(!ferror(f));
    CHECK(feof(f)); fclose(f); return n;
}

int main(int argc, char **argv)
{
    struct radar_record r;
    int16_t i, q;
    size_t n, pair_count = 0;
    unsigned record;
    CHECK(argc == 2);
    n = load(argv[1], "steady-chirp0.bin");
    CHECK(n == 2056);
    CHECK(radar_record_decode(data, n, &r) == RADAR_RECORD_VALID);
    CHECK(r.rx_index == 1 && r.chirp == 0 && r.declared_pairs == 512);
    CHECK(r.packet_valid && r.checksum_checked && r.checksum_stored == 0x07e6);
    CHECK(radar_record_iq(&r, 0, &i, &q) == 0 && i == -2054 && q == 2913);
    CHECK(radar_record_iq(&r, 512, &i, &q) == -1);
    data[4] ^= 1;
    CHECK(radar_record_decode(data, n, &r) == RADAR_RECORD_BAD_CHECKSUM);
    CHECK(!r.packet_valid && r.checksum_checked);
    data[4] ^= 1; data[n - 1] ^= 1;
    CHECK(radar_record_decode(data, n, &r) == RADAR_RECORD_BAD_TRAILER);
    CHECK(!r.packet_valid && !r.checksum_checked);
    data[n - 1] ^= 1;
    CHECK(radar_record_decode(data, n - 8, &r) == RADAR_RECORD_INCOMPLETE);
    CHECK(!r.packet_valid && r.observed_pairs == 511);
    data[0] = 0xab;
    CHECK(radar_record_decode(data, n, &r) == RADAR_RECORD_BAD_HEADER);
    CHECK(r.iq == NULL);
    CHECK(radar_record_decode(NULL, 0, &r) == RADAR_RECORD_INCOMPLETE);
    CHECK(radar_record_decode(data, n, NULL) == RADAR_RECORD_BAD_HEADER);

    n = load(argv[1], "steady-chirp1.bin");
    CHECK(radar_record_decode(data, n, &r) == RADAR_RECORD_VALID);
    CHECK(r.chirp == 1 && r.checksum_stored == 0xd99d);

    n = load(argv[1], "boot.bin"); CHECK(n == 31908);
    for (record = 0; record < 31; ++record) {
        CHECK(radar_record_decode(data + 996u * record, 996, &r) == RADAR_RECORD_STARTUP_NO_TRAILER);
        CHECK(r.header == 0xaa600101 && r.declared_pairs == 256 && r.observed_pairs == 248);
        CHECK(!r.packet_valid && !r.checksum_checked);
        if (!record) {
            CHECK(radar_record_iq(&r, 0, &i, &q) == 0 && i == -32466 && q == 4686);
        }
        CHECK(radar_record_iq(&r, 247, &i, &q) == 0);
        CHECK(radar_record_iq(&r, 248, &i, &q) == -1);
        pair_count += r.observed_pairs;
    }
    CHECK(radar_record_decode(data + 31u * 996u, 1032, &r) == RADAR_RECORD_VALID);
    CHECK(r.observed_pairs == 256 && r.checksum_stored == 0xf1da);
    pair_count += r.observed_pairs;
    CHECK(pair_count == 7944);
    puts("Validated 34 captured records, all 7,944 boot pairs, and corruption/bounds handling.");
    return 0;
}
