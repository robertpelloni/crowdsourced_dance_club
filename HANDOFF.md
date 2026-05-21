# HANDOFF.md

## Current State
- **Version:** 0.1.7
- **Conductor Server:** Stable. Handles fit evaluation, voting, and broadcasts queue updates.
- **PWA:** Functional prototype for testing and admin control.
- **Native App:** Scaffolded in `mobile/`.
- **Submodule:** `external/auto_dj_script` is up-to-date with merged feature branches.
- **Protocol:** Defined in `AUDIO_ENGINE_PROTOCOL.md`.

## Key Files
- `src/main.py`: Core logic and WebSocket server.
- `src/static/index.html`: PWA implementation.
- `AUDIO_ENGINE_PROTOCOL.md`: Spec for the next major component (C++ Engine).

## Next Recommended Steps
1. **Mobile App Development:** Start implementing the UI in `mobile/app/App.js` and connecting to the `/ws/clubgoer` endpoint.
2. **Audio Engine Discovery:** Begin researching the C++ implementation for real-time playback, focusing on cross-platform compatibility (JUCE).
3. **Advanced Fit Logic:** Consider integrating a simple machine learning model to better predict "dancefloor success" based on historical voting data.
