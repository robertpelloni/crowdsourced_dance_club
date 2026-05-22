# TODO List

## Immediate Tasks
- [x] Create initial documentation (`AGENTS.md`, `VISION.md`, etc.).
- [x] Add `auto_dj_script` as a submodule.
- [x] Set up Python environment and `requirements.txt`.
- [x] Implement `src/main.py` with FastAPI and WebSockets.
- [x] Implement `evaluate_track_fit` logic.
- [x] Set up SQLite database for `TRACK_CATALOG`.
- [x] Write unit tests for fit logic and API endpoints.
- [x] Implement Harmonic Key matching logic.
- [x] Implement user voting system for queue reordering.
- [x] Expand `tracks.db` with genre and filepath metadata.
- [x] Implement simulation loop with voting velocity and energy peaks.

## Phase 2: Mobile & Web Client
- [x] Build functional Web Prototype in `src/static/index.html`.
- [x] Implement Vibe Match indicator.
- [x] Implement Admin Dashboard (Skip, BPM, Trend).
- [x] Port web logic to React Native mobile application.
- [x] Implement QR code scanning for venue sync.
- [x] Synchronize mobile app version to 0.2.0.

## Phase 3: Real-Time Audio Engine
- [x] Initialize C++ Audio Engine (`engine/`).
- [x] Implement real-time SoundTouch time-stretching.
- [x] Implement automated HPF sweep logic for Energy Peaks.
- [x] Wire `TRACK_SYNC` and `MASTER_CONTROL` messages.
- [x] Implement multi-track pre-loading.
- [ ] Add support for FLAC/WAV streaming from Conductor.

## Bug Fixes
- [x] Fix database schema to include `filepath`.

## Refactoring
- [x] Move mock data to persistent storage with full metadata.
- [x] Implement FastAPI lifespan for background task safety.
