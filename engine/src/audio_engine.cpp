#include "audio_engine.h"
#include <iostream>
#include <cmath>

AudioEngine::AudioEngine() : stream(nullptr), running(false), current_bpm(145.0), playback_pos(0.0), next_track_ready(false) {}

AudioEngine::~AudioEngine() {
    stop();
}

bool AudioEngine::initialize() {
    PaError err = Pa_Initialize();
    if (err != paNoError) return false;

    err = Pa_OpenDefaultStream(&stream,
                                0,          /* no input channels */
                                2,          /* stereo output */
                                paFloat32,  /* 32 bit floating point output */
                                44100,      /* sample rate */
                                256,        /* frames per buffer */
                                audio_callback,
                                this);

    if (err != paNoError) return false;
    return true;
}

void AudioEngine::start() {
    if (stream) {
        Pa_StartStream(stream);
        running = true;
        std::cout << "[AUDIO] Engine started (Mock Playback)" << std::endl;
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

void AudioEngine::handle_track_sync(const json& data) {
    next_track_id = data["track_id"];
    double bpm = data["bpm"];
    std::cout << "[AUDIO] Syncing next track: " << next_track_id << " at " << bpm << " BPM" << std::endl;
    next_track_ready = true;
}

int AudioEngine::audio_callback(const void *inputBuffer, void *outputBuffer,
                               unsigned long framesPerBuffer,
                               const PaStreamCallbackTimeInfo* timeInfo,
                               PaStreamCallbackFlags statusFlags,
                               void *userData) {
    AudioEngine* self = (AudioEngine*)userData;
    float *out = (float*)outputBuffer;

    for (unsigned int i = 0; i < framesPerBuffer; i++) {
        // Mock: Just play silence for now, or a very quiet heartbeat
        *out++ = 0.0f; // Left
        *out++ = 0.0f; // Right
    }

    return paContinue;
}
