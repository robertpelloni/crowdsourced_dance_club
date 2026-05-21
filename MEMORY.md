# MEMORY.md

## Observations
- `MAX_ENERGY_DELTA = 1.0` is the sweet spot for transition smoothness.
- `BPM_DELTA = 5.0` prevents excessive warp distortion.
- WebSockets provide sufficient low-latency sync for the PWA UI.
- Intelligently merging `auto_dj_script` feature branches (v5.5-5.8) added critical parallel warp and limiting capabilities.

## Preferences
- Use `time.time()` for absolute synchronization between server and client.
- Weighted ranking (70% Fit, 30% Votes) keeps the vibe stable while respecting user input.
- Admin mode hidden behind a 5-tap gesture on the header is effective for UI minimalism.

## Known Challenges
- Python's GIL necessitates a separate C++ process for the actual real-time audio pipeline.
- SQLite is sufficient for the catalog but might need WAL mode for high-concurrency voting.
