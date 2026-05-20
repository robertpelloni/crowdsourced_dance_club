import pytest
from src.main import evaluate_track_fit

def test_evaluate_track_fit_perfect_match():
    current = {"id": "1", "bpm": 145.0, "energy": 9.0, "key": "9A"}
    requested = {"id": "2", "bpm": 145.0, "energy": 9.0, "key": "9A"}
    fits, reason = evaluate_track_fit(requested, current)
    assert fits is True
    assert "perfectly" in reason

def test_evaluate_track_fit_bpm_clash():
    current = {"id": "1", "bpm": 145.0, "energy": 9.0, "key": "9A"}
    requested = {"id": "2", "bpm": 151.0, "energy": 9.0, "key": "9A"}
    fits, reason = evaluate_track_fit(requested, current)
    assert fits is False
    assert "BPM clash" in reason

def test_evaluate_track_fit_energy_clash():
    current = {"id": "1", "bpm": 145.0, "energy": 9.0, "key": "9A"}
    requested = {"id": "2", "bpm": 145.0, "energy": 5.0, "key": "9A"}
    fits, reason = evaluate_track_fit(requested, current)
    assert fits is False
    assert "Energy delta" in reason

def test_evaluate_track_fit_harmonic_clash():
    current = {"id": "1", "bpm": 145.0, "energy": 9.0, "key": "9A"}
    requested = {"id": "2", "bpm": 145.0, "energy": 9.0, "key": "1A"}
    fits, reason = evaluate_track_fit(requested, current)
    assert fits is False
    assert "Harmonic clash" in reason

def test_evaluate_track_fit_boundary():
    current = {"id": "1", "bpm": 145.0, "energy": 9.0, "key": "9A"}
    # Exactly 5.0 BPM difference
    requested_bpm = {"id": "2", "bpm": 150.0, "energy": 9.0, "key": "9A"}
    fits, _ = evaluate_track_fit(requested_bpm, current)
    assert fits is True

    # Exactly 3.0 energy difference
    requested_energy = {"id": "3", "bpm": 145.0, "energy": 6.0, "key": "9A"}
    fits, _ = evaluate_track_fit(requested_energy, current)
    assert fits is True

    # Harmonically compatible (+1 step)
    requested_key = {"id": "4", "bpm": 145.0, "energy": 9.0, "key": "10A"}
    fits, _ = evaluate_track_fit(requested_key, current)
    assert fits is True
