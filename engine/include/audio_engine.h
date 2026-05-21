#ifndef AUDIO_ENGINE_H
#define AUDIO_ENGINE_H

#include <string>
#include <vector>
#include <atomic>
#include <mutex>
#include <nlohmann/json.hpp>
#include <portaudio.h>
#include <sndfile.h>
#include <soundtouch/SoundTouch.h>

using json = nlohmann::json;

struct AudioBuffer {
    std::vector<float> data;
    sf_count_t frames;
    int channels;
    double samplerate;
    sf_count_t position;
    std::string track_id;
    double native_bpm;
    bool loaded;

    AudioBuffer() : frames(0), channels(0), samplerate(0), position(0), native_bpm(145.0), loaded(false) {}

    AudioBuffer& operator=(AudioBuffer&& other) noexcept {
        if (this != &other) {
            data = std::move(other.data);
            frames = other.frames;
            channels = other.channels;
            samplerate = other.samplerate;
            position = other.position;
            track_id = std::move(other.track_id);
            native_bpm = other.native_bpm;
            loaded = other.loaded;
            other.loaded = false;
        }
        return *this;
    }
};

class AudioEngine {
public:
    AudioEngine();
    ~AudioEngine();

    bool initialize();
    void start();
    void stop();

    // Protocol Handlers
    void handle_track_sync(const json& data);
    void handle_master_control(const json& data);
    void send_playback_state(void* wsi);

private:
    static int audio_callback(const void *inputBuffer, void *outputBuffer,
                             unsigned long framesPerBuffer,
                             const PaStreamCallbackTimeInfo* timeInfo,
                             PaStreamCallbackFlags statusFlags,
                             void *userData);

    bool load_audio_file(const std::string& path, AudioBuffer& buffer);
    void update_tempo();

    PaStream *stream;
    std::atomic<bool> running;

    AudioBuffer current_buffer;
    AudioBuffer next_buffer;
    std::mutex buffer_mutex;

    soundtouch::SoundTouch st_current;
    soundtouch::SoundTouch st_next;

    std::atomic<bool> is_transitioning;
    std::atomic<double> transition_progress;
    double transition_duration_frames;

    std::atomic<double> target_bpm;

    // Internal timing
    uint64_t last_state_time_ms;
};

#endif
