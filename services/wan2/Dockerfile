FROM --platform=linux/amd64 pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime
WORKDIR /app
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir \
    "git+https://github.com/Wan-Video/Wan2.1.git" \
    diffusers==0.30.0 transformers==4.44.0 accelerate==0.34.0 \
    fastapi==0.115.0 uvicorn==0.30.6 \
    imageio==2.36.0 imageio-ffmpeg==0.5.1 av==13.1.0
COPY server.py .
EXPOSE 7861
CMD ["python", "server.py"]
