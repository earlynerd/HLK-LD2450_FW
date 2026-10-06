#include <Arduino.h>
#include "hardware/pio.h"
#include "hardware/clocks.h"
#include "hardware/gpio.h"
#include "key_logic.h"

static_assert(KEY_DP_PIN < 23 && KEY_DM_PIN < 23 && KEY_BUTTON_PIN < 23 && KEY_PULLUP_PIN < 23,
              "Use exposed GPIOs on the Pico/Pico W");
static_assert(KEY_DP_PIN != KEY_DM_PIN && KEY_DP_PIN != KEY_BUTTON_PIN &&
              KEY_DM_PIN != KEY_BUTTON_PIN, "Pins must be distinct");
static_assert(KEY_PULLUP_PIN != KEY_DP_PIN && KEY_PULLUP_PIN != KEY_DM_PIN &&
              KEY_PULLUP_PIN != KEY_BUTTON_PIN, "Pullup supply must have its own pin");

namespace {
PIO pio = pio0;
int sm = -1;
uint keyOffset, pulseOffset;
const uint32_t lines = (1u << KEY_DP_PIN) | (1u << KEY_DM_PIN);
// One mandatory side-set bit controls CLOCK DIRECTION, not output value.
// Output latches stay zero throughout; highs come from external pullups.
// Constant encodings keep these inspectable in the ELF (the SDK's encoding
// helpers are not constexpr). tests/check_waveform.py executes these bytes.
constexpr uint16_t keyCode[] = {
    0x80a0, // pull block          side 0: released while stalled
    0xe02f, // set x,15            side 0
    0x7981, // out pindirs,1       side 1 [9]: 10 us clock low
    0xa842, // nop                 side 0 [8]: 9 us clock high
    0x0042, // jmp x--,2           side 0: +1 us high
    0xe080, // set pindirs,0       side 0: release DATA
    0xc000, // irq 0               side 0: frame complete
};
const pio_program keyProgram = {keyCode, 7, -1, 0};
// Optional clock-calibration stimulus, NOT USB packets. 10 us low + 990 us high.
constexpr uint16_t pulseCode[] = {
    0xe981, // set pindirs,1 [9]: 10 us low
    0xe080, // set pindirs,0: release high, 1 us
    0xe03d, // set x,29: 1 us
    0xbe42, // nop [30]: 31 us
    0x0043, // jmp x--,3: 1 us, loop executes 30 times
    0xbb42, // nop [27]: 28 us; total high = 1+1+30*32+28 = 990 us
};
const pio_program pulseProgram = {pulseCode, 6, -1, 0};

enum class State { Idle, WaitingHigh, Sending, Ack, AwaitRelease, Pulsing, Error };
State state = State::Idle;
key::LowInterval low;
key::ReadyGate ready;
uint32_t started, releasedAt, stageStarted, frames, mappingStarted;
bool calibration = false, swapped = false;
bool pullups = false;

void setPullups(bool enabled) {
    gpio_put(KEY_PULLUP_PIN, enabled);
    pullups = enabled;
}

void setLed(bool on) {
    // Pico W LED goes through CYW43; do not repeat that transaction every poll.
    static int previous = -1;
    if (previous != int(on)) { digitalWrite(LED_BUILTIN, on); previous = on; }
}

void releaseLines() {
    if (sm >= 0) pio_sm_set_enabled(pio, sm, false);
    // Set SIO direction BEFORE routing back from PIO to avoid a driven glitch.
    gpio_set_dir_in_masked(lines);
    gpio_put_masked(lines, 0);
    const uint pins[] = {KEY_DP_PIN, KEY_DM_PIN};
    for (uint pin : pins) {
        gpio_set_function(pin, GPIO_FUNC_SIO);
        gpio_disable_pulls(pin);
    }
}

void stop(State next, const char *message) {
    releaseLines();
    setPullups(false);
    state = next;
    setLed(next == State::Ack);
    Serial.println(message);
}

void configureKey() {
    releaseLines();
    uint clockPin = swapped ? KEY_DM_PIN : KEY_DP_PIN;
    uint dataPin = swapped ? KEY_DP_PIN : KEY_DM_PIN;
    pio_sm_config c = pio_get_default_sm_config();
    sm_config_set_wrap(&c, keyOffset, keyOffset + 6);
    sm_config_set_out_pins(&c, dataPin, 1);
    sm_config_set_set_pins(&c, dataPin, 1);
    sm_config_set_sideset(&c, 1, false, true);
    sm_config_set_sideset_pins(&c, clockPin);
    sm_config_set_out_shift(&c, false, false, 32); // MSB first, manual PULL
    sm_config_set_clkdiv(&c, float(clock_get_hz(clk_sys)) / 1000000.0f);
    pio_sm_init(pio, sm, keyOffset, &c);
    pio_sm_set_pins_with_mask(pio, sm, 0, lines);
    pio_sm_set_pindirs_with_mask(pio, sm, 0, lines);
    pio_gpio_init(pio, clockPin);
    pio_gpio_init(pio, dataPin);
    pio_interrupt_clear(pio, 0);
    pio_sm_set_enabled(pio, sm, true);
}

bool sendWord() {
    pio_interrupt_clear(pio, 0);
    pio_sm_put(pio, sm, key::Directions);
    uint32_t start = micros();
    while (!pio_interrupt_get(pio, 0)) {
        if (uint32_t(micros() - start) > 2000) {
            stop(State::Error, "PIO timeout; pins released.");
            return false;
        }
    }
    ++frames;
    releasedAt = micros();
    low.reset();
    return true;
}

void begin(bool withCalibration) {
    if (sm < 0) { Serial.println("PIO unavailable; restart Pico."); return; }
    releaseLines();
    calibration = withCalibration;
    frames = 0;
    low.reset();
    Serial.printf("Enabling GP%d pullups; restore TARGET power now. Waiting up to 3 s for both lines high. %s\n",
                  KEY_PULLUP_PIN, calibration ? "Calibration enabled." : "Manual USB swap.");
    setPullups(true);
    ready.reset(micros());
    state = State::WaitingHigh;
}

void startPulses() {
    releaseLines();
    pio_sm_config c = pio_get_default_sm_config();
    sm_config_set_wrap(&c, pulseOffset, pulseOffset + 5);
    sm_config_set_set_pins(&c, KEY_DP_PIN, 1);
    sm_config_set_clkdiv(&c, float(clock_get_hz(clk_sys)) / 1000000.0f);
    pio_sm_init(pio, sm, pulseOffset, &c);
    pio_sm_set_pins_with_mask(pio, sm, 0, lines);
    pio_sm_set_pindirs_with_mask(pio, sm, 0, lines);
    pio_gpio_init(pio, KEY_DP_PIN);
    pio_sm_set_enabled(pio, sm, true);
    stageStarted = micros();
    state = State::Pulsing;
    Serial.println("ACK ended; generating 1 kHz calibration edges for 2 s. Host must remain disconnected.");
}

void service() {
    uint32_t now = micros();
    if (state == State::WaitingHigh) {
        auto result = ready.sample(now, (gpio_get_all() & lines) == lines);
        if (result == key::ReadyGate::TimedOut) {
            stop(State::Error, "Lines not both high within 3 s; pullups OFF. Check power/pullups/wiring.");
        } else if (result == key::ReadyGate::Ready) {
            configureKey();
            started = mappingStarted = micros();
            state = State::Sending;
            sendWord();
        }
    } else if (state == State::Sending) {
        if (uint32_t(now - started) >= key::ArmUs) {
            stop(State::Error, "No ACK within 30 s; pins released."); return;
        }
        if (uint32_t(now - releasedAt) < 3) return; // pullup settling
        bool bothLow = (gpio_get_all() & lines) == 0;
        if (low.sample(now, bothLow)) {
            releaseLines();
            if (calibration) {
                state = State::AwaitRelease;
                stageStarted = now;
                Serial.println("ACK-shaped low interval detected; waiting for D+ release.");
            } else {
                stop(State::Ack, "ACK-shaped low interval detected. SWAP TO PC USB NOW; pins released.");
            }
            return;
        }
        // Once a low candidate begins, leave BOTH lines released until it
        // either qualifies or breaks. Never count our own driven-low period.
        if (!low.active && uint32_t(now - releasedAt) >= 40) {
            if (uint32_t(now - mappingStarted) >= key::MappingUs) {
                swapped = !swapped;
                configureKey();
                mappingStarted = micros();
            }
            sendWord();
        }
    } else if (state == State::AwaitRelease) {
        if (gpio_get(KEY_DP_PIN)) startPulses();
        else if (uint32_t(now - stageStarted) > 100000)
            stop(State::Error, "D+ stayed low after ACK; pins released.");
    } else if (state == State::Pulsing && uint32_t(now - stageStarted) >= 2000000) {
        stop(State::Ack, "Calibration stimulus finished. SWAP TO PC USB NOW; pins released.");
    }
}

void help() {
    Serial.println("JieLi USB_KEY: g=arm+calibration, m=arm/manual swap only, x=stop, s=swap initial mapping, ?=status");
    Serial.println("No ACK: clock/data mappings alternate every 500 ms. Solid LED means swap, not verified USB enumeration.");
    Serial.printf("GP%d resistor supply=%s; GP10/11/12 default drive=12 mA. x before target power OFF; g when restoring power.\n",
                  KEY_PULLUP_PIN, pullups ? "ON" : "OFF");
    Serial.printf("GP%d=D+, GP%d=D-, optional GP%d button to GND. Clock=%s. State=%u frames=%lu lines=%u%u\n",
                  KEY_DP_PIN, KEY_DM_PIN, KEY_BUTTON_PIN, swapped ? "D-" : "D+",
                  unsigned(state), (unsigned long)frames, gpio_get(KEY_DP_PIN), gpio_get(KEY_DM_PIN));
}
}

