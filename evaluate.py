"""Evaluación: matriz de confusión, sensibilidad, especificidad, precisión, F1, ROC-AUC y errores.

    python evaluate.py --run resnet18_base --split val
    python evaluate.py --run resnet18_base --split val --threshold 0.35            # cambiar umbral en vivo
    python evaluate.py --run resnet18_base --split val --target-sensitivity 0.90   # elegir umbral con VAL
    python evaluate.py --run resnet18_base --split test                            # SOLO al final, una vez

Salida en runs/<run>/: metrics_<split>.json, confusion_<split>.png, roc_<split>.png,
errors_<split>.csv (falsos negativos/positivos con ruta de imagen) y rejillas de errores.
"""
import argparse
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.metrics import roc_curve
from torch.utils.data import DataLoader

import config as C
from dataset import LesionDataset
from engine import get_device, load_model, predict
from metrics import compute_metrics, threshold_for_sensitivity


def save_grid(df, path, title, n=12):
    df = df.head(n)
    if df.empty:
        return
    cols = 4
    rows = int(np.ceil(len(df) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3.2 * rows))
    for ax in np.atleast_1d(axes).ravel():
        ax.axis("off")
    for ax, (_, r) in zip(np.atleast_1d(axes).ravel(), df.iterrows()):
        ax.imshow(Image.open(r["png_path"]), cmap="gray")
        ax.set_title(f"{r['lesion_id']}\npuntuación={r['score']:.2f}", fontsize=7)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--split", default="val", choices=["val", "test"])
    ap.add_argument("--threshold", type=float, default=None)
    ap.add_argument("--target-sensitivity", type=float, default=None)
    ap.add_argument("--workers", type=int, default=0)
    args = ap.parse_args()

    if args.split == "test":
        print("*** PRUEBA: úsala una sola vez, al final. No ajustes nada con este resultado. ***")
        if args.target_sensitivity is not None:
            raise SystemExit("El umbral NO se selecciona con prueba. Usa --split val.")

    device = get_device()
    model, cfg, run_dir = load_model(args.run, device)
    ds = LesionDataset(C.SPLITS_DIR / f"{args.split}.csv", train=False)
    dl = DataLoader(ds, batch_size=32, shuffle=False, num_workers=args.workers)
    y, s, _ = predict(model, dl, device)

    thr_file = run_dir / "threshold.json"
    if args.target_sensitivity is not None:
        thr = threshold_for_sensitivity(y, s, args.target_sensitivity)
        thr_file.write_text(json.dumps({"threshold": thr, "selected_on": "val",
                                        "target_sensitivity": args.target_sensitivity}, indent=2))
        print(f"Umbral elegido en validación para sensibilidad >= {args.target_sensitivity}: {thr:.4f}")
    elif args.threshold is not None:
        thr = args.threshold
    elif thr_file.exists():
        thr = json.loads(thr_file.read_text())["threshold"]
        print(f"Usando umbral guardado (elegido en validación): {thr:.4f}")
    else:
        thr = 0.5

    m = compute_metrics(y, s, thr)
    (run_dir / f"metrics_{args.split}.json").write_text(json.dumps(m, indent=2))
    print(f"\n== {args.run} | {args.split} | umbral {thr:.3f} ==")
    print(f"Matriz de confusión  TN={m['tn']} FP={m['fp']} | FN={m['fn']} TP={m['tp']}")
    for k in ["sensitivity", "specificity", "precision", "f1", "accuracy", "roc_auc"]:
        print(f"{k:12s}: {m[k]:.3f}")

    # Matriz de confusión
    cm = np.array([[m["tn"], m["fp"]], [m["fn"], m["tp"]]])
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(cm, cmap="Blues")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=14)
    ax.set_xticks([0, 1], C.CLASS_NAMES)
    ax.set_yticks([0, 1], C.CLASS_NAMES)
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Real")
    ax.set_title(f"{args.split} (umbral {thr:.2f})")
    fig.tight_layout()
    fig.savefig(run_dir / f"confusion_{args.split}.png", dpi=120)
    plt.close(fig)

    # Curva ROC
    if len(np.unique(y)) > 1:
        fpr, tpr, _ = roc_curve(y, s)
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.plot(fpr, tpr, label=f"AUC={m['roc_auc']:.3f}")
        ax.plot([0, 1], [0, 1], "--", color="gray")
        ax.set_xlabel("1 - especificidad")
        ax.set_ylabel("Sensibilidad")
        ax.legend()
        fig.tight_layout()
        fig.savefig(run_dir / f"roc_{args.split}.png", dpi=120)
        plt.close(fig)

    # Errores reales para analizar
    res = ds.df.copy()
    res["score"] = s
    res["pred"] = (s >= thr).astype(int)
    fn = res[(res["label"] == 1) & (res["pred"] == 0)].assign(error="falso_negativo")
    fp = res[(res["label"] == 0) & (res["pred"] == 1)].assign(error="falso_positivo")
    errors = pd.concat([fn.sort_values("score"), fp.sort_values("score", ascending=False)])
    errors.to_csv(run_dir / f"errors_{args.split}.csv", index=False)
    print(f"Errores guardados: {len(fn)} falsos negativos, {len(fp)} falsos positivos "
          f"-> {run_dir / f'errors_{args.split}.csv'}")
    save_grid(fn.sort_values("score"), run_dir / f"fn_grid_{args.split}.png", "Falsos negativos (malignas no detectadas)")
    save_grid(fp.sort_values("score", ascending=False), run_dir / f"fp_grid_{args.split}.png", "Falsos positivos")


if __name__ == "__main__":
    main()
