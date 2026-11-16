"""Comprobación anti-fuga: ningún paciente (ni imagen) puede estar en dos particiones.

Es lo que te pedirán mostrar en vivo el día 7:
    python check_split.py
"""
import sys

import pandas as pd

import config as C


def main():
    parts = {n: pd.read_csv(C.SPLITS_DIR / f"{n}.csv") for n in ["train", "val", "test"]}

    print(f"{'split':6s} {'lesiones':>9s} {'pacientes':>10s} {'benignas':>9s} {'malignas':>9s} {'% malignas':>11s}")
    for n, d in parts.items():
        pos = (d["label"] == 1).sum()
        print(f"{n:6s} {len(d):9d} {d['patient_id'].nunique():10d} {(d['label']==0).sum():9d} "
              f"{pos:9d} {100*pos/len(d):10.1f}%")

    ok = True
    names = list(parts)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            shared_p = set(parts[a]["patient_id"]) & set(parts[b]["patient_id"])
            shared_i = set(parts[a]["png_path"]) & set(parts[b]["png_path"])
            print(f"Pacientes compartidos {a}-{b}: {len(shared_p)} | imágenes compartidas: {len(shared_i)}")
            ok &= (len(shared_p) == 0 and len(shared_i) == 0)

    print("\nRESULTADO:", "OK, sin fuga entre particiones" if ok else "FUGA DETECTADA")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
