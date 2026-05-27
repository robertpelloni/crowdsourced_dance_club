# Changelog

## [2.0.0] - 2026-05-23
### Added
- **Qualitative Feedback Ecosystem:** Launched persistent real-time "Like" buttons for tracks and "Vibe Up/Down" buttons for transitions.
- **Data-Driven Neural Conductor:** Upgraded the transition engine to prioritize archetypes with high qualitative success rates.
- **Community-Weighted Vibe Fit:** The "Vibe Fit" algorithm now incorporates aggregate song popularity (net likes) into its prioritization logic.
- **Admin Insights Dashboard:** A new, real-time analytics panel displaying transition performance by archetype and community track popularity.
- **Club Management Suite:** Implemented a multi-tier club system (Owner, Admin, Member) with persistent club profiles and membership management.
- **Crowd Broadcast System:** Added a high-priority "Announcement" system for venue administrators to broadcast messages to all connected users.
- **Enhanced Mobile/Web Synchronization:** Unified real-time state broadcasts for "Crowd Energy" and "Peak Mode" across all tiers.
- **Improved User Profile:** Added "Favorite Tracks" history and "Change Password" functionality for enhanced personalization and security.

## [1.9.0] - 2026-05-23
### Added
- **Foundational RBAC:** Implemented Role-Based Access Control for administrative endpoints.
- **Club Schema Integration:** Established `clubs` and `club_members` persistence.
- **Modular Refactoring (Phase 2):** Decoupled club management logic from core playback state.

## [1.7.0] - 2026-05-23
### Added
- **Observability Suite:** Implemented structured logging, system health monitoring, and vibe consistency tracking.
- **Health Dashboard API:** Exposed /api/admin/health for real-time status of system resources and active client counts.
- **Vibe Performance Analytics:** Added /api/admin/analytics/vibe-report to aggregate genre success metrics and user feedback ratings.
- **Production Logging:** Introduced logging.conf for persistent file-based logging in production environments.

## [1.6.0] - 2026-05-23
### Added
- **Multi-Venue Support:** Introduced a decentralized architecture supporting multiple club arenas (e.g., Main Floor, VIP Lounge) within a single session.
- **Service Discovery:** Added a "Venues" discovery view to the mobile app for seamless arena switching.
- **Streaming Mapping:** Integrated Spotify/Apple Music deep-linking for the entire track catalog.
- **Enhanced Spatial Analytics:** USER_ACTIVITY now supports normalized X/Y coordinates to provide the data foundation for future AR heatmaps.
- **Multi-Zone Lighting:** Upgraded the LIGHTING_CONTROL protocol to support zone-specific RGB configurations.

## [1.5.1] - 2026-05-23
### Added
- **Integrated Feedback Loop:** Added "Refine" UI to the mobile application and a corresponding "Feedback Audit" panel to the Admin UI.
- **Admin Analytics:** Exposed all user-submitted vibe and technical ratings to administrators for data-driven system tuning.
- **Vision Update:** Codified the Feedback-Driven Evolution strategy in the project vision.

## [1.5.0] - 2026-05-23
### Added
- **Neural Conductor Foundation:** Introduced rule-based heuristic prediction for transition archetypes based on historical vibe performance.
- **Real-time Lighting Protocol:** Implemented LIGHTING_CONTROL WebSocket broadcast for dynamic RGB synchronization based on room energy.
- **Enhanced Mobile Resilience:** Added automatic WebSocket reconnection using AppState to handle foreground/background transitions on mobile.
- **Personalized Vibe Algorithm:** Integrated user genre preferences into the Conductor's vibe scoring algorithm (+10% matching bonus).

## [1.4.0] - 2026-05-23
### Added
- **Advanced User Profiles:** Users can now set and update their musical "vibe preference" (Psytrance, Techno, etc.) in their profile.
- **Enhanced Activity History:** Integrated "Recent Requests" and "Recent Votes" views into the mobile Profile tab.
- **Improved UI/UX:** Added a dedicated genre preference selector in the mobile app with real-time server synchronization.
- **Refined Modular Backend:** Finalized the transition to a modular architecture, ensuring all core logic resides in domain-specific packages (src/api, src/core, src/db).

## [1.2.1] - 2026-05-23
### Added
- **Final Integration Verification:** Successfully validated the backend services with a 100% pass rate across the 19-test suite.
- **Deployment Packaging:** Established a standardized dist/ directory for production release artifacts, including the native C++ engine binary.
- **Enhanced Staging Validation:** Confirmed full system integrity via automated staging pipeline and multi-user journey simulation.
