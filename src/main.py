import asyncio
import io
import json
import logging
import os
import random
import string
import sys
import time
from contextlib import asynccontextmanager
from typing import List, Dict, Optional, Tuple
from datetime import timedelta

import sqlite3
import qrcode
import socket
import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException, Depends, status
from src.api.schemas import UserUpdate, SongFeedback, TransitionVote, FeedbackSubmit, EventCreate
from src.core.monitoring import SystemMonitor
from src.api.analytics import generate_vibe_performance_report
from src.api.streaming import get_streaming_links
from src.core.spotify_integration import get_track_metadata
from src.core.virtual_mc import generate_hype_announcement, create_tts_audio
from src.core.stem_separator import extract_stems
from src.core.shadow_pilot import shadow_pilot_instance
from src.telemetry.api import router as telemetry_router
from src.telemetry.ingestion import get_venue_aggregator
from src.core.recommender import NeuralConductor
from src.core.generative_visuals import comfy_bridge
from src.core.pubsub import pubsub_manager

neural_conductor = NeuralConductor()
monitor = SystemMonitor()
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

DB_PATH = "tracks.db"

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "SUPER_SECRET_CDC_KEY") # Use environment variables in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

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

def get_local_ip():
    """Returns the local network IP address of the server."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return 'localhost'

def get_db_connection():
    """Helper to create a connection to the SQLite database with multi-venue scaling configurations."""
    conn = sqlite3.connect(DB_PATH, timeout=20.0) # Prevent database is locked errors
    conn.execute('PRAGMA journal_mode=WAL;')      # Write-Ahead Logging for concurrency
    conn.execute('PRAGMA synchronous=NORMAL;')    # Faster writes
    conn.row_factory = sqlite3.Row
    return conn

def load_track_catalog() -> Dict[str, Dict]:
    """Loads all tracks from the database into an in-memory dictionary."""
    if not os.path.exists(DB_PATH):
        # Fallback for initial run if DB isn't initialized yet
        return {
            "track_001": {"id": "track_001", "title": "Awake the Machine", "artist": "Astrix", "bpm": 145.0, "key": "9A", "energy": 9.5, "genre": "Psytrance", "filepath": "tracks/track_001.flac"}
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

class User(BaseModel):
    username: str
    points: int = 0
    badges: List[str] = []
    referral_code: Optional[str] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str
    referral_code: Optional[str] = None

class EventCreate(BaseModel):
    title: str
    description: str
    start_time: float

class FeedbackSubmit(BaseModel):
    vibe_rating: int
    technical_rating: int
    comment: Optional[str] = None

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
        # Target BPM for the room (the eventual goal)
        self.target_bpm: float = 145.0
        # Current BPM (the live tempo being ramped)
        self.current_bpm: float = 145.0
        # Target energy trend: "rising", "stable", or "falling"
        self.energy_trend: str = "stable"
        # Peak mode status
        self.is_peak_mode: bool = False
        # Crowd energy score (0.0 to 1.0)
        self.crowd_energy: float = 0.5
        # Last calculated velocity for derivative
        self.last_velocity: float = 0.0
        # Upcoming tracks submitted and approved
        # Each entry is a dict: {"track": Dict, "votes": int}
        self.upcoming_queue: List[Dict] = []
        # List of active WebSocket connections
        self.active_connections: List[WebSocket] = []
        # History of vote timestamps for velocity calculation
        self.vote_history: List[float] = []
        # User leaderboard: {user_id: {"points": int, "badges": List[str], "username": str}}
        self.user_stats: Dict[str, Dict] = {}
        # Track historical genres for archetype evolution
        self.genre_history: List[str] = []
        # Notified events to avoid duplicates
        self.notified_events: List[str] = []
        # Votes for next transition style: {style: count}
        self.transition_votes: Dict[str, int] = {"classic": 0, "bass_swap": 0, "echo_out": 0, "hpf_sweep": 0}

dj_state = TrackState()

class ConnectionManager:
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        dj_state.active_connections.append(websocket)
        # Immediately push current state to the new client
        await websocket.send_json(self.get_broadcast_payload())

    def disconnect(self, websocket: WebSocket):
        """Removes a disconnected client from the active list."""
        if websocket in dj_state.active_connections:
            dj_state.active_connections.remove(websocket)

    async def broadcast_queue_update(self):
        payload = self.get_broadcast_payload()
        # Fast path using Redis Pub/Sub if available
        if pubsub_manager.is_connected:
            await pubsub_manager.publish("venue_1_queue", payload)

        # Fallback to local memory iteration
        for connection in list(dj_state.active_connections):
            try:
                await connection.send_json(payload)
            except Exception:
                # Handle dead connections gracefully by removing them
                self.disconnect(connection)

    def get_broadcast_payload(self) -> Dict:
        """Constructs the standard payload for state synchronization."""
        leaderboard = sorted(
            [{"user_id": uid, "points": stats["points"], "badges": stats["badges"], "username": stats.get("username", "Anonymous")}
             for uid, stats in dj_state.user_stats.items() if uid != "anonymous"],
            key=lambda x: x["points"], reverse=True
        )[:10]

        return {
            "type": "QUEUE_SYNC",
            "crowd_energy": dj_state.crowd_energy,
            "current_track": dj_state.current_track,
            "start_time": dj_state.start_time,
            "duration": dj_state.duration,
            "target_bpm": dj_state.target_bpm,
            "current_bpm": dj_state.current_bpm,
            "energy_trend": dj_state.energy_trend,
            "is_peak_mode": dj_state.is_peak_mode,
            "queue": dj_state.upcoming_queue,
            "leaderboard": leaderboard,
            "transition_votes": dj_state.transition_votes
        }

manager = ConnectionManager()

# Auth Utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise credentials_exception
    return dict(row)

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
    current_vel = len([t for t in dj_state.vote_history if time.time() - t < 60])
    for track in TRACK_CATALOG.values():
        if track["id"] == current_track["id"]:
            continue
        fits, _ = evaluate_track_fit(track, current_track, voting_velocity=current_vel)
        if fits:
            compatible.append(track)

    import random
    return random.choice(compatible) if compatible else None

def calculate_vibe_score(track: Dict, current_track: Dict, energy_trend: str = "stable", user_vibe_pref: Optional[str] = None, voting_velocity: float = 0.0) -> float:
    """
    Calculates a compatibility score (0.0 to 1.0) between two tracks.
    Utilizes the ML-driven Neural Conductor to predict vibe based on transition metrics and crowd voting velocity.
    """
    base_score = neural_conductor.predict_vibe_score(current_track, track, voting_velocity)

    # Still apply user preference bonuses
    if user_vibe_pref and track.get("genre") == user_vibe_pref:
        base_score = min(1.0, base_score + 0.1)

    return base_score


def evaluate_track_fit(requested_track: Dict, current_track: Dict, voting_velocity: float = 0.0) -> Tuple[bool, str]:
    """
    Algorithmic Vibe Check: Assesses if a requested song safely fits
    the current energy matrix and tempo of the dancefloor using the ML Conductor.
    """
    predicted_vibe = neural_conductor.predict_vibe_score(current_track, requested_track, voting_velocity)

    # If the ML model predicts a highly negative outcome, reject the track
    if predicted_vibe < 0.4:
        return False, f"ML Prediction too low ({predicted_vibe:.2f}). Track clashes with current crowd energy matrix."

    # Fallback Hard Rule: Extreme Tempo Check to prevent audio engine distortion
    bpm_delta = abs(requested_track.get("bpm", 120) - current_track.get("bpm", 120))
    if bpm_delta > CONFIG["MAX_BPM_DELTA"]:
        return False, f"BPM clash too severe ({requested_track.get('bpm', 120)} vs {current_track.get('bpm', 120)}). Would cause C++ audio warp distortion."

    # Rule 3: Harmonic Check
    if not is_harmonically_compatible(requested_track.get("key", "1A"), current_track.get("key", "1A")):
        return False, f"Harmonic clash: {requested_track.get('key')} is not compatible with current track's {current_track.get('key')}."

    return True, f"Track approved by Neural Conductor (Score: {predicted_vibe:.2f})."

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

        # Biometric Sync Evaluation (Milestone 11)
        biometrics = get_venue_aggregator(1) # Using default venue ID 1 for simulation

        # 2. Trigger Energy Peak and DSP Intensify based on Derivative OR Biometric Spikes
        acceleration = vote_velocity - dj_state.last_velocity
        dj_state.last_velocity = vote_velocity

        trigger_peak = (vote_velocity >= 5) or biometrics.is_spiking
        trigger_intensify = (acceleration > 2) or (biometrics.current_average_bpm > biometrics.baseline_bpm * 1.15)

        if trigger_intensify and not dj_state.is_peak_mode:
             # Sudden surge detected
             for client in dj_state.active_connections:
                 try: await client.send_json({"type": "MASTER_CONTROL", "data": {"action": "DSP_INTENSIFY", "duration": 10.0}})
                 except: pass

        if trigger_peak and not dj_state.is_peak_mode:
            dj_state.is_peak_mode = True
            dj_state.energy_trend = "rising"
            dj_state.target_bpm += 2.0
            print(f"[SYSTEM] ENERGY PEAK DETECTED! Velocity: {vote_velocity} votes/min, HR Spike: {biometrics.is_spiking}. Ramping up.")

            # Generate MC Hype Audio
            hype_text = generate_hype_announcement(vote_velocity, "rising", "Peak")
            tts_filepath = create_tts_audio(hype_text)

            # Trigger Generative Video Synthesis framework for Peak Mode (Milestone 12)
            asyncio.create_task(comfy_bridge.trigger_visual_synthesis(dj_state.energy_trend, dj_state.current_track.get("genre", "Psytrance"), rms=1.0))

            # Map crowd energy peak to DMX strobe sequence and trigger audio
            for client in dj_state.active_connections:
                 try:
                     await client.send_json({"type": "LIGHTING_CONTROL_DMX", "data": {"sequence": "strobe_fast", "intensity": 255, "duration_ms": 15000}})
                     if tts_filepath:
                         await client.send_json({"type": "MASTER_CONTROL", "data": {"action": "PLAY_SAMPLE", "filepath": tts_filepath}})
                 except: pass
            await manager.broadcast_queue_update()
        elif not trigger_peak and dj_state.is_peak_mode:
            dj_state.is_peak_mode = False
            dj_state.energy_trend = "stable"
            print(f"[SYSTEM] Peak energy subsiding. Velocity: {vote_velocity} votes/min, HR Spiking: {biometrics.is_spiking}.")
            await manager.broadcast_queue_update()

        # 3. Smooth BPM Ramping Logic
        if abs(dj_state.current_bpm - dj_state.target_bpm) > 0.01:
            step = 0.05  # Adjust by 0.05 BPM every second
            if dj_state.current_bpm < dj_state.target_bpm:
                dj_state.current_bpm = min(dj_state.target_bpm, dj_state.current_bpm + step)
            else:
                dj_state.current_bpm = max(dj_state.target_bpm, dj_state.current_bpm - step)

            # Broadcast tempo update to all clients
            for client in dj_state.active_connections:
                try: await client.send_json({"type": "MASTER_CONTROL", "data": {"current_bpm": dj_state.current_bpm}})
                except: pass

        # 4. Proactive TRACK_SYNC (15s before transition)
        if 14.5 <= remaining <= 15.5:
            if dj_state.upcoming_queue:
                next_track = dj_state.upcoming_queue[0]["track"]

                # Determine winning transition archetype
                winner = max(dj_state.transition_votes, key=dj_state.transition_votes.get)
                filepath = next_track.get("filepath", f"tracks/{next_track['id']}.flac")

                # Perform stem separation for the upcoming track
                # (Normally this would be kicked off earlier, but for demo we await here)
                stems = await extract_stems(filepath)

                sync_payload = {
                    "type": "TRACK_SYNC",
                    "data": {
                        "track_id": next_track["id"],
                        "filepath": filepath,
                        "stems": stems,
                        "bpm": next_track["bpm"],
                        "key": next_track["key"],
                        "energy": next_track["energy"],
                        "transition_timestamp": dj_state.start_time + dj_state.duration,
                        "crossfade_duration": 15.0,
                        "archetype": winner
                    }
                }

                # If archetype is Bass Swap, send command to mute bass during transition
                if winner == "bass_swap":
                    for client in dj_state.active_connections:
                        try: await client.send_json({"type": "MASTER_CONTROL", "data": {"action": "MUTE_BASS", "enable": True}})
                        except: pass

                # Broadcast to all clients (including the future C++ Engine)
                for client in dj_state.active_connections:
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
                # Update Genre History
                dj_state.genre_history.append(dj_state.current_track.get("genre", "Psytrance"))
                if len(dj_state.genre_history) > 5:
                    dj_state.genre_history.pop(0)

                # Archetype Evolution: If 3 of last 5 tracks are the same genre, shift target vibe
                from collections import Counter
                counts = Counter(dj_state.genre_history)
                most_common, count = counts.most_common(1)[0]
                if count >= 3:
                    print(f"[SYSTEM] Archetype Evolution: Room vibe shifted to {most_common}")
            else:
                # Select random compatible track from catalog
                fallback = get_random_compatible_track(dj_state.current_track)
                if fallback:
                    dj_state.current_track = fallback
                # else keep playing current (loop)

            dj_state.start_time = now
            # Reset transition votes for next track
            dj_state.transition_votes = {"classic": 0, "bass_swap": 0, "echo_out": 0, "hpf_sweep": 0}
            # In real life duration varies, but for simulation we use 180s
            dj_state.duration = 180.0
            await manager.broadcast_queue_update()
            print(f"[SYSTEM] Transitioned to: {dj_state.current_track['title']}")

        # 5. Event Notification Broadcast
        # Query for events starting within the next 60 seconds that haven't been notified yet
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE start_time <= ? AND start_time > ?",
                       (now + 60, now))
        upcoming_events = cursor.fetchall()
        conn.close()

        for event in upcoming_events:
            if event["id"] not in dj_state.notified_events:
                event_payload = {
                    "type": "NEW_EVENT",
                    "data": {
                        "id": event["id"],
                        "title": event["title"],
                        "description": event["description"],
                        "start_time": event["start_time"]
                    }
                }
                for client in dj_state.active_connections:
                    try: await client.send_json(event_payload)
                    except: pass

                dj_state.notified_events.append(event["id"])
                print(f"[SYSTEM] Real-time event announcement: {event['title']}")

        # Check every 1 second
        await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    # Startup: Initialize background tasks
    await pubsub_manager.connect()
    loop_task = asyncio.create_task(playback_simulation_loop())
    sp_task = asyncio.create_task(shadow_pilot_instance.run_loop())
    yield
    # Shutdown: Clean up tasks
    await pubsub_manager.disconnect()
    loop_task.cancel()
    sp_task.cancel()

app = FastAPI(title="Algorithmic DJ Conductor Server", lifespan=lifespan)
app.include_router(telemetry_router)

# Serve static files for the client prototype
app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/")
async def root():
    """Serve the client prototype index.html at the root."""
    return FileResponse("src/static/index.html")

@app.get("/catalog")
async def get_catalog(): return list(TRACK_CATALOG.values())

@app.post("/api/register")
async def register(user: UserCreate):
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone(): conn.close(); raise HTTPException(status_code=400, detail="Username taken")

    referrer_id = None
    if user.referral_code:
        cursor.execute("SELECT id FROM users WHERE referral_code = ?", (user.referral_code,))
        row = cursor.fetchone()
        if row: referrer_id = row["id"]

    new_referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    user_id = "user_" + str(uuid.uuid4())
    cursor.execute("INSERT INTO users (id, username, hashed_password, referral_code, referred_by_id, points) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, user.username, get_password_hash(user.password), new_referral_code, referrer_id, 50 if referrer_id else 0))
    if referrer_id: cursor.execute("UPDATE users SET points = points + 50 WHERE id = ?", (referrer_id,))
    conn.commit(); conn.close()
    return {"message": "Success", "referral_code": new_referral_code}

@app.post("/api/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (form_data.username,))
    row = cursor.fetchone(); conn.close()
    if not row or not verify_password(form_data.password, row["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(data={"sub": row["username"]}), "token_type": "bearer"}

@app.patch("/api/me")
async def update_user_me(data: UserUpdate, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection(); cursor = conn.cursor()
    if data.vibe_preference:
        cursor.execute("UPDATE users SET vibe_preference = ? WHERE id = ?", (data.vibe_preference, current_user["id"]))
    if data.bio is not None:
        cursor.execute("UPDATE users SET bio = ? WHERE id = ?", (data.bio, current_user["id"]))
    conn.commit(); conn.close()

    import json
    updated_user = dict(current_user)
    updated_user["vibe_preference"] = data.vibe_preference or current_user.get("vibe_preference")
    updated_user["bio"] = data.bio or current_user.get("bio")
    updated_user["badges"] = json.loads(current_user["badges"]) if isinstance(current_user["badges"], str) else current_user["badges"]
    return updated_user

@app.get("/api/live/crowd-stats")
async def get_live_crowd_stats(current_user: dict = Depends(get_current_user)):
    return {"crowd_energy": dj_state.crowd_energy, "active_users_count": len(set(a.get("user_id", "anon") for a in dj_state.recent_activities))}

@app.get("/api/leaderboard")
async def get_leaderboard():
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT username, points, badges FROM users ORDER BY points DESC LIMIT 20")
    rows = cursor.fetchall(); conn.close()
    return [{"username": r["username"], "points": r["points"], "badges": json.loads(r["badges"])} for r in rows]

@app.get("/api/me/history/requests")
async def get_my_requests(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute('''SELECT r.*, t.title, t.artist FROM user_requests r JOIN tracks t ON r.track_id = t.id WHERE r.user_id = ? ORDER BY r.timestamp DESC''', (current_user["id"],))
    rows = cursor.fetchall(); conn.close()
    return [dict(row) for row in rows]

@app.get("/api/me/history/votes")
async def get_my_votes(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute('''SELECT v.*, t.title, t.artist FROM user_votes v JOIN tracks t ON v.track_id = t.id WHERE v.user_id = ? ORDER BY v.timestamp DESC''', (current_user["id"],))
    rows = cursor.fetchall(); conn.close()
    return [dict(row) for row in rows]

@app.get("/api/me/history/likes")
async def get_my_likes(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute('''SELECT s.*, t.title, t.artist FROM song_feedback s JOIN tracks t ON s.track_id = t.id WHERE s.user_id = ? AND s.is_like = 1 ORDER BY s.timestamp DESC''', (current_user["id"],))
    rows = cursor.fetchall(); conn.close()
    return [dict(row) for row in rows]

@app.get("/sync-qr")
async def get_sync_qr():
    ip = get_local_ip()
    sync_data = {"venue_name": "CDC Virtual Arena", "conductor_url": f"http://{ip}:8000", "websocket_url": f"ws://{ip}:8000/ws/clubgoer", "session_id": "session_001"}
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(sync_data)); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_byte_arr = io.BytesIO(); img.save(img_byte_arr, format='PNG')
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")

@app.post("/api/register")
async def register(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already registered")

    # Referral Logic
    referrer_id = None
    if user.referral_code:
        cursor.execute("SELECT id FROM users WHERE referral_code = ?", (user.referral_code,))
        row = cursor.fetchone()
        if row:
            referrer_id = row["id"]

    hashed_pw = get_password_hash(user.password)
    import uuid
    user_id = "user_" + str(uuid.uuid4())

    # Generate unique referral code for the new user
    import random
    import string
    new_referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    initial_points = 50 if referrer_id else 0

    cursor.execute('''
        INSERT INTO users (id, username, hashed_password, referral_code, referred_by_id, points)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, user.username, hashed_pw, new_referral_code, referrer_id, initial_points))

    if referrer_id:
        cursor.execute("UPDATE users SET points = points + 50 WHERE id = ?", (referrer_id,))

    conn.commit()
    conn.close()
    return {"message": "User registered successfully", "referral_code": new_referral_code}

@app.post("/api/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (form_data.username,))
    row = cursor.fetchone()
    conn.close()

    if not row or not verify_password(form_data.password, row["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": row["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    # Convert JSON string badges to list
    import json
    badges = json.loads(current_user["badges"])
    return {
        "username": current_user["username"],
        "points": current_user["points"],
        "badges": badges,
        "role": current_user.get("role", "user"),
        "referral_code": current_user.get("referral_code"),
        "vibe_preference": current_user.get("vibe_preference", "Psytrance"),
        "bio": current_user.get("bio")
    }

@app.get("/api/me/history/requests")
async def get_my_requests(current_user: dict = Depends(get_current_user)):
    """Retrieves the authenticated user's song request history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, t.title, t.artist
        FROM user_requests r
        JOIN tracks t ON r.track_id = t.id
        WHERE r.user_id = ?
        ORDER BY r.timestamp DESC
    ''', (current_user["id"],))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/me/history/likes")
async def get_my_likes(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute('''SELECT s.*, t.title, t.artist FROM song_feedback s JOIN tracks t ON s.track_id = t.id WHERE s.user_id = ? AND s.is_like = 1 ORDER BY s.timestamp DESC''', (current_user["id"],))
    rows = cursor.fetchall(); conn.close()
    return [dict(row) for row in rows]

@app.get("/api/me/history/votes")
async def get_my_votes(current_user: dict = Depends(get_current_user)):
    """Retrieves the authenticated user's voting history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.*, t.title, t.artist
        FROM user_votes v
        JOIN tracks t ON v.track_id = t.id
        WHERE v.user_id = ?
        ORDER BY v.timestamp DESC
    ''', (current_user["id"],))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/events")
