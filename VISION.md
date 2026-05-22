# Project Vision: Crowdsourced Dance Club

## Ultimate Goal
To build a collaborative, algorithmic club-night engine where users dynamically steer the musical direction via a mobile application. CDC is not just a player; it's a "Cybernetic DJ" that understands energy, harmony, and crowd sentiment.

## Core Pillars

### 1. Collaborative Curation
Users aren't just listeners; they are part of the feedback loop. Through voting and requests, the crowd influences the sequence, energy, and even the BPM of the night.

### 2. Algorithmic Integrity (The "Cybernetic DJ")
The AI Conductor acts as the gatekeeper, ensuring every transition is musically sound. It uses:
- **Harmonic Mixing:** Camelot Wheel logic to ensure keys are compatible.
- **Energy Management:** Tracking energy trends to prevent abrupt vibe-kills.
- **Vibe Scoring:** A weighted system that balances algorithmic fit with democratic choice.

### 3. Real-Time Physical Feedback
The system is designed for venue deployment.
- **Low Latency:** C++ engine ensures rock-solid audio performance.
- **Visual Sync:** Real-time dashboards and mobile updates keep the crowd in sync with the "pulse" of the room.
- **Automated Show Control:** Energy peaks trigger DSP sweeps and control signals for lighting or haptics.

## 3-Tier Architecture

- **The Brain (Python):** High-level orchestration, database, and API.
- **The Body (C++):** Real-time signal processing and audio I/O.
- **The Interface (JS/React Native):** The bridge between the audience and the machine.
