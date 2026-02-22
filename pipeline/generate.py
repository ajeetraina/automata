#!/usr/bin/env python3
"""
KidsStory AI — Main Pipeline Orchestrator
Usage:
    python3 generate.py --prompt "A brave little elephant who learns to fly" --duration 60
"""

import argparse
import asyncio
import json
import os
import time
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table

from story_generator import StoryGenerator
from image_generator import ImageGenerator
from video_generator import VideoGenerator
from tts_generator import TTSGenerator
from music_generator import MusicGenerator
from video_assembler import VideoAssembler

console = Console()


async def generate_story_video(
    prompt: str,
    duration: int = 60,
    style: str = "colorful cartoon, children's book illustration",
    language: str = "english",
    output_path: str = None,
    story_id: str = None,
) -> str:
    story_id = story_id or f"story_{int(time.time())}"
    output_dir = Path("output") / story_id
    output_dir.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        output_path = str(output_dir / "final.mp4")

    console.print(Panel.fit(
        f"[bold cyan]🧸 KidsStory AI Pipeline[/bold cyan]\n"
        f"[yellow]Prompt:[/yellow] {prompt}\n"
        f"[yellow]Duration:[/yellow] {duration}s | [yellow]Style:[/yellow] {style}",
        border_style="cyan"
    ))

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                  BarColumn(), TimeElapsedColumn(), console=console) as progress:

        task1 = progress.add_task("[cyan]📖 Generating story script...", total=None)
        story = await StoryGenerator().generate(prompt=prompt, duration=duration, language=language)
        story_path = output_dir / "story.json"
        story_path.write_text(json.dumps(story, indent=2))
        progress.update(task1, description=f"[green]✅ Story: {len(story['scenes'])} scenes generated")

        task2 = progress.add_task("[cyan]🎨 Generating scene images...", total=len(story["scenes"]))
        image_gen = ImageGenerator()
        image_paths = []
        for i, scene in enumerate(story["scenes"]):
            img_path = output_dir / f"scene_{i:02d}.png"
            await image_gen.generate(
                prompt=f"{scene['image_prompt']}, {style}, high quality, vibrant colors",
                output_path=str(img_path),
            )
            image_paths.append(str(img_path))
            progress.advance(task2)
        progress.update(task2, description=f"[green]✅ Images: {len(image_paths)} scenes rendered")

        task3 = progress.add_task("[cyan]🎥 Animating scenes (Wan2.1)...", total=len(story["scenes"]))
        video_gen = VideoGenerator()
        clip_paths = []
        for i, (scene, img_path) in enumerate(zip(story["scenes"], image_paths)):
            clip_path = output_dir / f"clip_{i:02d}.mp4"
            await video_gen.generate(
                image_path=img_path,
                motion_prompt=scene["motion_prompt"],
                duration=scene["duration"],
                output_path=str(clip_path),
            )
            clip_paths.append(str(clip_path))
            progress.advance(task3)
        progress.update(task3, description=f"[green]✅ Video: {len(clip_paths)} clips animated")

        task4 = progress.add_task("[cyan]🎙️ Generating narration...", total=None)
        narration_path = output_dir / "narration.wav"
        await TTSGenerator().generate(text=story["narration_text"], output_path=str(narration_path))
        progress.update(task4, description="[green]✅ Narration audio generated")

        task5 = progress.add_task("[cyan]🎵 Generating background music...", total=None)
        music_path = output_dir / "bgm.wav"
        await MusicGenerator().generate(prompt=story["music_prompt"], duration=duration + 5, output_path=str(music_path))
        progress.update(task5, description="[green]✅ Background music generated")

        task6 = progress.add_task("[cyan]🎞️ Assembling final video...", total=None)
        await VideoAssembler().assemble(
            clip_paths=clip_paths,
            narration_path=str(narration_path),
            music_path=str(music_path),
            scene_durations=[s["duration"] for s in story["scenes"]],
            output_path=output_path,
            title=story["title"],
        )
        progress.update(task6, description="[green]✅ Final video assembled!")

    table = Table(title="🎉 Generation Complete!", border_style="green")
    table.add_column("Asset", style="cyan")
    table.add_column("Path", style="white")
    table.add_row("📖 Story Script", str(story_path))
    table.add_row("🎞️ Final Video", f"[bold green]{output_path}[/bold green]")
    console.print(table)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="KidsStory AI — Generate animated children's story videos")
    parser.add_argument("--prompt", "-p", required=True)
    parser.add_argument("--duration", "-d", type=int, default=60)
    parser.add_argument("--style", "-s", default="colorful cartoon, children's book illustration, Pixar style")
    parser.add_argument("--language", "-l", default="english", choices=["english", "hindi", "tamil", "kannada"])
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()
    output = asyncio.run(generate_story_video(
        prompt=args.prompt, duration=args.duration,
        style=args.style, language=args.language, output_path=args.output,
    ))
    console.print(f"\n[bold green]🎬 Your video is ready:[/bold green] {output}")


if __name__ == "__main__":
    main()
