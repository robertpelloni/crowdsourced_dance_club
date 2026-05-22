#include "audio_engine.h"
#include <libwebsockets.h>
#include <iostream>
#include <cmath>
#include <algorithm>
#include <chrono>

AudioEngine::AudioEngine() : stream(nullptr), running(false),
                             is_transitioning(false), transition_progress(0.0),
                             transition_duration_frames(44100.0 * 15.0),
                             transition_timestamp(0.0),
                             is_intensifying(false), intensify_progress(0.0),
                             intensify_duration_frames(44100.0 * 10.0),
                             excitement_level(0.5),
                             target_bpm(145.0), last_state_time_ms(0) {

    st_current.setSampleRate(44100);
    st_current.setChannels(2);

    st_next.setSampleRate(44100);
    st_next.setChannels(2);

    hpf_l.set_cutoff(20.0f, 44100.0f);
    hpf_r.set_cutoff(20.0f, 44100.0f);
}

AudioEngine::~AudioEngine() {
    stop();
}

bool AudioEngine::initialize() {
    PaError err = Pa_Initialize();
    if (err != paNoError) return false;

    err = Pa_OpenDefaultStream(&stream, 0, 2, paFloat32, 44100, 256, audio_callback, this);
    if (err != paNoError) return false;
    return true;
}

void AudioEngine::start() {
    if (stream) {
        Pa_StartStream(stream);
        running = true;
        std::cout << "[AUDIO] Engine started" << std::endl;
    }
}

void AudioEngine::stop() {
    if (stream) {
        Pa_StopStream(stream);
        Pa_CloseStream(stream);
        stream = nullptr;
    }
    Pa_Terminate();
    running = false;
}

bool AudioEngine::load_audio_file(const std::string& path, AudioBuffer& buffer) {
    SF_INFO sfinfo;
    SNDFILE* infile = sf_open(path.c_str(), SFM_READ, &sfinfo);
    if (!infile) {
        std::cerr << "[AUDIO] Failed to open file: " << path << std::endl;
        return false;
    }

    buffer.data.resize(sfinfo.frames * sfinfo.channels);
    sf_count_t read_count = sf_readf_float(infile, buffer.data.data(), sfinfo.frames);

    buffer.frames = sfinfo.frames;
    buffer.channels = sfinfo.channels;
    buffer.samplerate = sfinfo.samplerate;
    buffer.position = 0;
    buffer.loaded = true;

    sf_close(infile);
    std::cout << "[AUDIO] Loaded " << path << " (" << sfinfo.frames << " frames)" << std::endl;
    return true;
}

void AudioEngine::update_tempo() {
    if (current_buffer.loaded) {
        double tempo = target_bpm / current_buffer.native_bpm;
        st_current.setTempo(tempo);
    }
    if (next_buffer.loaded) {
        double tempo = target_bpm / next_buffer.native_bpm;
        st_next.setTempo(tempo);
    }
}

void AudioEngine::handle_track_sync(const json& data) {
    std::string path = data["filepath"];
    std::string id = data["track_id"];
    double bpm = data["bpm"];
    double timestamp = data["transition_timestamp"];
    std::string archetype = data.value("archetype", "classic");

    // 1. Perform Disk I/O outside of the mutex lock to avoid blocking the audio thread
    AudioBuffer temp_buffer;
    if (load_audio_file(path, temp_buffer)) {
        temp_buffer.track_id = id;
        temp_buffer.native_bpm = bpm;

        std::lock_guard<std::mutex> lock(buffer_mutex);

        // 2. Safely swap the new buffer into the engine state
        if (next_buffer.loaded && next_buffer.track_id != id) {
            preloaded_buffers.push_back(std::move(next_buffer));
        }

        next_buffer = std::move(temp_buffer);
        transition_timestamp = timestamp;
        transition_archetype = archetype;

        update_tempo();
        st_next.clear();
        std::cout << "[AUDIO] Prepared next track: " << id << std::endl;
    }
}

