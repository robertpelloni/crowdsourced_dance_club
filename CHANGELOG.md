# Changelog

## [0.5.0] - 2026-05-23
### Added
- **User Referral Program:** Implemented a new growth-focused referral system. Users now receive a unique 8-character referral code upon registration, displayed in their profile.
- **Referral Incentives:** New users registering with a valid referral code, along with their referrers, are automatically awarded 50 bonus Vibe Points.
- **Web Auth Overlay:** Replaced the minimal auth placeholder with a fully functional login/registration overlay in the Web Prototype, including a field for referral codes.

### Changed
- **Database Schema:** Updated the `users` table in SQLite to support `referral_code` and `referred_by_id`.
- **API Enhancements:** Updated the `/api/register` and `/api/me` endpoints to support referral data.

## [0.4.3] - 2026-05-23
### Added
- **Global Vibe Leaderboard:** Implemented a real-time leaderboard view in the Web Prototype and a corresponding `/api/leaderboard` endpoint to track top audience contributors across sessions.
- **Dynamic IP Detection:** The Conductor now automatically detects its local network IP address, ensuring that generated QR codes for venue synchronization remain valid on any local network without manual configuration.
- **Hardware Sample Rate Detection:** Refactored the C++ Audio Engine to dynamically query and utilize the host's hardware sample rate via PortAudio, preventing pitch/speed distortion on non-standard audio interfaces.

### Changed
- **WebSocket Enhancements:** Broadcasters now include real-time leaderboard updates in the `QUEUE_SYNC` payload.
- **C++ Engine Modernization:** All internal DSP calculations (HPF, Crossfading) now scale precisely with the detected hardware sample rate.

## [0.4.2] - 2025-05-22
... [rest of the file remains same]
