# IDEAS.md

## Algorithmic Enhancements
- **Energy Derivative Voting:** If many users vote "Up" simultaneously, trigger an "Energy Peak" event that speeds up the BPM and shifts the energy trend to "Rising".
- **Haptic Sync:** Use the mobile app's haptic motor to pulse on the beat (synchronized via server-side NTP-like protocol).
- **Genre Heatmaps:** Show a visual map of the tracks currently in the catalog and their "fit" relative to the playing track.

## Infrastructure
- **Peer-to-Peer Sync:** Explore using WebRTC for clients to sync state directly in case of spotty venue Wi-Fi.
- **Auto-Gain Control:** Implement EBU R128 loudness normalization in the C++ engine.

## Social Features
- **DJ Profiles:** Allow users to see who requested the current track (if opted-in).
- **Vibe Badges:** Award users for requesting tracks that "save the dancefloor" (high fit score).
