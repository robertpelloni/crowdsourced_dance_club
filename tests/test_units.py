import pytest
import time
from src.core.conductor import is_harmonically_compatible, calculate_vibe_score
from src.core.recommender import NeuralConductor
from src.core.monitoring import SystemMonitor
from src.api.streaming import get_streaming_links

def test_harmonic_compatibility():
    assert is_harmonically_compatible("8A", "8A") is True
    assert is_harmonically_compatible("8A", "9A") is True
    assert is_harmonically_compatible("8A", "7A") is True
    assert is_harmonically_compatible("8A", "8B") is True
    assert is_harmonically_compatible("12A", "1A") is True
    assert is_harmonically_compatible("8A", "10A") is False

def test_vibe_score_personalization():
    current = {"id": "1", "bpm": 140.0, "energy": 5.0, "key": "8A", "genre": "Techno"}
    track = {"id": "2", "bpm": 140.0, "energy": 5.0, "key": "8A", "genre": "Psytrance"}

    # No preference
    score1 = calculate_vibe_score(track, current, "stable", None)
    # With matching preference
    score2 = calculate_vibe_score(track, current, "stable", "Psytrance")

    assert score2 > score1
    assert score2 == min(1.0, score1 + 0.1)

def test_neural_conductor_heuristics():
    catalog = {"t1": {"id": "t1", "genre": "Psytrance"}, "t2": {"id": "t2", "genre": "Techno"}}
    nc = NeuralConductor(catalog)

    # Test genre prediction
    history = ["Techno", "Techno", "Psytrance"]
    assert nc.predict_next_track_vibe(history) == "Techno"

    # Test transition archetype suggestion
    archetype = nc.get_best_transition_archetype("t1", "t2")
    # v2.0.0 incorporates many more archetypes including filter_sweep, beat_sync, etc.
    assert isinstance(archetype, str)
    assert len(archetype) > 0

def test_system_monitor_health():
    sm = SystemMonitor()
    stats = sm.get_health_stats()
    assert "status" in stats
    assert "uptime_seconds" in stats
    assert stats["database_connected"] is True

def test_streaming_link_generation():
    links = get_streaming_links("Title", "Artist")
    assert "spotify" in links
    assert "apple_music" in links
    assert "Title" in links["spotify"]
    assert "Artist" in links["spotify"]
