# Guía de ejecución para el docente

El repositorio incluye el modelo final entrenado (`runs/resnet18_base/best.pt`) y tres imágenes de ejemplo (`ejemplos/`), de modo que la interfaz se puede ejecutar sin descargar el conjunto de datos ni volver a entrenar. No se necesita GPU.

## Opción 1: en el computador propio (Windows, macOS o Linux)

Requisitos: Python 3.10 a 3.13 y Git.

```bash
git clone https://github.com/a23andres1223-source/mamografias-ac.git
cd mamografias-ac
python -m venv .venv
.venv\Scripts\activate            # Windows. En macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt   # primera vez: unos minutos (descarga PyTorch)
python app.py
```

La interfaz se abre en el navegador en `http://127.0.0.1:7860`. Para cerrarla, pulse `Ctrl + C` en la terminal.

## Opción 2: en Google Colab (sin instalar nada)

En un cuaderno nuevo de Colab, ejecute en una celda:

```python
!git clone https://github.com/a23andres1223-source/mamografias-ac.git
%cd mamografias-ac
!pip -q install gradio
!python app.py --share
```

Tras unos 30 segundos aparece un enlace `https://….gradio.live` que abre la interfaz.

## Uso de la interfaz

1. Haga clic en uno de los ejemplos, al pie de la página, o suba el recorte de una lesión (PNG, JPG, BMP o WEBP).
2. Pulse **Clasificar**.
3. La interfaz muestra la clase asignada, la puntuación del modelo y el umbral (0,045). Si la puntuación es mayor o igual que el umbral, la lesión se clasifica como maligna.

| Ejemplo | Patología real | Resultado esperado |
|---|---|---|
| `benigna_P_00021_LEFT_CC_mass_1.png` | Benigna | Benigna (puntuación 0,036) |
| `maligna_P_00009_RIGHT_CC_mass_1.png` | Maligna | Maligna (puntuación 0,206) |
| `maligna_falso_negativo_P_01744_LEFT_MLO_mass_1.png` | Maligna | Benigna (0,002): falso negativo, analizado en la sección 7 del informe |

Los ejemplos pertenecen a la partición de validación y provienen de CBIS-DDSM (TCIA, licencia CC BY 3.0).

## Resultados y reproducción completa

- Las métricas, curvas, matrices de confusión y listados de errores de cada modelo están en `runs/<modelo>/`. No hace falta ejecutar nada para consultarlos.
- Para repetir el entrenamiento y la evaluación se necesitan las imágenes de CBIS-DDSM, que por su tamaño no están en el repositorio. Los pasos están en la sección "Cómo reproducir" del `README.md`.

> Prototipo académico; no apto para diagnóstico ni para decisiones clínicas.
