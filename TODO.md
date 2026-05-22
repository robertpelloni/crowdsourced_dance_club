# TODO List

## Immediate Tasks
- [x] Create initial documentation (`AGENTS.md`, `VISION.md`, etc.).
- [x] Add `auto_dj_script` as a submodule.
- [x] Implement `src/main.py` with FastAPI and WebSockets.
- [x] Implement `evaluate_track_fit` logic.
- [x] Write unit tests for fit logic and API endpoints.
- [x] Implement Harmonic Key matching logic.
- [x] Implement user voting system for queue reordering.
<<<<<<< HEAD
- [x] Develop Mobile-First PWA Prototype.
- [x] Implement Playback Simulation & Auto-Transitions.
- [x] Implement "Vibe-Aware" Weighted Ranking.
- [x] Implement Energy Ramping logic.
- [x] Implement Genre Compatibility Matrix.
- [x] Implement "DJ Control Panel" (Admin Mode).
- [x] Implement `/sync-qr` endpoint.
- [x] Design Real-Time Audio Engine Protocol.
- [x] Initialize Mobile App scaffold.

## Phase 3: Mobile Client (Native) (Completed)
- [x] Implement WebSocket client in React Native.
- [x] Mirror PWA functionality in Native UI.
- [x] Implement Haptic Feedback on transitions.

## Phase 4: Real-Time Audio Engine
- [x] Implement proactive `TRACK_SYNC` broadcasting.
- [x] Create `src/mock_engine.py` for testing.
- [x] Initialize C++ `engine/` repository.
- [x] Implement PortAudio callback and libwebsockets client.
- [x] Integrate SoundTouch for real-time time-stretching.
- [x] Implement Playback State heartbeat reporting.
- [x] Implement real-time SoundTouch sample processing.
- [x] Implement timestamp-based auto-transitions.
- [x] Implement haptic beat synchronization.
- [x] Implement Vibe Badge gamification.
- [x] Implement Mobile QR Sync scanner.
- [x] Refine Conductor highlight worker with temporary directories.
- [x] Implement Energy Derivative voting acceleration.
- [x] Implement real-time HPF sweeps in C++.
- [x] Implement audio soft-clipper in C++.
- [x] Implement animated Vibe Visualizer in mobile app.
- [ ] Refine SoundTouch buffer management (FIFO logic).

## Bug Fixes
- None identified.
=======
- [x] Expand `tracks.db` with genre and filepath metadata.
- [x] Implement simulation loop with voting velocity and energy peaks.

## Phase 2: Mobile & Web Client
- [x] Build functional Web Prototype in `src/static/index.html`.
- [x] Implement Vibe Match indicator.
- [x] Implement Admin Dashboard (Skip, BPM, Trend).
- [x] Port web logic to React Native mobile application.
- [x] Implement QR code scanning for venue sync.
- [x] Synchronize mobile app version to 0.2.0.
- [x] Implement smooth BPM ramping.
- [x] Implement dynamic QR generation.
- [x] Implement transition voting UI.
- [x] Implement Venue Excitement level tracking.
- [x] Implement "Vibe Streak" gamification.
- [x] Refine "Pulse Orb" into "Vibe Heatmap".

## Phase 3: Real-Time Audio Engine (Complete)
- [x] Initialize C++ Audio Engine (`engine/`).
- [x] Implement real-time SoundTouch time-stretching.
- [x] Implement automated HPF sweep logic for Energy Peaks.
- [x] Implement real-time Dynamic Range Compressor.
- [x] Implement dynamic DSP scaling (Excitement-aware).
- [x] Wire `TRACK_SYNC` and `MASTER_CONTROL` messages.
- [x] Implement multi-track pre-loading.

## Phase 4: Polish & Scaling
- [ ] **Research:** ML-driven vibe analysis models.
- [ ] **Feature:** FLAC/WAV binary streaming via WebSockets.
- [ ] **UI:** Real-time Waveform visualization.
- [ ] **Infrastructure:** Edge-deployment configuration for Audio Engine.

## Bug Fixes
- [x] Fix database schema to include `filepath`.

## Refactoring
- [x] Move mock data to persistent storage with full metadata.
- [x] Implement FastAPI lifespan for background task safety.
>>>>>>> main
