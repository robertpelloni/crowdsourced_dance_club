# Project Structure & Submodules

## Project Overview
Crowdsourced Dance Club (CDC) is a 3-tier real-time audio ecosystem.

## Directory Layout

### Tier 1: Mobile Client (React Native)
- `mobile/`: Official audience interface.
  - `app/App.js`: Core mobile application logic using Expo. Handles queue visualization, transition voting, and haptic feedback.
  - `package.json`: Dependency management for the React Native app.

### Tier 2: AI Conductor (Python)
- `src/`: Central coordination logic.
  - `main.py`: FastAPI Conductor Server. Manages room state, calculates vibe scores, excitement levels, handles WebSockets, and runs the playback simulation loop.
  - `init_db.py`: SQLite database initialization script. Sets up `tracks.db` with schema and mock metadata.
  - `static/`: Web-based dashboard prototype and assets.
  - `mock_engine.py`: Standalone Python script to simulate audio engine WebSocket behavior for testing.

### Tier 3: Real-Time Audio Engine (C++)
- `engine/`: High-performance audio playback.
  - `src/`: Implementation files.
    - `audio_engine.cpp`: Core engine logic, PortAudio callback, SoundTouch integration, and dynamic DSP processing (Compressor, HPF).
    - `main.cpp`: Entry point, libwebsockets client setup, and signal handling.
  - `include/`: Header files.
    - `audio_engine.h`: Class definitions for `AudioEngine`, `AudioBuffer`, `Compressor`, and `HighPassFilter`.
  - `Makefile`: Build instructions for the C++ engine.

### Shared & Infrastructure
- `external/`: Submodules.
  - `auto_dj_script/`: Offline mixing and mastering engine.
- `tests/`: Project unit and integration tests.
- `tracks.db`: SQLite database for persistent track and user metadata.
- `VERSION.md`: Central project version tracking.
- `AUDIO_ENGINE_PROTOCOL.md`: WebSocket JSON specification for Conductor-Engine communication.
- `LIBRARIES.md`: Documentation of all major project dependencies and rationales.

## Submodule Details

### Auto DJ Script
- **URL:** https://github.com/robertpelloni/auto_dj_script
- **Location:** `external/auto_dj_script`
- **Role:** High-fidelity offline rendering of session highlights or master sets.
- **Key Technologies:** Librosa, NumPy, SciPy, EBU R128 Normalization.
