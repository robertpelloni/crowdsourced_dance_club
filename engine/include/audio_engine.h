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
#include "dmx_controller.h"

using json = nlohmann::json;

// Simple One-pole High-Pass Filter for real-time sweeps
// Simple Dynamics Compressor for Master Bus
struct Compressor {
    float threshold_db;
    float ratio;
    float attack_ms;
    float release_ms;
    float makeup_gain_db;

    float envelope;

    Compressor() : threshold_db(-12.0f), ratio(4.0f), attack_ms(10.0f), release_ms(100.0f), makeup_gain_db(3.0f), envelope(0.0f) {}

    float process(float in, float sample_rate) {
        float in_db = 20.0f * std::log10(std::max(std::abs(in), 0.000001f));

        float over_db = in_db - threshold_db;
        if (over_db < 0.0f) over_db = 0.0f;

        float attack_coeff = std::exp(-1.0f / (attack_ms * 0.001f * sample_rate));
        float release_coeff = std::exp(-1.0f / (release_ms * 0.001f * sample_rate));

        if (over_db > envelope) {
            envelope = attack_coeff * envelope + (1.0f - attack_coeff) * over_db;
        } else {
            envelope = release_coeff * envelope + (1.0f - release_coeff) * over_db;
        }

        float gain_reduction_db = envelope * (1.0f - 1.0f / ratio);
        float out_db = in_db - gain_reduction_db + makeup_gain_db;

        float out_linear = std::pow(10.0f, out_db / 20.0f);
        return in >= 0 ? out_linear : -out_linear;
    }
};

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

struct AudioBuffer {
    std::vector<float> data;
    sf_count_t frames;
    int channels;
    double samplerate;
    sf_count_t position;
    std::string track_id;
    double native_bpm;
    bool loaded;

    std::vector<float> data_stems[4]; // 0: vocals, 1: drums, 2: bass, 3: other
    bool stems_loaded;

    AudioBuffer() : frames(0), channels(0), samplerate(0), position(0), native_bpm(145.0), loaded(false), stems_loaded(false) {}

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
            for (int i=0; i<4; ++i) {
                data_stems[i] = std::move(other.data_stems[i]);
            }
            stems_loaded = other.stems_loaded;
            other.loaded = false;
            other.stems_loaded = false;
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
    void handle_lighting_control(const json& data);
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
    AudioBuffer sample_buffer; // For one-shot samples like Virtual MC
    std::mutex buffer_mutex;

    soundtouch::SoundTouch st_current;
    soundtouch::SoundTouch st_next;

    std::atomic<bool> is_transitioning;
    std::atomic<double> transition_progress;
    double transition_duration_frames;
    std::atomic<double> transition_timestamp;

    std::atomic<bool> is_intensifying;
    std::atomic<double> intensify_progress;
    double intensify_duration_frames;

    // Stem Mixing volumes (0.0 to 1.0)
    std::atomic<float> vol_vocals;
    std::atomic<float> vol_drums;
    std::atomic<float> vol_bass;
    std::atomic<float> vol_other;

    HighPassFilter hpf_l;
    HighPassFilter hpf_r;

    Compressor master_comp_l;
    Compressor master_comp_r;

    std::atomic<double> target_bpm;

    uint64_t last_state_time_ms;

    DmxController dmx;
};

#endif
