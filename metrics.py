"""Métricas de evaluación y selección de umbral."""
import numpy as np
from sklearn.metrics import confusion_matrix, roc_auc_score

NAN = float("nan")


def safe_auc(y, s):
    y = np.asarray(y)
    return float(roc_auc_score(y, s)) if len(np.unique(y)) > 1 else NAN


def compute_metrics(y, s, thr=0.5):
    """Clase positiva = maligna (1). Predice 'maligna' si puntuación >= umbral."""
    y = np.asarray(y).astype(int)
    s = np.asarray(s, dtype=float)
    pred = (s >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    sens = tp / (tp + fn) if (tp + fn) else NAN   # sensibilidad de malignidad (recall)
    spec = tn / (tn + fp) if (tn + fp) else NAN   # especificidad
    prec = tp / (tp + fp) if (tp + fp) else NAN   # precisión (VPP)
    f1 = 2 * prec * sens / (prec + sens) if (prec == prec and sens == sens and (prec + sens) > 0) else NAN
    return {
        "threshold": float(thr), "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "sensitivity": sens, "specificity": spec, "precision": prec, "f1": f1,
        "accuracy": float((tp + tn) / len(y)), "roc_auc": safe_auc(y, s),
    }


def threshold_for_sensitivity(y, s, target=0.90):
    """Umbral MÁS ALTO que aún logra sensibilidad >= target. Se calcula SOLO con validación."""
    y = np.asarray(y).astype(int)
    s = np.asarray(s, dtype=float)
    pos = s[y == 1]
    for t in np.unique(s)[::-1]:  # de mayor a menor: la sensibilidad no decrece al bajar el umbral
        if (pos >= t).mean() >= target:
            return float(t)
    return 0.0
