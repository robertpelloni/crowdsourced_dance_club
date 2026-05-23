from src.db.database import get_db_connection
import time

def log_vibe_performance(track_id: str, vibe_score: float, energy_delta: float, success_metric: float):
    """Logs the effectiveness of a played track for future ML training."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vibe_performance_logs (track_id, vibe_score, energy_delta, success_metric, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (track_id, vibe_score, energy_delta, success_metric, time.time()))
    conn.commit()
    conn.close()
