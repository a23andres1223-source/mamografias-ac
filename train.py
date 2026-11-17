"""Entrenamiento. Usa SOLO train (ajustar pesos) y val (elegir la mejor época). La prueba no se toca.

Ejemplos:
    python train.py --model baseline --run-name baseline
    python train.py --model resnet18 --run-name resnet18_base
    python train.py --model resnet18 --no-augment --run-name resnet18_sin_aug   # experimento controlado
"""
import argparse
import json
import time

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

import config as C
from dataset import LesionDataset
from engine import get_device, predict, set_seed
from metrics import compute_metrics
from models import build_model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="resnet18", choices=["baseline", "resnet18", "efficientnet_b0"])
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=None, help="por defecto 1e-3 baseline, 1e-4 transferencia")
    ap.add_argument("--optimizer", default="adam", choices=["adam", "sgd"])
    ap.add_argument("--seed", type=int, default=C.SEED)
    ap.add_argument("--no-augment", action="store_true")
    ap.add_argument("--freeze", action="store_true", help="congela el backbone (solo entrena la capa final)")
    ap.add_argument("--no-pretrained", action="store_true")
    ap.add_argument("--workers", type=int, default=0, help="0 es lo más seguro en Windows")
    ap.add_argument("--run-name", default=None)
    args = ap.parse_args()

    lr = args.lr or (1e-3 if args.model == "baseline" else 1e-4)
    name = args.run_name or f"{args.model}_s{args.seed}"
    run_dir = C.RUNS_DIR / name
    run_dir.mkdir(parents=True, exist_ok=True)

    set_seed(args.seed)
    device = get_device()
    print(f"Dispositivo: {device} | run: {name}")

    train_ds = LesionDataset(C.SPLITS_DIR / "train.csv", train=True, augment=not args.no_augment)
    val_ds = LesionDataset(C.SPLITS_DIR / "val.csv", train=False)
    gen = torch.Generator().manual_seed(args.seed)
    train_dl = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                          num_workers=args.workers, generator=gen)
    val_dl = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=args.workers)

    model = build_model(args.model, pretrained=not args.no_pretrained, freeze=args.freeze).to(device)
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.Adam(params, lr=lr) if args.optimizer == "adam" else \
        torch.optim.SGD(params, lr=lr, momentum=0.9)

    # Pesos de clase: compensan el desbalance (las clases no suelen estar 50/50)
    counts = train_ds.df["label"].value_counts().reindex([0, 1]).fillna(1).values
    weights = torch.tensor(counts.sum() / (2 * counts), dtype=torch.float32).to(device)
    criterion = nn.CrossEntropyLoss(weight=weights)

    history, best_auc, t0 = [], -1.0, time.time()
    for ep in range(1, args.epochs + 1):
        model.train()
        run_loss, n = 0.0, 0
        for x, y in train_dl:
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            opt.step()
            run_loss += loss.item() * len(y)
            n += len(y)
        yv, sv, vloss = predict(model, val_dl, device)
        m = compute_metrics(yv, sv, 0.5)
        row = {"epoch": ep, "train_loss": run_loss / n, "val_loss": vloss, "val_auc": m["roc_auc"],
               "val_sens@0.5": m["sensitivity"], "val_spec@0.5": m["specificity"]}
        history.append(row)
        print(f"ép {ep:2d} | train_loss {row['train_loss']:.4f} | val_loss {vloss:.4f} | "
              f"val_AUC {m['roc_auc']:.3f} | sens {m['sensitivity']:.3f} | espec {m['specificity']:.3f}")
        if m["roc_auc"] > best_auc:  # la mejor época se elige con VALIDACIÓN, nunca con prueba
            best_auc = m["roc_auc"]
            torch.save({"state_dict": model.state_dict(), "epoch": ep}, run_dir / "best.pt")

    elapsed = time.time() - t0
    pd.DataFrame(history).to_csv(run_dir / "history.csv", index=False)
    cfg = {**vars(args), "lr": lr, "run_name": name, "device": str(device),
           "n_train": len(train_ds), "n_val": len(val_ds),
           "class_counts_train": {"benigna": int(counts[0]), "maligna": int(counts[1])},
           "best_val_auc": best_auc, "train_seconds": round(elapsed, 1)}
    (run_dir / "config.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nListo en {elapsed/60:.1f} min. Mejor val_AUC={best_auc:.3f}. Guardado en {run_dir}")
    print(f"Siguiente: python evaluate.py --run {name} --split val")


if __name__ == "__main__":
    main()
