# Changelog

## [v3.5.6] - DAO Governance Proposals TTL Cache & Concurrency Optimization
- **Governance Proposals Caching (`src/api/governance.py`):** Added in-memory TTL caching (`CACHE_TTL_SECONDS = 15.0`) to `/api/governance/proposals` to prevent SQLite read contention during high-concurrency venue voting spikes.
- **Cache Invalidation Lifecycle:** Added `invalidate_governance_cache()` invoked immediately on proposal submission (`POST /api/governance/proposals`) to guarantee zero-latency consistency.
- **Automated Test Suite (`tests/test_governance_cache.py`):** Added tests verifying cache population, cache hit reuse, and automatic invalidation upon new proposal creation.

## [v3.5.5] - Conductor Vibe Performance & Genre Effectiveness Analytics
- **Conductor Vibe Performance & Analytics Card (`src/static/index.html`):** Integrated real-time analytics panel in the unified dashboard displaying average audience vibe rating, technical mixing quality, top genre effectiveness, and genre breakdown metrics.
- **Public Analytics Summary Endpoint (`GET /api/analytics/vibe-summary`):** Added lightweight public endpoint in `src/main.py` allowing clients and dashboard widgets to inspect venue performance without admin credentials.
- **Unit & RBAC Test Suite (`tests/test_analytics.py`):** Added comprehensive automated tests verifying public analytics summary, RBAC enforcement on `/api/admin/analytics/vibe-report`, and database aggregation of user ratings.

## [v3.5.4] - Generative Visuals Studio & ComfyUI Prompt Bridge Integration
- **Generative Visuals Studio (`src/core/generative_visuals.py`, `src/main.py`, `src/static/index.html`):** Integrated real-time ComfyUI / Stable Diffusion prompt synthesis into the unified command dashboard. Conductor state (genre, energy trend, audio RMS levels) is translated into dynamic audiovisual generation prompts.
- **REST Endpoints (`GET /api/visuals/status`, `POST /api/visuals/trigger`):** Exposes current generative video synthesis state and allows manual prompt triggering and preview.
- **Automated Test Suite (`tests/test_generative_visuals.py`):** Added tests validating prompt construction logic, endpoint responses, and latency handling.

## [v3.5.3] - In-Browser Live Club Audio Stream & Monitor Integration
- **In-Browser Live Club Audio Stream (`src/main.py`, `src/static/index.html`):** Implemented continuous PCM audio streaming endpoint `GET /api/audio/stream` generating a real-time 44.1kHz 16-bit stereo WAV stream dynamically synthesized and responsive to the live Conductor playback state (current BPM beat pulses and energy modulation).
- **Audio Monitor Widget & Player Controls:** Added an interactive "Live Club Audio Monitor" in the dashboard's Live Floor Dynamics section, featuring play/stop controls, live volume slider, connection status indicator, and tooltip guidance.
- **Automated Stream Test Suite (`tests/test_audio_stream.py`):** Added tests validating WAV header construction, audio chunk streaming, and parameter modulation based on Conductor engine state.

## [v3.5.2] - Dynamic Infinite Catalog Search & Import Integration
- **Infinite Catalog Search & Import (`src/core/spotify_integration.py`, `src/main.py`, `src/static/index.html`):** Integrated Spotify / external catalog searching with fallback mock pool and dynamic fallback generation. Users can search tracks directly in the unified command dashboard, view metadata (BPM, Camelot Key, Energy), and import & queue them into the live Conductor engine with one click.
- **REST Endpoints (`GET /api/catalog/search`, `POST /api/catalog/spotify-import`):** Search returns unified local and external results; import dynamically persists tracks into SQLite `tracks` and in-memory `TRACK_CATALOG`.
- **Automated Test Suite (`tests/test_spotify.py`):** Added tests covering search matching, dynamic fallback, search endpoint responses, and database catalog import persistence.

## [v3.5.1] - Secondary AI DJ Battle Arena Integration
- **Secondary AI DJ Battle Arena (`src/core/agents.py`, `src/static/index.html`):** Integrated the Secondary AI DJ personas ("The Purist", "The Mashup King", "The Goa Trance Shaman") into the unified single-page dashboard. Users can trigger AI agent battles for candidate tracks to view distinct style-biased vibe scores, risk thresholds, and commentary before queuing.
- **Battle Simulation Endpoint (`/api/agents/battle`):** Implemented REST endpoint in `src/main.py` accepting track metadata and ML baseline scores, calculating multi-agent compatibility, and returning the winning persona and commentary.
- **Unit & Integration Testing (`tests/test_agents.py`):** Added comprehensive automated test suite covering SecondaryDJAgent methods, agent battle simulations, and endpoint validation.

