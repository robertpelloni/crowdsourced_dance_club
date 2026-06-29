import pytest
from src.ml.neural_conductor import VibePredictor

def test_vibe_predictor_ranking():
    predictor = VibePredictor()
    current_state = {"bpm": 120, "energy": 5.0, "voting_velocity": 10}
    candidates = [
        {"id": "t1", "energy": 3.0},
        {"id": "t2", "energy": 8.0},
        {"id": "t3", "energy": 5.0},
    ]
    ranked = predictor.predict(current_state, candidates)

    assert len(ranked) == 3
    assert ranked[0]["id"] == "t2"  # Highest energy first in mock
    assert ranked[1]["id"] == "t3"
    assert ranked[2]["id"] == "t1"

def test_predictive_queue_payload():
    predictor = VibePredictor()
    candidates = [
        {"id": "t2", "energy": 8.0},
        {"id": "t3", "energy": 5.0},
    ]
    payload = predictor.generate_predictive_queue_payload(candidates)

    assert payload["type"] == "PREDICTIVE_QUEUE"
    assert len(payload["data"]["predicted_tracks"]) == 2
    assert payload["data"]["predicted_tracks"][0]["track_id"] == "t2"
    assert payload["data"]["predicted_tracks"][0]["confidence"] == 1.0
