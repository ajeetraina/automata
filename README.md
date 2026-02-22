# 🧸 KidsStory AI — Open Source Children's Animation Pipeline

> Fully automated pipeline to generate animated children's story videos using open source models on Docker — powered by NVIDIA Thor (128GB VRAM).

## 🎬 What This Does

Takes a simple story prompt and produces a **complete animated video** with:
- 📖 AI-generated story script (LLaMA 3.3 70B via Ollama)
- 🎨 Character & scene images (FLUX.1-dev)
- 🎥 Animated video clips (Wan2.1 / CogVideoX-5b)
- 🎙️ Child-friendly narration (Kokoro TTS)
- 🎵 Background music (MusicGen)
- 🎞️ Final stitched MP4 (FFmpeg)

## 🛠️ Stack

| Service | Model | Purpose |
|---------|-------|---------|
| Ollama | LLaMA 3.3 70B | Story & scene script generation |
| FLUX.1-dev | black-forest-labs/FLUX.1-dev | Character & scene image generation |
| Wan2.1 | Wan-AI/Wan2.1-T2V-14B | Text-to-video animation |
| CogVideoX | THUDM/CogVideoX-5b-I2V | Image-to-video animation |
| Kokoro TTS | hexgrad/Kokoro-82M | Narration voiceover |
| MusicGen | facebook/musicgen-medium | Background music |
| FFmpeg API | linuxserver/ffmpeg | Video assembly |

## ⚡ Requirements

- **GPU:** NVIDIA Thor (128GB VRAM recommended) or any GPU with 24GB+ VRAM
- **OS:** Ubuntu 22.04+
- **Docker:** 24.x+ with NVIDIA Container Toolkit
- **Storage:** 200GB+ free disk space (for models)

## 🚀 Quick Start

```bash
git clone https://github.com/ajeetraina/automata.git
cd automata
./scripts/install-nvidia-toolkit.sh
./scripts/pull-models.sh
docker compose up -d
python3 pipeline/generate.py --prompt "A brave little elephant who learns to fly" --duration 60
```

## 📁 Project Structure

```
automata/
├── docker-compose.yml
├── pipeline/
│   ├── generate.py             # Main orchestration script
│   ├── story_generator.py      # LLM story + scene script
│   ├── image_generator.py      # FLUX image generation
│   ├── video_generator.py      # Wan2.1 / CogVideoX animation
│   ├── tts_generator.py        # Kokoro TTS narration
│   ├── music_generator.py      # MusicGen background music
│   ├── video_assembler.py      # FFmpeg final assembly
│   └── server.py               # FastAPI REST API
├── services/
│   ├── flux/                   # FLUX.1-dev service
│   ├── wan2/                   # Wan2.1 service
│   ├── musicgen/               # MusicGen service
│   ├── ollama/                 # Ollama entrypoint
│   └── ffmpeg-api/             # FFmpeg API service
├── scripts/
│   ├── install-nvidia-toolkit.sh
│   └── pull-models.sh
└── stories/sample/prompts.md
```

## 📊 Performance on NVIDIA Thor (128GB)

| Task | Time |
|------|------|
| Story generation (LLaMA 70B) | ~15 sec |
| 6 scene images (FLUX.1) | ~2 min |
| 6 video clips (Wan2.1) | ~8 min |
| TTS narration | ~30 sec |
| Music generation | ~1 min |
| FFmpeg assembly | ~30 sec |
| **Total per video** | **~12 min** |

## 🤝 Community

Built by [Ajeet Singh Raina](https://github.com/ajeetraina) — Docker Captain & Collabnix Community Lead.

- 🌐 [Collabnix.com](https://collabnix.com)
- 💬 [Join Collabnix Slack](https://launchpass.com/collabnix)
- 🐦 [@ajeetraina](https://twitter.com/ajeetraina)

## 📄 License

Apache 2.0 — use freely, contribute back!

## 🔀 Branches

| Branch | LLM Backend | Notes |
|--------|-------------|-------|
| `main` | Ollama | Default, self-contained |
| `dmr` | Docker Model Runner | OpenAI-compatible, no extra container |

Switch to the DMR backend:
```bash
git checkout dmr
docker desktop enable model-runner --tcp 12434
docker model pull ai/llama3.2
docker compose up -d
```
