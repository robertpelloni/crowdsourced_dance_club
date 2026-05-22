# Project Memory

## Architectural Observations
- **Hybrid Vibe System:** The project successfully transitioned from a simple BPM/Energy check to a weighted "Vibe Score" that includes Harmonic Key and Genre compatibility.
- **Simulation Loop:** The FastAPI lifespan-based simulation loop is effective for testing real-time behavior (energy peaks, transitions) without a physical engine.
- **Protocol:** The `AUDIO_ENGINE_PROTOCOL.md` (WebSockets) is the critical contract between the Python Brain and C++ Body.
- **Submodule Synergy:** `auto_dj_script` provides the offline "mastering" capability, while the C++ engine handles the live "performance".

## Design Preferences
- **C++ for Audio:** Performance remains the priority for the audio callback.
- **FastAPI for Conductor:** Asynchronous handling is essential for managing multiple mobile clients.
- **SQLite for Metadata:** Keeps the system portable and easy to deploy for venues.

## Recent Findings
- **Voting Velocity:** Using the derivative of vote counts is a powerful way to detect "Energy Peaks" before they happen.
- **Proactive Sync:** Sending `TRACK_SYNC` 15 seconds early is necessary to give the C++ engine time to buffer and analyze the next file.