void AudioEngine::handle_master_control(const json& data) {
    if (data.contains("target_bpm")) {
        target_bpm = data["target_bpm"];
        update_tempo();
    }
    if (data.contains("current_bpm")) {
        target_bpm = data["current_bpm"]; // Sync with Conductor's live ramp
        update_tempo();
    }
    if (data.contains("excitement")) {
        excitement_level = data["excitement"];
    }
    if (data.contains("action") && data["action"] == "SKIP_NOW") {
        if (next_buffer.loaded) {
            is_transitioning = true;
            transition_progress = 0.0;
            transition_duration_frames = 44100.0 * 2.0;
            std::cout << "[AUDIO] >>> MANUAL SKIP INITIATED <<<" << std::endl;
        }
    }
    if (data.contains("action") && data["action"] == "DSP_INTENSIFY") {
        is_intensifying = true;
        intensify_progress = 0.0;
        double duration = data.value("duration", 10.0);
        intensify_duration_frames = 44100.0 * duration;
        std::cout << "[AUDIO] >>> DSP INTENSIFY: HPF SWEEP START <<<" << std::endl;
    }
}

void AudioEngine::send_playback_state(void* wsi_ptr) {
    struct lws *wsi = (struct lws *)wsi_ptr;
    if (!wsi) return;

    auto now_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();

    if (now_ms - last_state_time_ms < 500) return;
    last_state_time_ms = now_ms;

    json payload = {
        {"type", "PLAYBACK_STATE"},
        {"data", {
            {"current_track_id", current_buffer.track_id},
            {"playback_position_seconds", (double)current_buffer.position / 44100.0},
            {"current_bpm", (double)target_bpm},
            {"is_transitioning", (bool)is_transitioning}
        }}
    };

    std::string s = payload.dump();
    unsigned char *buf = (unsigned char*)malloc(LWS_PRE + s.length());
    memcpy(&buf[LWS_PRE], s.c_str(), s.length());
    lws_write(wsi, &buf[LWS_PRE], s.length(), LWS_WRITE_TEXT);
    free(buf);
}

