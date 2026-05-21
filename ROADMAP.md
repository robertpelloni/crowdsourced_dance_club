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

## Phase 3: Official Mobile Client & Hardware Integration (In Progress)
- [x] Implement "DJ Control Panel" (Admin Mode) in PWA.
- [x] Implement QR Code check-in API (/sync-qr).
- [x] Initialize React Native / Expo Mobile App.
- [x] Design Real-Time Audio Engine Protocol (`AUDIO_ENGINE_PROTOCOL.md`).
- [ ] Connect mobile client to Conductor Server via WebSockets.
- [ ] Implement song request and voting UI in Mobile App.

## Phase 4: Real-Time Audio Engine
- [ ] Research and select C++ audio framework (JUCE/PortAudio).
- [ ] Implement low-latency playback loop.
- [ ] Implement real-time time-stretching and crossfading.
- [ ] Integrate Audio Engine with Conductor Server using the Protocol.

## Phase 5: Polish & Deployment
- [ ] Advanced "Fit" algorithms using machine learning.
- [ ] Comprehensive UI/UX polish for mobile apps.
- [ ] Scalable cloud deployment for Conductor Server.
- [ ] On-site hardware setup instructions.
