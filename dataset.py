"""Dataset de PyTorch y transformaciones.

get_transforms() se reutiliza en la interfaz Gradio: así el preprocesamiento de inferencia
es idéntico al de validación/prueba.
"""
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms as T

import config as C

MEAN = [0.485, 0.456, 0.406]  # estadísticas de ImageNet (las espera ResNet/EfficientNet preentrenadas)
STD = [0.229, 0.224, 0.225]


class PadToSquare:
    """Rellena con negro hasta hacer la imagen cuadrada, para no deformar la lesión al redimensionar."""

    def __call__(self, img):
        w, h = img.size
        s = max(w, h)
        canvas = Image.new(img.mode, (s, s), 0)
        canvas.paste(img, ((s - w) // 2, (s - h) // 2))
        return canvas


def get_transforms(train, augment=True, img_size=C.IMG_SIZE):
    steps = [PadToSquare(), T.Resize((img_size, img_size))]
    if train and augment:
        # Aumentos moderados y SOLO en entrenamiento. Validación y prueba nunca se alteran.
        steps += [T.RandomHorizontalFlip(), T.RandomRotation(10),
                  T.ColorJitter(brightness=0.1, contrast=0.1)]
    steps += [T.ToTensor(), T.Normalize(MEAN, STD)]
    return T.Compose(steps)


class LesionDataset(Dataset):
    def __init__(self, csv_path, train=False, augment=True):
        self.df = pd.read_csv(csv_path).reset_index(drop=True)
        self.tf = get_transforms(train, augment)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, i):
        row = self.df.iloc[i]
        img = Image.open(row["png_path"]).convert("RGB")  # gris -> 3 canales (lo exige el modelo preentrenado)
        return self.tf(img), torch.tensor(int(row["label"]), dtype=torch.long)
