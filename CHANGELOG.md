# Changelog

## [0.5.1] - 2026-05-23
### Added
- **Mobile Referral Support:** Ported the user referral program to the React Native mobile application. Users can now enter referral codes during mobile registration and view their own codes in the profile.
- **Mobile UI Polishing:** Updated the mobile leaderboard to display display names (usernames) instead of internal UUIDs.

### Changed
- **Mobile Auth Logic:** Refactored `handleAuth` in the mobile app to support both Form-Data (login) and JSON (registration) payloads as required by the Python Conductor API.

## [0.5.0] - 2026-05-23
### Added
- **User Referral Program:** Implemented a new growth-focused referral system. Users now receive a unique 8-character referral code upon registration, displayed in their profile.
- **Referral Incentives:** New users registering with a valid referral code, along with their referrers, are automatically awarded 50 bonus Vibe Points.
- **Web Auth Overlay:** Replaced the minimal auth placeholder with a fully functional login/registration overlay in the Web Prototype, including a field for referral codes.

### Changed
- **Database Schema:** Updated the `users` table in SQLite to support `referral_code` and `referred_by_id`.
- **API Enhancements:** Updated the `/api/register` and `/api/me` endpoints to support referral data.

## [0.4.3] - 2026-05-23
... [rest of the file]