int AudioEngine::audio_callback(const void *inputBuffer, void *outputBuffer,
                               unsigned long framesPerBuffer,
                               const PaStreamCallbackTimeInfo* timeInfo,
                               PaStreamCallbackFlags statusFlags,
                               void *userData) {
    AudioEngine* self = (AudioEngine*)userData;
    float *out = (float*)outputBuffer;

    auto now_s = (double)std::chrono::duration_cast<std::chrono::microseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count() / 1000000.0;

    if (!self->is_transitioning && self->next_buffer.loaded && self->transition_timestamp > 0 && now_s >= self->transition_timestamp) {
        self->is_transitioning = true;
        self->transition_progress = 0.0;
    }

    static float stretched_curr[4096];
    static float stretched_next[4096];
    int samples_received_curr = 0;
    int samples_received_next = 0;

    if (self->current_buffer.loaded && self->current_buffer.position < self->current_buffer.frames) {
        if (self->st_current.numSamples() < framesPerBuffer) {
            int samples_to_feed = std::min((int)(self->current_buffer.frames - self->current_buffer.position), 512);
            self->st_current.putSamples(&self->current_buffer.data[self->current_buffer.position * 2], samples_to_feed);
            self->current_buffer.position += samples_to_feed;
        }
    }
    samples_received_curr = self->st_current.receiveSamples(stretched_curr, framesPerBuffer);

    if (self->is_transitioning && self->next_buffer.loaded && self->next_buffer.position < self->next_buffer.frames) {
        if (self->st_next.numSamples() < framesPerBuffer) {
            int samples_to_feed = std::min((int)(self->next_buffer.frames - self->next_buffer.position), 512);
            self->st_next.putSamples(&self->next_buffer.data[self->next_buffer.position * 2], samples_to_feed);
            self->next_buffer.position += samples_to_feed;
        }
        samples_received_next = self->st_next.receiveSamples(stretched_next, framesPerBuffer);
    }

    for (unsigned int i = 0; i < framesPerBuffer; i++) {
        float left = 0.0f;
        float right = 0.0f;

        double gain_next = self->is_transitioning ? self->transition_progress.load() : 0.0;
        double gain_curr = 1.0 - gain_next;

        float samples_curr_l = (i < (unsigned int)samples_received_curr) ? stretched_curr[i * 2] : 0.0f;
        float samples_curr_r = (i < (unsigned int)samples_received_curr) ? stretched_curr[i * 2 + 1] : 0.0f;
        float samples_next_l = (self->is_transitioning && i < (unsigned int)samples_received_next) ? stretched_next[i * 2] : 0.0f;
        float samples_next_r = (self->is_transitioning && i < (unsigned int)samples_received_next) ? stretched_next[i * 2 + 1] : 0.0f;

        if (self->is_transitioning && self->transition_archetype == "hpf_sweep") {
            // Apply automated HPF sweep during transition
            float cutoff = 20.0f + 2000.0f * (1.0f - std::abs(2.0f * (float)gain_next - 1.0f));
            self->hpf_l.set_cutoff(cutoff, 44100.0f);
            self->hpf_r.set_cutoff(cutoff, 44100.0f);

            samples_curr_l = self->hpf_l.process(samples_curr_l);
            samples_curr_r = self->hpf_r.process(samples_curr_r);
        }

        left = (samples_curr_l * gain_curr) + (samples_next_l * gain_next);
        right = (samples_curr_r * gain_curr) + (samples_next_r * gain_next);

        // Apply HPF Sweep
        if (self->is_intensifying) {
            float phase = self->intensify_progress;
            float exc = (float)self->excitement_level.load();

            // Sweep range based on excitement (max 3000Hz)
            float max_cutoff = 1000.0f + 2000.0f * exc;
            float cutoff = 20.0f + (max_cutoff - 20.0f) * (1.0f - std::abs(2.0f * phase - 1.0f));

            self->hpf_l.set_cutoff(cutoff, 44100.0f);
            self->hpf_r.set_cutoff(cutoff, 44100.0f);

            left = self->hpf_l.process(left);
            right = self->hpf_r.process(right);

            // Dynamically scale compression based on excitement
            // Excitement 0.0 -> Threshold 0.5, Ratio 4.0
            // Excitement 1.0 -> Threshold 0.2, Ratio 12.0
            float target_threshold = 0.5f - (0.3f * exc);
            float target_ratio = 4.0f + (8.0f * exc);

            self->comp_l.threshold = target_threshold;
            self->comp_l.ratio = target_ratio;
            self->comp_r.threshold = target_threshold;
            self->comp_r.ratio = target_ratio;

            self->intensify_progress = self->intensify_progress + (1.0 / self->intensify_duration_frames);
            if (self->intensify_progress >= 1.0) {
                self->is_intensifying = false;
                self->hpf_l.set_cutoff(20.0f, 44100.0f);
                self->hpf_r.set_cutoff(20.0f, 44100.0f);

                // Restore standard compression
                self->comp_l.threshold = 0.5f;
                self->comp_l.ratio = 4.0f;
                self->comp_r.threshold = 0.5f;
                self->comp_r.ratio = 4.0f;
            }
        }

        // Apply Dynamic Range Compression
        left = self->comp_l.process(left);
        right = self->comp_r.process(right);

        // 4. Peak Limiting (Simple Soft Clipper)
        auto soft_clip = [](float x) {
            if (x > 1.0f) return 1.0f;
            if (x < -1.0f) return -1.0f;
            return x;
        };

        *out++ = soft_clip(left);
        *out++ = soft_clip(right);

        if (self->is_transitioning) {
            self->transition_progress = self->transition_progress + (1.0 / self->transition_duration_frames);
        }
    }

    // 5. Finalize transition outside of the sample loop to ensure data consistency
    if (self->is_transitioning && self->transition_progress >= 1.0) {
        self->is_transitioning = false;
        self->transition_timestamp = 0;

        // Lock only for the duration of the pointer/buffer swap
        if (self->buffer_mutex.try_lock()) {
            self->current_buffer = std::move(self->next_buffer);
            self->next_buffer.loaded = false;
            self->buffer_mutex.unlock();

            self->st_current.clear();
            self->transition_duration_frames = 44100.0 * 15.0;
            std::cout << "[AUDIO] Transition complete" << std::endl;
        }
    }

    return paContinue;
}
