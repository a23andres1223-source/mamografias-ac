"""Utilidades compartidas por train.py, evaluate.py y app.py."""
import json
import random

import numpy as np
import torch
import torch.nn.functional as F

import config as C
from models import build_model


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@torch.no_grad()
def predict(model, loader, device):
    """Devuelve (etiquetas, puntuación de la clase maligna, pérdida media)."""
    model.eval()
    ys, ss, loss_sum, n = [], [], 0.0, 0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        loss_sum += F.cross_entropy(logits, y, reduction="sum").item()
        n += len(y)
        ss.append(torch.softmax(logits, 1)[:, 1].cpu().numpy())
        ys.append(y.cpu().numpy())
    return np.concatenate(ys), np.concatenate(ss), loss_sum / max(n, 1)


def load_model(run_name, device):
    run_dir = C.RUNS_DIR / run_name
    cfg = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    model = build_model(cfg["model"], pretrained=False)
    state = torch.load(run_dir / "best.pt", map_location=device)
    model.load_state_dict(state["state_dict"])
    return model.to(device).eval(), cfg, run_dir
