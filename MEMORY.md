# Project Memory

## Observations
- Phase 2 core logic is now feature-complete, including energy ramping and genre affinity.
- The transition from a basic web prototype to a mobile-first PWA significantly improves the user experience for "club-goers".
- Genre clashes are now algorithmically prevented, ensuring a more cohesive musical flow.
- The `playback_simulation_loop` provides a dynamic environment for testing transitions.

## Design Preferences
- **PWA over Native:** For the initial prototype, a PWA approach allows for faster iteration and immediate testing without app store deployment.
- **Weighted Ranking:** Currently favors Fit (70%) over Votes (30%). This may need adjustment if user engagement is low.
- **SQLite Schema:** Added `genre` column to `tracks` table. All future metadata additions should follow this pattern.
