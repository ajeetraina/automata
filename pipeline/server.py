"""KidsStory AI — FastAPI Pipeline Server"""

import uuid
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from generate import generate_story_video

app = FastAPI(title="KidsStory AI API", version="1.0.0")
jobs: dict = {}


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Story concept or theme")
    duration: int = Field(60, ge=20, le=300)
    style: str = Field("colorful cartoon, children's book illustration, Pixar style")
    language: str = Field("english")


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: Optional[str] = None
    output_path: Optional[str] = None
    error: Optional[str] = None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/generate", response_model=JobStatus)
async def generate(req: GenerateRequest, bg: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending", "progress": "Queued"}
    bg.add_task(_run_job, job_id, req)
    return JobStatus(job_id=job_id, status="pending", progress="Queued")


@app.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    j = jobs[job_id]
    return JobStatus(job_id=job_id, **j)


@app.get("/download/{job_id}")
async def download(job_id: str):
    if job_id not in jobs or jobs[job_id]["status"] != "done":
        raise HTTPException(400, "Not ready")
    return FileResponse(jobs[job_id]["output_path"], media_type="video/mp4",
                        filename=f"kidstory_{job_id[:8]}.mp4")


async def _run_job(job_id: str, req: GenerateRequest):
    try:
        jobs[job_id] = {"status": "running", "progress": "Starting..."}
        path = await generate_story_video(
            prompt=req.prompt, duration=req.duration,
            style=req.style, language=req.language, story_id=job_id)
        jobs[job_id] = {"status": "done", "progress": "Complete!", "output_path": path}
    except Exception as e:
        jobs[job_id] = {"status": "error", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
