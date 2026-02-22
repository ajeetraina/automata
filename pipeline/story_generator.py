"""
Story Generator — Docker Model Runner (DMR) edition.

Replaces Ollama with Docker Model Runner, which exposes an
OpenAI-compatible API. No separate container needed — DMR
runs as a host-level service built into Docker Desktop 4.40+.

Endpoints:
  From host:       http://localhost:12434/engines/v1
  From container:  http://model-runner.docker.internal:12434/engines/v1

Pull a model first:
  docker model pull ai/llama3.2
"""

import json
import os
from typing import Any
from openai import AsyncOpenAI

# DMR endpoint — containers use the special hostname below.
# extra_hosts in docker-compose.yml maps it to host-gateway.
DMR_BASE_URL = os.getenv(
    "DMR_BASE_URL",
    "http://model-runner.docker.internal:12434/engines/v1",
)

# Model pulled from Docker Hub via: docker model pull ai/llama3.2
# Swap to ai/llama3.3 on Thor (128GB) or ai/smollm2 for quick tests.
DMR_MODEL = os.getenv("DMR_MODEL", "ai/llama3.2")

SYSTEM_PROMPT = """You are a creative children's story writer specializing in animated videos for children aged 3-8.
Stories must have clear moral lessons, simple vivid language, and colorful imaginative scenes.
Always respond in valid JSON only. No markdown, no extra text."""

USER_PROMPT = """Create an animated children's story for: "{prompt}"
Target duration: {duration} seconds | Scenes: {num_scenes} | Language: {language}

Return JSON:
{{
  "title": "Story Title",
  "moral": "The moral of the story",
  "narration_text": "Full narration text for the whole video",
  "music_prompt": "Background music mood description",
  "scenes": [
    {{
      "scene_number": 1,
      "title": "Scene title",
      "narration": "Narrator text for this scene",
      "image_prompt": "Detailed image generation prompt",
      "motion_prompt": "How the scene should animate",
      "duration": 10
    }}
  ]
}}"""


class StoryGenerator:
    def __init__(
        self,
        model: str = DMR_MODEL,
        base_url: str = DMR_BASE_URL,
    ):
        self.model = model
        # DMR does not require an API key — pass any placeholder
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="dmr-no-key-needed",
        )

    async def generate(
        self,
        prompt: str,
        duration: int = 60,
        language: str = "english",
    ) -> dict[str, Any]:
        """Generate a structured story script via Docker Model Runner."""
        num_scenes = max(3, duration // 10)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": USER_PROMPT.format(
                        prompt=prompt,
                        duration=duration,
                        num_scenes=num_scenes,
                        language=language,
                    ),
                },
            ],
            temperature=0.8,
            max_tokens=2048,
            # JSON mode — DMR supports OpenAI's response_format
            response_format={"type": "json_object"},
        )

        story = json.loads(response.choices[0].message.content)
        self._fix_durations(story, duration)
        return story

    async def list_models(self) -> list[str]:
        """List all models currently available in Docker Model Runner."""
        models = await self.client.models.list()
        return [m.id for m in models.data]

    def _fix_durations(self, story: dict, target: int) -> None:
        total = sum(s.get("duration", 10) for s in story.get("scenes", []))
        if total and abs(total - target) > 5:
            ratio = target / total
            for scene in story["scenes"]:
                scene["duration"] = round(scene.get("duration", 10) * ratio)
