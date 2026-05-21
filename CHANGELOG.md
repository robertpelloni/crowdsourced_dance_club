# CHANGELOG

## [0.2.2] - 2024-05-23
### Added
- Integrated **SoundTouch** library for real-time time-stretching in the C++ engine.
- Implemented **Master BPM Sync** protocol (`MASTER_CONTROL`).
- Implemented **Playback State Heartbeat** (500ms) from engine to Conductor.
- Automated tempo adjustment based on server-side target BPM.

## [0.2.0] - 2024-05-23
### Added
- **Major Milestone:** Initialized the C++ Real-Time Audio Engine (`cdc_engine`).
- Implemented high-priority audio callback loop using **PortAudio**.
- Implemented low-latency WebSocket client using **libwebsockets** and **nlohmann/json**.
- Integrated Conductor synchronization (`TRACK_SYNC`) into the C++ engine.
- Created C++ build system (Makefile).

## [0.1.9] - 2024-05-23
### Added
- Implemented **Voting Velocity** tracking and **Energy Peaks** in the Conductor.
- Implemented proactive **TRACK_SYNC** broadcasting (15s before transitions).
- Wired offline rendering to the actual `auto_dj_script` submodule core.
- Created `src/mock_engine.py` for protocol verification.
- Integrated automated energy trend shifting based on crowd engagement.

## [0.1.8] - 2024-05-23
### Added
- Created `LIBRARIES.md` with detailed dependency analysis.
- Fully implemented React Native mobile app with WebSocket sync and haptics in `mobile/app/App.js`.
- Mirroring of PWA functionality (Now Playing, Queue, Voting) in native UI.
- Version bump to 0.1.8 and synchronized all project references.

## [0.1.7] - 2024-05-23
### Added
- Created `AUDIO_ENGINE_PROTOCOL.md` to define JSON communication for C++ integration.
- Initialized `mobile/` directory with React Native / Expo scaffold.
- Comprehensive documentation overhaul (`VISION.md`, `MEMORY.md`, `STRUCTURE.md`, `IDEAS.md`).
- Synchronized all model instruction files (`CLAUDE.md`, `GEMINI.md`, etc.).

## [0.1.6] - 2024-05-22
### Added
- Mobile-first PWA prototype with bottom navigation.
- Hidden "Admin Mode" with 5-tap gesture activation.
- `Playback Simulation` with auto-transition logic.
- `/sync-qr` endpoint for venue onboarding.
- Intelligent merge of `auto_dj_script` feature branches (v5.5, v5.7, v5.8).

## [0.1.0] - [0.1.5]
- Initial Conductor Server setup.
- WebSocket integration.
- Harmonic Key and Vibe Fit algorithms.
- SQLite persistence.
