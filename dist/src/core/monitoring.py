import time
import psutil
from typing import Dict
from src.db.database import get_db_connection

class SystemMonitor:
    """
    Tracks real-time performance and health metrics for the CDC platform.
    """
    def __init__(self):
        self.start_time = time.time()

    def get_health_stats(self) -> Dict:
        uptime = time.time() - self.start_time
        process = psutil.Process()

        # Database check
        db_alive = False
        try:
            conn = get_db_connection()
            conn.execute("SELECT 1")
            conn.close()
            db_alive = True
        except: pass

        return {
            "status": "healthy" if db_alive else "degraded",
            "uptime_seconds": int(uptime),
            "memory_usage_mb": process.memory_info().rss / (1024 * 1024),
            "cpu_percent": psutil.cpu_percent(),
            "database_connected": db_alive
        }

    def get_vibe_consistency(self) -> float:
        """
        Calculates average vibe score over the last 10 tracks to ensure
        the AI Conductor isn't drifting into musical chaos.
        """
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT AVG(vibe_score) FROM vibe_performance_logs ORDER BY timestamp DESC LIMIT 10")
            avg_vibe = cursor.fetchone()[0]
            conn.close()
            return avg_vibe or 1.0
        except: return 0.0
