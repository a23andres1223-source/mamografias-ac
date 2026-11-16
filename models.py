"""Modelos: línea base (CNN pequeña desde cero) y transferencia de aprendizaje."""
import torch.nn as nn
from torchvision import models


class SmallCNN(nn.Module):
    """Línea base: 4 bloques conv-BN-ReLU-pool + pooling global + capa lineal. ~100k parámetros."""

    def __init__(self, n_classes=2):
        super().__init__()

        def block(i, o):
            return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o),
                                 nn.ReLU(inplace=True), nn.MaxPool2d(2))

        self.features = nn.Sequential(block(3, 16), block(16, 32), block(32, 64), block(64, 128))
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Sequential(nn.Dropout(0.3), nn.Linear(128, n_classes))

    def forward(self, x):
        return self.classifier(self.pool(self.features(x)).flatten(1))


def build_model(name, pretrained=True, freeze=False):
    """Devuelve un modelo que produce 2 logits (benigna, maligna)."""
    if name == "baseline":
        return SmallCNN()
    if name == "resnet18":
        w = models.ResNet18_Weights.DEFAULT if pretrained else None
        m = models.resnet18(weights=w)
        if freeze:
            for p in m.parameters():
                p.requires_grad = False
        m.fc = nn.Linear(m.fc.in_features, 2)  # capa nueva: siempre entrenable
        return m
    if name == "efficientnet_b0":
        w = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        m = models.efficientnet_b0(weights=w)
        if freeze:
            for p in m.parameters():
                p.requires_grad = False
        m.classifier[1] = nn.Linear(m.classifier[1].in_features, 2)
        return m
    raise ValueError(f"Modelo desconocido: {name}")
