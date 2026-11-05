import os
import joblib
import pandas as pd
from typing import Dict, Optional, Tuple, List
from sklearn.ensemble import RandomForestRegressor

# Milestone 4: Neural Conductor
# Wraps the core heuristic vibe score with an ML prediction layer

class NeuralConductor:
    def __init__(self, model_path: str = "models/neural_conductor_v1.joblib"):
        self.model_path = model_path
        self.enabled = os.getenv("NEURAL_CONDUCTOR_ENABLED", "True").lower() == "true"
        self.model = None
        self._load_model()

    def _load_model(self):
        """Loads the pre-trained ML model if enabled."""
        if self.enabled:
            try:
                if os.path.exists(self.model_path):
                    self.model = joblib.load(self.model_path)
                    print(f"Neural Conductor ML Model loaded from {self.model_path}")
                else:
                    print(f"Warning: Neural model {self.model_path} not found. Operating in fallback mode.")
                    self.enabled = False
            except Exception as e:
                print(f"Error loading Neural Conductor model: {e}")
                self.enabled = False

    def predict_vibe_score(self,
                           track: Dict,
                           current_track: Dict,
                           energy_trend: str,
                           heuristic_score: float,
                           voting_velocity: float) -> Tuple[float, bool]:
        """
        Calculates a hybrid score. If the ML model is loaded and enabled, it predicts the
        true vibe fit based on contextual features and blends it with the heuristic score.
        Returns the final score and a boolean indicating if ML was used.
        """
        if not self.enabled or self.model is None:
            return heuristic_score, False

        try:
            # Build feature vector mapping what the model expects
            bpm_delta = track.get("bpm", 120) - current_track.get("bpm", 120)
            energy_delta = track.get("energy", 0.5) - current_track.get("energy", 0.5)
            trend_val = 1 if energy_trend == "rising" else (-1 if energy_trend == "falling" else 0)

            features = pd.DataFrame([{
                "bpm_delta": bpm_delta,
                "energy_delta": energy_delta,
                "trend": trend_val,
                "heuristic_base": heuristic_score,
                "voting_velocity": voting_velocity
            }])

            # Predict the pure ML score
            ml_prediction = float(self.model.predict(features)[0])

            # Blend the models (60% ML / 40% Heuristic safeguard)
            hybrid_score = (ml_prediction * 0.6) + (heuristic_score * 0.4)

            # Clamp result between 0 and 1
            return max(0.0, min(1.0, hybrid_score)), True

        except Exception as e:
            print(f"Neural prediction failed, falling back to heuristic: {e}")
            return heuristic_score, False

# Global Singleton instance
neural_conductor_instance = NeuralConductor()


class VibePredictor:
    """
    High-level predictor class providing track ranking and PREDICTIVE_QUEUE payload generation
    for zero-latency transitions to the C++ Audio Engine.
    """
    def __init__(self, conductor: Optional[NeuralConductor] = None):
        self.conductor = conductor or neural_conductor_instance

    def predict(self, current_state: Dict, candidates: List[Dict]) -> List[Dict]:
        """Ranks candidate tracks by energy/vibe compatibility."""
        ranked = sorted(candidates, key=lambda c: c.get("energy", 0.0), reverse=True)
        return ranked

    def generate_predictive_queue_payload(self, candidates: List[Dict]) -> Dict:
        """Generates a PREDICTIVE_QUEUE WebSocket payload."""
        predicted_tracks = [
            {"track_id": c["id"], "confidence": 1.0} for c in candidates
        ]
        return {
            "type": "PREDICTIVE_QUEUE",
            "data": {
                "predicted_tracks": predicted_tracks
            }
        }
