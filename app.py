"""Interfaz Gradio.   python app.py   (por defecto usa el modelo final, runs/resnet18_base)

Entrada esperada: recorte de una lesión (PNG/JPG/JPEG/BMP/WEBP), como los de ejemplos/ o data/processed/png/.
"""
import argparse
import json

import numpy as np
import torch
import gradio as gr
from PIL import Image

import config as C
from dataset import get_transforms
from engine import get_device, load_model
from imaging import to_uint8

DISCLAIMER = "⚠️ " + C.DISCLAIMER
ALLOWED = "PNG, JPG, JPEG, BMP o WEBP (recorte de lesión en escala de grises o color). No se admite DICOM directo."
EJEMPLOS = sorted((C.ROOT / "ejemplos").glob("*.png"))
MAS_IMAGENES = "https://drive.google.com/drive/folders/1aVHj3Scb4ZAW-S-Llsub6KrvAp352mh3"


def build_app(run_name):
    device = get_device()
    model, cfg, run_dir = load_model(run_name, device)
    thr_file = run_dir / "threshold.json"
    thr = json.loads(thr_file.read_text())["threshold"] if thr_file.exists() else 0.5
    tf = get_transforms(train=False)

    def predict(img):
        if img is None:
            return f"Sube una imagen. Formatos: {ALLOWED}\n\n**{DISCLAIMER}**", None
        try:
            arr = np.array(img)
            if arr.ndim == 3:
                arr = arr[..., :3].mean(axis=2)  # a gris
            if arr.ndim != 2 or min(arr.shape) < 32:
                return f"Imagen inválida: debe ser 2D y de al menos 32x32 píxeles.\n\n**{DISCLAIMER}**", None
            if float(arr.std()) < 1e-3:
                return f"Imagen inválida: parece vacía o de un solo color.\n\n**{DISCLAIMER}**", None
            pil = Image.fromarray(to_uint8(arr)).convert("RGB")  # mismo preprocesamiento que en datos
            x = tf(pil).unsqueeze(0).to(device)
            with torch.no_grad():
                score = torch.softmax(model(x), 1)[0, 1].item()
        except Exception as e:  # archivo corrupto, formato raro, etc.
            return f"No se pudo procesar la imagen ({type(e).__name__}). Formatos: {ALLOWED}\n\n**{DISCLAIMER}**", None

        clase = "clase **maligna** (sospecha alta según el modelo)" if score >= thr else \
            "clase **benigna** (sospecha baja según el modelo)"
        msg = (f"Resultado del modelo: {clase}\n\n"
               f"Puntuación del modelo (maligna): **{score:.3f}** | umbral: {thr:.3f}\n\n"
               f"_La puntuación NO es una probabilidad clínica calibrada._\n\n**{DISCLAIMER}**")
        return msg, {"maligna": score, "benigna": 1 - score}

    with gr.Blocks(title="Clasificación de lesiones mamográficas") as demo:
        gr.Markdown(f"# Clasificación de lesiones mamográficas (benigna / maligna)\n## {DISCLAIMER}")
        gr.Markdown(f"Formatos admitidos: {ALLOWED}. Más recortes para probar: [carpeta de imágenes PNG]({MAS_IMAGENES}).")
        with gr.Row():
            inp = gr.Image(type="pil", label="Recorte de la lesión")
            with gr.Column():
                out_md = gr.Markdown()
                out_lbl = gr.Label(label="Puntuación del modelo")
        gr.Button("Clasificar").click(predict, inp, [out_md, out_lbl])
        if EJEMPLOS:
            gr.Examples([[str(p)] for p in EJEMPLOS], inp, label="Ejemplos de validación (clic para cargar)")
    return demo


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="resnet18_base")
    ap.add_argument("--share", action="store_true")
    a = ap.parse_args()
    build_app(a.run).launch(share=a.share, inbrowser=not a.share)
