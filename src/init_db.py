import sqlite3
import os
import time

DB_PATH = "tracks.db"

def init_db():
    if os.path.exists(DB_PATH): os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
    cursor.execute('''CREATE TABLE tracks (id TEXT PRIMARY KEY, title TEXT, artist TEXT, bpm REAL, key TEXT, energy REAL, genre TEXT, filepath TEXT)''')
    cursor.execute('''CREATE TABLE users (id TEXT PRIMARY KEY, username TEXT UNIQUE, hashed_password TEXT, points INTEGER DEFAULT 0, badges TEXT DEFAULT '[]', streak INTEGER DEFAULT 0, role TEXT DEFAULT 'user', referral_code TEXT UNIQUE, referred_by_id TEXT, FOREIGN KEY (referred_by_id) REFERENCES users (id))''')
    cursor.execute('''CREATE TABLE events (id TEXT PRIMARY KEY, title TEXT, description TEXT, start_time REAL, venue_id TEXT DEFAULT 'CDC_MAIN')''')
    cursor.execute('''CREATE TABLE feedback (id TEXT PRIMARY KEY, user_id TEXT, vibe_rating INTEGER, technical_rating INTEGER, comment TEXT, timestamp REAL, FOREIGN KEY (user_id) REFERENCES users (id))''')
    cursor.execute('''CREATE TABLE user_requests (id TEXT PRIMARY KEY, user_id TEXT, track_id TEXT, timestamp REAL, vibe_score REAL, status TEXT, FOREIGN KEY (user_id) REFERENCES users (id), FOREIGN KEY (track_id) REFERENCES tracks (id))''')
    cursor.execute('''CREATE TABLE user_votes (id TEXT PRIMARY KEY, user_id TEXT, track_id TEXT, timestamp REAL, FOREIGN KEY (user_id) REFERENCES users (id), FOREIGN KEY (track_id) REFERENCES tracks (id))''')
    cursor.execute('''CREATE TABLE vibe_performance_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, track_id TEXT, vibe_score REAL, energy_delta REAL, success_metric REAL, timestamp REAL)''')

    tracks = [("track_001", "Awake the Machine", "Astrix", 145.0, "9A", 9.5, "Psytrance", "tracks/track_001.flac"),
              ("track_002", "Universal Frequencies", "Alienatic", 145.0, "10A", 8.8, "Psytrance", "tracks/track_002.flac"),
              ("track_003", "Interstellar Journey", "Electric Universe", 142.0, "11A", 7.5, "Psytrance", "tracks/track_003.flac"),
              ("track_004", "Cosmic Gateways", "Avalon", 144.0, "8A", 8.2, "Psytrance", "tracks/track_004.flac"),
              ("track_005", "Vibrational Shift", "Tristan", 146.0, "7A", 9.0, "Psytrance", "tracks/track_005.flac"),
              ("track_006", "Dimensional Rift", "Vini Vici", 138.0, "12A", 6.5, "Psytrance", "tracks/track_006.flac"),
              ("track_007", "Stellar Pulse", "Infected Mushroom", 140.0, "1A", 7.0, "Psytrance", "tracks/track_007.flac"),
              ("track_008", "Galactic Echoes", "Ace Ventura", 143.0, "2A", 8.5, "Psytrance", "tracks/track_008.flac"),
              ("track_009", "Neural Network", "Liquid Soul", 141.0, "3A", 7.8, "Psytrance", "tracks/track_009.flac"),
              ("track_010", "Infinite Horizons", "Sonic Species", 144.0, "4A", 8.9, "Psytrance", "tracks/track_010.flac")]
    cursor.executemany('INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?, ?)', tracks)
    cursor.execute("INSERT INTO events (id, title, description, start_time) VALUES (?, ?, ?, ?)", ("event_001", "Neon Solstice", "Peak Psytrance", time.time() + 600))
    conn.commit(); conn.close()

if __name__ == "__main__": init_db()
