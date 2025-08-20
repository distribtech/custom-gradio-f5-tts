FROM ghcr.io/swivid/f5-tts:main

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir gradio fastapi uvicorn

EXPOSE 7860
# Run the main script directly. Using ``python -m`` with the repository name
# fails because hyphens are not valid in Python module names.
CMD ["python", "__main__.py"]
