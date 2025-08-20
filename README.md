# Custom Gradio F5-TTS

This project provides a Dockerised Gradio application for the F5-TTS voice
cloning model.  It extends the standard Gradio server with additional API
endpoints to control model loading and unloading and to generate multiple
clips from a single reference voice.

## Features

- `/load` – load the F5-TTS model into VRAM.
- `/unload` – remove the model from VRAM while keeping cache files on disk.
- `/several` – supply a reference voice and newline separated phrases to
  generate several WAV files in one request.

## Running locally

```bash
python -m custom-gradio-f5-tts
```

## Docker

```bash
docker build -t custom-f5-tts .
docker run -p 7860:7860 custom-f5-tts
```

The Gradio UI will be available at `http://localhost:7860/`.  The additional
API routes can be accessed on the same host.
