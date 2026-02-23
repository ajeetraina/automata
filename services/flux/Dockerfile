FROM --platform=linux/amd64 pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime
WORKDIR /app
RUN pip install --no-cache-dir \
    diffusers==0.30.0 transformers==4.44.0 accelerate==0.34.0 \
    sentencepiece==0.2.0 protobuf==5.27.3 \
    fastapi==0.115.0 uvicorn==0.30.6 Pillow==10.4.0
COPY server.py .
EXPOSE 7860
CMD ["python", "server.py"]
