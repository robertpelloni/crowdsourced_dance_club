# Crowdsourced Dance Club

Welcome to the Crowdsourced Dance Club repository.
This system acts as a "Cybernetic DJ", taking crowd sentiment via live WebSockets and using an advanced ML-driven "Neural Conductor" to predict vibe trends, proactively syncing tracks to a C++ real-time audio engine.

## Getting Started

1. Set up a Python virtual environment and `pip install -r requirements.txt`.
2. Initialize DB using `python src/main.py`.
3. To build the engine, run `make -C engine` (requires portaudio, libsndfile, nlohmann-json3, libwebsocket).
4. Run `deploy_production.sh` to start the ecosystem.

## Milestones Status
- [x] Milestone 1: Python MVP & Mobile Voting
- [x] Milestone 2: C++ Audio Engine
- [x] Milestone 3: 3-Tier Integration
- [x] Milestone 4: Neural Conductor & UI Overhaul
