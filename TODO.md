# TODO List

## Immediate / Short-Term Tasks
- [x] Deduplicate route definitions in `src/main.py` and mount all modular routers (`ml_endpoints`, `governance`, `telemetry`).
- [x] Consolidate multi-page dashboard UI into unified single-page layout (`src/static/index.html`) with interactive tooltips and high-value feature prioritization.
- [x] Implement desktop System Tray controller application (`src/tray.py`) with process management, log viewing, and headless fallback.
- [x] Align `VibePredictor` interface with test specifications and pass all 36 test suite unit/integration tests.
- [x] Wire Secondary AI DJ Agent Battle Arena into the dashboard UI and expose `/api/agents/battle` endpoint (`v3.5.1`).
- [x] Connect Infinite Catalog Spotify dynamic search and import into dashboard UI (`v3.5.2`).
- [x] Connect In-Browser Live Club Audio Stream (`GET /api/audio/stream` chunked WAV stream + HTML5 audio monitor widget) (`v3.5.3`).
- [x] Integrate Generative Visuals Studio card & ComfyUI Prompt Bridge into Dashboard (`v3.5.4`).
- [x] Integrate Conductor Vibe Performance & Genre Effectiveness analytics reporting (`v3.5.5`).
- [x] Add TTL caching layer for `/api/governance/proposals` during massive load peaks (`v3.5.6`).
- [x] Consolidate Live Audio Stream Monitor & Transition Voting Studio with dynamic VU meters (`v3.5.7`).
- [x] Integrate sticky quick-navigation bar and deep-linking anchors on the unified dashboard (`v3.5.8`).
- [ ] Connect WebSocket audio state directly to WebRTC audio stream for ultra-low latency sub-50ms clubgoer audio monitoring.

## Backlog / Technical Debt
- [ ] Evaluate porting the core `evaluate_track_fit` Random Forest logic to a faster, compiled language (like Rust / C++ ONNX Runtime) if multi-agent concurrent evaluation becomes a bottleneck.

## Phase 5 Ideation
- [ ] Draft an architecture diagram for real-time mobile AR visualizers running on iOS/Android clients tracking native spatial position against the DMX venue grid.
- [ ] Design an Open Lighting Architecture (OLA) WebSocket proxy for the `dmx_controller.cpp` to decouple hardware from the core rendering engine.
