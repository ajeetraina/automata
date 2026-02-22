"""Music Generator — Uses MusicGen to generate background music."""

import os
import base64
import httpx
from pathlib import Path

MUSICGEN_URL = os.getenv("MUSICGEN_URL", "http://localhost:7863")

MUSIC_PRESETS = {
    "adventure": "upbeat orchestral adventure music, heroic, bright, children's story soundtrack",
    "bedtime":   "soft lullaby, gentle piano, dreamy, calming, children's bedtime music",
    "funny":     "playful cartoon music, whimsical, xylophone, silly, fun for kids",
    "magical":   "magical fairy tale music, sparkly, harp, flute, enchanted forest",
    "nature":    "peaceful nature music, birds, gentle breeze, outdoor adventure, children",
    "friendship":"warm heartfelt music, gentle strings, uplifting, friendship theme",
}


class MusicGenerator:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=300.0)

    async def generate(self, prompt: str, duration: int = 65,
                       output_path: str = None) -> str:
        enhanced = f"{prompt}, no lyrics, instrumental, child-safe, background music"
        response = await self.client.post(f"{MUSICGEN_URL}/generate", json={
            "prompt": enhanced, "duration": duration, "guidance_scale": 3.0,
            "model_id": "facebook/musicgen-medium",
        })
        response.raise_for_status()
        Path(output_path).write_bytes(base64.b64decode(response.json()["audio"]))
        return output_path

    @classmethod
    def get_preset(cls, story_type: str) -> str:
        return MUSIC_PRESETS.get(story_type, MUSIC_PRESETS["adventure"])
