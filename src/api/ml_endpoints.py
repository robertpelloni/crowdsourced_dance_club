from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import src.main

router = APIRouter(prefix="/api/ml", tags=["Neural Conductor"])

class PredictionRequest(BaseModel):
    current_track: Dict
    next_track: Dict
    voting_velocity: float = 0.0

@router.post("/predict")
async def predict_transition_vibe(req: PredictionRequest):
    """
    Predicts the expected vibe score for a transition using the Neural Conductor.
    Falls back to heuristic if ML is disabled via CONFIG.
    """
    if src.main.CONFIG.get("NEURAL_CONDUCTOR_ENABLED", True):
        base_heuristic = src.main.calculate_vibe_score(req.next_track, req.current_track)
        score, _ = src.main.neural_conductor.predict_vibe_score(
            track=req.next_track,
            current_track=req.current_track,
            energy_trend="stable",
            heuristic_score=base_heuristic,
            voting_velocity=req.voting_velocity
        )
        method = "ml_random_forest"
    else:
        score = src.main.calculate_vibe_score(req.next_track, req.current_track)
        method = "heuristic_fallback"

    return {
        "status": "success",
        "predicted_vibe_score": score,
        "method": method
    }
