"""Configuración central del proyecto: rutas y constantes compartidas por todos los scripts."""
from pathlib import Path

SEED = 42  # semilla global: particiones y entrenamiento

ROOT = Path(__file__).resolve().parent
DATA_RAW = ROOT / "data" / "raw"              # CSV y DICOM descargados de TCIA
DATA_PROCESSED = ROOT / "data" / "processed"
PNG_DIR = DATA_PROCESSED / "png"              # recortes de lesión convertidos a PNG 8 bits
LESIONS_CSV = DATA_PROCESSED / "lesions.csv"  # tabla maestra (1 fila = 1 lesión) con columna 'split'
SPLITS_DIR = DATA_PROCESSED / "splits"        # train.csv, val.csv, test.csv
RUNS_DIR = ROOT / "runs"                      # resultados de cada entrenamiento

IMG_SIZE = 224

# Mapeo etiqueta original (CBIS-DDSM, columna 'pathology') -> etiqueta del proyecto
# 0 = benigna, 1 = maligna.
LABEL_MAP = {
    "BENIGN": 0,
    "BENIGN_WITHOUT_CALLBACK": 0,
    "MALIGNANT": 1,
}
CLASS_NAMES = ["benigna", "maligna"]

# Proporciones train / val / test (la partición se hace POR PACIENTE)
SPLIT_FRACTIONS = (0.70, 0.15, 0.15)

DISCLAIMER = "Prototipo académico; no apto para diagnóstico ni decisiones clínicas"
