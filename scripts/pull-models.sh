#!/bin/bash
set -e
echo "🤖 Downloading all KidsStory AI models (~120GB, ~30-60 min)..."
sudo mkdir -p /data/huggingface-cache && sudo chmod 777 /data/huggingface-cache
export HF_HOME=/data/huggingface-cache

python3 - <<'PYEOF'
from huggingface_hub import snapshot_download
models = [
    ("black-forest-labs/FLUX.1-dev",   "FLUX.1-dev"),
    ("Wan-AI/Wan2.1-T2V-14B",          "Wan2.1 T2V 14B"),
    ("THUDM/CogVideoX-5b-I2V",         "CogVideoX I2V"),
    ("hexgrad/Kokoro-82M",             "Kokoro TTS"),
    ("facebook/musicgen-medium",       "MusicGen Medium"),
]
for model_id, name in models:
    print(f"\n📥 {name} ({model_id})...")
    try:
        snapshot_download(repo_id=model_id)
        print(f"✅ {name} done!")
    except Exception as e:
        print(f"⚠️  {name} failed: {e}")
print("\n✅ All models ready!")
PYEOF

echo "📥 Pulling LLaMA 3.3 70B via Ollama..."
docker run --rm --gpus all -v ollama-models:/root/.ollama ollama/ollama pull llama3.3:70b
echo "🎉 Done! Run: docker compose up -d"
