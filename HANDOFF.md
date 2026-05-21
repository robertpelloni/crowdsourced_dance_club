# HANDOFF.md

## Current State
- **Version:** 0.2.8
- **Conductor Server:** Stable. Supports **Genre Archetype Evolution** and automated vibe shifting.
- **Audio Engine:** Implements real-time **Peak Limiting** (Soft Clipper) and HPF sweeps.
- **Mobile App:** Features **Animated Vibe Visualizer** (Pulse Orb) and full Browse/Request system.
- **PWA:** Functional prototype for testing and admin control.
- **Native App:** Fully implemented feature parity with PWA in `mobile/app/App.js`, including WebSocket sync and haptics.
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
