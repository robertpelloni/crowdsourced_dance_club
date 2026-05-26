import os
import json
import socket
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from src.db.database import get_db_connection

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Fallback for development only. Production must set this environment variable.
    SECRET_KEY = "dev_secret_key_change_me_in_production"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except: return 'localhost'

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise HTTPException(status_code=401)
    except: raise HTTPException(status_code=401)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row is None: raise HTTPException(status_code=401)
    return dict(row)

async def check_and_award_badges(user_id: str, dj_state: any):
    """
    Service to check user activity and award achievement badges.
    """
    if user_id == "anonymous": return

    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT points, streak, badges FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row: conn.close(); return

    points, streak, badges_json = row
    badges = json.loads(badges_json)
    new_badges = []

    # Early Bird: Engaged within the first 10 minutes of session (simulated by points > 0)
    if points > 0 and "Early Bird" not in badges:
        new_badges.append("Early Bird")

    # Super Voter: Voted 5+ times
    cursor.execute("SELECT COUNT(*) FROM user_votes WHERE user_id = ?", (user_id,))
    vote_count = cursor.fetchone()[0]
    if vote_count >= 5 and "Super Voter" not in badges:
        new_badges.append("Super Voter")

    # Vibe Architect: 3 successful requests
    cursor.execute("SELECT COUNT(*) FROM user_requests WHERE user_id = ? AND status = 'ACCEPTED'", (user_id,))
    req_count = cursor.fetchone()[0]
    if req_count >= 3 and "Vibe Architect" not in badges:
        new_badges.append("Vibe Architect")

    # Streak Master: 5 song streak
    if streak >= 5 and "Streak Master" not in badges:
        new_badges.append("Streak Master")

    if new_badges:
        all_badges = badges + new_badges
        cursor.execute("UPDATE users SET badges = ? WHERE id = ?", (json.dumps(all_badges), user_id))
        dj_state.user_stats[user_id]["badges"] = all_badges
        # Signal the WebSocket to notify the user (this will be handled in main.py)
        conn.commit(); conn.close()
        return new_badges

    conn.close()
    return []
