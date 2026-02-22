# 🐳 Docker Model Runner (DMR) Setup Guide

This branch replaces Ollama with **Docker Model Runner (DMR)** for LLM inference.

DMR is built into Docker Desktop 4.40+ and exposes an **OpenAI-compatible API**,
so the swap is clean — same model, different endpoint, no extra container.

## Why DMR over Ollama?

| | Ollama | Docker Model Runner |
|--|--------|---------------------|
| Installation | Separate install | Built into Docker Desktop ✅ |
| Model source | Ollama Hub (GGUF) | Docker Hub (OCI artifacts) |
| API style | Custom `/api/generate` | OpenAI-compatible ✅ |
| Runs as | Docker container | Host-level service |
| Compose overhead | Extra service + volume | Zero — just `extra_hosts` |
| GPU support | llama.cpp | llama.cpp / vLLM / Diffusers |

## Prerequisites

Docker Desktop **4.40** or later.

## 1. Enable DMR

```bash
# Enable with TCP on port 12434
docker desktop enable model-runner --tcp 12434

# Verify
docker model status
```

## 2. Pull a Model

Choose based on your hardware:

```bash
# NVIDIA Thor (128GB) — best quality
docker model pull ai/llama3.3

# M1 Pro 32GB / mid-range — recommended default
docker model pull ai/llama3.2

# Lightweight — any machine, fast
docker model pull ai/smollm2
```

## 3. Verify the API

```bash
# List available models
curl http://localhost:12434/engines/v1/models

# Test a completion
curl http://localhost:12434/engines/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai/llama3.2",
    "messages": [{"role": "user", "content": "Say hello in one sentence"}]
  }'
```

## 4. Start the Pipeline

```bash
# Default model (ai/llama3.2)
docker compose up -d

# Override model for Thor
DMR_MODEL=ai/llama3.3 docker compose up -d
```

## 5. Generate a Story

```bash
python3 pipeline/generate.py \
  --prompt "A brave little elephant who learns to fly" \
  --duration 60
```

## How Containers Reach DMR

DMR is a host-level service, not a container. The `docker-compose.yml` uses
`extra_hosts` so the `pipeline-api` container can reach it:

```yaml
extra_hosts:
  - "model-runner.docker.internal:host-gateway"
```

Then in `story_generator.py`, the endpoint is:

```
http://model-runner.docker.internal:12434/engines/v1
```

## Model Reference

| Model | Params | Best For |
|-------|--------|----------|
| `ai/smollm2` | 1.7B | Testing, low RAM |
| `ai/llama3.2` | 3B | M1 Pro, everyday use ✅ |
| `ai/phi4-mini` | 3.8B | Fast reasoning |
| `ai/gemma3` | 4B | Creative writing |
| `ai/llama3.1` | 8B | Good quality, 32GB+ |
| `ai/llama3.3` | 70B | Best quality, Thor 128GB |

## Switching Branches

```bash
# Original Ollama version
git checkout main && docker compose up -d

# DMR version (this branch)
git checkout dmr && docker compose up -d
```
