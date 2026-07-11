# Neural Conductor Design Document

## 1. Overview
The Neural Conductor is the central ML-driven intelligence layer for the Crowdsourced Dance Club (CDC) system. It replaces heuristic-based track selection with predictive modeling to determine the optimal next track, ensuring high audience engagement based on historical data.

## 2. Core Features
- **Vibe Analysis:** Ingests historical data including user votes, track energy levels, and BPM trends to predict transition success (`vibe_score`).
- **Predictive Queuing:** Pre-computes the next N optimal tracks and sends a `PREDICTIVE_QUEUE` command to the C++ Audio Engine 15 seconds before the current track ends, ensuring zero-latency transitions.
- **Biometric Sync (Milestone 11):** Integrates physical crowd energy via WearOS/Apple Watch telemetry to override predictions during "Peak Mode".

## 3. Architecture
- **Model:** A lightweight Random Forest Regressor (via `scikit-learn`) or ONNX model.
- **Inputs (Features):**
  - `bpm_delta`: Absolute difference in BPM between current and candidate track.
  - `energy_delta`: Difference in energy levels.
  - `voting_velocity`: Rate of upvotes/downvotes over the last 60 seconds.
- **Target (Label):** `vibe_score` (0.0 to 1.0), representing the historical success of a transition.
- **API Endpoint:** `/api/ml/predict` receives current track, next track, and voting velocity, and returns the predicted vibe score.

## 4. Integration
- The Python FastAPI backend uses the predictor during the playback simulation loop.
- It is toggled via the `NEURAL_CONDUCTOR_ENABLED` feature flag.
- Communicates with the C++ engine via WebSockets (defined in `AUDIO_ENGINE_PROTOCOL.md`).
