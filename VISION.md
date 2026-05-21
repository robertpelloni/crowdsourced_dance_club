# VISION.md

## Ultimate Goal
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
