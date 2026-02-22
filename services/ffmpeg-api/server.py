"""FFmpeg API Service — health check endpoint"""
from fastapi import FastAPI
app = FastAPI(title="FFmpeg API")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8000)
