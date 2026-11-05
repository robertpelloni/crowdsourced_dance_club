import pytest
from fastapi.testclient import TestClient
from src.main import app, TRACK_CATALOG
from src.core.agents import SecondaryDJAgent, AGENTS, simulate_agent_battle

client = TestClient(app)

def test_secondary_dj_agent_personality():
    purist = AGENTS["The Purist"]
    current_track = {"genre": "Techno", "bpm": 128.0}
    track_match = {"genre": "Techno", "bpm": 128.0}
    track_clash = {"genre": "Psytrance", "bpm": 145.0}

    score_match = purist.evaluate_track_for_battle(track_match, current_track, 0.7)
    score_clash = purist.evaluate_track_for_battle(track_clash, current_track, 0.7)

    assert score_match > score_clash
    assert score_match == 0.85 # 0.7 + 0.15 style bias

def test_simulate_agent_battle_dict():
    current_track = {"genre": "Psytrance", "bpm": 145.0}
    candidate = {"genre": "Psytrance", "bpm": 145.0}
    results = simulate_agent_battle(candidate, current_track, 0.8)

    assert "The Purist" in results
    assert "The Mashup King" in results
    assert "The Goa Trance Shaman" in results
    assert results["The Goa Trance Shaman"] > 0.8 # Style bias bonus

def test_api_agents_battle_endpoint():
    res = client.post("/api/agents/battle", json={"track_id": "track_002"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "agent_scores" in data
    assert "The Purist" in data["agent_scores"]
    assert "The Mashup King" in data["agent_scores"]
    assert "The Goa Trance Shaman" in data["agent_scores"]
