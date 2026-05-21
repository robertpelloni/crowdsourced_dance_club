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
                             target_bpm(145.0), last_state_time_ms(0) {

    st_current.setSampleRate(44100);
    st_current.setChannels(2);

    st_next.setSampleRate(44100);
    st_next.setChannels(2);
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

    std::lock_guard<std::mutex> lock(buffer_mutex);
    if (load_audio_file(path, next_buffer)) {
        next_buffer.track_id = id;
        next_buffer.native_bpm = bpm;
        transition_timestamp = timestamp;
        update_tempo();
        st_next.clear();
        std::cout << "[AUDIO] Prepared transition at " << timestamp << std::endl;
    }
}

void AudioEngine::handle_master_control(const json& data) {
    if (data.contains("target_bpm")) {
        target_bpm = data["target_bpm"];
        update_tempo();
    }
    if (data.contains("action") && data["action"] == "SKIP_NOW") {
        if (next_buffer.loaded) {
            is_transitioning = true;
            transition_progress = 0.0;
            // Shorten transition for manual skip: 2 seconds
            transition_duration_frames = 44100.0 * 2.0;
            std::cout << "[AUDIO] >>> MANUAL SKIP INITIATED <<<" << std::endl;
        }
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

    // Check for transition start
    if (!self->is_transitioning && self->next_buffer.loaded && self->transition_timestamp > 0 && now_s >= self->transition_timestamp) {
        self->is_transitioning = true;
        self->transition_progress = 0.0;
        std::cout << "[AUDIO] >>> TRIGGERING TRANSITION <<<" << std::endl;
    }

    static float stretched_curr[4096];
    static float stretched_next[4096];
    int samples_received_curr = 0;
    int samples_received_next = 0;

    // 1. Current Buffer Processing
    if (self->current_buffer.loaded && self->current_buffer.position < self->current_buffer.frames) {
        if (self->st_current.numSamples() < framesPerBuffer) {
            int samples_to_feed = std::min((int)(self->current_buffer.frames - self->current_buffer.position), 512);
            self->st_current.putSamples(&self->current_buffer.data[self->current_buffer.position * 2], samples_to_feed);
            self->current_buffer.position += samples_to_feed;
        }
    }
    samples_received_curr = self->st_current.receiveSamples(stretched_curr, framesPerBuffer);

    // 2. Next Buffer Processing (if transitioning)
    if (self->is_transitioning && self->next_buffer.loaded && self->next_buffer.position < self->next_buffer.frames) {
        if (self->st_next.numSamples() < framesPerBuffer) {
            int samples_to_feed = std::min((int)(self->next_buffer.frames - self->next_buffer.position), 512);
            self->st_next.putSamples(&self->next_buffer.data[self->next_buffer.position * 2], samples_to_feed);
            self->next_buffer.position += samples_to_feed;
        }
        samples_received_next = self->st_next.receiveSamples(stretched_next, framesPerBuffer);
    }

    // 3. Mix Output
    for (unsigned int i = 0; i < framesPerBuffer; i++) {
        float left = 0.0f;
        float right = 0.0f;

        double gain_next = self->is_transitioning ? self->transition_progress.load() : 0.0;
        double gain_curr = 1.0 - gain_next;

        if (i < (unsigned int)samples_received_curr) {
            left += stretched_curr[i * 2] * gain_curr;
            right += stretched_curr[i * 2 + 1] * gain_curr;
        }

        if (self->is_transitioning && i < (unsigned int)samples_received_next) {
            left += stretched_next[i * 2] * gain_next;
            right += stretched_next[i * 2 + 1] * gain_next;
        }

        *out++ = left;
        *out++ = right;

        if (self->is_transitioning) {
            self->transition_progress = self->transition_progress + (1.0 / self->transition_duration_frames);
            if (self->transition_progress >= 1.0) {
                self->is_transitioning = false;
                self->transition_timestamp = 0;
                std::lock_guard<std::mutex> lock(self->buffer_mutex);
                self->current_buffer = std::move(self->next_buffer);
                self->next_buffer.loaded = false;
                self->st_current.clear();
                // Reset duration for future transitions
                self->transition_duration_frames = 44100.0 * 15.0;
            }
        }
    }

    return paContinue;
}
