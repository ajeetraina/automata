"""Wan2.1 Video Generation Service"""

import io, base64, os, tempfile, torch
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel

MODEL_ID = os.getenv("MODEL_ID", "Wan-AI/Wan2.1-T2V-14B")
app = FastAPI(title="Wan2.1 Service")

print(f"Loading {MODEL_ID}...")
try:
    from wan import WanT2V
    model = WanT2V.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16).to("cuda")
except ImportError:
    from diffusers import WanPipeline
    model = WanPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16).to("cuda")
print("Wan2.1 ready!")


class Req(BaseModel):
    image: str
    prompt: str
    num_frames: int = 240
    fps: int = 24
    guidance_scale: float = 6.0
    num_inference_steps: int = 50
    negative_prompt: str = "blurry, low quality, distorted, violence, scary"
    seed: int = -1


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_ID}


@app.post("/generate")
async def generate(req: Req):
    import imageio
    from PIL import Image
    image = Image.open(io.BytesIO(base64.b64decode(req.image))).convert("RGB")
    gen = torch.Generator("cuda").manual_seed(req.seed) if req.seed >= 0 else None
    with torch.inference_mode():
        output = model(image=image, prompt=req.prompt, negative_prompt=req.negative_prompt,
                       num_frames=req.num_frames, num_inference_steps=req.num_inference_steps,
                       guidance_scale=req.guidance_scale, generator=gen)
    frames = output.frames[0]
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        writer = imageio.get_writer(tmp.name, fps=req.fps, codec="libx264", quality=8)
        for f in frames: writer.append_data(f)
        writer.close()
        video_b64 = base64.b64encode(open(tmp.name, "rb").read()).decode()
        Path(tmp.name).unlink(missing_ok=True)
    return {"video": video_b64, "num_frames": len(frames), "fps": req.fps}


if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=7861)
