#include "key_logic.h"
#include <cassert>
#include <cstdio>

int main() {
    key::ReadyGate gate;
    gate.reset(0);
    assert(gate.sample(0, false) == key::ReadyGate::Waiting);
    assert(gate.sample(100, true) == key::ReadyGate::Waiting);
    assert(gate.sample(599, true) == key::ReadyGate::Waiting);
    assert(gate.sample(600, false) == key::ReadyGate::Waiting);
    assert(gate.sample(700, true) == key::ReadyGate::Waiting);
    assert(gate.sample(1199, true) == key::ReadyGate::Waiting);
    assert(gate.sample(1200, true) == key::ReadyGate::Ready);
    gate.reset(0);
    assert(gate.sample(key::ReadyTimeoutUs - 1, false) == key::ReadyGate::Waiting);
    assert(gate.sample(key::ReadyTimeoutUs, false) == key::ReadyGate::TimedOut);
    gate.reset(0xffffff00u);
    assert(gate.sample(0xffffff00u, true) == key::ReadyGate::Waiting);
    assert(gate.sample(0xf4u, true) == key::ReadyGate::Ready);
    gate.reset(0xffffff00u);
    assert(gate.sample(uint32_t(0xffffff00u + key::ReadyTimeoutUs), true) == key::ReadyGate::TimedOut);
    key::LowInterval a;
    assert(!a.sample(0, true));
    assert(!a.sample(499, true));
    assert(a.sample(500, true));
    assert(!a.sample(501, false));
    assert(!a.sample(600, true));
    assert(!a.sample(1099, true));
    assert(a.sample(1100, true));
    a.reset();
    assert(!a.sample(0xffffff00u, true));
    assert(!a.sample(0x000000f3u, true));
    assert(a.sample(0x000000f4u, true));
    for (unsigned n = 0; n < 1000; ++n) {
        // Short repeated lows never accumulate into an ACK.
        assert(!a.sample(n * 20, false));
        assert(!a.sample(n * 20 + 1, true));
        assert(!a.sample(n * 20 + 10, true));
    }
    puts("Startup settling/timeout and ACK threshold, broken intervals, timer wrap: passed");
}
