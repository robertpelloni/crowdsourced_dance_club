# 🌌 Crowdsourced Dance Club (v0.2.3)

[![Version](https://img.shields.io/badge/version-0.2.3-blueviolet)](./VERSION.md)
[![Status](https://img.shields.io/badge/status-active-success)](./ROADMAP.md)

**Crowdsourced Dance Club** is a next-generation, real-time algorithmic club-night engine. It allows dancers to dynamically steer the musical direction of a venue via a mobile app, while a central "AI Conductor" ensures harmonic perfection and energetic flow.

## 🏗️ 3-Tier Architecture

The system is split into three distinct layers to ensure low-latency performance and high-fidelity audio:

1.  **Mobile Client App (React Native/Flutter):** The user interface for clubgoers to browse the catalog, submit requests, and vote on the queue in real-time.
2.  **Python AI Conductor (FastAPI Server):** The "brain" that manages votes and runs the **Algorithmic Vibe Check** to ensure requested songs fit the current energy and BPM of the floor.
3.  **Real-Time Audio Engine (C++):** A dedicated, low-latency playback loop that performs instant time-stretching and automated mixing.

## 🧠 Algorithmic Vibe Check

Every request is evaluated against the currently playing track:
- **BPM Sync:** Maximum $\pm 5.0$ BPM delta to prevent extreme audio warping.
- **Energy Flow:** Maximum $\pm 3.0$ energy variance to maintain the dancefloor vibe.
- **Harmonic Key:** Camelot Wheel step matching for transparent transitions.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- SQLite3

### Installation
1.  **Clone with submodules:**
    ```bash
    git clone --recursive https://github.com/robertpelloni/crowdsourced_dance_club.git
    cd crowdsourced_dance_club
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Initialize the database:**
    ```bash
    python src/init_db.py
    ```

### Running the Conductor Server
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 🛠️ Project Structure
- `src/`: Conductor Server logic and database initialization.
- `external/auto_dj_script/`: High-fidelity offline rendering engine (Submodule).
- `tests/`: Comprehensive unit and integration tests.
- `Documentation/`: Detailed `VISION.md`, `ROADMAP.md`, and `STRUCTURE.md`.

## 📜 Global LLM Instructions
This project is developed using autonomous AI agents. See `LLM_INSTRUCTIONS.md` and `AGENTS.md` for operational protocols and memory standards.

---
*Magnificent! Extraordinary! The Party Never Stops.*