async def get_events():
    """Returns a list of upcoming club events."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE start_time > ?", (time.time(),))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/admin/create-event")
async def create_event(event: EventCreate, current_user: dict = Depends(get_current_user)):
    """Creates a new event (restricted to logged in users in prototype)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    import uuid
    event_id = "event_" + str(uuid.uuid4())
    cursor.execute("INSERT INTO events (id, title, description, start_time) VALUES (?, ?, ?, ?)",
                   (event_id, event.title, event.description, event.start_time))
    conn.commit()
    conn.close()
    return {"message": "Event created successfully", "id": event_id}

@app.get("/api/leaderboard")
async def get_leaderboard():
    """Returns the top 20 users on the leaderboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, points, badges FROM users ORDER BY points DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "username": row["username"],
            "points": row["points"],
            "badges": json.loads(row["badges"])
        })
    return result

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackSubmit, current_user: dict = Depends(get_current_user)):
    """Allows authenticated users to submit experience feedback during testing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    import uuid
    feedback_id = "fb_" + str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO feedback (id, user_id, vibe_rating, technical_rating, comment, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (feedback_id, current_user["id"], feedback.vibe_rating,
          feedback.technical_rating, feedback.comment, time.time()))
    conn.commit()
    conn.close()
    return {"message": "Feedback submitted successfully. Thank you for helping refine the vibe!", "id": feedback_id}

