# Handoff Document

## Current Status
- Conductor Server (Python/FastAPI) is fully autonomous with a playback simulation loop.
- "Vibe-Aware" weighted ranking ensures high-quality sets while respecting user votes.
- Enhanced web client prototype includes track progress bars and match percentage indicators.
- Version 0.1.4.

## Accomplished in this Session
- Implemented `playback_simulation_loop` for automatic track transitions.
- Developed `calculate_vibe_score` for multi-factor compatibility assessment.
- Implemented weighted queue reordering (Votes + Vibe Score).
- Added progress bar and match score indicators to the web client.
- Integrated background task management in FastAPI.

## Project Structure
- `src/main.py`: Conductor Server with autonomous playback logic.
- `src/static/index.html`: Enhanced web client prototype.
- `src/init_db.py`: Database initialization.
- `tracks.db`: SQLite database.
- `external/auto_dj_script/`: Submodule for audio processing (v5.8.0 merged).
- `tests/`: Unit and integration tests.

## Next Steps for the Next Session
1. **Official Mobile App:**
   - Initialize React Native / Expo environment.
   - Implement the same real-time logic from the web prototype in the mobile app.
2. **Audio Engine Real-Time POC:**
   - Investigate using `pyaudio` or `sounddevice` for a basic Python-based real-time player (for development).
   - Define the OSC or WebSocket protocol for the C++ engine.
3. **Advanced Fit Rules:**
   - Add "Energy Ramping" - prioritize tracks that gradually increase/decrease energy if desired.
   - Implement "Genre Transitions" - specific rules for moving between genres.
