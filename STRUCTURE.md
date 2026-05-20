# Project Structure & Submodules

## Directory Layout
- `src/`: Main source code for the Python AI Conductor Server.
  - `main.py`: FastAPI server, WebSocket management, and vibe-check logic.
  - `init_db.py`: Database initialization script.
- `external/`: External dependencies integrated as submodules.
  - `auto_dj_script/`: High-fidelity offline audio mixing engine (Merged v5.5.0, v5.7.0, v5.8.0).
- `tests/`: Unit and integration tests.
- `tracks.db`: SQLite database for track metadata.
- `requirements.txt`: Python dependencies.
- `VERSION.md`: Centralized version number.

## Submodules

### Auto DJ Script
- **URL:** https://github.com/robertpelloni/auto_dj_script
- **Location:** `external/auto_dj_script`
- **Description:** A batch audio processor that uses simulated annealing and advanced DSP to create studio-grade DJ sets.
- **Role in Project:** Acts as the offline "heavy lifter" for rendering high-quality master files from the crowdsourced playlists.
- **Recent Merges:**
  - **v5.5.0:** Ultimate Console Evolution, Parallelized Warp Engine, True-Peak Limiter.
  - **v5.7.0:** Interactive Tempo Ramping and Perform Project Audit.
  - **v5.8.0:** Enhanced Genre Inference and 3-Band Compression.

## Libraries & Dependencies
- **FastAPI:** High-performance web framework.
- **Uvicorn:** ASGI server.
- **Pydantic:** Data validation.
- **Websockets:** Real-time communication.
- **SQLite3:** Persistent storage.
- **Pytest:** Testing framework.
