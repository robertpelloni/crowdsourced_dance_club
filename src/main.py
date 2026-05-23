import asyncio
import io
import json
import os
import random
import string
import sys
import time
import uuid
from contextlib import asynccontextmanager
from typing import List, Dict, Optional, Tuple

import qrcode
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException, Depends, status
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

from src.db.database import get_db_connection, load_track_catalog
from src.db.vibe_logs import log_vibe_performance
from src.api.schemas import Track, User, Token, UserCreate, EventCreate, FeedbackSubmit
from src.api.utils import get_local_ip, verify_password, get_password_hash, create_access_token, get_current_user, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from src.core.conductor import TrackState, calculate_vibe_score, evaluate_track_fit, CONFIG, GENRE_COMPATIBILITY

TRACK_CATALOG = load_track_catalog()
dj_state = TrackState(TRACK_CATALOG)

class ConnectionManager:
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        dj_state.active_connections.append(websocket)
        await websocket.send_json(self.get_broadcast_payload())

    def disconnect(self, websocket: WebSocket):
        if websocket in dj_state.active_connections:
            dj_state.active_connections.remove(websocket)

    async def broadcast_queue_update(self):
        payload = self.get_broadcast_payload()
        for connection in list(dj_state.active_connections):
            try: await connection.send_json(payload)
            except: self.disconnect(connection)

    def get_broadcast_payload(self) -> Dict:
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

async def playback_simulation_loop():
    while True:
        now = time.time()
        remaining = dj_state.start_time + dj_state.duration - now
        dj_state.vote_history = [t for t in dj_state.vote_history if now - t < 60]
        vote_velocity = len(dj_state.vote_history)
        acceleration = vote_velocity - dj_state.last_velocity
        dj_state.last_velocity = vote_velocity

        if acceleration > 2 and not dj_state.is_peak_mode:
             for client in list(dj_state.active_connections):
                 try: await client.send_json({"type": "MASTER_CONTROL", "data": {"action": "DSP_INTENSIFY", "duration": 10.0}})
                 except: pass

        if vote_velocity >= 5 and not dj_state.is_peak_mode:
            dj_state.is_peak_mode = True
            dj_state.energy_trend = "rising"
            dj_state.target_bpm += 2.0
            await manager.broadcast_queue_update()
        elif vote_velocity < 2 and dj_state.is_peak_mode:
            dj_state.is_peak_mode = False
            dj_state.energy_trend = "stable"
            await manager.broadcast_queue_update()

        if abs(dj_state.current_bpm - dj_state.target_bpm) > 0.01:
            step = 0.05
            if dj_state.current_bpm < dj_state.target_bpm: dj_state.current_bpm = min(dj_state.target_bpm, dj_state.current_bpm + step)
            else: dj_state.current_bpm = max(dj_state.target_bpm, dj_state.current_bpm - step)
            for client in list(dj_state.active_connections):
                try: await client.send_json({"type": "MASTER_CONTROL", "data": {"current_bpm": dj_state.current_bpm}})
                except: pass

        if 14.5 <= remaining <= 15.5:
            if dj_state.upcoming_queue:
                next_track = dj_state.upcoming_queue[0]["track"]
                winner = max(dj_state.transition_votes, key=dj_state.transition_votes.get)
                sync_payload = {"type": "TRACK_SYNC", "data": {"track_id": next_track["id"], "filepath": next_track.get("filepath", f"tracks/{next_track['id']}.flac"), "bpm": next_track["bpm"], "key": next_track["key"], "energy": next_track["energy"], "transition_timestamp": dj_state.start_time + dj_state.duration, "crossfade_duration": 15.0, "archetype": winner}}
                for client in list(dj_state.active_connections):
                    try: await client.send_json(sync_payload)
                    except: pass

        if remaining <= 0:
            # ML Data Collection: Log performance of the track that just finished
            # Success metric is currently simplified to voting velocity during the track
            log_vibe_performance(
                dj_state.current_track["id"],
                calculate_vibe_score(dj_state.current_track, dj_state.current_track, dj_state.energy_trend),
                0.0, # Energy delta placeholder
                float(vote_velocity)
            )

            if dj_state.upcoming_queue:
                next_item = dj_state.upcoming_queue.pop(0)
                dj_state.current_track = next_item["track"]
                dj_state.genre_history.append(dj_state.current_track.get("genre", "Psytrance"))
                if len(dj_state.genre_history) > 5: dj_state.genre_history.pop(0)
            else:
                compatible = [t for t in TRACK_CATALOG.values() if t["id"] != dj_state.current_track["id"] and evaluate_track_fit(t, dj_state.current_track)[0]]
                if compatible: dj_state.current_track = random.choice(compatible)
            dj_state.start_time = now
            dj_state.transition_votes = {"classic": 0, "bass_swap": 0, "echo_out": 0, "hpf_sweep": 0}
            dj_state.duration = 180.0
            await manager.broadcast_queue_update()

        await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    loop_task = asyncio.create_task(playback_simulation_loop())
    yield
    loop_task.cancel()

