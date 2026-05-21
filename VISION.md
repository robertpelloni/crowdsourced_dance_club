# VISION.md

## Ultimate Goal
To create a "collaborative, algorithmic club-night engine" where dancers dynamically influence the music's direction via a smartphone app.

## Key Design Principles
1. **Interactive Democracy:** Users vote and request songs, but the AI Conductor ensures a cohesive "vibe" and harmonic flow.
2. **Zero-Latency Mixing:** A dedicated C++ engine handles real-time time-stretching and DSP to prevent audio dropouts.
3. **Harmonic Intelligence:** The system uses Camelot Wheel logic and energy profiling to select the best transitions.
4. **Mobile Integration:** Venue-aware check-in (QR) and real-time state synchronization.

## Architecture
- **Layer 1: Mobile Clients** (React Native) - User interface for voting/requests.
- **Layer 2: Python AI Conductor** (FastAPI) - The "brains" that evaluates fit and manages the queue.
- **Layer 3: C++ Audio Engine** (JUCE/PortAudio) - The high-performance playback engine.
