import asyncio
import json
import os
import sqlite3
import sys
from typing import List, Dict, Optional, Tuple

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

DB_PATH = "tracks.db"

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
        # Target BPM for the room
        self.target_bpm: float = 145.0
        # Upcoming tracks submitted and approved
        # Each entry is a dict: {"track": Dict, "votes": int}
        self.upcoming_queue: List[Dict] = []
        # List of active WebSocket connections
        self.connected_clients: List[WebSocket] = []

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
            "target_bpm": dj_state.target_bpm,
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

def evaluate_track_fit(requested_track: Dict, current_track: Dict) -> Tuple[bool, str]:
    """
    Algorithmic Vibe Check: Assesses if a requested song safely fits
    the current energy matrix and tempo of the dancefloor.

    Rules:
    1. BPM Delta: Maximum allowed difference is 5.0 BPM to avoid heavy distortion.
    2. Energy Delta: Maximum allowed difference is 3.0 to avoid abrupt vibe shifts.
    3. Harmonic Compatibility: Keys must be within 1 step on the Camelot Wheel or parallel.
    """
    # Rule 1: Tempo Check
    bpm_delta = abs(requested_track["bpm"] - current_track["bpm"])
    if bpm_delta > 5.0:
        return False, f"BPM clash too severe ({requested_track['bpm']} vs {current_track['bpm']}). Would cause audio warp distortion."

    # Rule 2: Energy Vibe Check
    energy_delta = abs(requested_track["energy"] - current_track["energy"])
    if energy_delta > 3.0:
         return False, "Energy delta error: Transition is too abrupt for the current floor vibe."

    # Rule 3: Harmonic Check
    if not is_harmonically_compatible(requested_track["key"], current_track["key"]):
        return False, f"Harmonic clash: {requested_track['key']} is not compatible with current track's {current_track['key']}."

    return True, "Track fits the sonic profile perfectly."

app = FastAPI(title="Algorithmic DJ Conductor Server")

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

            if action == "REQUEST_SONG":
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
                        found = True
                        break

                if found:
                    # Reorder queue based on votes
                    # In Phase 2, we might want more complex reordering that still considers FIT
                    # For now, just sort by votes descending.
                    dj_state.upcoming_queue.sort(key=lambda x: x["votes"], reverse=True)
                    await manager.broadcast_queue_update()
                else:
                    await websocket.send_json({"type": "ERROR", "message": "Track not found in queue."})

            else:
                await websocket.send_json({"type": "ERROR", "message": f"Unknown action: {action}"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        # Catch unexpected errors to prevent the endpoint from crashing silently
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Integration with auto_dj_script submodule
# This is a placeholder for background rendering tasks.
def run_offline_compiler_worker(source_dir: str, output_file: str, bpm: float):
    """
    Background worker that calls the submodule to crunch audio offline.
    """
    # Ensure submodule path is in sys.path
    submodule_path = os.path.abspath("./external/auto_dj_script")
    if submodule_path not in sys.path:
        sys.path.append(submodule_path)

    try:
        # Import Jules's core compilation engine directly
        # Note: We use a try-except here because the submodule might not be perfectly compatible yet.
        from auto_dj.compiler import compile_master_set
        compile_master_set(source_dir, output_file, bpm=bpm)
    except ImportError:
        print("Error: Could not import auto_dj.compiler from submodule.")
    except Exception as e:
        print(f"Error during offline compilation: {e}")

@app.post("/api/render-set")
async def render_compiled_set(background_tasks: BackgroundTasks, source_folder: str, output_path: str):
    """
    API endpoint that accepts a finalized room playlist and spins up
    the offline script in a background thread to render a high-quality mix.
    """
    # Delegate the heavy lifting to the submodule without blocking the main event loop
    background_tasks.add_task(run_offline_compiler_worker, source_folder, output_path, dj_state.target_bpm)

    return {"status": "processing", "message": "Submodule background worker initialized."}
