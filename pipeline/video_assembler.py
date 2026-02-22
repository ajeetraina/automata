"""Video Assembler — Uses FFmpeg to stitch clips, narration, and music."""

import asyncio
import os
from pathlib import Path


class VideoAssembler:
    def __init__(self):
        self.ffmpeg = "ffmpeg"

    async def assemble(self, clip_paths: list, narration_path: str, music_path: str,
                       scene_durations: list, output_path: str, title: str = "",
                       music_volume: float = 0.25, fade_duration: float = 1.0) -> str:
        work_dir = Path(output_path).parent
        concat_path = str(work_dir / "concat.mp4")
        mixed_audio = str(work_dir / "mixed_audio.wav")
        total = sum(scene_durations)

        # 1. Concatenate clips
        list_path = work_dir / "concat_list.txt"
        list_path.write_text("\n".join(f"file '{os.path.abspath(c)}'" for c in clip_paths))
        await self._run([
            self.ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-vf", "fps=24,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", concat_path,
        ])
        list_path.unlink(missing_ok=True)

        # 2. Mix audio
        await self._run([
            self.ffmpeg, "-y", "-i", narration_path, "-i", music_path,
            "-filter_complex",
            f"[0:a]volume=1.0[narr];[1:a]volume={music_volume},atrim=0:{total+3}[music];"
            f"[narr][music]amix=inputs=2:duration=first:dropout_transition=3[out]",
            "-map", "[out]", "-ar", "44100", "-t", str(total + 1), mixed_audio,
        ])

        # 3. Combine + finalize
        vf = f"fade=t=in:st=0:d={fade_duration}"
        if title:
            vf += (f",drawtext=text='{title}':fontsize=60:fontcolor=white"
                   f":x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,3)'"
                   f":shadowcolor=black:shadowx=3:shadowy=3")
        await self._run([
            self.ffmpeg, "-y", "-i", concat_path, "-i", mixed_audio,
            "-vf", vf,
            "-af", f"afade=t=in:st=0:d={fade_duration},afade=t=out:st=-{fade_duration}:d={fade_duration}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "-shortest", output_path,
        ])

        Path(concat_path).unlink(missing_ok=True)
        Path(mixed_audio).unlink(missing_ok=True)
        return output_path

    async def _run(self, cmd: list) -> None:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg failed:\n{stderr.decode()}")
