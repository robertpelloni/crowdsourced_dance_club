# TODO List

## Phase 4: Polish, Scaling & Auth (Current)
- [x] Implement JWT-based user authentication.
- [x] Implement persistent user profiles in SQLite.
- [x] Refactor existing gamification (points, badges) to use DB.
- [x] Integrated Auth UI in Web and Mobile prototypes.
- [ ] Research: ML-driven vibe analysis models.
- [ ] Feature: FLAC/WAV binary streaming via WebSockets.
- [ ] UI: Real-time Waveform visualization.
- [ ] Infrastructure: Edge-deployment configuration for Audio Engine.

## Phase 3: Real-Time Audio Engine (Complete)
- [x] Initialize C++ Audio Engine (`engine/`).
- [x] Implement real-time SoundTouch time-stretching.
- [x] Implement automated HPF sweep logic for Energy Peaks.
- [x] Implement real-time Dynamic Range Compressor.
- [x] Wire `TRACK_SYNC` and `MASTER_CONTROL` messages.
- [x] Implement multi-track pre-loading.
- [x] Thread-safe buffer swapping (Disk I/O isolation).

## Phase 2: Mobile & Web Client (Complete)
- [x] Build functional Web Prototype in `src/static/index.html`.
- [x] Implement Vibe Match indicator.
- [x] Implement Admin Dashboard (Skip, BPM, Trend).
- [x] Port web logic to React Native mobile application.
- [x] Implement QR code scanning for venue sync.
- [x] Synchronize mobile app version to 0.2.x.
- [x] Implement smooth BPM ramping.
- [x] Implement dynamic QR generation.
- [x] Implement transition voting UI.
- [x] Implement "Vibe Streak" gamification.
- [x] Refine "Pulse Orb" into "Vibe Heatmap".

## Phase 1: Foundation (Complete)
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
