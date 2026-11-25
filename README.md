# Clasificación de lesiones mamográficas benignas/malignas (CBIS-DDSM)

> **Prototipo académico; no apto para diagnóstico ni decisiones clínicas.**
> Clasifica recortes de masas con patología conocida. No detecta lesiones ni diagnostica pacientes.

Proyecto final de Aprendizaje Computacional – Ingeniería de Sistemas, Universidad de Córdoba.
**Integrantes:** Andrés Alfonso Burgos y Carmelo de Jesús Quiceno Páez. Informe: [`informe.md`](informe.md).

## Demostración en línea

**https://andres1223-mamografias.static.hf.space**: el modelo final (exportado a ONNX con `web/exportar_onnx.py`) se ejecuta en el navegador, sin instalar nada. Código de la página: `web/index.html`. Más recortes para probar (solo lectura): [carpeta de imágenes PNG en Google Drive](https://drive.google.com/drive/folders/1aVHj3Scb4ZAW-S-Llsub6KrvAp352mh3).

## Ejecutar la interfaz

El repositorio incluye el modelo final (`runs/resnet18_base/best.pt`) y tres imágenes de ejemplo (`ejemplos/`); no se necesita GPU ni descargar datos:

```bash
git clone https://github.com/a23andres1223-source/mamografias-ac.git
cd mamografias-ac
pip install -r requirements.txt
python app.py                    # abre http://127.0.0.1:7860
```

Instrucciones detalladas (entorno virtual, Google Colab y ejemplos): [`GUIA_PROFESOR.md`](GUIA_PROFESOR.md).

## Resultado final

Modelo: **ResNet18 preentrenada en ImageNet, ajuste completo, con aumento de datos** (`runs/resnet18_base`).
Umbral **0,045**, elegido en validación para sensibilidad ≥ 0,90. La prueba se usó una sola vez.

| Partición | ROC-AUC | Sensibilidad | Especificidad | Precisión | F1 | TN / FP / FN / TP |
|---|---|---|---|---|---|---|
| Validación (244) | 0,836 | 0,908 | 0,512 | 0,639 | 0,750 | 64 / 61 / 11 / 108 |
| Prueba (273) | 0,821 | 0,896 | 0,500 | 0,566 | 0,694 | 79 / 79 / 12 / 103 |

Comparación en validación (sensibilidad 0,908 en los tres): CNN pequeña val_AUC 0,634 y especificidad 0,128; ResNet18 sin aumento val_AUC 0,837 y especificidad 0,592.

## Datos

CBIS-DDSM (TCIA, versión 1, CC BY 3.0), solo masas: 1.691 lesiones de 892 pacientes (911 benignas, 780 malignas).
Partición **por paciente** (semilla 42): train 1.174, val 244, test 273; 0 pacientes compartidos.
Las imágenes no están en el repositorio (`data/` está en `.gitignore`), salvo los tres ejemplos de `ejemplos/`. De los pesos, solo se incluye el del modelo final (`runs/resnet18_base/best.pt`); los datos procesados y los pesos de los demás modelos están respaldados en Google Drive (`Proyecto_Mamografias/trabajo/`).

## Estructura

| Archivo | Para qué sirve |
|---|---|
| `config.py` | Rutas, semilla, mapeo de etiquetas |
| `prepare_data.py` | CSV + DICOM → PNG + tabla de lesiones + partición por paciente |
| `check_split.py` | Comprueba que no hay fuga entre particiones |
| `dataset.py`, `models.py`, `engine.py`, `metrics.py`, `imaging.py` | Piezas reutilizables |
| `train.py` | Entrena (solo usa train y val) |
| `evaluate.py` | Métricas, umbral, errores (FN/FP) |
| `app.py` | Interfaz Gradio (`python app.py`) |
| `helpers.py` | Funciones para retomar sesiones de Colab (respaldo en Drive, bitácora, commits) |
| `runs/` | Configuración, curvas, métricas, figuras y errores de cada corrida |
| `ejemplos/` | Tres recortes de validación para probar la interfaz |
| `GUIA_PROFESOR.md` | Cómo ejecutar la interfaz en un computador propio o en Colab |
| `web/` | Página estática de la demostración en línea (`index.html`), script de exportación a ONNX y etiquetas de las lesiones |
| `eda/`, `eda_conclusiones.md` | Análisis exploratorio |
| `hipotesis.md`, `mapeo_etiquetas.md` | Problema, hipótesis y etiquetas |
| `bitacora.md`, `registro_ia.md` | Bitácora de decisiones y registro de uso de IA |
| `informe.md`, `informe.pdf`, `informe.docx`, `informe/` | Informe final y el script, plantilla y estilo con que se genera (`python informe/generar_informe.py`) |
| `requirements.txt`, `requirements-lock.txt`, `entorno.json` | Dependencias y versiones exactas del entorno final |

## Cómo reproducir

```bash
python -m venv .venv            # Windows: .venv\Scripts\activate   Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt  # versiones exactas: requirements-lock.txt
```
En Google Colab (GPU T4) se usó el cuaderno `MamografiasProyecto.ipynb`; la sección "Cierre del proyecto" restaura el entorno desde GitHub y Drive.

1. Descarga los CSV de masas de CBIS-DDSM y los recortes DICOM con NBIA Data Retriever (manifiesto filtrado por los UID de los CSV) en `data/raw/`.
2. Prepara y verifica los datos:
   ```bash
   python prepare_data.py --types mass
   python check_split.py
   ```
3. Entrena:
   ```bash
   python train.py --model baseline --run-name baseline_cnn
   python train.py --model resnet18 --run-name resnet18_base
   python train.py --model resnet18 --no-augment --run-name resnet18_sin_aug
   ```
4. Evalúa y elige el umbral en validación; la prueba, una sola vez al final:
   ```bash
   python evaluate.py --run resnet18_base --split val --target-sensitivity 0.90
   python evaluate.py --run resnet18_base --split test
   ```
5. Interfaz: `python app.py` (usa `runs/resnet18_base`; con `--share` genera un enlace temporal).

## Cambios en vivo

| Cambio | Cómo hacerlo |
|---|---|
| Cambiar el umbral | `python evaluate.py --run resnet18_base --split val --threshold 0.35` |
| Localizar un falso negativo | `runs/<run>/errors_val.csv` (columna `error` = falso_negativo, `png_path`) y `fn_grid_val.png` |
| Revisar identificadores | `python check_split.py`; o `pd.read_csv('data/processed/splits/val.csv')['patient_id']` |
| Alterar una transformación | `get_transforms()` en `dataset.py` (p. ej. quitar `RandomRotation` o cambiar `img_size`) y reentrenar |
| Cambiar una semilla / partición | `--seed` en `prepare_data.py` (regenera particiones) y en `train.py` |

> Cambiar el umbral con `--threshold` reescribe `metrics_val.json`; el umbral oficial sigue en `threshold.json`, así que `python evaluate.py --run resnet18_base --split val` (sin `--threshold`) restaura las métricas oficiales.
