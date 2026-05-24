import time
from typing import List, Dict, Optional
from src.db.database import get_db_connection

class NeuralConductor:
    """
    Foundation for ML-driven vibe analysis and track prediction.
    As of v1.5.0, implements rule-based heuristic prediction based on vibe performance logs.
    """
    def __init__(self, track_catalog: Dict):
        self.track_catalog = track_catalog

    def get_best_transition_archetype(self, current_track_id: str, next_track_id: str) -> str:
        """
        Analyzes historical success metrics for transitions between specific genres.
        """
        conn = get_db_connection(); cursor = conn.cursor()
        # Find similar historical transitions
        cursor.execute('''
            SELECT track_id, vibe_score, success_metric
            FROM vibe_performance_logs
            WHERE vibe_score > 0.8
            ORDER BY success_metric DESC LIMIT 5
        ''')
        top_performers = cursor.fetchall(); conn.close()

        # If the next track is a historically high performer, use an 'intensify' archetype
        if any(row["track_id"] == next_track_id for row in top_performers):
            return "hpf_sweep"

        return "bass_swap"

    def predict_next_track_vibe(self, recent_history: List[str]) -> str:
        """
        Simple heuristic: predicts the next best genre based on repetition patterns.
        """
        if not recent_history: return "Psytrance"
        from collections import Counter
        counts = Counter(recent_history)
        return counts.most_common(1)[0][0]

    def get_vibe_summary(self) -> Dict:
        """
        Returns aggregate performance data for the Neural Conductor dashboard.
        """
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("SELECT AVG(vibe_score), AVG(success_metric) FROM vibe_performance_logs")
        avg_vibe, avg_success = cursor.fetchone()
        conn.close()
        return {"avg_vibe": avg_vibe or 0.0, "avg_success": avg_success or 0.0}
