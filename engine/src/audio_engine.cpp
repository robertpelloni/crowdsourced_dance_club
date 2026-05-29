#include "audio_engine.h"
#include <iostream>
#include <cmath>
#include <algorithm>
#include <chrono>
#include <cstring>
#include <libwebsockets.h>

AudioEngine::AudioEngine() : stream(nullptr), sample_rate(44100), running(false),
                             is_transitioning(false), transition_progress(0.0),
                             transition_duration_frames(0), transition_timestamp(0),
                             is_intensifying(false), intensify_progress(0.0),
                             intensify_duration_frames(0), target_bpm(145.0),
                             last_state_time_ms(0) {
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

    // Auto-detect hardware sample rate
    const PaDeviceInfo* device_info = Pa_GetDeviceInfo(Pa_GetDefaultOutputDevice());
    if (device_info) {
        sample_rate = device_info->defaultSampleRate;
    }

    err = Pa_OpenDefaultStream(&stream, 0, 2, paFloat32, sample_rate, 256, audio_callback, this);
    if (err != paNoError) return false;

    return true;
}

void AudioEngine::start() {
    if (stream) Pa_StartStream(stream);
    running = true;
}

void AudioEngine::stop() {
    running = false;
    if (stream) {
        Pa_StopStream(stream);
        Pa_CloseStream(stream);
        stream = nullptr;
    }
    Pa_Terminate();
}

bool AudioEngine::load_audio_file(const std::string& path, AudioBuffer& buffer) {
    SF_INFO sfinfo;
    SNDFILE* infile = sf_open(path.c_str(), SFM_READ, &sfinfo);
    if (!infile) {
        std::cerr << "Failed to open: " << path << std::endl;
        return false;
    }

    buffer.data.resize(sfinfo.frames * sfinfo.channels);
    sf_count_t read_count = sf_readf_float(infile, buffer.data.data(), sfinfo.frames);
    (void)read_count; // Suppress unused variable warning

    buffer.frames = sfinfo.frames;
    buffer.channels = sfinfo.channels;
    buffer.samplerate = sfinfo.samplerate;
    buffer.position = 0;
    buffer.loaded = true;

    sf_close(infile);
    return true;
}

void AudioEngine::handle_track_sync(const json& data) {
    std::string tid = data["track_id"];
    std::string path = data["filepath"];
    double bpm = data["bpm"];
    double ts = data["transition_timestamp"];
    double dur = data["crossfade_duration"];

    AudioBuffer next;
    if (load_audio_file(path, next)) {
        std::lock_guard<std::mutex> lock(buffer_mutex);
        next.track_id = tid;
        next.native_bpm = bpm;
        next_buffer = std::move(next);
        transition_timestamp = ts;
        transition_duration_frames = dur * sample_rate;
        std::cout << "[ENGINE] Preloaded: " << tid << std::endl;
    }
}

void AudioEngine::handle_master_control(const json& data) {
    if (data.contains("target_bpm")) {
        target_bpm = data["target_bpm"];
    }
    if (data.contains("action")) {
        std::string action = data["action"];
        if (action == "DSP_INTENSIFY") {
            is_intensifying = true;
            intensify_progress = 0.0;
            intensify_duration_frames = data.value("duration", 10.0) * sample_rate;
        } else if (action == "SKIP_NOW") {
            std::lock_guard<std::mutex> lock(buffer_mutex);
            if (next_buffer.loaded) {
                current_buffer = std::move(next_buffer);
                current_buffer.position = 0;
                is_transitioning = false;
            }
        }
    }
}

void AudioEngine::send_playback_state(void* wsi) {
    auto now_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()
    ).count();

    if (now_ms - last_state_time_ms < 500) return;
    last_state_time_ms = now_ms;

    json payload = {
        {"type", "PLAYBACK_STATE"},
        {"current_track_id", current_buffer.track_id},
        {"position_seconds", (double)current_buffer.position / sample_rate}
    };

    std::string s = payload.dump();
    unsigned char* buf = new unsigned char[LWS_PRE + s.length()];
    memcpy(&buf[LWS_PRE], s.c_str(), s.length());
    lws_write((struct lws*)wsi, &buf[LWS_PRE], s.length(), LWS_WRITE_TEXT);
    delete[] buf;
}

int AudioEngine::audio_callback(const void *inputBuffer, void *outputBuffer,
                             unsigned long framesPerBuffer,
                             const PaStreamCallbackTimeInfo* timeInfo,
                             PaStreamCallbackFlags statusFlags,
                             void *userData) {
    AudioEngine* engine = (AudioEngine*)userData;
    float* out = (float*)outputBuffer;
    std::memset(out, 0, framesPerBuffer * 2 * sizeof(float));

    if (!engine->current_buffer.loaded) return paContinue;

    // Simple pass-through implementation for v2.2.0 stable shell
    // Real implementation would use engine->st_current.putSamples and receiveSamples
    for (unsigned int i = 0; i < framesPerBuffer; ++i) {
        if (engine->current_buffer.position < engine->current_buffer.frames) {
            float l = engine->current_buffer.data[engine->current_buffer.position * 2];
            float r = engine->current_buffer.data[engine->current_buffer.position * 2 + 1];

            if (engine->is_intensifying) {
                engine->hpf_l.set_cutoff(1000.0f, engine->sample_rate);
                engine->hpf_r.set_cutoff(1000.0f, engine->sample_rate);
                l = engine->hpf_l.process(l);
                r = engine->hpf_r.process(r);

                engine->intensify_progress = engine->intensify_progress + 1.0;
                if (engine->intensify_progress >= engine->intensify_duration_frames) {
                    engine->is_intensifying = false;
                }
            }

            *out++ = engine->comp_l.process(l);
            *out++ = engine->comp_r.process(r);
            engine->current_buffer.position++;
        } else {
            *out++ = 0.0f;
            *out++ = 0.0f;
        }
    }

    return paContinue;
}