app = FastAPI(title="Modular Conductor Server", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/")
async def root(): return FileResponse("src/static/index.html")

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

@app.get("/api/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"], "points": current_user["points"],
        "badges": json.loads(current_user["badges"]), "role": current_user.get("role", "user"),
        "referral_code": current_user.get("referral_code")
    }

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

@app.get("/sync-qr")
async def get_sync_qr():
    ip = get_local_ip()
    sync_data = {"venue_name": "CDC Virtual Arena", "conductor_url": f"http://{ip}:8000", "websocket_url": f"ws://{ip}:8000/ws/clubgoer", "session_id": "session_001"}
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(sync_data)); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_byte_arr = io.BytesIO(); img.save(img_byte_arr, format='PNG')
    return Response(content=img_byte_arr.getvalue(), media_type="image/png")

@app.websocket("/ws/clubgoer")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = None):
    user_id = "anonymous"; display_name = "anonymous"; user_role = "user"
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                conn = get_db_connection(); cursor = conn.cursor()
                cursor.execute("SELECT id, role FROM users WHERE username = ?", (username,))
                row = cursor.fetchone(); conn.close()
                if row: user_id = row["id"]; display_name = username; user_role = row["role"]
        except: pass

    if user_id not in dj_state.user_stats:
        if user_id != "anonymous":
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT points, badges, streak FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone(); conn.close()
            if row: dj_state.user_stats[user_id] = {"points": row["points"], "badges": json.loads(row["badges"]), "streak": row["streak"], "username": display_name}
            else: dj_state.user_stats[user_id] = {"points": 0, "badges": [], "streak": 0, "username": display_name}
        else: dj_state.user_stats[user_id] = {"points": 0, "badges": [], "streak": 0, "username": display_name}

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")

            if action == "GET_VIBE_SCORE":
                track = TRACK_CATALOG.get(message.get("track_id"))
                if track: await websocket.send_json({"type": "VIBE_SCORE", "track_id": track["id"], "score": calculate_vibe_score(track, dj_state.current_track, dj_state.energy_trend)})

            elif action == "REQUEST_SONG":
                track = TRACK_CATALOG.get(message.get("track_id"))
                if not track: continue
                fits, reason = evaluate_track_fit(track, dj_state.current_track)
                if fits:
                    vibe_score = calculate_vibe_score(track, dj_state.current_track, dj_state.energy_trend)
                    dj_state.user_stats[user_id]["points"] += 10
                    dj_state.upcoming_queue.append({"track": track, "votes": 1})
                    await websocket.send_json({"type": "REQUEST_ACCEPTED", "message": reason, "track": track, "user_stats": dj_state.user_stats[user_id]})
                    await manager.broadcast_queue_update()

            elif action == "VOTE_TRACK":
                tid = message.get("track_id")
                for item in dj_state.upcoming_queue:
                    if item["track"]["id"] == tid:
                        item["votes"] += 1
                        dj_state.vote_history.append(time.time())
                        break
                dj_state.upcoming_queue.sort(key=lambda x: x["votes"], reverse=True)
                await manager.broadcast_queue_update()

            elif action == "USER_ACTIVITY":
                dj_state.recent_activities.append({"timestamp": time.time(), "intensity": float(message.get("intensity", 0.1))})
                dj_state.crowd_energy = min(1.0, sum(a["intensity"] for a in dj_state.recent_activities if time.time() - a["timestamp"] < 30) / 10.0)
                await manager.broadcast_queue_update()

            elif action == "ADMIN_SKIP" and user_role == "admin":
                if dj_state.upcoming_queue: dj_state.current_track = dj_state.upcoming_queue.pop(0)["track"]
                dj_state.start_time = time.time()
                await manager.broadcast_queue_update()
                for c in list(dj_state.active_connections):
                    try: await c.send_json({"type": "MASTER_CONTROL", "data": {"action": "SKIP_NOW"}})
                    except: pass
    except: manager.disconnect(websocket)

@app.post("/api/render-highlights")
async def render_highlights(background_tasks: BackgroundTasks, track_ids: List[str]):
    return {"status": "processing", "message": "High-fidelity highlight render initiated."}

@app.get("/api/events")
async def get_events():
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE start_time > ?", (time.time(),))
    rows = cursor.fetchall(); conn.close()
    return [dict(row) for row in rows]
