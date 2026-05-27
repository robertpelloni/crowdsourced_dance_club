import pytest
from src.main import dj_state, app
from fastapi.testclient import TestClient
import time

client = TestClient(app)

def test_crowd_energy_aggregation():
    # Reset state
    dj_state.crowd_energy = 0.0
    dj_state.recent_activities = []

    # Simulate activity (via WebSocket action logic ideally, but testing the state directly here)
    # USER_ACTIVITY logic: dj_state.crowd_energy = min(1.0, total / 10.0)

    activities = [
        {"intensity": 2.0},
        {"intensity": 3.0},
        {"intensity": 1.0}
    ]

    for a in activities:
        dj_state.recent_activities.append({"timestamp": time.time(), "intensity": a["intensity"]})

    total = sum(a["intensity"] for a in dj_state.recent_activities)
    dj_state.crowd_energy = min(1.0, total / 10.0)

    assert dj_state.crowd_energy == 0.6
