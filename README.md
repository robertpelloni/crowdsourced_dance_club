# Crowdsourced Dance Club (CDC)

A prototype "algorithmic DJ" system: a FastAPI backend (`src/main.py`,
~50 KB, with `api/`, `core/`, `db/`, `ml/`, `telemetry/` packages) that
tracks a music library in SQLite (`tracks.db`), takes crowd votes/requests
over WebSockets, and picks tracks; a small C++ audio engine under
`engine/` (Makefile + `include/` + `src/`); and a `mobile/` client
directory. `requirements.txt` is short: FastAPI, uvicorn, pydantic, pytest,
httpx, websockets, qrcode.

## Reality check against the old README

The README this replaces declared "v3.4.0 — Phase 1–4 officially complete
and successfully tested via Playwright and Locust", with a scikit-learn
"Neural Conductor", Demucs 4-stem mixing, WearOS biometric sync, DAO
governance CRUD, and a Three.js WebXR "Vibe Orb". The tree does not back
most of that:

- **Versions disagree with each other**: README said v3.4.0,
  `FINAL_RELEASE_NOTES.md` says v2.1.0, `VERSION.md` says neither clearly.
- **Claimed dependencies are absent**: no scikit-learn, demucs, or gTTS in
  `requirements.txt`.
- **The "C++ real-time engine" is mocked in the Python app**
  (`src/mock_engine.py`); the actual C++ engine is a small standalone
  directory.
- The repo carries a stack of self-issued completion documents —
  `FINAL_PROJECT_RETROSPECTIVE.md`, `POST_COMPLETION_REVIEW.md`,
  `POST_LAUNCH_REVIEW.md`, `UAT_REPORT.md`, `STAGING_REPORT.md` — written
  by the same agent process that wrote the code. They are not independent
  verification of anything.
- Root-level `bypass*.txt`, `trigger2`, `exit_loop.txt` files are agent
  loop artifacts, not project files.

What's solid: a working-shape FastAPI service with DB init
(`src/init_db.py`), an ML package directory, deploy scripts
(`deploy_staging.sh`, `deploy_production.sh`), tests under `tests/`, and a
lot of design documentation (`AUDIO_ENGINE_PROTOCOL.md`,
`NEURAL_CONDUCTOR_DESIGN.md`, `OLA_ARCHITECTURE.md`, `GLOBAL_NETWORK_SYNC.md`).

## Running

```bash
pip install -r requirements.txt
python src/main.py            # initializes DB and starts the API
make -C engine                # C++ engine (needs portaudio, libsndfile, nlohmann-json, libwebsocket)
```

## Status

Agent-built prototype from May–August 2026; latest commits are automated
checkpoints. Treat as an experiment with a real backend skeleton, not a
finished or launched product.
