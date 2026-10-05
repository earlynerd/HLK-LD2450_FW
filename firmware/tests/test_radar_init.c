#include "ld2450_radar_init.h"
#include "ld2450_peripherals.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(x) do { if (!(x)) { fprintf(stderr, "line %d: %s\n", __LINE__, #x); exit(1); } } while (0)
static uint8_t transactions[80][4];
static size_t calls, fail_on;
static int fail_error;

/* Exercise the production stage writer at its bus boundary. The existing
 * peripheral suite separately tests STOP/NACK/deadline behavior of this API. */
int ld2450_i2c_transfer(uint8_t address, const uint8_t *tx, size_t tx_size,
                       uint8_t *rx, size_t rx_size, uint32_t timeout_ms)
{
    CHECK(calls < 80 && address == 0x20);
    CHECK(tx && tx_size == 3 && !rx && !rx_size && timeout_ms == 100);
    transactions[calls][0] = (uint8_t)(address << 1);
    memcpy(transactions[calls] + 1, tx, 3);
    ++calls;
    return calls == fail_on ? fail_error : LD2450_OK;
}

static void reset(void)
{
    calls = fail_on = 0;
    fail_error = LD2450_I2C_NACK;
    memset(transactions, 0, sizeof(transactions));
}

static void test_sequence(void)
{
    struct ld2450_radar_init_result result;
    const struct ld2450_radar_profile *p = &ld2450_build_radar_profile;
    size_t i;
    CHECK(p->count == 80 && p->name && p->table_sha256 && strlen(p->table_sha256) == 64);
    reset();
    CHECK(ld2450_radar_apply_init_stage(p, LD2450_RADAR_PRE_SPI, 100, &result) == LD2450_OK);
    CHECK(calls == 75 && result.completed == 75 && !result.failed_sequence);
    CHECK(transactions[0][1] == 0x40 && transactions[0][2] == 0x42 && transactions[0][3] == 0x07);
    CHECK(transactions[74][1] == 0x2f);
    /* Application integration must setup/arm SPI and establish bias/delays here. */
    CHECK(ld2450_radar_apply_init_stage(p, LD2450_RADAR_POST_SPI, 100, &result) == LD2450_OK);
    CHECK(calls == 80 && result.completed == 5 && !result.failed_sequence);
    CHECK(transactions[75][1] == 0x72 && transactions[76][1] == 0x67);
    CHECK(transactions[77][1] == 0x01 && transactions[78][1] == 0x41 && transactions[79][1] == 0x40);
    for (i = 0; i < 80; ++i) {
        CHECK(transactions[i][0] == 0x40 && transactions[i][1] == p->writes[i].reg);
        CHECK(transactions[i][2] == (uint8_t)(p->writes[i].value >> 8));
        CHECK(transactions[i][3] == (uint8_t)p->writes[i].value);
    }
}

static void test_failure(void)
{
    struct ld2450_radar_init_result result;
    const struct ld2450_radar_profile *p = &ld2450_build_radar_profile;
    reset(); fail_on = 5;
    CHECK(ld2450_radar_apply_init_stage(p, LD2450_RADAR_PRE_SPI, 100, &result) == LD2450_I2C_NACK);
    CHECK(calls == 5 && result.completed == 4 && result.failed_sequence == 5);
    reset(); fail_on = 2; fail_error = LD2450_TIMEOUT;
    CHECK(ld2450_radar_apply_init_stage(p, LD2450_RADAR_POST_SPI, 100, &result) == LD2450_TIMEOUT);
    CHECK(calls == 2 && result.completed == 1 && result.failed_sequence == 77);
}

static void test_validation(void)
{
    struct ld2450_radar_init_result result;
    struct ld2450_radar_profile p = ld2450_build_radar_profile;
    struct ld2450_radar_write writes[80];
    reset();
    CHECK(ld2450_radar_apply_init_stage(NULL, LD2450_RADAR_PRE_SPI, 100, &result) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_radar_apply_init_stage(&p, LD2450_RADAR_PRE_SPI, 100, NULL) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_radar_apply_init_stage(&p, (enum ld2450_radar_init_stage)2, 100, &result) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_radar_apply_init_stage(&p, LD2450_RADAR_PRE_SPI, 0, &result) == LD2450_BAD_ARGUMENT);
    CHECK(ld2450_radar_apply_init_stage(&p, LD2450_RADAR_PRE_SPI, 1001, &result) == LD2450_BAD_ARGUMENT);
    p.count = 79;
    CHECK(ld2450_radar_apply_init_stage(&p, LD2450_RADAR_PRE_SPI, 100, &result) == LD2450_BAD_ARGUMENT);
    p = ld2450_build_radar_profile;
    memcpy(writes, p.writes, sizeof(writes)); writes[79].reg = 0; p.writes = writes;
    CHECK(ld2450_radar_apply_init_stage(&p, LD2450_RADAR_PRE_SPI, 100, &result) == LD2450_BAD_ARGUMENT);
    CHECK(!calls && !result.completed && !result.failed_sequence);
}

int main(void)
{
    test_sequence(); test_failure(); test_validation();
    puts("Validated 75/5 write stages, wire byte order, fail-fast reporting, and invalid input rejection.");
    return 0;
}
