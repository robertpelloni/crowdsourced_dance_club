import asyncio
import json
import os
import sqlite3
import sys
import time
from contextlib import asynccontextmanager
from typing import List, Dict, Optional, Tuple

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

DB_PATH = "tracks.db"

# AI Conductor Configuration Thresholds
CONFIG = {
    "MAX_BPM_DELTA": 5.0,      # Max BPM difference allowed for fit
    "MAX_ENERGY_DELTA": 1.0,   # Max Energy difference allowed for fit (Tightened from 1.5)
    "VIBE_WEIGHT_BPM": 0.20,
    "VIBE_WEIGHT_ENERGY": 0.20,
    "VIBE_WEIGHT_RAMPING": 0.10,
    "VIBE_WEIGHT_KEY": 0.30,
    "VIBE_WEIGHT_GENRE": 0.20,
    "VOTE_WEIGHT": 0.30,       # How much votes matter vs algorithmic fit
}

# Genre Compatibility Matrix (1.0 = perfect, 0.0 = clash)
GENRE_COMPATIBILITY = {
    "Psytrance": {"Psytrance": 1.0, "Techno": 0.7, "Progressive": 0.8, "Ambient": 0.2},
    "Techno": {"Techno": 1.0, "Psytrance": 0.7, "Progressive": 0.6, "Ambient": 0.3},
    "Progressive": {"Progressive": 1.0, "Psytrance": 0.8, "Techno": 0.6, "Ambient": 0.5},
    "Ambient": {"Ambient": 1.0, "Progressive": 0.5, "Techno": 0.3, "Psytrance": 0.1},
}

