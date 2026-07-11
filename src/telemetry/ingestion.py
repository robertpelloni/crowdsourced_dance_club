import asyncio
import logging
from typing import Dict, List
from collections import deque
from datetime import datetime, timedelta

logger = logging.getLogger("TelemetryIngestion")

class BiometricAggregator:
    def __init__(self, window_size_seconds: int = 15):
        self.window_size = timedelta(seconds=window_size_seconds)
        # Store individual heart rate readings: (timestamp, bpm)
        self.readings: deque = deque()
        self.current_average_bpm: float = 0.0
        self.baseline_bpm: float = 80.0  # Assumed resting/baseline rate
        self.is_spiking: bool = False

    def add_reading(self, bpm: float):
        now = datetime.utcnow()
        self.readings.append((now, bpm))
        self._prune_old_readings(now)
        self._calculate_metrics()

    def _prune_old_readings(self, current_time: datetime):
        while self.readings and (current_time - self.readings[0][0]) > self.window_size:
            self.readings.popleft()

    def _calculate_metrics(self):
        if not self.readings:
            self.current_average_bpm = self.baseline_bpm
            self.is_spiking = False
            return

        total = sum(bpm for _, bpm in self.readings)
        self.current_average_bpm = total / len(self.readings)

        # Determine if there's a significant spike (e.g., > 20% above baseline)
        if self.current_average_bpm > (self.baseline_bpm * 1.20):
            self.is_spiking = True
        else:
            self.is_spiking = False

# Global aggregators per venue
venue_biometrics: Dict[int, BiometricAggregator] = {}

def get_venue_aggregator(venue_id: int) -> BiometricAggregator:
    if venue_id not in venue_biometrics:
        venue_biometrics[venue_id] = BiometricAggregator()
    return venue_biometrics[venue_id]
