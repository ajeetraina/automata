"""FLUX.1-dev Image Generation Service"""

import io, base64, os, torch
from fastapi import FastAPI
from pydantic import BaseModel
from diffusers import FluxPipeline

app = FastAPI(title="FLUX Service")
MODEL_ID = os.getenv("MODEL_ID", "black-forest-labs/FLUX.1-dev")

print(f"Loading {MODEL_ID}...")
pipe = FluxPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16).to("cuda")
pipe.enable_model_cpu_offload()
print("FLUX ready!")


class Req(BaseModel):
    prompt: str
    negative_prompt: str = ""
    width: int = 1920
    height: int = 1080
    num_inference_steps: int = 28
    guidance_scale: float = 3.5
    seed: int = -1


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_ID}


@app.post("/generate")
async def generate(req: Req):
    gen = torch.Generator("cuda").manual_seed(req.seed) if req.seed >= 0 else None
    image = pipe(prompt=req.prompt, width=req.width, height=req.height,
                 num_inference_steps=req.num_inference_steps,
                 guidance_scale=req.guidance_scale, generator=gen).images[0]
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return {"image": base64.b64encode(buf.getvalue()).decode()}


if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=7860)
