# Crowdsourced Dance Club (CDC)

An autonomous "algorithmic DJ & cybernetic venue" system featuring a
Python FastAPI AI Conductor (`src/main.py`, ~53 KB), a consolidated
single-page command dashboard (`src/static/index.html`), a desktop
System Tray application (`src/tray.py`), SQLite storage (`tracks.db`),
and a small standalone C++ audio engine (`engine/`).

**Version:** 3.5.9

## Quickstart

Run via the desktop system tray controller (GUI with terminal CLI
fallback):

```bash
python3 src/tray.py
```

Or start the FastAPI server directly:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000` for the dashboard: master audio &
transitions (44.1 kHz PCM WAV streaming, VU/RMS meters, transition
voting), floor/telemetry dynamics, track catalog search/import with BPM
and Camelot key verification, visuals/analytics, and an "AI DJ Battle
Arena" of multi-agent deck battles.

## Reality check

Earlier versions of this README declared "Phase 1–4 officially
complete and successfully tested via Playwright and Locust", with a
scikit-learn "Neural Conductor", Demucs 4-stem mixing, WearOS
biometric sync, DAO governance CRUD, and a Three.js WebXR "Vibe Orb".
The tree backs only part of that:

- **What is real now:** `scikit-learn` is a declared dependency and
  `src/ml/neural_conductor.py` exists; the FastAPI service, DB init
  (`src/init_db.py`), dashboard, tray app, deploy scripts, and tests
  under `tests/` are real; recent work (v3.5.5–v3.5.9) added dashboard
  consolidation, analytics, and governance-proposal caching.
- **Still not backed:** no Demucs or gTTS in `requirements.txt`; the
  "C++ real-time engine" is mocked in the Python app
  (`src/mock_engine.py`) while the actual C++ engine is a small
  standalone directory; WearOS/Apple Watch biometrics are simulated.
- The repo carries a stack of self-issued completion documents —
  `FINAL_PROJECT_RETROSPECTIVE.md`, `POST_COMPLETION_REVIEW.md`,
  `POST_LAUNCH_REVIEW.md`, `UAT_REPORT.md`, `STAGING_REPORT.md` —
  written by the same agent process that wrote the code. They are not
  independent verification of anything.
- Root-level `bypass*.txt`, `trigger2`, `exit_loop.txt` files are
  agent loop artifacts, not project files.

## Running

```bash
pip install -r requirements.txt
python src/main.py            # initializes DB and starts the API
make -C engine                # C++ engine (needs portaudio, libsndfile, nlohmann-json, libwebsocket)
```

## Status

Agent-built prototype, actively developed through November 2026 (last
commit 2026-11-07). Treat as an experiment with a real backend
skeleton, not a finished or launched product.
