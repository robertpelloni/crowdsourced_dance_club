from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import logging
from src.telemetry.ingestion import get_venue_aggregator

logger = logging.getLogger("TelemetryAPI")
router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])

class BiometricPayload(BaseModel):
    venue_id: int
    heart_rate_bpm: float
    device_id: str

@router.post("/biometrics")
async def ingest_biometric_data(payload: BiometricPayload):
    """
    High-frequency ingestion endpoint for WearOS / Apple Watch aggregate data.
    In a fully scaled production environment, this might be replaced by a UDP socket or Redis Pub/Sub stream.
    """
    aggregator = get_venue_aggregator(payload.venue_id)
    aggregator.add_reading(payload.heart_rate_bpm)

    return {"status": "ok", "current_avg_bpm": aggregator.current_average_bpm, "is_spiking": aggregator.is_spiking}

@router.get("/biometrics/{venue_id}")
async def get_venue_biometrics(venue_id: int):
    """
    Retrieve the current biometric state for a specific venue.
    """
    aggregator = get_venue_aggregator(venue_id)
    return {
        "venue_id": venue_id,
        "current_avg_bpm": aggregator.current_average_bpm,
        "is_spiking": aggregator.is_spiking,
        "active_readings_count": len(aggregator.readings)
    }
