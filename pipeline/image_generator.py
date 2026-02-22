"""Image Generator — Uses FLUX.1-dev to generate scene images."""

import os
import base64
import httpx
from pathlib import Path

FLUX_URL = os.getenv("FLUX_URL", "http://localhost:7860")


class ImageGenerator:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=180.0)

    async def generate(self, prompt: str, output_path: str,
                       width: int = 1920, height: int = 1080) -> str:
        enhanced = (f"{prompt}, children's book illustration, bright colors, "
                    "friendly atmosphere, safe for children, high quality")
        response = await self.client.post(f"{FLUX_URL}/generate", json={
            "prompt": enhanced,
            "negative_prompt": "violence, scary, dark, adult content, realistic, photo",
            "width": width, "height": height,
            "num_inference_steps": 28, "guidance_scale": 3.5, "seed": -1,
        })
        response.raise_for_status()
        Path(output_path).write_bytes(base64.b64decode(response.json()["image"]))
        return output_path
