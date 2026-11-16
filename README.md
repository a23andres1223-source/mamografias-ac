# Clasificación de lesiones mamográficas benignas/malignas (CBIS-DDSM)

> **Prototipo académico; no apto para diagnóstico ni decisiones clínicas.**
> Clasifica recortes de lesiones con patología conocida. No diagnostica cáncer ni a pacientes.

Aprendizaje Computacional – Ingeniería de Sistemas. Estructura de archivos (todo en la raíz):

| Archivo | Para qué sirve |
|---|---|
| `config.py` | Rutas, semilla, mapeo de etiquetas |
| `prepare_data.py` | CSV + DICOM → PNG + tabla de lesiones + partición por paciente |
| `check_split.py` | Comprueba que no hay fuga entre particiones |
| `dataset.py`, `models.py`, `engine.py`, `metrics.py`, `imaging.py` | Piezas reutilizables |
| `train.py` | Entrena (solo usa train y val) |
| `evaluate.py` | Métricas, umbral, errores (FN/FP) |
| `app.py` | Interfaz Gradio |
| `bitacora.md`, `registro_ia.md`, `hipotesis.md`, `mapeo_etiquetas.md`, `guia_sustentacion.md` | Documentación y evidencias |

## Paso 0. Entorno

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```
Si usas **Google Colab** (GPU gratis): sube el proyecto, activa GPU en *Entorno de ejecución* y copia los datos a `/content` (leer desde Drive es lento).
Con solo CPU funciona, pero con pocas épocas y un subconjunto pequeño.

## Paso 1 (días 1–2). Conseguir los datos

1. Abre la página de CBIS-DDSM en TCIA: https://www.cancerimagingarchive.net/collection/cbis-ddsm/
   Anota **versión, licencia, origen de las etiquetas** (para el informe; verifica la licencia en la página).
2. Descarga los 4 CSV: `calc_case_description_train_set.csv`, `calc_case_description_test_set.csv`,
   `mass_case_description_train_set.csv`, `mass_case_description_test_set.csv`.
3. Con **NBIA Data Retriever** descarga un **subconjunto** de las imágenes DICOM de **recortes/ROI** (cropped images + ROI masks).
   La opción exacta puede variar en la web de TCIA. Con los recortes basta; no necesitas las mamografías completas.
4. Pon todo dentro de `data/raw/` (cualquier subcarpeta sirve). **No subas `data/` a GitHub** (ya está en `.gitignore`).
5. Crea el repositorio (`git init`) y haz el primer commit. **Haz commits pequeños y con sentido durante todo el proyecto.**
6. Rellena `hipotesis.md` con tus dos hipótesis **antes** de entrenar. Empieza la `bitacora.md`.

## Paso 2 (días 3–5). Preparar datos, EDA y línea base

```bash
python prepare_data.py --types calc mass     # genera PNGs, data/processed/lesions.csv y splits/
python check_split.py                        # debe decir: OK, sin fuga
```
- **EDA** (haz un notebook o script corto): balance de clases, tamaños de los recortes, tipo calc vs mass,
  ejemplos visuales de cada clase, lesiones excluidas y por qué, posibles sesgos (¿subconjunto descargado?).
- Entrena la línea base:
```bash
python train.py --model baseline --run-name baseline
python evaluate.py --run baseline --split val
```

## Paso 3 (días 6–7). Transferencia de aprendizaje y preparación del control

```bash
python train.py --model resnet18 --run-name resnet18_base
python evaluate.py --run resnet18_base --split val
python evaluate.py --run resnet18_base --split val --target-sensitivity 0.90   # umbral elegido con VAL
```
Abre `runs/resnet18_base/` y mira la matriz de confusión, `fn_grid_val.png` y `errors_val.csv`.
Anota en la bitácora un inconveniente real y cómo lo resolviste (ej.: rutas DICOM que no coinciden, pocas imágenes, sobreajuste).

### Lista de verificación del día 7
- [ ] Repositorio abierto con commits fechados; puedo explicar **dos decisiones mías**.
- [ ] `python check_split.py` muestra distribución por clases y 0 pacientes compartidos.
- [ ] Tengo un entrenamiento preliminar y sé interpretar su resultado.
- [ ] Bitácora al día (fecha, dificultad, alternativas, decisión, evidencia, contribución).
- [ ] Registro de consultas a IA al día (`registro_ia.md`).
- [ ] Sé hacer en vivo: cambiar umbral, localizar un falso negativo, revisar identificadores, alterar una transformación (ver abajo).

### Cambios en vivo: dónde tocar
| Te piden… | Haz esto |
|---|---|
| Cambiar el umbral | `python evaluate.py --run resnet18_base --split val --threshold 0.35` |
| Localizar un falso negativo | Abre `runs/<run>/errors_val.csv` (columna `error`=falso_negativo, `png_path`) y `fn_grid_val.png` |
| Revisar identificadores | `python check_split.py`; o `pd.read_csv('data/processed/splits/val.csv')['patient_id']` |
| Alterar una transformación | `get_transforms()` en `dataset.py` (ej. quitar `RandomRotation` o cambiar `img_size`) y reentrenar |
| Cambiar una semilla / partición | `--seed` en `prepare_data.py` (regenera particiones) y `train.py` |

## Pasos posteriores (días 8–15)

- **Experimento controlado** (cambia UNA sola cosa): sin aumentos vs con aumentos, `--freeze` vs ajuste completo, o `resnet18` vs `efficientnet_b0`.
  ```bash
  python train.py --model resnet18 --no-augment --run-name resnet18_sin_aug
  python evaluate.py --run resnet18_sin_aug --split val
  ```
- **Umbral**: se elige con validación (`--target-sensitivity`). Analiza FN/FP y el costo de mover el umbral.
- **Interfaz**: `python app.py --run resnet18_base`
- **Prueba final (una sola vez, días 12–14)**: `python evaluate.py --run resnet18_base --split test`
- **Informe** (máx. 10 páginas): EDA, decisiones, experimentos, métricas, errores, límites.
- **Reproducibilidad**: `pip freeze > requirements-lock.txt`, documentar semilla, particiones y tiempos (ya quedan en `runs/<run>/config.json`).
