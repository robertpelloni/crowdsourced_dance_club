# MEMORY.md - Internal Architectural Observations

## Current Sweet Spots
- **BPM Drift:** The current maximum BPM delta of 5.0 provides enough variety while maintaining harmonic integrity for 15-second crossfades.
- **Energy Ramping:** Transitioning from "stable" to "rising" energy trend works best when the target BPM is increased by 2.0 and the DSP is intensified (HPF sweep).
- **Feedback Weighting:** User "Likes" provide a +2% bonus to Vibe Fit score per net-like, maxing at +20% (v2.0.0).

## Technical Learnings
- **Audio Engine:** SoundTouch's real-time time-stretching is sensitive to sample rate mismatches. v1.7.0 added hardware-aware detection to mitigate this.
- **Persistence:** SQLite is sufficient for single-venue participation, but multi-venue decentralization (v1.6.0+) requires careful connection management to avoid `database is locked` errors during peak voting.
- **Admin Security:** Explicitly promoting users to "admin" role via the database is necessary for security, as the UI hidden gesture only reveals the panel, but the backend restricts the actual actions.

## Neural Conductor Observations
- **Archetype Success:** "Crossfade" is a safe baseline, but "Filter Sweep" and "Bass Swap" have significantly higher "Vibe Up" rates during "Peak Mode".
- **Genre Compatibility:** Transitioning from Psytrance to Ambient requires a 2-track "Progressive" buffer to avoid severe vibe clash.

## Integration Dependencies
- **Submodules:** The `auto_dj_script` is essential for high-fidelity master renders. Ensure it is synced recursively.
- **Networking:** Static IPs or dynamic IP detection (implemented in v1.7.0) are critical for QR-based venue synchronization.
