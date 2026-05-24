import asyncio
import io
import json
import os
import sqlite3
import sys
import time
from contextlib import asynccontextmanager
from typing import List, Dict, Optional, Tuple

import qrcode
import socket
import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException, Depends, status
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
    "VIBE_WEIGHT_BPM": 0.15,
    "VIBE_WEIGHT_ENERGY": 0.15,
    "VIBE_WEIGHT_RAMPING": 0.10,
    "VIBE_WEIGHT_KEY": 0.35,
    "VIBE_WEIGHT_GENRE": 0.25,
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
    """Helper to create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
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
