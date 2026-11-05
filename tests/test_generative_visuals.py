import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.generative_visuals import comfy_bridge, ComfyUIBridge

client = TestClient(app)

def test_comfy_bridge_prompt_generation():
    bridge = ComfyUIBridge()
    # Test Psytrance rising energy
    prompt_psy = bridge._build_prompt("rising", "Psytrance", 0.9)
    assert "fractal alien landscapes" in prompt_psy
    assert "extreme hyper-detailed chaos" in prompt_psy

    # Test Techno calm energy
    prompt_techno = bridge._build_prompt("stable", "Techno", 0.4)
    assert "brutalist concrete architecture" in prompt_techno
    assert "smooth morphing calm" in prompt_techno

    # Test Ambient
    prompt_ambient = bridge._build_prompt("falling", "Ambient", 0.2)
    assert "slow morphing nebulas" in prompt_ambient

def test_visuals_status_endpoint():
    response = client.get("/api/visuals/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "last_prompt" in data
    assert "comfy_url" in data

def test_visuals_trigger_endpoint():
    payload = {
        "genre": "Psytrance",
        "energy_trend": "rising",
        "rms": 0.88
    }
    response = client.post("/api/visuals/trigger", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "fractal alien landscapes" in data["state"]["last_prompt"]
    assert data["state"]["status"] == "active"
