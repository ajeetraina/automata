"""MusicGen Background Music Service"""

import base64, os, tempfile, torch, soundfile as sf
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from audiocraft.models import MusicGen

app = FastAPI(title="MusicGen Service")
MODEL_ID = os.getenv("MODEL_ID", "facebook/musicgen-medium")

print(f"Loading {MODEL_ID}...")
model = MusicGen.get_pretrained(MODEL_ID)
model.set_generation_params(use_sampling=True, top_k=250)
print("MusicGen ready!")


class Req(BaseModel):
    prompt: str
    duration: int = 65
    guidance_scale: float = 3.0
    model_id: str = MODEL_ID


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_ID}


@app.post("/generate")
async def generate(req: Req):
    model.set_generation_params(use_sampling=True, top_k=250,
                                 duration=req.duration, cfg_coef=req.guidance_scale)
    with torch.inference_mode():
        wav = model.generate([req.prompt])
    wav_np = wav[0].cpu().numpy().T
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, wav_np, samplerate=32000)
        audio_b64 = base64.b64encode(open(tmp.name, "rb").read()).decode()
        Path(tmp.name).unlink(missing_ok=True)
    return {"audio": audio_b64, "duration": req.duration, "sample_rate": 32000}


if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=7863)
