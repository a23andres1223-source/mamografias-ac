"""Genera informe.pdf e informe.docx a partir de informe.md.

Requisitos: pandoc, weasyprint, python-docx, matplotlib y la fuente IBM Plex
(en Colab: apt-get install pandoc fonts-ibm-plex; pip install weasyprint python-docx).

    python informe/generar_informe.py
"""
import json
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from matplotlib import font_manager
from PIL import Image, ImageOps

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
FIG = AQUI / "figuras"
SERIF, SANS = "IBM Plex Serif", "IBM Plex Sans"
NEGRO, GRIS_OSCURO, GRIS, GRIS_CLARO = "#111111", "#444444", "#8c8c8c", "#d9d9d9"


def estilo_graficos():
    disponibles = {f.name for f in font_manager.fontManager.ttflist}
    plt.rcParams.update({
        "font.family": SANS if SANS in disponibles else "DejaVu Sans",
        "font.size": 9, "axes.edgecolor": GRIS_OSCURO, "axes.labelcolor": NEGRO,
        "xtick.color": GRIS_OSCURO, "ytick.color": GRIS_OSCURO,
        "axes.spines.top": False, "axes.spines.right": False,
        "savefig.dpi": 200, "savefig.bbox": "tight",
    })


def figura_clases():
    filas = []
    for parte, nombre in [("train", "Entrenamiento"), ("val", "Validación"), ("test", "Prueba")]:
        df = pd.read_csv(RAIZ / "data" / "processed" / "splits" / f"{parte}.csv")
        filas.append((nombre, int((df["label"] == 0).sum()), int((df["label"] == 1).sum())))
    x = np.arange(len(filas))
    fig, ax = plt.subplots(figsize=(5.2, 2.8))
    b = ax.bar(x - 0.19, [f[1] for f in filas], 0.38, color=GRIS, label="Benigna")
    m = ax.bar(x + 0.19, [f[2] for f in filas], 0.38, color=NEGRO, label="Maligna")
    ax.bar_label(b, fontsize=8, color=GRIS_OSCURO, padding=2)
    ax.bar_label(m, fontsize=8, color=GRIS_OSCURO, padding=2)
    ax.set_xticks(x, [f[0] for f in filas])
    ax.set_ylabel("Lesiones")
    ax.legend(frameon=False, loc="upper right")
    fig.savefig(FIG / "clases_por_particion.png")
    plt.close(fig)


def figura_confusion_roc():
    m = json.loads((RAIZ / "runs" / "resnet18_base" / "metrics_test.json").read_text())
    cm = np.array([[m["tn"], m["fp"]], [m["fn"], m["tp"]]])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 3.4), gridspec_kw={"width_ratios": [1, 1.15]})
    a1.imshow(cm, cmap="Greys", vmin=0, vmax=cm.max() * 1.6)
    for i in range(2):
        for j in range(2):
            a1.text(j, i, cm[i, j], ha="center", va="center", fontsize=13, color=NEGRO)
    a1.set_xticks([0, 1], ["Benigna", "Maligna"])
    a1.set_yticks([0, 1], ["Benigna", "Maligna"])
    a1.set_xlabel("Predicción")
    a1.set_ylabel("Real")
    a1.set_title(f"Umbral {m['threshold']:.3f}", fontsize=9, color=GRIS_OSCURO)
    for s in a1.spines.values():
        s.set_visible(False)
    roc = ImageOps.grayscale(Image.open(RAIZ / "runs" / "resnet18_base" / "roc_test.png").convert("RGB"))
    a2.imshow(roc, cmap="gray")
    a2.axis("off")
    fig.savefig(FIG / "confusion_roc_test.png")
    plt.close(fig)


def figura_falsos_negativos():
    img = Image.open(RAIZ / "runs" / "resnet18_base" / "fn_grid_test.png").convert("RGB")
    ImageOps.grayscale(img).save(FIG / "fn_grid_test.png")


