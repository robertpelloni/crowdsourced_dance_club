import sqlite3
import os
from typing import Dict

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
            "track_001": {"id": "track_001", "title": "Awake the Machine", "artist": "Astrix", "bpm": 145.0, "key": "9A", "energy": 9.5, "genre": "Psytrance", "filepath": "tracks/track_001.flac"}
        }

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracks")
    rows = cursor.fetchall()
    conn.close()

    return {row["id"]: dict(row) for row in rows}
