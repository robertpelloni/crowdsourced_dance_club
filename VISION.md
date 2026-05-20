# Project Vision: Crowdsourced Dance Club

## Ultimate Goal
To build a collaborative, algorithmic club-night engine where users dynamically steer the musical direction via a mobile application.

## 3-Tier System Architecture

### 1. Mobile Client App (React Native or Flutter)
- **Workflow:** Users at the venue see the current track (artwork, BPM, key) and a voting queue.
- **Action:** Browse curated catalog, submit requests, or vote on upcoming songs.
- **Networking:** Persistent WebSocket connection for real-time updates.

### 2. Python AI Conductor (The Gatekeeper Server)
- **Role:** Brain of the operation.
- **Function:** Hosts API endpoints, manages votes, runs "Theme & Fit" evaluation logic.
- **Fit Algorithm:** Evaluates requests against the current track based on Harmonic Distance (Camelot Wheel ±1) and Energy Variance (±5% energy).

### 3. Low-Latency Audio Engine (The Heavy Lifter)
- **Role:** Real-time audio playback.
- **Implementation:** C++ (JUCE, SuperCollider) or specialized Node.js/C++ pipeline.
- **Function:** High-priority steady audio buffer, instant linear interpolation time-stretching, automated frequency filters for crossfading.

## Offline Compilation Integration
Uses `auto_dj_script` as a submodule for high-quality offline rendering of planned sets.