void setup() {
    gpio_init(KEY_PULLUP_PIN); // output latch low before enabling output
    gpio_put(KEY_PULLUP_PIN, false);
    gpio_set_drive_strength(KEY_PULLUP_PIN, GPIO_DRIVE_STRENGTH_12MA);
    gpio_set_dir(KEY_PULLUP_PIN, GPIO_OUT);
    gpio_set_drive_strength(KEY_DP_PIN, GPIO_DRIVE_STRENGTH_12MA);
    gpio_set_drive_strength(KEY_DM_PIN, GPIO_DRIVE_STRENGTH_12MA);
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(KEY_BUTTON_PIN, INPUT_PULLUP);
    releaseLines();
    Serial.begin(115200); // never wait for a USB monitor to open
    sm = pio_claim_unused_sm(pio, false);
    if (sm < 0 || !pio_can_add_program(pio, &keyProgram)) {
        if (sm >= 0) { pio_sm_unclaim(pio, sm); sm = -1; }
        stop(State::Error, "PIO unavailable."); return;
    }
    keyOffset = pio_add_program(pio, &keyProgram);
    if (!pio_can_add_program(pio, &pulseProgram)) {
        pio_sm_unclaim(pio, sm); sm = -1;
        stop(State::Error, "PIO program space unavailable."); return;
    }
    pulseOffset = pio_add_program(pio, &pulseProgram);
    help();
}

void loop() {
    service();
    if (Serial.available()) {
        char c = Serial.read();
        if (c == 'x') stop(State::Idle, "Stopped; signal pins released, pullup supply OFF.");
        else if (c == '?' || c == 'h') help();
        else if (c == 's') {
            stop(State::Idle, "Stopped before changing mapping."); swapped = !swapped; help();
        } else if (c == 'g' || c == 'm') begin(c == 'g');
    }
    static bool lastButton = true;
    static uint32_t changed = 0;
    static bool rawLast = true;
    bool raw = digitalRead(KEY_BUTTON_PIN);
    if (raw != rawLast) { rawLast = raw; changed = millis(); }
    if (raw != lastButton && uint32_t(millis() - changed) >= 25) {
        lastButton = raw;
        if (!raw) {
            if (state == State::WaitingHigh || state == State::Sending || state == State::AwaitRelease || state == State::Pulsing)
                stop(State::Idle, "Stopped by button; pins released.");
            else begin(true);
        }
    }
    if (state != State::Ack) {
        uint32_t period = state == State::Error ? 100 : 250;
        setLed(state != State::Idle && ((millis() / period) & 1));
    }
}
