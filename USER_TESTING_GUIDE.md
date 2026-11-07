# CrowdClub User Testing Guide (v3.5.9)

## Overview
This guide provides instructions for validating the unified single-page command dashboard, real-time master audio streaming monitor, dynamic transition archetype voting consensus, and desktop system tray controller.

## Environment Setup
1. Launch the Conductor server via system tray or command line:
   ```bash
   python3 src/tray.py  # or uvicorn src.main:app --port 8000
   ```
2. Navigate to `http://localhost:8000` to access the unified command dashboard.
3. (Optional) Launch the 3D WebXR Vibe Orb at `http://localhost:8000/static/vibe_orb.html`.

## Testing Modules

### 1. Unified Sticky Navigation
- Use the sticky navigation bar pills (`🔥 Floor Dynamics`, `🔊 Master Audio & Transitions`, `📊 Crowd Biometrics`, etc.) to smoothly jump between cards.
- Confirm that deep links and smooth scrolling function properly on desktop and mobile viewports.

### 2. Live Audio Monitor & Real-Time Transition Voting Studio
- Click **▶ Listen Live** to connect to the `/api/audio/stream` chunked WAV stream.
- Adjust the volume slider and confirm output level modulation.
- Inspect the dynamic VU/RMS level meter reacting to playback telemetry.
- Click any of the 4 transition archetype buttons (`Classic Fade`, `Bass Swap`, `Echo Out`, `HPF Sweep`) and verify immediate vote increments, progress bar distribution shifts, and winning archetype updates.

### 3. Infinite Spotify Catalog & Instant Vibe Request
- Type a track title (e.g., "Strobe", "Trance") into the Infinite Catalog search box and click **Search**.
- Select a search result and click **Import & Queue**. Verify the track is harmonically evaluated (BPM & Camelot key) and placed into the set queue.

### 4. Generative Visuals Studio (ComfyUI Bridge)
- Select genre (Psytrance/Techno/Ambient) and energy trend (Rising/Stable/Falling).
- Click **Generate & Inject Prompt** and verify the active prompt is synthesized and dispatched.

### 5. Conductor Vibe Performance & Analytics
- Click **🔄 Refresh Analytics** to query `/api/analytics/vibe-summary`.
- Verify average vibe rating, technical rating, top genre, and genre breakdown metrics populate.

### 6. Secondary AI DJ Battle Arena
- Click **⚔️ Trigger AI DJ Battle** to pit "The Purist", "The Mashup King", and "The Goa Trance Shaman" against the current candidate track.
- Verify score calculations, style biases, and DJ commentary are displayed.

### 7. Desktop System Tray Application
- Launch `python3 src/tray.py` in GUI or headless terminal mode.
- Test server status checks, log viewing, and process controls.

## Success Criteria
- 100% of 'Perfect Matches' are accepted.
- Audio Engine crossfades trigger precisely at the Conductor's timestamp.
- ML Model updates influence transition archetype selection within 2 cycles.
