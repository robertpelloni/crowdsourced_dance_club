# Project Memory

## Observations
- The project is transitioning into Phase 2 with enhanced logic and a functional web prototype.
- Harmonic Key Matching (Camelot Wheel) significantly improves the "fit" algorithm's sophistication.
- The voting system enables basic crowdsourcing of the set order.
- FastAPI's `StaticFiles` and `FileResponse` are effective for serving the prototype.

## Design Preferences
- Maintain strict "fit" constraints even when reordering by votes (implemented in Phase 2.5).
- Web prototype should remain lightweight and focus on core interactions (request/vote).
- Versioning remains the single source of truth for build tracking.
