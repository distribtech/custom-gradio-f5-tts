FROM ghcr.io/f5audio/f5-tts:latest

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir gradio fastapi uvicorn

EXPOSE 7860
CMD ["python", "-m", "custom-gradio-f5-tts"]
