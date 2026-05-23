# TODO List

## Phase 5: Production & Post-Production (Active)
- [x] Conduct User Acceptance Testing (UAT).
- [x] Finalize `UAT_REPORT.md`.
- [x] Increment version to 0.4.0 (Production Candidate).
- [x] Implement Global Vibe Leaderboard in Web UI.
- [x] Dynamic IP detection for QR synchronization.
- [x] Hardware sample rate detection in C++ Engine.
- [x] Implement User Referral Program with point rewards.
- [x] Port Referral features to Mobile Application.
- [x] Execute staging deployment and validation flow.
- [x] Final project retrospective and Gold Release (v1.0.0).
- [ ] Maintenance: Monitor feedback and performance.
- [ ] Implement multi-venue load balancing.
- [ ] Integration: Spotify/Apple Music catalog import.
- [ ] Feature: Mobile AR "Vibe Heatmap" visualization.

## Phase 4: Polish, Scaling & Auth (Complete)
- [x] Implement JWT-based user authentication.
- [x] Implement persistent user profiles in SQLite.
- [x] Refactor existing gamification (points, badges) to use DB.
- [x] Integrated Auth UI in Web and Mobile prototypes.
- [x] Real-time event notifications and announcements.
- [x] Unique UUIDs for users and events to prevent database collisions.
- [x] Switch to `pbkdf2_sha256` for cross-platform password hashing compatibility.

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
