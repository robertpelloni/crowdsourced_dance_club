import logging
import httpx
import asyncio
from typing import Dict, Optional

logger = logging.getLogger("GenerativeVisuals")

class ComfyUIBridge:
    """
    Bridge interface connecting the Neural Conductor to an external ComfyUI node.
    Triggers audio-reactive video synthesis prompts based on crowd energy and audio stems.
    """
    def __init__(self, comfy_url: str = "http://127.0.0.1:8188"):
        self.comfy_url = comfy_url
        self.is_connected = False
        self.last_prompt = ""
        self.last_status = "idle"
        # For now, we mock the connection state to avoid breaking tests without a real node.

    async def trigger_visual_synthesis(self, energy_trend: str, genre: str, rms: float) -> bool:
        """
        Sends an injection prompt to the generative video synthesis pipeline.
        """
        prompt = self._build_prompt(energy_trend, genre, rms)
        self.last_prompt = prompt
        self.last_status = "generating"
        logger.info(f"[ComfyUI] Triggering visual synthesis prompt: '{prompt}'")

        # Mocking the REST request to the ComfyUI API endpoint (/prompt)
        # In production, this posts a massive JSON workflow template with the injected prompt.
        try:
            await asyncio.sleep(0.05) # Simulate network latency
            self.last_status = "active"
            return True
        except Exception as e:
            self.last_status = "error"
            logger.error(f"[ComfyUI] Failed to trigger synthesis: {e}")
            return False

    def get_state(self) -> Dict[str, str]:
        """Returns the current state and last synthesized prompt."""
        return {
            "status": self.last_status,
            "last_prompt": self.last_prompt or "No prompt generated yet.",
            "comfy_url": self.comfy_url
        }

    def _build_prompt(self, energy_trend: str, genre: str, rms: float) -> str:
        """
        Constructs a dynamic Stable Diffusion prompt based on the current vibe.
        """
        base_aesthetics = "psychedelic, highly detailed, fluid motion, 8k resolution, volumetric lighting, abstract geometry"

        if genre == "Psytrance":
            subject = "fractal alien landscapes, pulsing organic machinery, neon biomechanical roots"
        elif genre == "Techno":
            subject = "brutalist concrete architecture, strobing laser corridors, dark minimal futurism"
        elif genre == "Ambient":
            subject = "slow morphing nebulas, deep space anomalies, gentle bioluminescent oceans"
        else:
            subject = "vibrant morphing abstract shapes, endless tunnel"

        intensity = "extreme hyper-detailed chaos" if energy_trend == "rising" or rms > 0.8 else "smooth morphing calm"

        return f"{subject}, {base_aesthetics}, {intensity}"

comfy_bridge = ComfyUIBridge()
