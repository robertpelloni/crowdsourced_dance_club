#include "dmx_controller.h"
#include <iostream>
#include <chrono>

using namespace std::chrono;

DmxController::DmxController() : ftdi(nullptr), is_initialized(false), running(false), current_intensity(0), sequence_end_time_ms(0) {
    dmx_data.resize(512, 0);
}

DmxController::~DmxController() {
    stop();
}

bool DmxController::initialize() {
    // Phase 5 Decoupling: We simulate initialization here but log that an external proxy should be used.
    std::cout << "[DMX] Note: Direct FTDI integration is deprecated per Phase 5 OLA Architecture." << std::endl;
    std::cout << "[DMX] Hardware initializing in proxy-simulation mode." << std::endl;

    running = true;
    dmx_thread = std::thread(&DmxController::dmx_loop, this);
    return true;
}

void DmxController::stop() {
    if (running) {
        running = false;
        if (dmx_thread.joinable()) {
            dmx_thread.join();
        }

        if (is_initialized && ftdi) {
            // ftdi_usb_close(ftdi);
            // ftdi_free(ftdi);
            ftdi = nullptr;
            is_initialized = false;
        }
    }
}

void DmxController::trigger_sequence(const std::string& sequence, int intensity, int duration_ms) {
    std::lock_guard<std::mutex> lock(data_mutex);
    current_sequence = sequence;
    current_intensity = intensity;

    auto now = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
    sequence_end_time_ms = now + duration_ms;

    std::cout << "[DMX] Triggering sequence via internal queue: " << sequence << " (Intensity: " << intensity << ") for " << duration_ms << "ms" << std::endl;
}

void DmxController::dmx_loop() {
    while (running) {
        auto now = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();

        {
            std::lock_guard<std::mutex> lock(data_mutex);

            // Basic sequences
            if (now <= sequence_end_time_ms) {
                if (current_sequence == "strobe_fast") {
                    // Toggle every 50ms
                    bool on = (now / 50) % 2 == 0;
                    dmx_data[0] = on ? current_intensity : 0; // Assuming Ch 1 is master/strobe
                } else if (current_sequence == "peak_flash") {
                    dmx_data[0] = current_intensity;
                } else {
                    dmx_data[0] = 0;
                }
            } else {
                // Idle state
                dmx_data[0] = 0;
                current_sequence = "";
            }
        }

        send_dmx_packet();

        // DMX typical refresh rate ~44Hz (22.7ms)
        std::this_thread::sleep_for(std::chrono::milliseconds(25));
    }
}

void DmxController::send_dmx_packet() {
    // In Phase 5, this method will be replaced entirely by a UDP socket dispatch
    // pointing to localhost:9090 where the OLA Proxy listens.

    // std::vector<unsigned char> packet;
    // packet.push_back(0x7E); // Start of message
    // ...
    // ftdi_write_data(ftdi, packet.data(), packet.size());
}
