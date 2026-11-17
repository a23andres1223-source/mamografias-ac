"""Paso 1: de los CSV + DICOM de CBIS-DDSM a una tabla de lesiones, PNGs y particiones POR PACIENTE.

Uso:
    python prepare_data.py --types calc mass

Qué hace:
  1. Lee los CSV oficiales (calc/mass, train/test) que estén bajo data/raw/.
  2. Mapea 'pathology' -> etiqueta binaria (ver config.LABEL_MAP).
  3. Para cada lesión localiza el DICOM del RECORTE (cropped image) y lo guarda como PNG 8 bits.
     Los DICOM de máscara (binarios) se descartan automáticamente.
  4. Parte en train/val/test agrupando por patient_id (sin fuga entre pacientes).
"""
import argparse

import numpy as np
import pandas as pd
import pydicom
from PIL import Image
from sklearn.model_selection import GroupShuffleSplit
from tqdm import tqdm

import config as C
from imaging import to_uint8

CSV_FILES = {
    "calc": ["calc_case_description_train_set.csv", "calc_case_description_test_set.csv"],
    "mass": ["mass_case_description_train_set.csv", "mass_case_description_test_set.csv"],
}
REQUIRED = ["patient_id", "left_or_right_breast", "image_view", "abnormality_id",
            "pathology", "cropped_image_file_path", "roi_mask_file_path"]


def load_tables(types):
    frames = []
    for t in types:
        for name in CSV_FILES[t]:
            found = list(C.DATA_RAW.rglob(name))
            if not found:
                print(f"[aviso] no encontré {name} bajo {C.DATA_RAW}")
                continue
            df = pd.read_csv(found[0])
            # normaliza nombres de columnas: 'breast density' -> 'breast_density'
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            df["lesion_type"] = t
            df["source_csv"] = name
            frames.append(df)
    if not frames:
        raise SystemExit("No se encontró ningún CSV. Colócalos bajo data/raw/ (ver README).")
    df = pd.concat(frames, ignore_index=True)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise SystemExit(f"Faltan columnas en los CSV: {missing}. Columnas halladas: {list(df.columns)}")
    return df


def index_dirs():
    """nombre de carpeta -> rutas. Permite localizar series por nombre aunque la estructura varíe."""
    idx = {}
    for p in C.DATA_RAW.rglob("*"):
        if p.is_dir():
            idx.setdefault(p.name, []).append(p)
    return idx


def dcm_candidates(path_str, idx):
    """Devuelve los .dcm asociados a una ruta del CSV.

    El CSV trae rutas tipo  Calc-Test_P_00038_LEFT_CC_1/<studyUID>/<seriesUID>/000000.dcm
    pero la descarga de TCIA (NBIA) puede nombrar las carpetas distinto. Por eso se prueba primero
    la carpeta de la serie y, si no existe, la carpeta del caso (primer componente), que se conserva.
    """
    parts = [x for x in str(path_str).strip().replace("\\", "/").split("/") if x]
    dirs = []
    if len(parts) >= 2 and parts[-2] in idx:
        dirs = idx[parts[-2]]
    elif parts and parts[0] in idx:
        dirs = idx[parts[0]]
    files = []
    for d in dirs:
        files += sorted(d.rglob("*.dcm"))
    return files


def is_binary(arr):
    lo, hi = arr.min(), arr.max()
    return np.count_nonzero((arr != lo) & (arr != hi)) == 0


def read_crop(row, idx):
    """Devuelve (array, invertir) del recorte de la lesión, o None si no se encuentra."""
    files = dcm_candidates(row["cropped_image_file_path"], idx)
    files += dcm_candidates(row["roi_mask_file_path"], idx)
    seen = set()
    for f in files:
        if f in seen:
            continue
        seen.add(f)
        ds = pydicom.dcmread(str(f))
        arr = ds.pixel_array
        if arr.ndim == 2 and not is_binary(arr):  # el recorte NO es binario; la máscara sí
            return arr, getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1"
    return None


