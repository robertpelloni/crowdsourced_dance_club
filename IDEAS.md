# Improvements & Expansion Ideas

## Conductor Server
- **Harmonic Key Matching:** Implement full Camelot Wheel logic for smoother transitions.
- **Dynamic Energy Scaling:** Adjust the allowed energy delta based on the time of night (e.g., more variance allowed during peak hours).
- **User Reputation System:** Weight votes based on a user's history of "good" requests (songs that kept the floor moving).
- **Genre Sub-tagging:** Add more granular tags (Full-on, Twilight, Progressive) to the fit algorithm.
- **Auto-BPM Ramping:** Slowly adjust the room BPM to match the vibe without sudden jumps.

## Mobile Client
- **Real-time Waveform Visualization:** Show the upcoming transition point.
- **Collaborative Playlist Creation:** Allow users to propose "mini-sets" of 3-4 songs.
- **Social Features:** "Like" current track, see who else is on the floor.

## Audio Engine
- **Vibe-Responsive DSP:** Link high-pass filters or reverb to the aggregate "excitement" level of the crowd votes.
- **AI-Driven Crossfading:** Use neural networks to find the optimal transition point between two tracks.
- **Live Stream Integration:** Broadcast the mix to remote listeners with real-time metadata.

## General
- **Porting to Rust:** Consider rewriting the conductor logic in Rust for extreme performance and safety.
- **Hardware Controller Integration:** Allow a physical DJ to "intervene" or supervise the AI decisions.
