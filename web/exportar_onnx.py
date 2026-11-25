"""Exporta el modelo final a ONNX para la página web estática (web/index.html).

    python web/exportar_onnx.py

Genera web/modelo.onnx y compara, con las imágenes de ejemplos/, la puntuación de
PyTorch (mismo preprocesamiento que app.py) con la del modelo ONNX.
Requiere: pip install onnx onnxruntime
"""
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from dataset import get_transforms  # noqa: E402
from engine import load_model  # noqa: E402
from imaging import to_uint8  # noqa: E402

SALIDA = RAIZ / "web" / "modelo.onnx"


def tensor_como_app(ruta):
    """Mismo flujo que app.py: RGB -> gris -> to_uint8 -> RGB -> transformaciones de validación."""
    arr = np.array(Image.open(ruta).convert("RGB")).astype(np.float64).mean(axis=2)
    pil = Image.fromarray(to_uint8(arr)).convert("RGB")
    return get_transforms(train=False)(pil).unsqueeze(0)


def exportar(model):
    x = torch.zeros(1, 3, 224, 224)
    args = dict(input_names=["entrada"], output_names=["logits"], opset_version=17)
    try:
        torch.onnx.export(model, x, str(SALIDA), dynamo=False, **args)
    except Exception as e:  # versiones de PyTorch sin el exportador clásico
        print("Exportador clásico no disponible:", type(e).__name__)
        torch.onnx.export(model, x, str(SALIDA), dynamo=True, external_data=False, **args)


if __name__ == "__main__":
    import onnxruntime as ort

    model, _, _ = load_model("resnet18_base", torch.device("cpu"))
    exportar(model)
    sesion = ort.InferenceSession(str(SALIDA))
    nombre = sesion.get_inputs()[0].name
    for ruta in sorted((RAIZ / "ejemplos").glob("*.png")):
        t = tensor_como_app(ruta)
        with torch.no_grad():
            pt = torch.softmax(model(t), 1)[0, 1].item()
        lo = sesion.run(None, {nombre: t.numpy()})[0][0].astype(np.float64)
        on = float(np.exp(lo[1] - lo.max()) / np.exp(lo - lo.max()).sum())
        print(f"{ruta.name}: PyTorch {pt:.6f} | ONNX {on:.6f}")
    print("Archivos:", [(p.name, round(p.stat().st_size / 1e6, 1)) for p in SALIDA.parent.glob("modelo.onnx*")])
