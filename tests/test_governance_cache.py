import pytest
import time
from fastapi.testclient import TestClient
from src.main import app
import src.api.governance as gov

client = TestClient(app)

def test_governance_proposals_caching():
    # Force clean cache
    gov.invalidate_governance_cache()
    assert gov._proposals_cache is None

    # First request should populate cache
    res1 = client.get("/api/governance/proposals")
    assert res1.status_code == 200
    assert gov._proposals_cache is not None
    initial_cache_time = gov._proposals_cache_expiry

    # Second request should return from cache
    res2 = client.get("/api/governance/proposals")
    assert res2.status_code == 200
    assert res2.json() == res1.json()
    assert gov._proposals_cache_expiry == initial_cache_time

def test_governance_cache_invalidation_on_create():
    # Ensure cache is warm
    client.get("/api/governance/proposals")
    assert gov._proposals_cache is not None

    # Create new proposal
    prop_payload = {
        "title": "BPM Ceiling 145",
        "description": "Lock maximum BPM tempo to 145",
        "rule_type": "bpm_cap",
        "rule_value": "145"
    }
    create_res = client.post("/api/governance/proposals", json=prop_payload)
    assert create_res.status_code == 200

    # Cache should be invalidated immediately
    assert gov._proposals_cache is None

    # Next request refreshes cache and includes newly created proposal
    res = client.get("/api/governance/proposals")
    assert res.status_code == 200
    titles = [p["title"] for p in res.json()]
    assert "BPM Ceiling 145" in titles
