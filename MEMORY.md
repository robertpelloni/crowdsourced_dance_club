# Project Memory

## Observations
- The project has achieved a basic autonomous state with `playback_simulation_loop`.
- "Vibe-Aware" ranking (70% compatibility, 30% user votes) balances crowd desire with sonic consistency.
- Web client prototype provides excellent visibility into the server's internal state (progress, match scores).
- Background tasks in FastAPI (`asyncio.create_task`) are working reliably for simulation.

## Design Preferences
- Weighted ranking coefficients (0.7 vibe, 0.3 votes) are subject to tuning based on user feedback.
- Use `Match %` in the UI to give users immediate feedback on why some requests are prioritized.
- Simulation duration (180s) is sufficient for testing but should be dynamic in the real engine.
