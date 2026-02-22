"""Video Generator — Uses Wan2.1 (primary) or CogVideoX (fallback) to animate scenes."""

import os
import base64
import httpx
from pathlib import Path

WAN2_URL = os.getenv("WAN2_URL", "http://localhost:7861")
COGVIDEOX_URL = os.getenv("COGVIDEOX_URL", "http://localhost:7862")


class VideoGenerator:
    def __init__(self, prefer_wan2: bool = True):
        self.prefer_wan2 = prefer_wan2
        self.client = httpx.AsyncClient(timeout=600.0)

    async def generate(self, image_path: str, motion_prompt: str,
                       duration: int = 10, output_path: str = None, fps: int = 24) -> str:
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()

        prompt = (f"{motion_prompt}, smooth gentle motion, children's animation style, "
                  "bright and colorful, friendly atmosphere")

        url = WAN2_URL if self.prefer_wan2 else COGVIDEOX_URL
        response = await self.client.post(f"{url}/generate", json={
            "image": image_b64, "prompt": prompt,
            "num_frames": duration * fps, "fps": fps,
            "guidance_scale": 6.0, "num_inference_steps": 50,
            "negative_prompt": "violence, scary, dark, adult content, blurry, low quality",
        })
        response.raise_for_status()
        Path(output_path).write_bytes(base64.b64decode(response.json()["video"]))
        return output_path