def make_splits(df, seed):
    tr, va, te = C.SPLIT_FRACTIONS
    g1 = GroupShuffleSplit(n_splits=1, test_size=te, random_state=seed)
    trv_idx, te_idx = next(g1.split(df, groups=df["patient_id"]))
    trv, test = df.iloc[trv_idx], df.iloc[te_idx]
    g2 = GroupShuffleSplit(n_splits=1, test_size=va / (tr + va), random_state=seed)
    tr_idx, va_idx = next(g2.split(trv, groups=trv["patient_id"]))
    train, val = trv.iloc[tr_idx], trv.iloc[va_idx]
    return train.assign(split="train"), val.assign(split="val"), test.assign(split="test")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--types", nargs="+", default=["calc", "mass"], choices=["calc", "mass"])
    ap.add_argument("--seed", type=int, default=C.SEED)
    args = ap.parse_args()

    C.PNG_DIR.mkdir(parents=True, exist_ok=True)
    C.SPLITS_DIR.mkdir(parents=True, exist_ok=True)

    df = load_tables(args.types)
    print(f"Filas en los CSV: {len(df)}")

    df["pathology"] = df["pathology"].astype(str).str.strip().str.upper()
    unknown = df[~df["pathology"].isin(C.LABEL_MAP)]
    if len(unknown):
        print(f"[aviso] {len(unknown)} filas con patología desconocida se excluyen: "
              f"{unknown['pathology'].unique().tolist()}")
    df = df[df["pathology"].isin(C.LABEL_MAP)].copy()
    df["label"] = df["pathology"].map(C.LABEL_MAP)

    df["lesion_id"] = (df["patient_id"].astype(str) + "_" + df["left_or_right_breast"].astype(str) + "_"
                       + df["image_view"].astype(str) + "_" + df["lesion_type"] + "_"
                       + df["abnormality_id"].astype(str))
    before = len(df)
    df = df.drop_duplicates(subset="lesion_id")
    print(f"Duplicados eliminados: {before - len(df)}")

    print("Indexando carpetas de data/raw (puede tardar)...")
    idx = index_dirs()

    rows, missing = [], 0
    for _, r in tqdm(df.iterrows(), total=len(df), desc="Convirtiendo a PNG"):
        out = C.PNG_DIR / f"{r['lesion_id']}.png"
        if not out.exists():
            res = read_crop(r, idx)
            if res is None:
                missing += 1
                continue
            arr, inv = res
            Image.fromarray(to_uint8(arr, invert=inv)).save(out)
        rows.append({
            "lesion_id": r["lesion_id"], "patient_id": r["patient_id"],
            "side": r["left_or_right_breast"], "view": r["image_view"],
            "lesion_type": r["lesion_type"], "pathology": r["pathology"],
            "label": int(r["label"]), "png_path": str(out), "source_csv": r["source_csv"],
        })
    print(f"Lesiones sin imagen encontrada (se excluyen): {missing}")
    if not rows:
        raise SystemExit("No se pudo convertir ninguna imagen. Revisa que los DICOM estén bajo data/raw/.")

    data = pd.DataFrame(rows)
    train, val, test = make_splits(data, args.seed)
    full = pd.concat([train, val, test], ignore_index=True)
    full.to_csv(C.LESIONS_CSV, index=False)
    for name, part in [("train", train), ("val", val), ("test", test)]:
        part.to_csv(C.SPLITS_DIR / f"{name}.csv", index=False)

    print("\nResumen por partición (semilla %d):" % args.seed)
    for name, part in [("train", train), ("val", val), ("test", test)]:
        print(f"  {name:5s} lesiones={len(part):5d} pacientes={part['patient_id'].nunique():4d} "
              f"benignas={(part['label']==0).sum():5d} malignas={(part['label']==1).sum():5d}")
    print("\nSiguiente paso: python check_split.py")


if __name__ == "__main__":
    main()
