import json
import pytest
from fastapi.testclient import TestClient
from src.main import app, dj_state, TRACK_CATALOG

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Algorithmic DJ Conductor Server is running."}

def test_get_catalog():
    response = client.get("/catalog")
    assert response.status_code == 200
    catalog = response.json()
    assert len(catalog) >= 1
    assert any(track["id"] == "track_001" for track in catalog)

def test_websocket_request_song():
    with client.websocket_connect("/ws/clubgoer") as websocket:
        # Initial sync
        data = websocket.receive_json()
        assert data["type"] == "QUEUE_SYNC"

        # Request a valid song
        websocket.send_json({"action": "REQUEST_SONG", "track_id": "track_002"})
        data = websocket.receive_json()
        assert data["type"] == "REQUEST_ACCEPTED"

        # Verify broadcast
        data = websocket.receive_json()
        assert data["type"] == "QUEUE_SYNC"
        assert any(t["id"] == "track_002" for t in data["queue"])

def test_websocket_request_invalid_song():
    with client.websocket_connect("/ws/clubgoer") as websocket:
        websocket.receive_json() # Initial sync

        websocket.send_json({"action": "REQUEST_SONG", "track_id": "non_existent"})
        data = websocket.receive_json()
        assert data["type"] == "ERROR"
        assert "Track not found" in data["message"]

def test_websocket_request_denied_song():
    with client.websocket_connect("/ws/clubgoer") as websocket:
        websocket.receive_json() # Initial sync

        # track_004 has 138 BPM, current is 145 BPM (delta 7.0 > 5.0)
        websocket.send_json({"action": "REQUEST_SONG", "track_id": "track_004"})
        data = websocket.receive_json()
        assert data["type"] == "REQUEST_DENIED"
        assert "BPM clash" in data["message"]
