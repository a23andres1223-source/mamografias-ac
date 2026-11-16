"""Conversión de matrices de píxeles a imágenes de 8 bits.

Se usa tanto en la preparación de datos como en la interfaz Gradio, para que el
preprocesamiento sea EL MISMO en entrenamiento y en inferencia.
"""
import numpy as np


def to_uint8(arr, invert=False, p_low=1, p_high=99):
    """Recorta en los percentiles [p_low, p_high] y escala a 0-255.

    Por qué percentiles: las mamografías DICOM vienen en 12-16 bits y tienen píxeles
    extremos (ruido, marcas). Recortar el 1% de cada extremo evita que unos pocos
    valores atípicos aplasten el contraste del resto.
    """
    a = np.asarray(arr, dtype=np.float32)
    lo, hi = np.percentile(a, [p_low, p_high])
    if hi <= lo:
        lo, hi = float(a.min()), float(a.max())
    if hi <= lo:
        return np.zeros(a.shape, dtype=np.uint8)
    a = np.clip((a - lo) / (hi - lo), 0.0, 1.0)
    if invert:  # DICOM MONOCHROME1: el valor mínimo es blanco
        a = 1.0 - a
    return (a * 255).astype(np.uint8)
