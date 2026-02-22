# 🧸 KidsStory AI — Open Source Children's Animation Pipeline

> Fully automated pipeline to generate animated children's story videos using open source models on Docker.
> **This branch uses [Docker Model Runner (DMR)](docs/dmr.md) instead of Ollama for LLM inference.**

## 🎬 What This Does

Takes a simple story prompt and produces a **complete animated video** with:
- 📖 AI-generated story script (LLaMA via **Docker Model Runner**)
- 🎨 Character & scene images (FLUX.1-dev)
- 🎥 Animated video clips (Wan2.1 / CogVideoX-5b)
- 🎙️ Child-friendly narration (Kokoro TTS)
- 🎵 Background music (MusicGen)
- 🎞️ Final stitched MP4 (FFmpeg)

## 🛠️ Stack

| Service | Model | Purpose |
|---------|-------|---------|
| **Docker Model Runner** | ai/llama3.2 (or ai/llama3.3) | Story & scene script generation |
| FLUX.1-dev | black-forest-labs/FLUX.1-dev | Character & scene image generation |
| Wan2.1 | Wan-AI/Wan2.1-T2V-14B | Text-to-video animation |
| CogVideoX | THUDM/CogVideoX-5b-I2V | Image-to-video animation (optional) |
| Kokoro TTS | hexgrad/Kokoro-82M | Narration voiceover |
| MusicGen | facebook/musicgen-medium | Background music |
| FFmpeg API | linuxserver/ffmpeg | Video assembly |

> **Why DMR?** Docker Model Runner is built into Docker Desktop 4.40+ and exposes an
> OpenAI-compatible API. No extra container, no separate install —
> just `docker model pull ai/llama3.2` and you're running.

## ⚡ Requirements

- **GPU:** NVIDIA Thor (128GB VRAM recommended) or any GPU with 24GB+ VRAM
- **OS:** Ubuntu 22.04+ or macOS (Apple Silicon supported)
- **Docker Desktop:** 4.40+ (includes Docker Model Runner)
- **Storage:** 200GB+ free disk space (for models)

## 🚀 Quick Start

```bash
# 1. Enable Docker Model Runner (built into Docker Desktop 4.40+)
docker desktop enable model-runner --tcp 12434

# 2. Pull a model from Docker Hub
docker model pull ai/llama3.2        # M1 Pro / mid-range
# docker model pull ai/llama3.3      # NVIDIA Thor 128GB (best quality)
# docker model pull ai/smollm2       # Any machine, quick test

# 3. Clone and start
git clone -b dmr https://github.com/ajeetraina/automata.git
cd automata
docker compose up -d

# 4. Generate your first story!
python3 pipeline/generate.py \
  --prompt "A brave little elephant who learns to fly" \
  --duration 60
```

## 📁 Project Structure

```
automata/
├── docker-compose.yml          # No Ollama service — DMR runs on the host
├── docs/
│   └── dmr.md                  # Docker Model Runner setup guide
├── pipeline/
│   ├── generate.py             # Main orchestration script
│   ├── story_generator.py      # LLM via DMR (OpenAI SDK)
│   ├── image_generator.py      # FLUX image generation
│   ├── video_generator.py      # Wan2.1 / CogVideoX animation
│   ├── tts_generator.py        # Kokoro TTS narration
│   ├── music_generator.py      # MusicGen background music
│   ├── video_assembler.py      # FFmpeg final assembly
│   └── server.py               # FastAPI REST API
├── services/
│   ├── flux/
│   ├── wan2/
│   ├── musicgen/
│   └── ffmpeg-api/
├── scripts/
│   ├── install-nvidia-toolkit.sh
│   └── pull-models.sh
└── stories/sample/prompts.md
```

## 🐳 How DMR Works

DMR runs as a **host-level service** — not a Docker container. The `pipeline-api`
container reaches it via a special hostname enabled by `extra_hosts` in `docker-compose.yml`:

```yaml
extra_hosts:
  - "model-runner.docker.internal:host-gateway"
```

`story_generator.py` uses the **OpenAI Python SDK** pointed at the DMR endpoint:

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="http://model-runner.docker.internal:12434/engines/v1",
    api_key="dmr-no-key-needed",   # DMR doesn't require a key
)
response = await client.chat.completions.create(
    model="ai/llama3.2",
    messages=[...],
    response_format={"type": "json_object"},
)
```

See [docs/dmr.md](docs/dmr.md) for the full setup guide and model reference.

## 📊 Performance on NVIDIA Thor (128GB)

| Task | Time |
|------|------|
| Story generation (DMR + LLaMA 70B) | ~15 sec |
| 6 scene images (FLUX.1) | ~2 min |
| 6 video clips (Wan2.1) | ~8 min |
| TTS narration | ~30 sec |
| Music generation | ~1 min |
| FFmpeg assembly | ~30 sec |
| **Total per video** | **~12 min** |

## 🔀 Branches

| Branch | LLM Backend | Notes |
|--------|-------------|-------|
| [`main`](https://github.com/ajeetraina/automata/tree/main) | Ollama | Self-contained, no extra setup |
| [`dmr`](https://github.com/ajeetraina/automata/tree/dmr) | Docker Model Runner | OpenAI-compatible, built into Docker Desktop |

```bash
# Switch back to Ollama version
git checkout main && docker compose up -d

# Stay on DMR version
git checkout dmr && docker compose up -d
```

## 🤝 Community

Built by [Ajeet Singh Raina](https://github.com/ajeetraina) — Docker Captain & Collabnix Community Lead.

- 🌐 [Collabnix.com](https://collabnix.com)
- 💬 [Join Collabnix Slack](https://launchpass.com/collabnix)
- 🐦 [@ajeetraina](https://twitter.com/ajeetraina)

## 📄 License

Apache 2.0 — use freely, contribute back!
