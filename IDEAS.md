# Improvements & Expansion Ideas

## Conductor Server
- **ML-Driven Vibe Analysis:** Use a small neural network to predict the "next best song" based on historical vote patterns and time of night.
- **Collaborative Transitions:** Let users vote on the *type* of transition (e.g., "Bass Swap", "Echo Out", "Long Fade").
- **Dynamic Master Compressor:** Adjust the server-side "target energy" to influence the audio engine's soft-clipper and gain stages.

## Mobile Client
- **Dynamic Haptic Rhythms:** Use `expo-haptics` to pulse the phone in time with the BPM, intensifying during peak modes.
- **AR Visualizer:** Use the phone's camera to display an augmented "Vibe Orb" floating over the dancefloor.
- **Venue Social Graph:** See "Vibe Affinity" with other users based on shared song requests.

## Audio Engine
- **Vibe-Responsive Reverb:** Increase reverb tail length as the room BPM rises to create a more "expansive" peak feel.
- **GPU-Accelerated FFT:** Move spectral analysis to the GPU for even lower latency and higher resolution.
- **Multi-Node Audio:** Support distributed audio output across multiple synced hardware engines for massive venues.