def pdf():
    html = AQUI / "informe.html"
    subprocess.run(["pandoc", str(RAIZ / "informe.md"), "-s", "-o", str(html),
                    "--template", str(AQUI / "plantilla.html"), "-c", "informe/estilo.css"], check=True)
    from weasyprint import HTML
    HTML(filename=str(html), base_url=str(RAIZ)).write_pdf(RAIZ / "informe.pdf")
    html.unlink()


def _borde(celda, lado, grosor, color):
    tcPr = celda._tc.get_or_add_tcPr()
    bordes = tcPr.find(qn("w:tcBorders"))
    if bordes is None:
        bordes = OxmlElement("w:tcBorders")
        tcPr.append(bordes)
    b = OxmlElement(f"w:{lado}")
    b.set(qn("w:val"), "single")
    b.set(qn("w:sz"), str(grosor))
    b.set(qn("w:color"), color)
    bordes.append(b)


def _fuente(estilo, nombre, tam, negrita=None, color=NEGRO, cursiva=None):
    f = estilo.font
    f.name, f.size, f.color.rgb = nombre, Pt(tam), RGBColor.from_string(color.lstrip("#"))
    if negrita is not None:
        f.bold = negrita
    if cursiva is not None:
        f.italic = cursiva
    rpr = estilo.element.get_or_add_rPr()
    fuentes = rpr.find(qn("w:rFonts"))
    if fuentes is None:
        fuentes = OxmlElement("w:rFonts")
        rpr.append(fuentes)
    for atributo in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fuentes.set(qn(atributo), nombre)
    for atributo in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        fuentes.attrib.pop(qn(atributo), None)


def docx():
    ref = AQUI / "referencia.docx"
    subprocess.run(["pandoc", "-o", str(ref), "--print-default-data-file", "reference.docx"], check=True)
    d = Document(ref)
    estilos = {s.name: s for s in d.styles}
    for nombre in ["Normal", "Body Text", "First Paragraph", "Compact"]:
        if nombre in estilos:
            _fuente(estilos[nombre], SERIF, 10.5)
    _fuente(estilos["Title"], SANS, 20, negrita=True)
    _fuente(estilos["Subtitle"], SANS, 13, negrita=False, color=GRIS_OSCURO)
    for nombre in ["Author", "Date"]:
        if nombre in estilos:
            _fuente(estilos[nombre], SANS, 11, color=GRIS_OSCURO)
    _fuente(estilos["Heading 2"], SANS, 13, negrita=True)
    _fuente(estilos["Heading 3"], SANS, 11, negrita=True, color=GRIS_OSCURO)
    for nombre in ["Caption", "Table Caption", "Image Caption"]:
        if nombre in estilos:
            _fuente(estilos[nombre], SANS, 9, color=GRIS_OSCURO, cursiva=False)
    if "Block Text" in estilos:
        _fuente(estilos["Block Text"], SANS, 9.5, color=GRIS_OSCURO)
    d.save(ref)

    salida = RAIZ / "informe.docx"
    subprocess.run(["pandoc", str(RAIZ / "informe.md"), "-o", str(salida), "--reference-doc", str(ref),
                    "--resource-path", str(RAIZ)], check=True)
    ref.unlink()

    d = Document(salida)
    for p in d.paragraphs:
        if p.style.name in ("Body Text", "First Paragraph"):
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for tabla in d.tables:
        filas = tabla.rows
        for i, fila in enumerate(filas):
            for celda in fila.cells:
                for p in celda.paragraphs:
                    for r in p.runs:
                        r.font.name, r.font.size = SANS, Pt(9)
                        if i == 0:
                            r.font.bold = True
                if i == 0:
                    _borde(celda, "top", 12, "111111")
                    _borde(celda, "bottom", 6, "111111")
                elif i == len(filas) - 1:
                    _borde(celda, "bottom", 12, "111111")
                else:
                    _borde(celda, "bottom", 2, "BFBFBF")
    d.save(salida)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    estilo_graficos()
    figura_clases()
    figura_confusion_roc()
    figura_falsos_negativos()
    pdf()
    docx()
    print("Generados: informe.pdf, informe.docx y", ", ".join(p.name for p in sorted(FIG.glob("*.png"))))
