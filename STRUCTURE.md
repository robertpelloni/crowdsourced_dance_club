# STRUCTURE.md

## Directory Layout

- `src/`: Conductor Server source code.
  - `main.py`: FastAPI application, WebSockets, and AI logic.
  - `init_db.py`: Database initialization script.
  - `static/`: Mobile-first PWA prototype.
- `mobile/`: Official React Native / Expo application scaffold.
- `external/auto_dj_script/`: Git submodule for the offline audio compiler.
- `tests/`: Pytest suite for API and logic verification.
- `docs/`: (Future) Extended documentation and manuals.
- `AUDIO_ENGINE_PROTOCOL.md`: Protocol specification for C++ engine integration.
- `tracks.db`: SQLite database for catalog and queue persistence.

## Data Flow
1. **Client** (PWA/Mobile) sends vote/request via **WebSocket**.
2. **Conductor** (FastAPI) receives message, evaluates fit, and updates `tracks.db`.
3. **Conductor** broadcasts updated queue to all **Clients**.
4. **Conductor** sends `TRACK_SYNC` to **Audio Engine**.
5. **Audio Engine** crossfades tracks and sends `PLAYBACK_STATE` back to **Conductor**.
