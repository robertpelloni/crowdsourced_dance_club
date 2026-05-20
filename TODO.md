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
- [x] Develop web-based client prototype.
- [x] Implement Playback Simulation & Auto-Transitions.
- [x] Implement "Vibe-Aware" Weighted Ranking.

## Phase 2: Mobile Client Prototype
- [ ] Design and implement basic React Native client.
- [ ] Connect client to Conductor Server via WebSockets.
- [ ] Implement song request and voting UI.

## Phase 3: Real-Time Audio Engine
- [ ] Research and select C++ audio framework (JUCE/PortAudio).
- [ ] Implement low-latency playback loop.

## Bug Fixes
- None identified.

## Refactoring
- [x] Move mock data to persistent storage.
