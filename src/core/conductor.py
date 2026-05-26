import time
import random
import asyncio
from typing import List, Dict, Optional, Tuple
from collections import Counter
from src.db.database import get_db_connection, load_track_catalog

# AI Conductor Configuration Thresholds
CONFIG = {
    "MAX_BPM_DELTA": 5.0,      # Max BPM difference allowed for fit
    "MAX_ENERGY_DELTA": 1.0,   # Max Energy difference allowed for fit
    "VIBE_WEIGHT_BPM": 0.15,
    "VIBE_WEIGHT_ENERGY": 0.15,
    "VIBE_WEIGHT_RAMPING": 0.10,
    "VIBE_WEIGHT_KEY": 0.35,
    "VIBE_WEIGHT_GENRE": 0.25,
    "VOTE_WEIGHT": 0.30,       # How much votes matter vs algorithmic fit
}

# Genre Compatibility Matrix
GENRE_COMPATIBILITY = {
    "Psytrance": {"Psytrance": 1.0, "Techno": 0.7, "Progressive": 0.8, "Ambient": 0.2},
    "Techno": {"Techno": 1.0, "Psytrance": 0.7, "Progressive": 0.6, "Ambient": 0.3},
    "Progressive": {"Progressive": 1.0, "Psytrance": 0.8, "Techno": 0.6, "Ambient": 0.5},
    "Ambient": {"Ambient": 1.0, "Progressive": 0.5, "Techno": 0.3, "Psytrance": 0.1},
}

class TrackState:
    def __init__(self, track_catalog):
        self.track_catalog = track_catalog
        self.crowd_energy: float = 0.0
        self.recent_activities: List[Dict] = []
        self.current_track: Dict = track_catalog["track_001"]
        self.start_time: float = time.time()
        self.duration: float = 180.0
        self.target_bpm: float = 145.0
        self.current_bpm: float = 145.0
        self.energy_trend: str = "stable"
        self.is_peak_mode: bool = False
        self.last_velocity: float = 0.0
        self.upcoming_queue: List[Dict] = []
        self.active_connections: List = []
        self.vote_history: List[float] = []
        self.user_stats: Dict[str, Dict] = {}
        self.genre_history: List[str] = []
        self.notified_events: List[str] = []
        self.transition_votes: Dict[str, int] = {"classic": 0, "bass_swap": 0, "echo_out": 0, "hpf_sweep": 0}

def is_harmonically_compatible(key1: str, key2: str) -> bool:
    if not key1 or not key2: return False
    if key1 == key2: return True
    try:
        val1 = int(key1[:-1]); mode1 = key1[-1]
        val2 = int(key2[:-1]); mode2 = key2[-1]
        if val1 == val2 and mode1 != mode2: return True
        if mode1 == mode2:
            diff = abs(val1 - val2)
            if diff == 1 or diff == 11: return True
    except: return False
    return False

def calculate_vibe_score(track: Dict, current_track: Dict, energy_trend: str, user_pref: Optional[str] = None) -> float:
    bpm_delta = abs(track["bpm"] - current_track["bpm"])
    bpm_score = max(0, 1 - (bpm_delta / CONFIG["MAX_BPM_DELTA"]))
    energy_delta = abs(track["energy"] - current_track["energy"])
    energy_score = max(0, 1 - (energy_delta / CONFIG["MAX_ENERGY_DELTA"]))
    ramping_score = 0.5
    if energy_trend == "rising":
        if track["energy"] > current_track["energy"]: ramping_score = 1.0
        elif track["energy"] < current_track["energy"]: ramping_score = 0.0
    elif energy_trend == "falling":
        if track["energy"] < current_track["energy"]: ramping_score = 1.0
        elif track["energy"] > current_track["energy"]: ramping_score = 0.0
    key_score = 1.0 if is_harmonically_compatible(track["key"], current_track["key"]) else 0.0
    genre1 = current_track.get("genre", "Psytrance")
    genre2 = track.get("genre", "Psytrance")
    genre_score = GENRE_COMPATIBILITY.get(genre1, {}).get(genre2, 0.5)

    # User Personalization Bonus (v1.5.0)
    pref_bonus = 0.0
    if user_pref and user_pref == genre2:
        pref_bonus = 0.1 # 10% boost for matching user's favorite genre

    return min(1.0, (bpm_score * CONFIG["VIBE_WEIGHT_BPM"]) + (energy_score * CONFIG["VIBE_WEIGHT_ENERGY"]) + \
            (ramping_score * CONFIG["VIBE_WEIGHT_RAMPING"]) + (key_score * CONFIG["VIBE_WEIGHT_KEY"]) + \
            (genre_score * CONFIG["VIBE_WEIGHT_GENRE"]) + pref_bonus)

def evaluate_track_fit(requested_track: Dict, current_track: Dict) -> Tuple[bool, str]:
    bpm_delta = abs(requested_track["bpm"] - current_track["bpm"])
    if bpm_delta > CONFIG["MAX_BPM_DELTA"]:
        return False, "BPM clash too severe."
    energy_delta = abs(requested_track["energy"] - current_track["energy"])
    if energy_delta > CONFIG["MAX_ENERGY_DELTA"]:
         return False, "Energy delta clash."
    if not is_harmonically_compatible(requested_track["key"], current_track["key"]):
        return False, "Harmonic clash."
    genre1 = current_track.get("genre", "Psytrance")
    genre2 = requested_track.get("genre", "Psytrance")
    if GENRE_COMPATIBILITY.get(genre1, {}).get(genre2, 0.5) < 0.3:
        return False, "Genre clash."

    if bpm_delta == 0 and energy_delta == 0 and requested_track["key"] == current_track["key"]:
        return True, "Track fits the vibe perfectly."
    return True, "Track fits the vibe."
