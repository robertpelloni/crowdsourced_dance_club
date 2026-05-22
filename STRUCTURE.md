# Project Structure & Submodules

## Directory Layout
- `src/`: Python Conductor Server.
  - `main.py`: Core logic, FastAPI endpoints, WebSocket manager, and simulation loop.
  - `init_db.py`: Database schema and mock data initialization.
  - `static/`: Web client prototype and assets.
- `engine/`: C++ Real-Time Audio Engine.
  - `src/`: C++ source files (`audio_engine.cpp`, `main.cpp`).
  - `include/`: C++ headers (`audio_engine.h`).
- `external/`: External dependencies as submodules.
  - `auto_dj_script/`: Offline audio mixing and mastering engine.
- `mobile/`: Placeholder for React Native mobile application.
- `tests/`: Python unit and integration tests.
- `tracks.db`: SQLite database for track metadata.

## Submodules

### Auto DJ Script
- **URL:** https://github.com/robertpelloni/auto_dj_script
- **Location:** `external/auto_dj_script`
- **Description:** High-fidelity offline audio mixing engine. Used for rendering highlights and master sets.

## Critical Files
- `VERSION.md`: Centralized project version.
- `AUDIO_ENGINE_PROTOCOL.md`: WebSocket JSON specification for Brain-Body communication.
- `LIBRARIES.md`: Rationale and versions for all major dependencies.
