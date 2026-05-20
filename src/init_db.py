import sqlite3
import os

DB_PATH = "tracks.db"

def init_db():
    """Initializes the SQLite database with the track catalog."""
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
        energy REAL NOT NULL
    )
    ''')

    # Mock database data
    tracks = [
        ("track_001", "Awake the Machine", "Astrix", 145.0, "9A", 9.5),
        ("track_002", "Universal Frequencies", "Alienatic", 145.0, "10A", 8.8),
        ("track_003", "Mushroom Song (EU Remix)", "Killerwatts", 145.0, "9A", 9.8),
        ("track_004", "Deep Dive", "Save The Robot", 138.0, "5A", 6.2),
        ("track_005", "Shamanic Tales", "Astrix", 145.0, "7A", 9.0),
        ("track_006", "Beyond the Senses", "Vini Vici", 138.0, "11A", 7.5),
    ]

    cursor.executemany('INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?)', tracks)

    conn.commit()
    conn.close()
    print(f"Database {DB_PATH} initialized with {len(tracks)} tracks.")

if __name__ == "__main__":
    init_db()
