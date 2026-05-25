import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_venue_endpoints():
    # 1. Get all venues
    res = client.get("/api/venues")
    assert res.status_code == 200
    venues = res.json()
    assert len(venues) > 0
    assert venues[0]["id"] == "CDC_MAIN"

    # 2. Get specific venue state
    res_state = client.get("/api/venues/CDC_MAIN/state")
    assert res_state.status_code == 200
    assert "current_track" in res_state.json()

def test_streaming_endpoint():
    res = client.get("/api/tracks/track_001/streaming")
    assert res.status_code == 200
    links = res.json()
    assert "spotify" in links
    assert "Awake" in links["spotify"]
