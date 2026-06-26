import logging
from typing import Dict, Optional

logger = logging.getLogger("MultiAgentDJ")

class SecondaryDJAgent:
    """
    Represents an alternative DJ Persona battling for control of the deck.
    """
    def __init__(self, name: str, style_bias: str, risk_tolerance: float):
        self.name = name
        self.style_bias = style_bias # e.g., 'Psytrance', 'Techno'
        self.risk_tolerance = risk_tolerance # 0.0 to 1.0, higher means more likely to break rules

    def evaluate_track_for_battle(self, track: Dict, current_track: Dict, base_score: float) -> float:
        """
        Modifies the base ML vibe score based on this specific DJ's personality.
        """
        modified_score = base_score

        # Style Bias
        if track.get("genre") == self.style_bias:
            modified_score += 0.15
        elif self.risk_tolerance < 0.3 and track.get("genre") != current_track.get("genre"):
            # Conservative DJs hate genre switching
            modified_score -= 0.2

        # Risk Tolerance on BPM
        bpm_delta = abs(track.get("bpm", 120) - current_track.get("bpm", 120))
        if bpm_delta > 3.0:
            if self.risk_tolerance > 0.7:
                modified_score += 0.1 # Risky DJs love chaotic tempo jumps
            else:
                modified_score -= 0.3 # Conservative DJs hate tempo jumps

        return max(0.0, min(1.0, modified_score))

# Pre-defined Battle Agents
AGENTS = {
    "The Purist": SecondaryDJAgent("The Purist", style_bias="Techno", risk_tolerance=0.1),
    "The Mashup King": SecondaryDJAgent("The Mashup King", style_bias="Progressive", risk_tolerance=0.9),
    "The Goa Trance Shaman": SecondaryDJAgent("The Goa Trance Shaman", style_bias="Psytrance", risk_tolerance=0.4)
}

def simulate_agent_battle(track: Dict, current_track: Dict, base_ml_score: float) -> Dict[str, float]:
    """
    Runs the track through all secondary AI DJ personas.
    """
    results = {}
    for agent_id, agent in AGENTS.items():
        score = agent.evaluate_track_for_battle(track, current_track, base_ml_score)
        results[agent_id] = score
    return results
