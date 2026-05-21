#include "audio_engine.h"
#include <libwebsockets.h>
#include <iostream>
#include <cmath>
#include <algorithm>
#include <chrono>

AudioEngine::AudioEngine() : stream(nullptr), running(false),
                             is_transitioning(false), transition_progress(0.0),
                             transition_duration_frames(44100.0 * 15.0),
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
        std::cout << "[AUDIO] Engine started (Real-time Stretch Enabled)" << std::endl;
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
    sf_readf_float(infile, buffer.data.data(), sfinfo.frames);

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

    std::lock_guard<std::mutex> lock(buffer_mutex);
    if (load_audio_file(path, next_buffer)) {
        next_buffer.track_id = id;
        next_buffer.native_bpm = bpm;
        update_tempo();
        st_next.clear();
    }
}

void AudioEngine::handle_master_control(const json& data) {
    if (data.contains("target_bpm")) {
        target_bpm = data["target_bpm"];
        update_tempo();
    }
}

void AudioEngine::send_playback_state(void* wsi_ptr) {
    struct lws *wsi = (struct lws *)wsi_ptr;
    if (!wsi) return;

    auto now = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();

    if (now - last_state_time_ms < 500) return;
    last_state_time_ms = now;

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

    // Fixed size temporary buffer for SoundTouch output
    static float stretched_current[4096];
    int samples_received_curr = 0;

    // 1. Feed SoundTouch current buffer if it needs more data
    if (self->current_buffer.loaded && self->current_buffer.position < self->current_buffer.frames) {
        if (self->st_current.numSamples() < framesPerBuffer) {
            int samples_to_feed = std::min((int)(self->current_buffer.frames - self->current_buffer.position), 512);
            self->st_current.putSamples(&self->current_buffer.data[self->current_buffer.position * 2], samples_to_feed);
            self->current_buffer.position += samples_to_feed;
        }
    }

    samples_received_curr = self->st_current.receiveSamples(stretched_current, framesPerBuffer);

    for (unsigned int i = 0; i < framesPerBuffer; i++) {
        if (i < (unsigned int)samples_received_curr) {
            *out++ = stretched_current[i * 2];
            *out++ = stretched_current[i * 2 + 1];
        } else {
            *out++ = 0.0f;
            *out++ = 0.0f;
        }
    }

    return paContinue;
}
