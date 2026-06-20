# Changelog

## [2.5.0] - 2026-06-19
### Added
- **Multi-Tenant State Management:** Restructured `venue_states` dictionary allowing for concurrent operations across physical locations.
- **Geographic Service Discovery:** Venues table populated with latitude and longitude data.
- **Geographic Proximity API:** `GET /api/venues` now supports `latitude`, `longitude`, and `radius_km` queries to rank nearby clubs using the Haversine formula.
### Changed
- **Database Scalability:** Upgraded the global SQLite connection `PRAGMA` to use `WAL` journaling mode with `timeout=20.0` ensuring high concurrency scaling.

## [2.4.0] - 2026-06-19
### Added
- **Hardware Integration:** Integrated `libftdi` for USB-to-DMX hardware support in the C++ Audio Engine.
- **DMX Protocol:** Added `LIGHTING_CONTROL_DMX` protocol via WebSockets.
- **Lighting Automation:** The Python Conductor now maps crowd energy peaks to DMX strobe sequences.

## [2.3.0] - 2026-05-23
### Added
- **Personalization & Identity:** Users can now maintain a profile `bio` and update it via the UI.
- **Enhanced Security:** Implemented password change and account deletion functionality.
- **Qualitative Feedback Expansion:** Added granular feedback loops for specific songs (Like/Dislike) and transitions (Upvote/Downvote).
- **Web Prototype v2:** Integrated profile management and feedback interactions into the dashboard.

## [2.2.0] - 2026-05-23
### Added
- **Cybernetic Intelligence (ML Integration):** Integrated `scikit-learn` and `pandas` to implement a Random Forest regression model for transition prediction.
- **ML Retraining Pipeline:** Added Admin API and UI for on-demand model retraining based on qualitative crowd feedback.
- **Neural Conductor Upgrade:** Neural Conductor now predicts the optimal transition archetype using the trained ML model.

## [2.1.0] - 2026-05-23
### Added
- **Professional Analytics:** Added Admin User Directory and personalized "Vibe Impact" metrics (Boost Factor, Success Rate).
- **Admin Insights Dashboard:** Real-time visualization of track and archetype performance.

## [2.0.0] - 2026-05-23
### Added
- **Feedback-Driven Evolution:** Launched qualitative feedback system (Likes/Vibe Votes) for songs and transitions.
- **Enhanced Data Collection:** Created `song_feedback` and `transition_feedback` database schemas.
