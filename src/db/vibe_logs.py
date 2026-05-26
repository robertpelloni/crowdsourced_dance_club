import time
from src.db.database import get_db_connection

def log_vibe_performance(track_id: str, vibe_score: float, energy_delta: float, success_metric: float):
    """
    Logs track performance metrics for future Neural Conductor training.
    success_metric is typically derived from voting velocity or crowd energy surgest.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vibe_performance_logs (track_id, vibe_score, energy_delta, success_metric, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (track_id, vibe_score, energy_delta, success_metric, time.time()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Failed to log vibe performance: {e}")
