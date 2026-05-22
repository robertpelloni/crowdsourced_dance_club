# Project Roadmap

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

## Phase 3: Real-Time Audio Engine (Complete)
- [x] Implement C++ Audio Engine with PortAudio and SoundTouch.
- [x] Implement WebSocket communication protocol with Conductor.
- [x] Implement real-time time-stretching and automated transitions.
- [x] Implement automated HPF sweeps for energy peaks.
- [x] Implement real-time Dynamic Range Compressor.
- [x] Implement multi-track pre-loading and thread-safe buffer swapping.

## Phase 4: Polish, Scaling & Venue Deployment
- [x] **User Authentication:** Implement JWT-based auth and persistent user profiles.
- [ ] **Machine Learning Conductor:** Implement a neural network to predict the optimal next track based on crowd history and time-of-night.
- [ ] **Streaming Audio Pipeline:** Replace local file paths with real-time FLAC/WAV streaming from Conductor to Engine.
- [ ] **Mobile AR Visualizer:** Develop an AR "Vibe Orb" that visualizes the room's energy heatmap through the phone camera.
- [ ] **Multi-Node Audio:** Support distributed audio output across multiple synced hardware engines for large-scale venues.
- [ ] **Cloud-Edge Hybrid Deployment:** Deploy the Conductor in the cloud with low-latency edge-resident Audio Engines.
