# 🐳 Docker Model Runner (DMR) Setup Guide

This branch replaces Ollama with **Docker Model Runner (DMR)** for LLM inference.

DMR exposes an **OpenAI-compatible API** — the code change is just a different
base URL and model name. No extra container needed.

## Why DMR over Ollama?

| | Ollama | Docker Model Runner |
|--|--------|---------------------|
| Model source | Ollama Hub (GGUF) | Docker Hub (OCI artifacts) |
| API style | Custom `/api/generate` | OpenAI-compatible ✅ |
| Runs as | Docker container | Host-level service |
| Compose overhead | Extra service + volume | Zero — just `extra_hosts` |
| GPU support | llama.cpp | llama.cpp / vLLM / Diffusers |

---

## Installation

DMR installs differently depending on your platform.

### 🖥️ NVIDIA Thor / Linux (Docker Engine)

On Linux servers, DMR runs as a **Docker CLI plugin** — no Docker Desktop involved.

```bash
# Ubuntu / Debian
sudo apt-get update
sudo apt-get install -y docker-model-plugin

# Fedora / RHEL
sudo dnf install -y docker-model-plugin

# Verify the plugin is installed
docker model version
```

> The plugin integrates directly with Docker Engine. No daemon restart needed.

### 🍎 macOS (Docker Desktop)

On macOS, DMR is built into Docker Desktop 4.40+.

```bash
# Enable DMR with TCP access on port 12434
docker desktop enable model-runner --tcp 12434

# Verify
docker model status
```

---

## Pull a Model

```bash
# NVIDIA Thor (128GB VRAM) — best quality
docker model pull ai/llama3.3

# M1 Pro 32GB / mid-range
docker model pull ai/llama3.2

# Lightweight — any machine, quick test
docker model pull ai/smollm2
```

---

## Verify the API

```bash
# List available models
docker model ls

# Or via the REST API
curl http://localhost:12434/engines/v1/models

# Test a completion
curl http://localhost:12434/engines/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai/llama3.2",
    "messages": [{"role": "user", "content": "Say hello in one sentence"}]
  }'
```

---

## Start the Pipeline

```bash
# Default model (ai/llama3.2)
docker compose up -d

# Override model for Thor
DMR_MODEL=ai/llama3.3 docker compose up -d
```

---

## How Containers Reach DMR

DMR is a **host-level service**, not a container. The `pipeline-api` container
reaches it via a special hostname set by `extra_hosts` in `docker-compose.yml`:

```yaml
extra_hosts:
  - "model-runner.docker.internal:host-gateway"
```

`story_generator.py` then calls DMR via the OpenAI SDK:

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="http://model-runner.docker.internal:12434/engines/v1",
    api_key="dmr-no-key-needed",  # DMR doesn't require a key
)
response = await client.chat.completions.create(
    model="ai/llama3.2",
    messages=[...],
    response_format={"type": "json_object"},
)
```

---

## Model Reference

| Model | Params | Best For |
|-------|--------|----------|
| `ai/smollm2` | 1.7B | Testing, low RAM |
| `ai/llama3.2` | 3B | M1 Pro, everyday use |
| `ai/phi4-mini` | 3.8B | Fast reasoning |
| `ai/gemma3` | 4B | Creative writing |
| `ai/llama3.1` | 8B | Good quality, 32GB+ |
| `ai/llama3.3` | 70B | Best quality, NVIDIA Thor 128GB |

---

## Switching Branches

```bash
# Original Ollama version
git checkout main && docker compose up -d

# DMR version (this branch)
git checkout dmr && docker compose up -d
```