def get_db_connection():
    """Helper to create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_track_catalog() -> Dict[str, Dict]:
    """Loads all tracks from the database into an in-memory dictionary."""
    if not os.path.exists(DB_PATH):
        # Fallback for initial run if DB isn't initialized yet
        return {
            "track_001": {"id": "track_001", "title": "Awake the Machine", "artist": "Astrix", "bpm": 145.0, "key": "9A", "energy": 9.5}
        }

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracks")
    rows = cursor.fetchall()
    conn.close()

    return {row["id"]: dict(row) for row in rows}

TRACK_CATALOG = load_track_catalog()

class Track(BaseModel):
    id: str
    title: str
    artist: str
    bpm: float
    key: str
    energy: float

class TrackState:
    """
    Maintains the live state of the club's audio system.
    This is a singleton-like object in the current implementation.
    """
    def __init__(self):
        # Current track being played
        self.current_track: Dict = TRACK_CATALOG["track_001"]
        # Start time of the current track (epoch seconds)
        self.start_time: float = time.time()
        # Duration of current track in seconds (default 180 for simulation)
        self.duration: float = 180.0
        # Target BPM for the room
        self.target_bpm: float = 145.0
        # Target energy trend: "rising", "stable", or "falling"
        self.energy_trend: str = "stable"
        # Peak mode status
        self.is_peak_mode: bool = False
        # Upcoming tracks submitted and approved
        # Each entry is a dict: {"track": Dict, "votes": int}
        self.upcoming_queue: List[Dict] = []
        # List of active WebSocket connections
        self.connected_clients: List[WebSocket] = []
        # History of vote timestamps for velocity calculation
        self.vote_history: List[float] = []

dj_state = TrackState()

class ConnectionManager:
    """
    Manages active smartphone WebSocket client connections.
    Handles connection, disconnection, and broadcasting updates.
    """
    async def connect(self, websocket: WebSocket):
        """Accepts a new connection and sends the initial state."""
        await websocket.accept()
        dj_state.connected_clients.append(websocket)
        # Immediately push current state to the new client
        await websocket.send_json(self.get_broadcast_payload())

    def disconnect(self, websocket: WebSocket):
        """Removes a disconnected client from the active list."""
        if websocket in dj_state.connected_clients:
            dj_state.connected_clients.remove(websocket)

    async def broadcast_queue_update(self):
        """Sends the current queue state to all connected clients."""
        payload = self.get_broadcast_payload()
        # Create a copy of the list to avoid issues during iteration if a client disconnects
        for connection in list(dj_state.connected_clients):
            try:
                await connection.send_json(payload)
            except Exception:
                # Handle dead connections gracefully by removing them
                self.disconnect(connection)

    def get_broadcast_payload(self) -> Dict:
        """Constructs the standard payload for state synchronization."""
        return {
            "type": "QUEUE_SYNC",
            "current_track": dj_state.current_track,
            "start_time": dj_state.start_time,
            "duration": dj_state.duration,
            "target_bpm": dj_state.target_bpm,
            "energy_trend": dj_state.energy_trend,
            "queue": dj_state.upcoming_queue
        }

manager = ConnectionManager()

def is_harmonically_compatible(key1: str, key2: str) -> bool:
    """
    Checks if two Camelot keys are compatible.
    Compatible keys are the same, +/- 1 step, or parallel major/minor.
    Example: '8A' is compatible with '8A', '7A', '9A', and '8B'.
    """
    if not key1 or not key2:
        return False

    if key1 == key2:
        return True

    try:
        val1 = int(key1[:-1])
        mode1 = key1[-1]
        val2 = int(key2[:-1])
        mode2 = key2[-1]

        # Parallel major/minor (e.g., 8A -> 8B)
        if val1 == val2 and mode1 != mode2:
            return True

        # Same mode, +/- 1 step
        if mode1 == mode2:
            diff = abs(val1 - val2)
            # Handle wrap-around (12 to 1)
            if diff == 1 or diff == 11:
                return True

    except (ValueError, IndexError):
        return False

    return False

def get_random_compatible_track(current_track: Dict) -> Optional[Dict]:
    """Finds a random compatible track from the catalog as a fallback."""
    compatible = []
    for track in TRACK_CATALOG.values():
        if track["id"] == current_track["id"]:
            continue
        fits, _ = evaluate_track_fit(track, current_track)
        if fits:
            compatible.append(track)

    import random
    return random.choice(compatible) if compatible else None

def calculate_vibe_score(track: Dict, current_track: Dict) -> float:
    """
    Calculates a compatibility score (0.0 to 1.0) between two tracks.
    Considers BPM, Energy, Key, Energy Ramping, and Genre Compatibility.
    """
    # BPM Score
    bpm_delta = abs(track["bpm"] - current_track["bpm"])
    bpm_score = max(0, 1 - (bpm_delta / CONFIG["MAX_BPM_DELTA"]))

    # Energy Score
    energy_delta = abs(track["energy"] - current_track["energy"])
    energy_score = max(0, 1 - (energy_delta / CONFIG["MAX_ENERGY_DELTA"]))

    # Energy Ramping Bonus/Penalty
    ramping_score = 0.5
    if dj_state.energy_trend == "rising":
        if track["energy"] > current_track["energy"]: ramping_score = 1.0
        elif track["energy"] < current_track["energy"]: ramping_score = 0.0
    elif dj_state.energy_trend == "falling":
        if track["energy"] < current_track["energy"]: ramping_score = 1.0
        elif track["energy"] > current_track["energy"]: ramping_score = 0.0

    # Key Score
    key_score = 1.0 if is_harmonically_compatible(track["key"], current_track["key"]) else 0.0

    # Genre Score
    genre1 = current_track.get("genre", "Psytrance")
    genre2 = track.get("genre", "Psytrance")
    genre_score = GENRE_COMPATIBILITY.get(genre1, {}).get(genre2, 0.5)

    # Weighted Average
    # 20% BPM, 20% Energy, 10% Ramping, 30% Key, 20% Genre
    return (bpm_score * 0.20) + (energy_score * 0.20) + (ramping_score * 0.1) + (key_score * 0.3) + (genre_score * 0.2)

def evaluate_track_fit(requested_track: Dict, current_track: Dict) -> Tuple[bool, str]:
    """
    Algorithmic Vibe Check: Assesses if a requested song safely fits
    the current energy matrix and tempo of the dancefloor.
    """
    # Rule 1: Tempo Check
    bpm_delta = abs(requested_track["bpm"] - current_track["bpm"])
    if bpm_delta > CONFIG["MAX_BPM_DELTA"]:
        return False, f"BPM clash too severe ({requested_track['bpm']} vs {current_track['bpm']}). Would cause audio warp distortion."

    # Rule 2: Energy Vibe Check
    energy_delta = abs(requested_track["energy"] - current_track["energy"])
    if energy_delta > CONFIG["MAX_ENERGY_DELTA"]:
         return False, f"Energy delta clash ({requested_track['energy']} vs {current_track['energy']}): Transition is too abrupt for the current vibe."

    # Rule 3: Harmonic Check
    if not is_harmonically_compatible(requested_track["key"], current_track["key"]):
        return False, f"Harmonic clash: {requested_track['key']} is not compatible with current track's {current_track['key']}."

    # Rule 4: Genre Check
    genre1 = current_track.get("genre", "Psytrance")
    genre2 = requested_track.get("genre", "Psytrance")
    if GENRE_COMPATIBILITY.get(genre1, {}).get(genre2, 0.5) < 0.3:
        return False, f"Genre clash: {genre2} is not compatible with current vibe ({genre1})."

    return True, "Track fits the sonic profile perfectly."

async def playback_simulation_loop():
    """
    Background task that simulates track progress and transitions.
    Includes logic for Voting Velocity and Energy Peaks.
    """
    while True:
        now = time.time()
        remaining = dj_state.start_time + dj_state.duration - now

        # 1. Calculate Voting Velocity (votes in the last 60 seconds)
        dj_state.vote_history = [t for t in dj_state.vote_history if now - t < 60]
        vote_velocity = len(dj_state.vote_history)

        # 2. Trigger Energy Peak if velocity is high (> 5 votes/min for prototype)
        if vote_velocity >= 5 and not dj_state.is_peak_mode:
            dj_state.is_peak_mode = True
            dj_state.energy_trend = "rising"
            dj_state.target_bpm += 2.0
            print(f"[SYSTEM] ENERGY PEAK DETECTED! Velocity: {vote_velocity} votes/min. Ramping up.")
            await manager.broadcast_queue_update()
        elif vote_velocity < 2 and dj_state.is_peak_mode:
            dj_state.is_peak_mode = False
            dj_state.energy_trend = "stable"
            print(f"[SYSTEM] Peak energy subsiding. Velocity: {vote_velocity} votes/min.")
            await manager.broadcast_queue_update()

        # 3. Proactive TRACK_SYNC (15s before transition)
        if 14.5 <= remaining <= 15.5:
            if dj_state.upcoming_queue:
                next_track = dj_state.upcoming_queue[0]["track"]
                sync_payload = {
                    "type": "TRACK_SYNC",
                    "data": {
                        "track_id": next_track["id"],
                        "filepath": next_track.get("filepath", f"tracks/{next_track['id']}.flac"),
                        "bpm": next_track["bpm"],
                        "key": next_track["key"],
                        "energy": next_track["energy"],
                        "transition_timestamp": dj_state.start_time + dj_state.duration,
                        "crossfade_duration": 15.0
                    }
                }
                # Broadcast to all clients (including the future C++ Engine)
                for client in dj_state.connected_clients:
                    try:
                        await client.send_json(sync_payload)
                    except:
                        pass
                print(f"[SYSTEM] Proactive TRACK_SYNC sent for: {next_track['title']}")

        # 4. Handle Transitions
        if remaining <= 0:
            # Transition to next track
            if dj_state.upcoming_queue:
                next_item = dj_state.upcoming_queue.pop(0)
                dj_state.current_track = next_item["track"]
            else:
                # Select random compatible track from catalog
                fallback = get_random_compatible_track(dj_state.current_track)
                if fallback:
                    dj_state.current_track = fallback
                # else keep playing current (loop)

            dj_state.start_time = now
            # In real life duration varies, but for simulation we use 180s
            dj_state.duration = 180.0
            await manager.broadcast_queue_update()
            print(f"[SYSTEM] Transitioned to: {dj_state.current_track['title']}")

        # Check every 1 second
        await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    # Startup: Initialize background tasks
    loop_task = asyncio.create_task(playback_simulation_loop())
    yield
    # Shutdown: Clean up tasks
    loop_task.cancel()

app = FastAPI(title="Algorithmic DJ Conductor Server", lifespan=lifespan)

# Serve static files for the client prototype
app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/")
async def root():
    """Serve the client prototype index.html at the root."""
    return FileResponse("src/static/index.html")

@app.get("/catalog")
async def get_catalog():
    """Returns the list of available tracks in the curated catalog."""
    return list(TRACK_CATALOG.values())

@app.get("/sync-qr")
async def get_sync_qr():
    """Returns metadata for venue synchronization (QR data placeholder)."""
    return {
        "venue_name": "CDC Virtual Arena",
        "conductor_url": "http://localhost:8000",
        "websocket_url": "ws://localhost:8000/ws/clubgoer",
        "session_id": "session_" + str(int(time.time())),
        "qr_placeholder": "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=CDC_SYNC"
    }

@app.websocket("/ws/clubgoer")
async def websocket_endpoint(websocket: WebSocket):
    """
    Real-time portal for clubgoers to vote and request songs.
    Clients send JSON messages with actions like 'REQUEST_SONG'.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Wait for incoming JSON messages from a user's phone
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "ERROR", "message": "Invalid JSON format."})
                continue

            action = message.get("action")

            if action == "GET_VIBE_SCORE":
                track_id = message.get("track_id")
                track = TRACK_CATALOG.get(track_id)
                if track:
                    score = calculate_vibe_score(track, dj_state.current_track)
                    await websocket.send_json({"type": "VIBE_SCORE", "track_id": track_id, "score": score})
                else:
                    await websocket.send_json({"type": "ERROR", "message": "Track not found."})

            elif action == "REQUEST_SONG":
                track_id = message.get("track_id")
                requested_track = TRACK_CATALOG.get(track_id)

                if not requested_track:
                    await websocket.send_json({"type": "ERROR", "message": "Track not found in club database."})
                    continue

                # Run the algorithmic fit validation against the current track
                fits, reason = evaluate_track_fit(requested_track, dj_state.current_track)

                if fits:
                    # Append to queue and notify the entire room via real-time broadcast
                    # Check if already in queue
                    if any(item["track"]["id"] == track_id for item in dj_state.upcoming_queue):
                        await websocket.send_json({"type": "ERROR", "message": "Track already in queue."})
                        continue

                    dj_state.upcoming_queue.append({"track": requested_track, "votes": 1})
                    await websocket.send_json({"type": "REQUEST_ACCEPTED", "message": reason, "track": requested_track})
                    await manager.broadcast_queue_update()
                else:
                    # Deny request and give the user feedback on why it failed the vibe check
                    await websocket.send_json({"type": "REQUEST_DENIED", "message": reason})

            elif action == "VOTE_TRACK":
                track_id = message.get("track_id")
                found = False
                for item in dj_state.upcoming_queue:
                    if item["track"]["id"] == track_id:
                        item["votes"] += 1
                        dj_state.vote_history.append(time.time())
                        found = True
                        break

                if found:
                    # Reorder queue based on weighted score of votes and vibe compatibility
                    for item in dj_state.upcoming_queue:
                        vibe = calculate_vibe_score(item["track"], dj_state.current_track)
                        # Normalize votes: 1 vote = 0.1, 10 votes = 1.0 (capped)
                        vote_score = min(1.0, item["votes"] * 0.1)
                        # Use CONFIG weight
                        item["weighted_score"] = (vibe * (1 - CONFIG["VOTE_WEIGHT"])) + (vote_score * CONFIG["VOTE_WEIGHT"])

                    dj_state.upcoming_queue.sort(key=lambda x: x.get("weighted_score", 0), reverse=True)
                    await manager.broadcast_queue_update()
                else:
                    await websocket.send_json({"type": "ERROR", "message": "Track not found in queue."})

            elif action == "ADMIN_SKIP":
                if dj_state.upcoming_queue:
                    next_item = dj_state.upcoming_queue.pop(0)
                    dj_state.current_track = next_item["track"]
                else:
                    fallback = get_random_compatible_track(dj_state.current_track)
                    if fallback:
                        dj_state.current_track = fallback

                dj_state.start_time = time.time()
                await manager.broadcast_queue_update()
                await websocket.send_json({"type": "ADMIN_SUCCESS", "message": "Track skipped."})

            elif action == "ADMIN_SET_TREND":
                trend = message.get("trend")
                if trend in ["rising", "stable", "falling"]:
                    dj_state.energy_trend = trend
                    await manager.broadcast_queue_update()
                    await websocket.send_json({"type": "ADMIN_SUCCESS", "message": f"Trend set to {trend}."})

            elif action == "ADMIN_SET_BPM":
                bpm = float(message.get("bpm", 145.0))
                dj_state.target_bpm = bpm
                await manager.broadcast_queue_update()
                # Notify Audio Engine
                for client in dj_state.connected_clients:
                    try:
                        await client.send_json({"type": "MASTER_CONTROL", "data": {"target_bpm": bpm}})
                    except: pass
                await websocket.send_json({"type": "ADMIN_SUCCESS", "message": f"BPM set to {bpm}."})

            elif action == "ADMIN_SET_GENRE":
                genre = message.get("genre")
                # For simplicity, we just notify logs in prototype, but could influence auto-selection
                print(f"[ADMIN] Requested genre shift to: {genre}")
                await websocket.send_json({"type": "ADMIN_SUCCESS", "message": f"Vibe shifting to {genre}."})

            else:
                await websocket.send_json({"type": "ERROR", "message": f"Unknown action: {action}"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        # Catch unexpected errors to prevent the endpoint from crashing silently
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Integration with auto_dj_script submodule
def run_offline_compiler_worker(track_ids: List[str], output_path: str, bpm: float):
    """
    Calls the Auto DJ submodule to render a set based on specific track IDs.
    """
    submodule_path = os.path.abspath("./external/auto_dj_script")
    if submodule_path not in sys.path:
        sys.path.append(submodule_path)

    try:
        from autodj.core import compile_master_set

        # Create a mock args object for the submodule
        class Args:
            def __init__(self, input_dir, output_file, target_bpm):
                self.input = input_dir
                self.output = output_file
                self.bpm = target_bpm
                self.end_bpm = target_bpm
                self.beats_per_bar = 4
                self.transition_bars = 8
                self.lowpass = 500
                self.highpass = 1500
                self.archetype = 'auto'

        # In a real scenario, we'd copy the specific files to a temporary directory
        # For this implementation, we assume track files are in a standard location
        input_dir = "tracks/"
        if not os.path.exists(input_dir):
            os.makedirs(input_dir)

        args = Args(input_dir, output_path, bpm)

        print(f"[AUTO-DJ] Starting high-fidelity render to: {output_path}")
        compile_master_set(args)
        print(f"[AUTO-DJ] Render complete: {output_path}")

    except Exception as e:
        print(f"[ERROR] Offline compilation failed: {e}")

@app.post("/api/render-highlights")
async def render_highlights(background_tasks: BackgroundTasks, track_ids: List[str]):
    """
    API endpoint to trigger an offline render of set highlights.
    """
    output_path = f"static/renders/highlights_{int(time.time())}.flac"
    background_tasks.add_task(run_offline_compiler_worker, track_ids, output_path, dj_state.target_bpm)
    return {"status": "processing", "message": "High-fidelity highlight render initiated."}

@app.post("/api/render-set")
async def render_compiled_set(background_tasks: BackgroundTasks, source_folder: str, output_path: str):
    """
    API endpoint that accepts a finalized room playlist and spins up
    the offline script in a background thread to render a high-quality mix.
    """
    # Delegate the heavy lifting to the submodule without blocking the main event loop
    background_tasks.add_task(run_offline_compiler_worker, source_folder, output_path, dj_state.target_bpm)

    return {"status": "processing", "message": "Submodule background worker initialized."}
