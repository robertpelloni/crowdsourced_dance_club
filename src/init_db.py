import sqlite3
import os

DB_PATH = "tracks.db"

def init_db():
    """Initializes the SQLite database with tracks, users, and events tables."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tracks table
    cursor.execute('''
    CREATE TABLE tracks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        bpm REAL NOT NULL,
        key TEXT NOT NULL,
        energy REAL NOT NULL,
        genre TEXT NOT NULL DEFAULT 'Psytrance',
        filepath TEXT
    )
    ''')

    # Create users table for authentication and profile management
    cursor.execute('''
    CREATE TABLE users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        points INTEGER DEFAULT 0,
        badges TEXT DEFAULT '[]',
        streak INTEGER DEFAULT 0
    )
    ''')

    # Create events table for upcoming club announcements
    cursor.execute('''
    CREATE TABLE events (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        start_time REAL NOT NULL,
        venue_id TEXT DEFAULT 'CDC_MAIN'
    )
    ''')

    # Create feedback table for user testing and experience refinement
    cursor.execute('''
    CREATE TABLE feedback (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        vibe_rating INTEGER,
        technical_rating INTEGER,
        comment TEXT,
        timestamp REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Create user_requests table for persistent request history
    cursor.execute('''
    CREATE TABLE user_requests (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        track_id TEXT,
        timestamp REAL NOT NULL,
        vibe_score REAL,
        status TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (track_id) REFERENCES tracks (id)
    )
    ''')

    # Create user_votes table for persistent voting history
    cursor.execute('''
    CREATE TABLE user_votes (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        track_id TEXT,
        timestamp REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (track_id) REFERENCES tracks (id)
    )
    ''')

    # Expanded catalog with diverse genres and energy levels
    tracks = [
        # Psytrance (Peak)
        ("track_001", "Awake the Machine", "Astrix", 145.0, "9A", 9.5, "Psytrance", "tracks/track_001.flac"),
        ("track_002", "Universal Frequencies", "Alienatic", 145.0, "10A", 8.8, "Psytrance", "tracks/track_002.flac"),
        ("track_003", "Mushroom Song (EU Remix)", "Killerwatts", 145.0, "9A", 9.8, "Psytrance", "tracks/track_003.flac"),

        # Techno (Driving)
        ("track_007", "Dark Matter", "Charlotte de Witte", 132.0, "8A", 8.5, "Techno", "tracks/track_007.flac"),
        ("track_008", "The Age of Love", "Enrico Sangiuliano", 130.0, "5A", 8.0, "Techno", "tracks/track_008.flac"),

        # Progressive (Flow)
        ("track_004", "Deep Dive", "Save The Robot", 138.0, "5A", 6.2, "Progressive", "tracks/track_004.flac"),
        ("track_005", "Shamanic Tales", "Astrix", 145.0, "7A", 9.0, "Psytrance", "tracks/track_005.flac"),
        ("track_009", "Gaia", "Liquid Soul", 138.0, "11A", 7.2, "Progressive", "tracks/track_009.flac"),

        # Ambient (Cool-down)
        ("track_010", "Solaris", "Carbon Based Lifeforms", 90.0, "1B", 2.0, "Ambient", "tracks/track_010.flac"),
        ("track_011", "Inner Motion", "Solar Fields", 100.0, "3A", 3.5, "Ambient", "tracks/track_011.flac"),

        # Vini Vici (Psytrance/Techno Hybrid Vibe)
        ("track_006", "Beyond the Senses", "Vini Vici", 138.0, "11A", 7.5, "Psytrance", "tracks/track_006.flac"),
    ]

    cursor.executemany('INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?, ?)', tracks)

    # Seed an example event starting in 10 minutes
    import time
    example_event = ("event_001", "Neon Solstice", "Peak Psytrance Ritual", time.time() + 600, "CDC_MAIN")
    cursor.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?)", example_event)

    conn.commit()
    conn.close()
    print(f"Database {DB_PATH} initialized with {len(tracks)} tracks, users, and events.")

if __name__ == "__main__":
    init_db()
