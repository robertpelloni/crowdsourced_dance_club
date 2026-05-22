# Changelog

## [0.3.2] - 2025-05-22
### Added
- **Real-Time Event Notifications:** The Conductor now broadcasts `NEW_EVENT` alerts to all clients 60 seconds before a club event starts.
- **Event Overlay UI:** Added a dynamic, animated announcement overlay to the Web Prototype.
- **WebSocket Authentication:** The `/ws/clubgoer` endpoint now supports optional JWT token validation for persistent user sessions.

## [0.3.1] - 2025-05-22
### Added
- **User Authentication:** Implemented JWT-based authentication system with `/api/register` and `/api/login` endpoints.
- **Persistent User Profiles:** Added a `users` table to SQLite and refactored stats (points, badges, streaks) to be persistent across sessions.
- **Authenticated WebSockets:** Updated the Conductor to require a valid token for real-time interaction.
- **Auth UI:** Integrated login and registration overlays in both the Web Prototype and Mobile Application.

## [0.3.0] - 2025-05-22
### Added
- **Phase Transition:** Formally concluded the prototype phase and transitioned to Phase 4 (Polish & Scaling).
- **Project Audit:** Conducted a comprehensive post-completion review and updated `MEMORY.md`.

## [0.2.4] - 2025-05-22
### Added
- **Venue Excitement Tracking:** The Conductor now calculates a global `excitement_level` based on voting velocity and active user streaks.
- **Dynamic DSP Scaling:** The C++ engine now scales compressor aggressiveness and HPF sweep ranges based on the room's excitement level.
- **Improved C++ Thread Safety:** Disk I/O is now isolated from the audio callback thread to prevent glitches.
- **Structural Mapping:** Updated `STRUCTURE.md` with a detailed 3-tier architectural layout.

## [0.2.3] - 2025-05-22
### Added (Merged)
- Implemented smooth BPM ramping in Conductor Server.
- Added dynamic QR code generation for venue synchronization.
- Implemented user-voted transition archetypes.

## [0.2.2] - 2025-05-22
### Added
- **Dynamic Mastering:** Implemented real-time Dynamic Range Compressor in the C++ engine with energy-aware "pumping" behavior.
- **Vibe Streak Gamification:** Added server-side tracking of consecutive high-match requests, awarding bonus points and "Vibe Master" badges.
- **Vibe Heatmap:** Refined the mobile "Pulse Orb" into a multi-layered heatmap with dynamic color interpolation based on track energy.

## [0.2.1] - 2025-05-22
### Added
- **Dynamic Transition Voting:** Users can now vote on the upcoming transition archetype (Classic, Bass Swap, Echo Out, HPF Sweep) via the mobile app.
- **Smooth BPM Ramping:** The Conductor Server now gradually ramps the live room tempo towards the target BPM.
- **Dynamic QR Venue Sync:** The server now generates actual QR codes containing venue connection metadata.

### Changed
- Enhanced C++ Audio Engine with automated HPF sweep transition support.
- Updated Mobile UI with transition voting grid and improved haptic feedback.

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
