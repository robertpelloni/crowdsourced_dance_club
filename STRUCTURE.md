# STRUCTURE.md

## Directory Layout

- `src/`: Conductor Server source code.
  - `main.py`: FastAPI application, WebSockets, "Vibe Check" logic, and Vibe Point gamification.
  - `init_db.py`: Database initialization script.
  - `static/`: Mobile-first PWA prototype and Admin Console.
- `engine/`: Real-Time Audio Engine (C++).
  - `src/main.cpp`: WebSocket client and PortAudio lifecycle.
  - `src/audio_engine.cpp`: Real-time SoundTouch processing and timestamp-based auto-transitions.
  - `include/audio_engine.h`: Engine headers and AudioBuffer structures.
- `mobile/`: Official React Native / Expo application.
  - `app/App.js`: Integrated UI for Dance (Haptic Sync), Browse, and Profile (Badges).
- `external/auto_dj_script/`: Git submodule for offline rendering.
- `tests/`: Pytest suite for Conductor logic.

## Data Flow
1. **User** (Mobile) sends request via **WebSocket**.
2. **Conductor** (Python) awards **Vibe Points**, updates `tracks.db`, and reorders queue.
3. **Conductor** broadcasts state to all clients.
4. **Conductor** sends `TRACK_SYNC` (including `transition_timestamp`) to **Audio Engine**.
5. **Audio Engine** (C++) monitors clock, time-stretches samples via **SoundTouch**, and crossfades exactly on time.
6. **Mobile App** pulses haptic motor on each beat based on the broadcasted BPM.
