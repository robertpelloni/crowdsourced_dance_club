#ifndef DMX_CONTROLLER_H
#define DMX_CONTROLLER_H

#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <mutex>
#include <ftdi.h>

class DmxController {
public:
    DmxController();
    ~DmxController();

    bool initialize();
    void stop();

    // Set a sequence for the next duration
    void trigger_sequence(const std::string& sequence, int intensity, int duration_ms);

private:
    void dmx_loop();
    void send_dmx_packet();

    struct ftdi_context *ftdi;
    bool is_initialized;

    std::atomic<bool> running;
    std::thread dmx_thread;

    std::mutex data_mutex;
    std::vector<unsigned char> dmx_data; // 512 channels

    std::string current_sequence;
    int current_intensity;
    long sequence_end_time_ms;
};

#endif
