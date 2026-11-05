import pytest
from fastapi.testclient import TestClient
from src.main import app, TRACK_CATALOG
from src.core.spotify_integration import search_spotify_tracks, get_track_metadata

client = TestClient(app)

def test_search_spotify_tracks_mock_pool():
    """Verify mock external search returns appropriate results when credentials are not configured."""
    results = search_spotify_tracks("Strobe", limit=3)
    assert len(results) > 0
    assert any("deadmau5" in t["artist"] for t in results)
    first = results[0]
    assert "bpm" in first
    assert "key" in first
    assert "energy" in first

def test_search_spotify_tracks_dynamic_fallback():
    """Verify query fallback generates dynamic catalog track."""
    results = search_spotify_tracks("Psychedelic Journey 2026", limit=1)
    assert len(results) == 1
    assert "Psychedelic Journey 2026" in results[0]["title"]
    assert results[0]["bpm"] == 132.0

def test_api_catalog_search_endpoint():
    """Verify /api/catalog/search returns both local and external candidates."""
    resp = client.get("/api/catalog/search?q=Machine")
    assert resp.status_code == 200
    data = resp.json()
    assert "local" in data
    assert "external" in data
    # "Awake the Machine" should match in local catalog
    assert any(t["title"] == "Awake the Machine" for t in data["local"])

def test_api_catalog_spotify_import_endpoint():
    """Verify importing an external track persists to tracks catalog."""
    payload = {
        "id": "mock_sp_strobe_test",
        "title": "Strobe",
        "artist": "deadmau5",
        "bpm": 128.0,
        "key": "8B",
        "energy": 7.8,
        "genre": "Progressive House"
    }
    resp = client.post("/api/catalog/spotify-import", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "imported"
    assert data["track"]["id"].startswith("sp_")
    assert data["track"]["title"] == "Strobe"

    # Verify track is now present in in-memory catalog
    assert data["track"]["id"] in TRACK_CATALOG
