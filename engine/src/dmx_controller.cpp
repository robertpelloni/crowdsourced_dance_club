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
    ftdi = ftdi_new();
    if (ftdi == nullptr) {
        std::cerr << "[DMX] ftdi_new failed" << std::endl;
        return false;
    }

    // Attempt to open Enttec USB DMX Pro (VID 0x0403, PID 0x6001)
    if (ftdi_usb_open(ftdi, 0x0403, 0x6001) < 0) {
        std::cerr << "[DMX] Unable to open FTDI device: " << ftdi->error_str << std::endl;
        std::cerr << "[DMX] Continuing in mock mode..." << std::endl;
        // Proceeding in mock mode for testing if device isn't present
    } else {
        // Configure FTDI for DMX (250000 baud, 8 data bits, 2 stop bits, no parity)
        ftdi_set_baudrate(ftdi, 250000);
        ftdi_set_line_property(ftdi, BITS_8, STOP_BIT_2, NONE);
        is_initialized = true;
        std::cout << "[DMX] Hardware initialized successfully." << std::endl;
    }

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
            ftdi_usb_close(ftdi);
            ftdi_free(ftdi);
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

    std::cout << "[DMX] Triggering sequence: " << sequence << " (Intensity: " << intensity << ") for " << duration_ms << "ms" << std::endl;
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
    if (!is_initialized) return;

    std::vector<unsigned char> packet;
    // Enttec DMX Pro Protocol
    packet.push_back(0x7E); // Start of message
    packet.push_back(6);    // Send DMX Packet Label
    packet.push_back(dmx_data.size() + 1); // Length LSB
    packet.push_back((dmx_data.size() + 1) >> 8); // Length MSB
    packet.push_back(0); // Start code

    {
        std::lock_guard<std::mutex> lock(data_mutex);
        packet.insert(packet.end(), dmx_data.begin(), dmx_data.end());
    }

    packet.push_back(0xE7); // End of message

    ftdi_write_data(ftdi, packet.data(), packet.size());
}