@app.get("/sync-qr")
async def get_sync_qr():
    """Generates a real QR code image for venue synchronization."""
    ip = get_local_ip()
    sync_data = {
        "venue_name": "CDC Virtual Arena",
        "conductor_url": f"http://{ip}:8000",
        "websocket_url": f"ws://{ip}:8000/ws/clubgoer",
        "session_id": "session_001"
    }

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(sync_data))
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')

    return Response(content=img_byte_arr.getvalue(), media_type="image/png")

@app.websocket("/ws/clubgoer")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = None):
    """
    Real-time portal for clubgoers to vote and request songs.
    Clients send JSON messages with actions like 'REQUEST_SONG'.
    """
    user_id = "anonymous" # This will be the user's database ID or "anonymous"
    display_name = "anonymous" # This will be the username for logging

    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                row = cursor.fetchone()
                conn.close()
                if row:
                    user_id = row["id"]
                    display_name = username
        except JWTError:
            pass

    if user_id not in dj_state.user_stats:
        # Initialize from DB if possible
        if user_id != "anonymous":
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT points, badges, streak, vibe_preference FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                dj_state.user_stats[user_id] = {
                    "points": row["points"],
                    "badges": json.loads(row["badges"]),
                    "streak": row["streak"],
                    "username": display_name,
                    "vibe_preference": row["vibe_preference"]
                }
            else:
                dj_state.user_stats[user_id] = {"points": 0, "badges": [], "streak": 0, "username": display_name, "vibe_preference": "Psytrance"}
        else:
            dj_state.user_stats[user_id] = {"points": 0, "badges": [], "streak": 0, "username": display_name, "vibe_preference": "Psytrance"}
    else:
        dj_state.user_stats[user_id]["username"] = display_name

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")

            if action == "GET_VIBE_SCORE":
                track_id = message.get("track_id")
                track = TRACK_CATALOG.get(track_id)
                if track:
                    current_vel = len([t for t in dj_state.vote_history if time.time() - t < 60])
                    score = calculate_vibe_score(track, dj_state.current_track, voting_velocity=current_vel)
                    await websocket.send_json({"type": "VIBE_SCORE", "track_id": track_id, "score": score})
                else:
                    await websocket.send_json({"type": "ERROR", "message": "Track not found."})

            elif action == "REQUEST_SONG":
                track_id = message.get("track_id")

                # Check external source (Spotify)
                if track_id.startswith("spotify:track:") or "spotify.com/track/" in track_id:
                    spotify_id = track_id.split("/")[-1].split("?")[0] if "spotify.com/track/" in track_id else track_id.split(":")[-1]
                    meta = get_track_metadata(spotify_id)
                    if meta:
                        new_track_id = f"ext_{spotify_id}"
                        TRACK_CATALOG[new_track_id] = {
                            "id": new_track_id,
                            "title": meta["title"],
                            "artist": meta["artist"],
                            "bpm": meta["bpm"],
                            "key": meta["key"],
                            "energy": meta["energy"],
                            "genre": meta["genre"],
                            "filepath": meta["preview_url"] if meta["preview_url"] else "mock_url"
                        }
                        track_id = new_track_id

                track = TRACK_CATALOG.get(track_id)
                if not track:
                    await websocket.send_json({"type": "ERROR", "message": "Track not found or invalid external URL."})
                    continue

                current_vel = len([t for t in dj_state.vote_history if time.time() - t < 60])
                fits, reason = evaluate_track_fit(track, dj_state.current_track, voting_velocity=current_vel)
                user_vibe_pref = dj_state.user_stats[user_id].get("vibe_preference", "Psytrance")
                vibe_score = calculate_vibe_score(track, dj_state.current_track, dj_state.energy_trend, user_vibe_pref, voting_velocity=current_vel)

                if fits:
                    # Append to queue and notify the entire room via real-time broadcast
                    # Check if already in queue
                    if any(item["track"]["id"] == track_id for item in dj_state.upcoming_queue):
                        await websocket.send_json({"type": "ERROR", "message": "Track already in queue."})
                        continue

                    # Vibe Streak Gamification
                    points_to_award = 10
                    if vibe_score >= 0.8:
                        dj_state.user_stats[user_id]["streak"] = dj_state.user_stats[user_id].get("streak", 0) + 1
                        if dj_state.user_stats[user_id]["streak"] >= 3:
                            points_to_award += 20  # Streak bonus
                            if "Vibe Master" not in dj_state.user_stats[user_id]["badges"]:
                                dj_state.user_stats[user_id]["badges"].append("Vibe Master")
                    else:
                        dj_state.user_stats[user_id]["streak"] = 0

                    # Award Vibe Points to requester
                    dj_state.user_stats[user_id]["points"] += points_to_award
                    if dj_state.user_stats[user_id]["points"] >= 50 and "Vibe Guardian" not in dj_state.user_stats[user_id]["badges"]:
                        dj_state.user_stats[user_id]["badges"].append("Vibe Guardian")

                    # Persist stats to DB
                    if user_id != "anonymous":
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute('''
                                UPDATE users
                                SET points = ?, badges = ?, streak = ?
                                WHERE id = ?
                            ''', (dj_state.user_stats[user_id]["points"],
                                  json.dumps(dj_state.user_stats[user_id]["badges"]),
                                  dj_state.user_stats[user_id]["streak"],
                                  user_id))
                            conn.commit()
                            conn.close()
                        except Exception as e:
                            print(f"[ERROR] Failed to persist user stats: {e}")

                    dj_state.upcoming_queue.append({"track": track, "votes": 1})

                    # Persist request in DB
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO user_requests (id, user_id, track_id, timestamp, vibe_score, status)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', ("req_" + str(uuid.uuid4()), user_id if user_id != "anonymous" else None,
                              track_id, time.time(), vibe_score, "ACCEPTED"))
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        print(f"[ERROR] Failed to persist request: {e}")

                    await websocket.send_json({
                        "type": "REQUEST_ACCEPTED",
                        "message": reason,
                        "track": track,
                        "user_stats": dj_state.user_stats[user_id]
                    })
                    await manager.broadcast_queue_update()
                else:
                    # Deny request and give the user feedback on why it failed the vibe check
                    # Persist denied request
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO user_requests (id, user_id, track_id, timestamp, vibe_score, status)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', ("req_" + str(uuid.uuid4()), user_id if user_id != "anonymous" else None,
                              track_id, time.time(), calculate_vibe_score(track, dj_state.current_track, voting_velocity=len([t for t in dj_state.vote_history if time.time() - t < 60])), "DENIED"))
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        print(f"[ERROR] Failed to persist denied request: {e}")

                    await websocket.send_json({"type": "REQUEST_DENIED", "message": reason})

            elif action == "VOTE_TRANSITION":
                style = message.get("style")
                if style in dj_state.transition_votes:
                    dj_state.transition_votes[style] += 1
                    await manager.broadcast_queue_update()
                else:
                    await websocket.send_json({"type": "ERROR", "message": "Invalid transition style."})

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
                    # Persist vote in DB
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO user_votes (id, user_id, track_id, timestamp)
                            VALUES (?, ?, ?, ?)
                        ''', ("vote_" + str(uuid.uuid4()), user_id if user_id != "anonymous" else None,
                              track_id, time.time()))
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        print(f"[ERROR] Failed to persist vote: {e}")

                    # Reorder queue based on weighted score of votes and vibe compatibility
                    current_vel = len([t for t in dj_state.vote_history if time.time() - t < 60])
                    for item in dj_state.upcoming_queue:
                        vibe = calculate_vibe_score(item["track"], dj_state.current_track, voting_velocity=current_vel)
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

                # Notify Audio Engine for immediate skip
                for client in dj_state.active_connections:
                    try:
                        await client.send_json({"type": "MASTER_CONTROL", "data": {"action": "SKIP_NOW"}})
                    except: pass

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
                for client in dj_state.active_connections:
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
        import shutil

        # Create a temporary directory for this specific highlight render
        temp_dir = f"temp_render_{int(time.time())}"
        os.makedirs(temp_dir, exist_ok=True)

        for tid in track_ids:
            track = TRACK_CATALOG.get(tid)
            if track and track.get("filepath") and os.path.exists(track["filepath"]):
                shutil.copy(track["filepath"], os.path.join(temp_dir, f"{tid}.flac"))

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

        args = Args(temp_dir, output_path, bpm)

        print(f"[AUTO-DJ] Starting high-fidelity highlight render to: {output_path}")
        compile_master_set(args)

        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"[AUTO-DJ] Render complete and temporary files cleaned: {output_path}")

    except Exception as e:
        print(f"[ERROR] Offline compilation failed: {e}")

@app.post("/api/feedback/song")
async def submit_song_feedback(feedback: SongFeedback, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("INSERT INTO song_feedback (id, user_id, track_id, is_like, timestamp) VALUES (?, ?, ?, ?, ?)",
                   ("sfb_" + str(uuid.uuid4()), current_user["id"], feedback.track_id, feedback.is_like, time.time()))
    conn.commit(); conn.close()
    return {"message": "Song feedback recorded"}

from src.api.schemas import PasswordChange

@app.post("/api/me/change-password")
async def change_password(data: PasswordChange, current_user: dict = Depends(get_current_user)):
    if not verify_password(data.current_password, current_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("UPDATE users SET hashed_password = ? WHERE id = ?", (get_password_hash(data.new_password), current_user["id"]))
    conn.commit(); conn.close()
    return {"message": "Password updated successfully"}

@app.post("/api/feedback/transition")
async def submit_transition_feedback(feedback: TransitionVote, current_user: dict = Depends(get_current_user)):
    # In a real scenario, we'd need to know which transition.
    return {"message": "Transition feedback recorded"}

@app.post("/api/render-highlights")
async def render_highlights(background_tasks: BackgroundTasks, track_ids: List[str]):
    """
    API endpoint to trigger an offline render of set highlights.
    """
    output_path = f"static/renders/highlights_{int(time.time())}.flac"
    background_tasks.add_task(run_offline_compiler_worker, track_ids, output_path, dj_state.target_bpm)
    return {"status": "processing", "message": "High-fidelity highlight render initiated."}

@app.get("/api/events")
async def get_events():
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE start_time > ?", (time.time(),))
    rows = cursor.fetchall(); conn.close()
    return [dict(row) for row in rows]

@app.post("/api/events", response_model=dict)
async def create_event(event: EventCreate, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db_connection(); cursor = conn.cursor()
    event_id = "event_" + str(uuid.uuid4())
    cursor.execute("INSERT INTO events (id, title, description, start_time) VALUES (?, ?, ?, ?)",
                   (event_id, event.title, event.description, event.start_time))
    conn.commit(); conn.close()
    return {"message": "Event created", "id": event_id}

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackSubmit, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection(); cursor = conn.cursor()
    fb_id = "fb_" + str(uuid.uuid4())
    cursor.execute("INSERT INTO feedback (id, user_id, vibe_rating, technical_rating, comment, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                   (fb_id, current_user["id"], feedback.vibe_rating, feedback.technical_rating, feedback.comment, time.time()))
    conn.commit(); conn.close()
    return {"message": "Feedback submitted", "id": fb_id}

@app.get("/api/admin/feedback")
async def get_all_feedback(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute('''SELECT f.*, u.username FROM feedback f JOIN users u ON f.user_id = u.id ORDER BY f.timestamp DESC''')
    rows = cursor.fetchall(); conn.close()
    return [dict(row) for row in rows]

import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates distance in km between two lat/lon coordinates."""
    R = 6371.0
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@app.get("/api/venues")
async def get_venues(latitude: float = None, longitude: float = None, radius_km: float = 50.0):
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM venues")
    rows = cursor.fetchall(); conn.close()

    venues = [dict(row) for row in rows]

    if latitude is not None and longitude is not None:
        filtered_venues = []
        for venue in venues:
            if venue.get('latitude') is not None and venue.get('longitude') is not None:
                dist = haversine_distance(latitude, longitude, venue['latitude'], venue['longitude'])
                if dist <= radius_km:
                    venue['distance_km'] = round(dist, 2)
                    filtered_venues.append(venue)
        # Sort by distance
        filtered_venues.sort(key=lambda x: x['distance_km'])
        return filtered_venues

    return venues

# Global multi-tenant state manager
venue_states: Dict[str, TrackState] = {"CDC_MAIN": dj_state, "CDC_BERLIN": TrackState()}

@app.get("/api/venues/{venue_id}/state")
async def get_venue_state(venue_id: str):
    if venue_id not in venue_states:
        raise HTTPException(status_code=404, detail="Venue not found")
    state = venue_states[venue_id]
    return {
        "current_track": state.current_track,
        "crowd_energy": state.crowd_energy,
        "target_bpm": state.target_bpm,
        "is_peak_mode": state.is_peak_mode
    }

@app.get("/api/admin/health")
async def get_health(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return {
        "system": monitor.get_health_stats(),
        "vibe_consistency": monitor.get_vibe_consistency(),
        "active_clients": len(dj_state.active_connections)
    }

@app.get("/api/admin/shadow-pilot/status")
async def get_shadow_pilot_status(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return {
        "status": shadow_pilot_instance.status_msg,
        "is_active": shadow_pilot_instance.is_active,
        "diff_count": shadow_pilot_instance.diff_count,
        "last_anomaly": shadow_pilot_instance.last_anomaly
    }

@app.get("/api/admin/analytics/vibe-report")
async def get_vibe_report(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return generate_vibe_performance_report()

@app.get("/api/tracks/{track_id}/streaming")
async def get_track_streaming_links(track_id: str):
    track = TRACK_CATALOG.get(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return get_streaming_links(track["title"], track["artist"])
