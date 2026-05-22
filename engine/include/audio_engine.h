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

// Simple One-pole High-Pass Filter for real-time sweeps
struct HighPassFilter {
    float last_in;
    float last_out;
    float alpha;

    HighPassFilter() : last_in(0), last_out(0), alpha(0) {}

    void set_cutoff(float cutoff, float sample_rate) {
        float rc = 1.0f / (2.0f * M_PI * cutoff);
        float dt = 1.0f / sample_rate;
        alpha = rc / (rc + dt);
    }

    float process(float in) {
        float out = alpha * (last_out + in - last_in);
        last_in = in;
        last_out = out;
        return out;
    }
};

struct Compressor {
    float threshold;
    float ratio;
    float attack;
    float release;
    float envelope;

    Compressor() : threshold(0.5f), ratio(4.0f), attack(0.01f), release(0.1f), envelope(0.0f) {}

    float process(float in) {
        float abs_in = std::abs(in);
        float target = (abs_in > envelope) ? attack : release;
        envelope = envelope + target * (abs_in - envelope);

        if (envelope > threshold) {
            float desired_gain = threshold + (envelope - threshold) / ratio;
            return in * (desired_gain / envelope);
        }
        return in;
    }
};

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

    AudioBuffer(AudioBuffer&& other) noexcept {
        *this = std::move(other);
    }

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
    std::vector<AudioBuffer> preloaded_buffers;
    std::mutex buffer_mutex;

    soundtouch::SoundTouch st_current;
    soundtouch::SoundTouch st_next;

    std::atomic<bool> is_transitioning;
    std::atomic<double> transition_progress;
    double transition_duration_frames;
    std::atomic<double> transition_timestamp;
    std::string transition_archetype;

    std::atomic<bool> is_intensifying;
    std::atomic<double> intensify_progress;
    double intensify_duration_frames;

    HighPassFilter hpf_l;
    HighPassFilter hpf_r;

    std::atomic<double> excitement_level;

    Compressor comp_l;
    Compressor comp_r;

    std::atomic<double> target_bpm;

    uint64_t last_state_time_ms;
};

#endif
