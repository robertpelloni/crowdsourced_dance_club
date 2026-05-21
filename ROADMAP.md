# Project Roadmap

## Phase 1: Foundation & Conductor Server (Completed)
- [x] Initialize project structure and documentation.
- [x] Integrate `auto_dj_script` as a submodule.
- [x] Implement FastAPI Conductor Server with WebSockets.
- [x] Implement "Theme & Fit" algorithm (BPM & Energy).
- [x] Implement track catalog persistence (SQLite).

## Phase 2: Enhanced Conductor Logic & Client Prototype (Completed)
- [x] Implement Harmonic Key Matching (Camelot Wheel).
- [x] Implement User Voting System for queue reordering.
- [x] Develop Mobile-First PWA Prototype.
- [x] Implement Playback Simulation & Auto-Transitions.
- [x] Implement "Vibe-Aware" Weighted Ranking.
- [x] Implement Energy Ramping & Genre Compatibility Matrix.

## Phase 3: Official Mobile Client & Hardware Integration (Completed)
- [x] Implement "DJ Control Panel" (Admin Mode) in PWA.
- [x] Implement QR Code check-in API (/sync-qr).
- [x] Initialize React Native / Expo Mobile App.
- [x] Design Real-Time Audio Engine Protocol (`AUDIO_ENGINE_PROTOCOL.md`).
- [x] Connect mobile client to Conductor Server via WebSockets.
- [x] Implement song request and voting UI in Mobile App.

## Phase 4: Real-Time Audio Engine (In Progress)
- [x] Design Real-Time Audio Engine Protocol (`AUDIO_ENGINE_PROTOCOL.md`).
- [x] Implement proactive `TRACK_SYNC` logic in Conductor.
- [x] Create Mock Audio Engine for protocol verification (`src/mock_engine.py`).
- [x] Select C++ audio framework (**PortAudio**) and Networking (**libwebsockets**).
- [x] Implement initial high-priority playback loop in C++.
- [x] Implement C++ WebSocket Client for real-time Conductor sync.
- [x] Implement real-time file loading and dual-buffering (C++).
- [x] Implement real-time time-stretching (C++) via SoundTouch.
- [x] Implement visual Energy Meter in mobile app.
- [x] Implement Haptic Beat Synchronization (Mobile).
- [x] Implement Playback State reporting protocol.
- [x] Implement timestamp-based auto-transitions (C++).
- [x] Implement user gamification (Vibe Points & Badges).
- [x] Implement haptic beat synchronization (Mobile).
- [ ] Integrate C++ Audio Engine with Conductor Server state machine.

## Phase 5: Polish & Deployment
- [ ] Advanced "Fit" algorithms using machine learning.
- [ ] Comprehensive UI/UX polish for mobile apps.
- [ ] Scalable cloud deployment for Conductor Server.
- [ ] On-site hardware setup instructions.