## [v3.5.0] - Unified Single-Page Command Dashboard, System Tray & Router Deduplication
- **Unified Single-Page Command Dashboard (`src/static/index.html`):** Redesigned and consolidated all venue operations into a single-page responsive command center prioritized by high-value features (Live Floor & Now Playing dynamics, real-time Queue & Transition voting, Telemetry/Wearables, ML Neural Conductor retraining/prediction, DAO Governance proposals/voting, Master Highlight rendering, and Clubgoer Profiles with helpful tooltip markers throughout).
- **Desktop System Tray Controller (`src/tray.py`):** Added a system tray manager application providing server status inspection, background start/stop/restart, real-time log viewing, direct launching of the Dashboard and 3D Vibe Orb WebXR visualizer, and headless terminal CLI fallback.
- **Backend Routing & Deduplication:** Mounted missing modular routers (`ml_endpoints`, `governance`, `telemetry`), eliminated duplicate routes in `src/main.py`, resolved variable bindings in WebSocket action handlers, and implemented profile extension routes (`/api/me/change-password`, `/api/feedback/song`, `/api/me/history/likes`).
- **Test Suite Verification:** Fixed `VibePredictor` interface and `monitor` singleton binding, resulting in 100% test passing across the entire test suite (36 tests passing).

## [v3.4.0] - Neural Conductor & Generative Immersion
- **Milestone 4 (Scaling & Expansion):** Fully activated the ML-driven `NeuralConductor` (using `scikit-learn` RandomForestRegressor). The Conductor now predicts transition `vibe_score` dynamically based on historical DB tracking logs instead of static heuristics.
- **Milestone 11 (Biometric Sync):** Initialized `src/telemetry/` microservice. Added `BiometricAggregator` to process high-frequency WearOS/Apple Watch HR data, actively modifying Peak Mode logic.
- **Milestone 12 (Generative Immersion):**
  - Extracted real-time `audio_rms` and `audio_peak` within the C++ `AudioEngine` `audio_callback`.
  - Built `src/static/vibe_orb.html`, a Three.js WebXR visualization reactive to C++ feature extraction.
  - Initialized `ComfyUIBridge` to dispatch dynamic text prompts based on audio properties for generative video synthesis.
- Executed comprehensive Submodule Tracking and Intelligent Git Branch Merging protocols to resolve remote branch fragmentation.

## [v3.3.0] - Automated Repository Sync & Intelligent Merge
- Synchronized with upstream parent repositories, recursively updating all submodules including `external/auto_dj_script` to track the latest head.
- Intelligently resolved git branch conflicts combining `origin/main-12832833913319381157` changes representing autonomous auto-healing code for shadow pilots.
- Merged the background anomaly detector `ShadowPilot` into the core engine lifecycle for proactive Git tracking and auto-healing features.
- Updated `VERSION.md`, `ROADMAP.md`, `TODO.md`, `IDEAS.md`, and `HANDOFF.md` to reflect Phase 4 planning states.

## [v3.2.0] - Phase 3 Completion: The Sentient Venue
- Stem-Level Mixing (Milestone 10): Replaced `spleeter` with `demucs` (Python 3.12 compatible) for asynchronous 4-stem separation.
- Real-time stem mixing capabilities directly integrated into the C++ `AudioEngine` (vocals, drums, bass, other) controlled via WebSocket.
- Finalized Spotify API integration for Infinite Catalog (Milestone 8) using `librosa` for BPM/Key extraction.
- Generative TTS hype announcements via Virtual MC (Milestone 9) driven by `gTTS`.

## [v2.6.0] - Audio Precision Update
- Stabilized SoundTouch C++ pitch-shifting logic (disabled quick-seek, enabled AA filtering).
- Added Master Bus digital compression via C++ implementation.

## [v2.5.0] - Decentralization & Multitenancy
- Re-architected SQLite connection to strictly utilize `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=NORMAL` preventing multi-venue locking.
- Introduced a multi-tenant `venue_states` dictionary replacing the old `dj_state` singleton.

## [v2.4.0] - Hardware Ecosystem
- Integrated USB-to-DMX protocol via `libftdi` directly in the C++ Audio Engine, enabling automated strobe lights synced to algorithmically detected crowd energy peaks.

## [v2.3.0] - Personalization & Granular Feedback
- Implemented user profiles with bio traits for identity tracking.
- Split explicit track requests/likes from algorithmic transition feedback, improving machine learning accuracy.

## [v2.0.0] - The Neural Conductor
- Introduced Random Forest modeling for predicting track "Vibe Fit" based on historical transition metrics.

## [v1.0.0] - Cybernetic MVP
- Basic WebSocket audio control, track requests, and initial DSP crossfading.
