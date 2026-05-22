import sqlite3
import os

DB_PATH = "tracks.db"

def init_db():
    """Initializes the SQLite database with an expanded track catalog."""
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
<<<<<<< HEAD
        genre TEXT NOT NULL DEFAULT 'Psytrance'
=======
        genre TEXT NOT NULL DEFAULT 'Psytrance',
        filepath TEXT
>>>>>>> main
    )
    ''')

    # Expanded catalog with diverse genres and energy levels
    tracks = [
        # Psytrance (Peak)
<<<<<<< HEAD
        ("track_001", "Awake the Machine", "Astrix", 145.0, "9A", 9.5, "Psytrance"),
        ("track_002", "Universal Frequencies", "Alienatic", 145.0, "10A", 8.8, "Psytrance"),
        ("track_003", "Mushroom Song (EU Remix)", "Killerwatts", 145.0, "9A", 9.8, "Psytrance"),

        # Techno (Driving)
        ("track_007", "Dark Matter", "Charlotte de Witte", 132.0, "8A", 8.5, "Techno"),
        ("track_008", "The Age of Love", "Enrico Sangiuliano", 130.0, "5A", 8.0, "Techno"),

        # Progressive (Flow)
        ("track_004", "Deep Dive", "Save The Robot", 138.0, "5A", 6.2, "Progressive"),
        ("track_005", "Shamanic Tales", "Astrix", 145.0, "7A", 9.0, "Psytrance"),
        ("track_009", "Gaia", "Liquid Soul", 138.0, "11A", 7.2, "Progressive"),

        # Ambient (Cool-down)
        ("track_010", "Solaris", "Carbon Based Lifeforms", 90.0, "1B", 2.0, "Ambient"),
        ("track_011", "Inner Motion", "Solar Fields", 100.0, "3A", 3.5, "Ambient"),

        # Vini Vici (Psytrance/Techno Hybrid Vibe)
        ("track_006", "Beyond the Senses", "Vini Vici", 138.0, "11A", 7.5, "Psytrance"),
    ]

    cursor.executemany('INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?)', tracks)
=======
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
>>>>>>> main

    conn.commit()
    conn.close()
    print(f"Database {DB_PATH} initialized with {len(tracks)} tracks.")

if __name__ == "__main__":
    init_db()
