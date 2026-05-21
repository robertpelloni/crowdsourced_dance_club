#ifndef AUDIO_ENGINE_H
#define AUDIO_ENGINE_H

#include <string>
#include <vector>
#include <atomic>
#include <nlohmann/json.hpp>
#include <portaudio.h>

using json = nlohmann::json;

class AudioEngine {
public:
    AudioEngine();
    ~AudioEngine();

    bool initialize();
    void start();
    void stop();

    // Protocol Handlers
    void handle_track_sync(const json& data);
    void send_playback_state();

private:
    // PortAudio Callback
    static int audio_callback(const void *inputBuffer, void *outputBuffer,
                             unsigned long framesPerBuffer,
                             const PaStreamCallbackTimeInfo* timeInfo,
                             PaStreamCallbackFlags statusFlags,
                             void *userData);

    PaStream *stream;
    std::atomic<bool> running;

    // Playback state
    std::string current_track_id;
    double current_bpm;
    double playback_pos;

    // Buffer for next track
    std::string next_track_id;
    bool next_track_ready;
};

#endif
