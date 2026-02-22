FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime
WORKDIR /app
RUN apt-get update && apt-get install -y libsndfile1 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir audiocraft==1.3.0 fastapi==0.115.0 uvicorn==0.30.6 soundfile==0.12.1
COPY server.py .
EXPOSE 7863
CMD ["python", "server.py"]
