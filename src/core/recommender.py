import time
import os
import joblib
import pandas as pd
from typing import List, Dict, Optional
from src.db.database import get_db_connection

MODEL_PATH = "models/neural_conductor_v1.joblib"
ENCODER_PATH = "models/archetype_encoder.joblib"

class NeuralConductor:
    """
    Foundation for ML-driven vibe analysis and track prediction.
    As of v1.5.0, implements rule-based heuristic prediction based on vibe performance logs.
    """
    def __init__(self, track_catalog: Dict):
        self.track_catalog = track_catalog
        self.model = None
        self.encoder = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.encoder = joblib.load(ENCODER_PATH)
            except Exception:
                pass

    def get_best_transition_archetype(self, current_track_id: str, next_track_id: str) -> str:
        """
        Analyzes historical success metrics for transitions between specific genres.
        Incorporates qualitative user feedback (v2.0.0).
        """
        conn = get_db_connection(); cursor = conn.cursor()

        # 1. Check qualitative transition feedback for this specific track pair/archetype
        cursor.execute('''
            SELECT archetype, AVG(CASE WHEN is_upvote THEN 1.0 ELSE 0.0 END) as success_rate
            FROM transition_feedback
            WHERE track_id_from = ? AND track_id_to = ?
            GROUP BY archetype
            HAVING COUNT(*) > 2
            ORDER BY success_rate DESC
            LIMIT 1
        ''', (current_track_id, next_track_id))

        best_feedback = cursor.fetchone()
        if best_feedback and best_feedback["success_rate"] > 0.7:
            conn.close()
            return best_feedback["archetype"]

        # 2. Fallback to general archetype success rates
        cursor.execute('''
            SELECT archetype, AVG(CASE WHEN is_upvote THEN 1.0 ELSE 0.0 END) as success_rate
            FROM transition_feedback
            GROUP BY archetype
            ORDER BY success_rate DESC
            LIMIT 1
        ''')
        general_best = cursor.fetchone()

        # 3. Fallback to performance logs (original logic)
        cursor.execute('''
            SELECT track_id FROM vibe_performance_logs
            WHERE vibe_score > 0.8 ORDER BY success_metric DESC LIMIT 5
        ''')
        top_performers = [r["track_id"] for r in cursor.fetchall()]
        conn.close()

        # 4. Use ML model for prediction if available
        if self.model and self.encoder:
            try:
                t1 = self.track_catalog.get(current_track_id)
                t2 = self.track_catalog.get(next_track_id)
                if t1 and t2:
                    archetypes = self.encoder.classes_
                    best_score = -1.0
                    best_arch = "bass_swap"

                    for arch in archetypes:
                        arch_encoded = self.encoder.transform([arch])[0]
                        features = pd.DataFrame([[
                            arch_encoded, t1['bpm'], t1['energy'], t2['bpm'], t2['energy'],
                            abs(t1['bpm'] - t2['bpm']), abs(t1['energy'] - t2['energy'])
                        ]], columns=['archetype_encoded', 'from_bpm', 'from_energy', 'to_bpm', 'to_energy', 'bpm_delta', 'energy_delta'])

                        score = self.model.predict(features)[0]
                        if score > best_score:
                            best_score = score
                            best_arch = arch

                    if best_score > 0.6:
                        return best_arch
            except Exception:
                pass

        if general_best and general_best["success_rate"] > 0.6:
            return general_best["archetype"]

        if next_track_id in top_performers:
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
