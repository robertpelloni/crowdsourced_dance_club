# Changelog

## [0.2.0] - 2025-05-22
### Added
- **Mobile App Refinements:**
    - Synchronized version to 0.2.0.
    - Added dynamic "Pulse Orb" intensity based on energy trends.
- **Audio Engine Enhancements:**
    - Implemented multi-track pre-loading logic.
- **Advanced Conductor Logic:**
    - Harmonic Key matching (Camelot Wheel logic).
    - Vibe-aware ranking system for queue prioritization.
    - Voting velocity tracking (Energy Derivative).
    - Automated Energy Peak modes and 'DSP_INTENSIFY' triggers.
    - Genre Archetype Evolution (dynamic target vibe shift).
    - Proactive `TRACK_SYNC` broadcasts for low-latency engine pre-loading.
- **Improved Data Model:**
    - Expanded `tracks.db` with genre and filepath metadata.
    - Added user stats (Vibe Points and Badges).
- **Web Client Prototype:**
    - Integrated 'Match %' indicator based on algorithmic fit.
    - Real-time energy trend visualization.
    - Progress bars for track playback synchronization.
    - Admin override dashboard (BPM, Trend, Genre, Skip).
- **Audio Engine Integration:**
    - C++ Audio Engine with PortAudio, libwebsockets, and SoundTouch.
    - Real-time time-stretching and automated HPF sweeps.
    - Support for immediate manual transitions via `SKIP_NOW`.

### Changed
- Refactored `evaluate_track_fit` to use a weighted vibe score (BPM, Energy, Key, Genre).
- Updated `src/main.py` with FastAPI lifespan management for the simulation loop.

## [0.1.1] - 2025-05-14
### Added
- Integrated `auto_dj_script` as a git submodule.
- Implemented Python FastAPI Conductor Server with WebSockets.
- Implemented Algorithmic Vibe Check (BPM and Energy fit).
- Implemented SQLite persistence for the track catalog.
- Added comprehensive unit and integration tests.

## [0.1.0] - 2025-05-14
### Added
- Initial project structure.
- Comprehensive documentation: `AGENTS.md`, `VISION.md`, `MEMORY.md`, `ROADMAP.md`, `TODO.md`, `LLM_INSTRUCTIONS.md`, `CLAUDE.md`, `GEMINI.md`, `GPT.md`, `copilot-instructions.md`.
- Centralized `VERSION.md`.
