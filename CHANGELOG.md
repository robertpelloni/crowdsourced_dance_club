# Changelog

## [1.8.0] - 2026-05-23
### Added
- **Engagement Streak System:** Users now earn engagement streaks (🔥) by interacting with the Conductor across multiple tracks.
- **Dynamic Badge Awarding:** Implemented an automated service to award achievement badges ("Early Bird", "Super Voter", "Vibe Architect", "Streak Master") based on real-time activity.
- **Milestone Notifications:** Real-time WebSocket alerts (ACHIEVEMENT_UNLOCKED) when users reach engagement milestones.
- **Enhanced Leaderboard:** Integrated streak counts into the mobile and web leaderboards for improved competition.

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
