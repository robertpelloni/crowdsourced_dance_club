# Changelog

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
