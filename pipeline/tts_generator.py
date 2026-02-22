"""TTS Generator — Uses Kokoro-82M for child-friendly narration."""

import os
import httpx
from pathlib import Path

KOKORO_URL = os.getenv("KOKORO_URL", "http://localhost:8880")


class TTSGenerator:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=120.0)

    VOICES = {
        "warm_female": "af_sky",
        "gentle_male": "am_adam",
        "child_like": "af_bella",
    }

    async def generate(self, text: str, output_path: str,
                       voice: str = "af_sky", speed: float = 0.9) -> str:
        response = await self.client.post(f"{KOKORO_URL}/v1/audio/speech", json={
            "model": "kokoro", "input": text,
            "voice": voice, "speed": speed, "response_format": "wav",
        })
        response.raise_for_status()
        Path(output_path).write_bytes(response.content)
        return output_path
