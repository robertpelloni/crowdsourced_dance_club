# VISION.md

## Ultimate Goal
<<<<<<< HEAD
To create a "collaborative, algorithmic club-night engine" where dancers dynamically influence the music's direction via a smartphone app, governed by an AI Conductor that ensures harmonic and energetic flow.

## Key Design Principles
1. **Interactive Democracy:** Users vote and request songs. The Conductor evaluates "Vibe Fit" and reorders the queue based on a 70% AI / 30% Vote weighting.
2. **Zero-Latency Mixing:** A dedicated C++ engine handles real-time time-stretching (SoundTouch) and DSP to prevent audio dropouts.
3. **Harmonic Intelligence:** The system uses Camelot Wheel logic and genre compatibility matrices to ensure transparent transitions.
4. **Gamified Engagement:** Users earn "Vibe Points" and badges for submitting high-quality requests that fit the floor's energy.
5. **Dynamic Energy Evolution:** Sudden bursts of crowd engagement trigger "Energy Peaks," automatically ramping BPM and energy trends.

## Architecture
- **Layer 1: Mobile Clients** (React Native) - User interface for voting, browsing, and haptic synchronization.
- **Layer 2: Python AI Conductor** (FastAPI) - The orchestration hub managing logic, persistence, and state broadcasting.
- **Layer 3: C++ Audio Engine** (PortAudio/SoundTouch) - The high-performance playback loop that executes the Conductor's decisions.
- **Utility: Offline Compiler** (auto_dj_script) - Used for pre-rendering high-fidelity highlight reels or master sets.
=======
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
>>>>>>> main
