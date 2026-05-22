# MEMORY.md

<<<<<<< HEAD
## Observations
- `MAX_ENERGY_DELTA = 1.0` and `MAX_BPM_DELTA = 5.0` are the stability boundaries for seamless transitions.
- SoundTouch provides excellent time-stretching quality in C++, but requires careful sample feeding (`putSamples`/`receiveSamples`) to avoid glitches.
- Haptic synchronization at 145+ BPM creates a high-energy "pulse" that significantly increases mobile user engagement.
- Timestamp-based transitions (monitoring the system clock in the C++ callback) provide much higher precision than simple duration counters.

## Preferences
- Use **Weighted Ranking** (70% Fit / 30% Votes) to prevent crowd-sourced "trolling" from ruining the vibe.
- Hidden "Admin View" (5-tap header) is essential for venue management without cluttering the user UI.
- All version increments must be synchronized across `VERSION.md`, `CHANGELOG.md`, and the PWA/Mobile headers.

## Known Challenges
- SoundTouch internal buffer latency must be accounted for in the `playback_position` calculation.
- WebSocket overhead on mobile devices can drain battery; 500ms heartbeat is a good compromise.
=======
## Architectural Observations
- **Hybrid Vibe System:** The project successfully transitioned from a simple BPM/Energy check to a weighted "Vibe Score" that includes Harmonic Key and Genre compatibility.
- **Simulation Loop:** The FastAPI lifespan-based simulation loop is effective for testing real-time behavior (energy peaks, transitions) without a physical engine.
- **Protocol:** The `AUDIO_ENGINE_PROTOCOL.md` (WebSockets) is the critical contract between the Python Brain and C++ Body.
- **Submodule Synergy:** `auto_dj_script` provides the offline "mastering" capability, while the C++ engine handles the live "performance".

## Design Preferences
- **C++ for Audio:** Performance remains the priority for the audio callback.
- **FastAPI for Conductor:** Asynchronous handling is essential for managing multiple mobile clients.
- **SQLite for Metadata:** Keeps the system portable and easy to deploy for venues.

## Recent Findings
- **Voting Velocity:** Using the derivative of vote counts is a powerful way to detect "Energy Peaks" before they happen.
- **Proactive Sync:** Sending `TRACK_SYNC` 15 seconds early is necessary to give the C++ engine time to buffer and analyze the next file.

## Prototype Completion Audit (v0.2.x)
- **Stability:** The C++ engine refactor (isolating Disk I/O) successfully addressed the most critical prototype risk: audible glitches on consumer hardware.
- **Engagement:** The "Vibe Streak" and "Venue Excitement" metrics provide a strong foundation for future social features and automated show control.
- **Portability:** The SQLite backend and header-only C++ JSON integration make the system highly portable for venue trials.
>>>>>>> main
