import pytest
from fastapi.testclient import TestClient
from src.main import app, TRACK_CATALOG, CONFIG

client = TestClient(app)

def test_ml_predict_endpoint_enabled():
    CONFIG["NEURAL_CONDUCTOR_ENABLED"] = True
    current = TRACK_CATALOG["track_001"]
    next_track = TRACK_CATALOG["track_002"]

    response = client.post("/api/ml/predict", json={
        "current_track": current,
        "next_track": next_track,
        "voting_velocity": 5.0
    })

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["method"] == "ml_random_forest"
    assert "predicted_vibe_score" in data

def test_ml_predict_endpoint_fallback():
    CONFIG["NEURAL_CONDUCTOR_ENABLED"] = False
    current = TRACK_CATALOG["track_001"]
    next_track = TRACK_CATALOG["track_002"]

    response = client.post("/api/ml/predict", json={
        "current_track": current,
        "next_track": next_track,
        "voting_velocity": 5.0
    })

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["method"] == "heuristic_fallback"
    assert "predicted_vibe_score" in data

    # Restore config
    CONFIG["NEURAL_CONDUCTOR_ENABLED"] = True
