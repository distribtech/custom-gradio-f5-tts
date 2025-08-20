import gradio as gr
from fastapi import FastAPI, UploadFile, File, Form
from typing import List
import torch

# Global model holder
model = None


def load_model():
    """Load the F5-TTS model into VRAM if it is not already loaded."""
    global model
    if model is None:
        from f5_tts import F5TTS  # type: ignore
        model = F5TTS()
    return model


def unload_model():
    """Remove the model from VRAM without clearing caches."""
    global model
    model = None
    torch.cuda.empty_cache()
    return {"status": "unloaded"}


def tts_single(text: str, reference: str):
    """Generate a single speech sample using a reference voice."""
    mdl = load_model()
    output_path = "output.wav"
    mdl.tts_to_file(text, reference, output_path)  # type: ignore[attr-defined]
    return output_path


async def several_tts(texts: List[str], reference_file: UploadFile):
    """Generate several speech samples with a single reference voice."""
    mdl = load_model()
    data = await reference_file.read()
    outputs: List[str] = []
    for idx, text in enumerate(texts):
        path = f"output_{idx}.wav"
        mdl.tts_bytes_to_file(text, data, path)  # type: ignore[attr-defined]
        outputs.append(path)
    return {"files": outputs}


fastapi_app = FastAPI()


@fastapi_app.post("/load")
def api_load():
    load_model()
    return {"status": "loaded"}


@fastapi_app.post("/unload")
def api_unload():
    return unload_model()


@fastapi_app.post("/several")
async def api_several(
    texts: str = Form(..., description="New line separated phrases"),
    reference: UploadFile = File(...)
):
    text_list = [t.strip() for t in texts.splitlines() if t.strip()]
    return await several_tts(text_list, reference)


gradio_interface = gr.Interface(
    fn=tts_single,
    inputs=[gr.Textbox(label="Text"), gr.Audio(type="filepath", label="Reference Voice")],
    outputs=gr.Audio(label="Generated Speech"),
    allow_flagging="never",
)

app = gr.mount_gradio_app(fastapi_app, gradio_interface, path="/")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
