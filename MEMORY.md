# MEMORY.md

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
