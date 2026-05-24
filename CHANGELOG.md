# Changelog

## [1.5.0] - 2026-05-23
### Added
- **Neural Conductor Foundation:** Introduced rule-based heuristic prediction for transition archetypes based on historical vibe performance.
- **Real-time Lighting Protocol:** Implemented `LIGHTING_CONTROL` WebSocket broadcast for dynamic RGB synchronization based on room energy.
- **Enhanced Mobile Resilience:** Added automatic WebSocket reconnection using `AppState` to handle foreground/background transitions on mobile.
- **Personalized Vibe Algorithm:** Integrated user genre preferences into the Conductor's vibe scoring algorithm (+10% matching bonus).

## [1.4.0] - 2026-05-23
### Added
- **Advanced User Profiles:** Users can now set and update their musical "vibe preference" (Psytrance, Techno, etc.) in their profile.
- **Enhanced Activity History:** Integrated "Recent Requests" and "Recent Votes" views into the mobile Profile tab.
- **Improved UI/UX:** Added a dedicated genre preference selector in the mobile app with real-time server synchronization.
- **Refined Modular Backend:** Finalized the transition to a modular architecture, ensuring all core logic resides in domain-specific packages (`src/api`, `src/core`, `src/db`).

## [1.2.1] - 2026-05-23
### Added
- **Final Integration Verification:** Successfully validated the backend services with a 100% pass rate across the 19-test suite.
- **Deployment Packaging:** Established a standardized `dist/` directory for production release artifacts, including the native C++ engine binary.
- **Enhanced Staging Validation:** Confirmed full system integrity via automated staging pipeline and multi-user journey simulation.

## [1.2.0] - 2026-05-23
... [rest of file]
