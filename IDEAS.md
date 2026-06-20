# IDEAS for Phase 3: The Sentient Venue

1. **AI Voice Announcer (The MC)**
   - Use ElevenLabs or a local TTS engine to generate dynamic "hype" announcements before massive energy drops.
   - Inject these audio clips into the C++ Engine's secondary buffer just before a `Bass Swap` transition.

2. **Spotify / SoundCloud Catalog Integration**
   - Move beyond local FLAC files and integrate with major streaming APIs to allow the audience to request *any* track.
   - We would need to implement an on-the-fly BPM and Key detection algorithm (using Librosa or essentia) to score requested tracks in real-time.

3. **Immersive "Vibe Orb" Visualizer**
   - Create an interactive React Three Fiber visualization representing the room's current energy, key, and genre archetype.
   - The orb physically pulses in sync with the WebSockets `PLAYBACK_STATE` messages.

4. **Biometric Feedback Loop**
   - Integrate with Apple Watch / WearOS SDKs to pull anonymous aggregate heart rate data from the dancefloor.
   - Use the average heart rate delta to automatically trigger "Peak Mode" instead of relying purely on voting velocity.

5. **Stem Separation & Live Mashups**
   - Integrate Demucs or Spleeter into the Python Conductor to pre-process upcoming tracks into stems (Vocals, Drums, Bass, Other).
   - The C++ Engine can then crossfade specific stems (e.g., swapping the bassline from Track A with the bassline from Track B) for true live mashups.
