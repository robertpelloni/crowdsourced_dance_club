import sqlite3
import time
import uuid
import random

DB_PATH = 'tracks.db'

def simulate_feedback():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get tracks
    cursor.execute('SELECT id FROM tracks')
    tracks = [r['id'] for r in cursor.fetchall()]

    # Get users
    cursor.execute('SELECT id FROM users')
    users = [r['id'] for r in cursor.fetchall()]

    if not users or not tracks:
        print("Missing users or tracks for simulation")
        return

    archetypes = ["crossfade", "bpm_match", "harmonic", "power_drop", "filter_sweep", "beat_sync"]

    print(f"Simulating feedback for {len(tracks)} tracks and {len(users)} users...")

    # Simulating 50 song likes/dislikes
    for _ in range(50):
        uid = random.choice(users)
        tid = random.choice(tracks)
        is_like = random.random() > 0.3 # 70% likes
        cursor.execute('INSERT INTO song_feedback (id, user_id, track_id, is_like, timestamp) VALUES (?, ?, ?, ?, ?)',
                       (str(uuid.uuid4()), uid, tid, 1 if is_like else 0, time.time()))

    # Simulating 30 transition votes
    for _ in range(30):
        uid = random.choice(users)
        t_from = random.choice(tracks)
        t_to = random.choice(tracks)
        arch = random.choice(archetypes)
        is_upvote = random.random() > 0.4 # 60% upvotes
        cursor.execute('INSERT INTO transition_feedback (id, user_id, track_id_from, track_id_to, archetype, is_upvote, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (str(uuid.uuid4()), uid, t_from, t_to, arch, 1 if is_upvote else 0, time.time()))

    conn.commit()
    conn.close()
    print("Simulation complete.")

if __name__ == "__main__":
    simulate_feedback()
