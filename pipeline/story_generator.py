"""Story Generator — Uses Ollama (LLaMA 3.3 70B) to generate structured story scripts."""

import json
import os
import httpx
from typing import Any

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

SYSTEM_PROMPT = """You are a creative children's story writer specializing in animated videos for children aged 3-8.
Stories must have clear moral lessons, simple vivid language, and colorful imaginative scenes.
Always respond in valid JSON only. No markdown, no extra text."""

USER_PROMPT = """Create an animated children's story for: "{prompt}"
Target duration: {duration} seconds | Scenes: {num_scenes} | Language: {language}

Return JSON:
{{
  "title": "Story Title",
  "moral": "The moral",
  "narration_text": "Full narration text for the whole video",
  "music_prompt": "Background music description",
  "scenes": [
    {{
      "scene_number": 1,
      "title": "Scene title",
      "narration": "Narrator text for this scene",
      "image_prompt": "Detailed image generation prompt",
      "motion_prompt": "How the scene animates",
      "duration": 10
    }}
  ]
}}"""


class StoryGenerator:
    def __init__(self, model: str = "llama3.3:70b"):
        self.model = model
        self.client = httpx.AsyncClient(timeout=120.0)

    async def generate(self, prompt: str, duration: int = 60, language: str = "english") -> dict[str, Any]:
        num_scenes = max(3, duration // 10)
        response = await self.client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": self.model,
                "system": SYSTEM_PROMPT,
                "prompt": USER_PROMPT.format(prompt=prompt, duration=duration,
                                              num_scenes=num_scenes, language=language),
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.8, "top_p": 0.9, "num_predict": 2048},
            },
        )
        response.raise_for_status()
        story = json.loads(response.json()["response"])
        self._fix_durations(story, duration)
        return story

    def _fix_durations(self, story: dict, target: int) -> None:
        total = sum(s.get("duration", 10) for s in story.get("scenes", []))
        if total and abs(total - target) > 5:
            ratio = target / total
            for scene in story["scenes"]:
                scene["duration"] = round(scene.get("duration", 10) * ratio)
