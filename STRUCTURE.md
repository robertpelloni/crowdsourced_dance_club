# Project Structure & Submodules

## Directory Layout
- `src/`: Python Conductor Server (Brain).
  - `main.py`: Core logic, FastAPI endpoints, WebSocket manager, and vibe simulation.
  - `init_db.py`: Database schema and mock data initialization.
  - `static/`: Web client prototype and assets.
- `engine/`: C++ Real-Time Audio Engine (Body).
  - `src/`: C++ source files (`audio_engine.cpp`, `main.cpp`).
  - `include/`: C++ headers (`audio_engine.h`).
- `external/`: External dependencies as submodules.
  - `auto_dj_script/`: Offline audio mixing and mastering engine.
- `mobile/`: Official React Native mobile application for clubgoers.
- `tests/`: Comprehensive Python unit and integration tests.
- `tracks.db`: SQLite database for track metadata.

## Submodules

### Auto DJ Script
- **URL:** https://github.com/robertpelloni/auto_dj_script.git
- **Location:** `external/auto_dj_script`
- **Current Version:** 4654b5b
- **Description:** High-fidelity offline audio mixing engine. Used for rendering highlights and master sets.

## Critical Files
- `VERSION.md`: Centralized project version governance (Current: 2.0.0).
- `AUDIO_ENGINE_PROTOCOL.md`: WebSocket JSON specification for Brain-Body communication.
- `LIBRARIES.md`: Rationale and versions for all major dependencies across all tiers.
- `deploy_staging.sh`: Automated deployment pipeline for staging validation.
