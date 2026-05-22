# Crowdsourced Dance Club (CDC)

## Overview
CDC is an algorithmic, crowdsourced DJ platform where the audience steers the musical direction in real-time. It combines a Python-based AI Conductor, a high-performance C++ Audio Engine, and a real-time mobile/web voting interface.

## Architecture
CDC follows a 3-tier architecture:

1.  **Mobile/Web Client:** React Native and Web-based UI for users to browse catalogs, request tracks, and vote on the upcoming queue.
2.  **AI Conductor (FastAPI):** The central brain that manages the room's state, calculates vibe scores, and coordinates playback between clients and the audio engine.
3.  **Real-Time Audio Engine (C++):** A low-latency playback system using PortAudio, SoundTouch (for time-stretching), and WebSockets (for sync).

## Features
- **Vibe-Aware Fit Algorithm:** Weighted evaluation of BPM, Energy, Harmonic Key (Camelot Wheel), and Genre compatibility.
- **Energy Peak Mode:** Automated detection of "voting velocity" surges that trigger intensified DSP effects (HPF sweeps) and BPM ramping.
- **Genre Archetype Evolution:** The room's target vibe dynamically shifts based on the history of played and requested tracks.
- **High-Fidelity Rendering:** Integration with the `auto_dj_script` submodule for rendering studio-quality master mixes of live sessions.

## Getting Started

### Conductor Server
```bash
pip install -r requirements.txt
python src/init_db.py
uvicorn src.main:app --reload
```

### Audio Engine
```bash
cd engine
make
./cdc_engine
```

## Documentation
- [VISION.md](VISION.md) - Project goals and design philosophy.
- [ROADMAP.md](ROADMAP.md) - Long-term project milestones.
- [TODO.md](TODO.md) - Immediate tasks and bug fixes.
- [DEPLOY.md](DEPLOY.md) - Deployment and environment setup.
- [STRUCTURE.md](STRUCTURE.md) - Repository and submodule layout.
