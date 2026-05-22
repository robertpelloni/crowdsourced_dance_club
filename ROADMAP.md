# Project Roadmap

<<<<<<< HEAD
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
=======
## Phase 1: Foundation & Conductor Server (Complete)
- [x] Initialize project structure and documentation.
- [x] Integrate `auto_dj_script` as a submodule.
- [x] Implement FastAPI Conductor Server with WebSockets.
- [x] Implement "Theme & Fit" algorithm (Weighted Vibe Score).
- [x] Implement track catalog persistence (SQLite).
- [x] Implement Harmonic Key matching logic (Camelot Wheel).
- [x] Implement User Voting & Queue Reordering.

## Phase 2: Mobile & Web Client Prototype (In Progress)
- [x] Develop Web Client Prototype with real-time state sync.
- [x] Implement song request and voting UI.
- [x] Implement Admin Override Dashboard.
- [x] Transition prototype to React Native for native mobile support.
- [x] Implement QR-based venue synchronization.
- [x] Implement User-Voted Transitions.
- [x] Implement Venue Excitement tracking.

## Phase 3: Real-Time Audio Engine (Initial Implementation)
- [x] Implement C++ Audio Engine with PortAudio and SoundTouch.
- [x] Implement WebSocket communication protocol with Conductor.
- [x] Implement real-time time-stretching and automated transitions.
- [x] Implement automated HPF sweeps for energy peaks.
- [ ] Optimize low-latency buffer management.
- [ ] Implement multi-track pre-loading.
>>>>>>> main

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
- [x] Implement Mobile QR Sync for venue onboarding.
- [x] Implement Highlight Rendering trigger from mobile.
- [x] Implement Energy Derivative detection (Surge control).
- [x] Implement real-time DSP Filter Sweeps (C++).
- [x] Implement real-time peak limiting (C++).
- [x] Implement Genre Archetype evolution.
- [ ] Integrate C++ Audio Engine with Conductor Server state machine.

## Phase 4: Polish, Scaling & Venue Deployment
- [ ] **Machine Learning Conductor:** Implement a neural network to predict the optimal next track based on crowd history and time-of-night.
- [ ] **Streaming Audio Pipeline:** Replace local file paths with real-time FLAC/WAV streaming from Conductor to Engine.
- [ ] **Mobile AR Visualizer:** Develop an AR "Vibe Orb" that visualizes the room's energy heatmap through the phone camera.
- [ ] **Multi-Node Audio:** Support distributed audio output across multiple synced hardware engines for large-scale venues.
- [ ] **Cloud-Edge Hybrid Deployment:** Deploy the Conductor in the cloud with low-latency edge-resident Audio Engines.
