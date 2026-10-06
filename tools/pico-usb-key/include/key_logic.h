#pragma once
#include <stdint.h>

namespace key {
constexpr uint16_t Word = 0x16ef;
// PIO drives only zero: direction 1 = low, direction 0 = externally pulled high.
constexpr uint32_t Directions = uint32_t(uint16_t(~Word)) << 16;
// The reported ACK is 1-2 ms; up to one 320 us word can elapse before
// observation starts. Qualify the remaining low interval for 500 us.
constexpr uint32_t AckUs = 500;
constexpr uint32_t ArmUs = 30000000;
constexpr uint32_t MappingUs = 500000;
constexpr uint32_t ReadyTimeoutUs = 3000000;
constexpr uint32_t ReadyHighUs = 500;

// Startup lows are allowed to settle but can never count as an ACK.
struct ReadyGate {
    enum Result { Waiting, Ready, TimedOut };
    uint32_t began = 0, highSince = 0;
    bool high = false;
    void reset(uint32_t now) { began = now; high = false; }
    Result sample(uint32_t now, bool bothHigh) {
        if (uint32_t(now - began) >= ReadyTimeoutUs) return TimedOut;
        if (!bothHigh) { high = false; return Waiting; }
        if (!high) { highSince = now; high = true; }
        return uint32_t(now - highSince) >= ReadyHighUs ? Ready : Waiting;
    }
};

struct LowInterval {
    uint32_t start = 0;
    bool active = false;
    void reset() { active = false; }
    bool sample(uint32_t now, bool bothLow) {
        if (!bothLow) { reset(); return false; }
        if (!active) { start = now; active = true; }
        return uint32_t(now - start) >= AckUs;
    }
};
}
