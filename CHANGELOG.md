# CHANGELOG

<<<<<<< HEAD
## [0.2.8] - 2024-05-23
=======
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
>>>>>>> main
### Added
- Implemented **Genre Archetype Evolution** in the Conductor.
- Implemented **Audio Peak Limiting** (Soft Clipper) in the C++ engine.
- Added **Animated Vibe Visualizer** (Vibe Orb) to the mobile app.
- Implemented **Session Leaderboard** synchronization.
- Enhanced **Highlight Render Worker** with isolated file logic.

## [0.2.7] - 2024-05-23
### Added
- Implemented **Energy Derivative Logic** to detect sudden surges in crowd voting.
- Implemented **DSP Intensify (HPF Sweeps)** in the C++ Audio Engine.
- Added **Session Leaderboard** to Conductor and Mobile app.
- Created exhaustive **LLM_INSTRUCTIONS.md** with architectural mandates.
- Enhanced C++ engine with automated filter sweep processing.

## [0.2.6] - 2024-05-23
### Added
- Implemented **Mobile QR Sync** using `BarCodeScanner` for dynamic venue connection.
- Added **GET SET HIGHLIGHTS** functionality to the mobile Profile view.
- Implemented **Dynamic Haptic Rhythms** with increased intensity during Peak Mode.
- Refined **Highlight Render Worker** with isolated temporary workspace logic.
- Updated mobile app with a unified multi-view navigation system.

## [0.2.5] - 2024-05-23
### Added
- Implemented **Browse & Request** view in the mobile app with full catalog search.
- Implemented **Profile & Vibe Badges** (Gamification) in the mobile app.
- Implemented **Immediate Skip** (2s crossfade) in the C++ Audio Engine.
- Enhanced C++ callback with **Timestamp-based Auto-Transitions**.
- Added **Haptic Beat Synchronization** to the mobile client.
- Awarded **Vibe Points** for compatible song requests in the Conductor.

## [0.2.4] - 2024-05-23
### Added
- Implemented **Timestamp-based Automatic Transitions** in the C++ engine.
- Implemented **Haptic Beat Synchronization** in the mobile app.
- Added **Vibe Badge System** (Gamification) for successful requests.
- Synchronized haptic feedback with live Conductor BPM.
- Enhanced mobile header with user status and points tracking.

## [0.2.3] - 2024-05-23
### Added
- Implemented **Real-Time SoundTouch Processing** in the C++ audio callback.
- Added **Energy Meter** to the mobile app for visual energy trend monitoring.
- Implemented **Genre Shift** controls in the Admin PWA and Conductor server.
- Refined C++ engine with high-quality time-stretching settings.

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
