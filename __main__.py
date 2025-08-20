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


def gr_load() -> str:
    """Button helper to load the model."""
    return api_load()["status"]


def gr_unload() -> str:
    """Button helper to unload the model."""
    return api_unload()["status"]


def gr_several(texts: str, reference: str) -> List[str]:
    """Generate several clips from the GUI."""
    text_list = [t.strip() for t in texts.splitlines() if t.strip()]
    mdl = load_model()
    with open(reference, "rb") as ref_file:
        data = ref_file.read()
    outputs: List[str] = []
    for idx, text in enumerate(text_list):
        path = f"output_{idx}.wav"
        mdl.tts_bytes_to_file(text, data, path)  # type: ignore[attr-defined]
        outputs.append(path)
    return outputs


with gr.Blocks() as gradio_interface:
    with gr.Tab("Single"):
        text_input = gr.Textbox(label="Text")
        ref_audio = gr.Audio(type="filepath", label="Reference Voice")
        generate_btn = gr.Button("Generate")
        single_output = gr.Audio(label="Generated Speech")
        generate_btn.click(tts_single, [text_input, ref_audio], single_output)

    with gr.Tab("Several"):
        texts_input = gr.Textbox(
            label="Texts",
            lines=5,
            placeholder="One phrase per line",
        )
        ref_audio_multi = gr.Audio(type="filepath", label="Reference Voice")
        several_btn = gr.Button("Generate Clips")
        several_output = gr.Files(label="Generated Files")
        several_btn.click(gr_several, [texts_input, ref_audio_multi], several_output)

    with gr.Row():
        load_button = gr.Button("Load Model")
        unload_button = gr.Button("Unload Model")
        status_box = gr.Textbox(label="Status")
        load_button.click(gr_load, outputs=status_box)
        unload_button.click(gr_unload, outputs=status_box)


app = gr.mount_gradio_app(fastapi_app, gradio_interface, path="/")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
