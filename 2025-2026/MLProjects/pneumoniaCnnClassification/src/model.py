from __future__ import annotations

import torch.nn as nn
from torchvision.models import ResNet18_Weights, resnet18


class BaselineCNN(nn.Module):
    """CNN baseline a 3 blocs utilisee dans le notebook 02."""

    def __init__(
        self,
        in_channels: int = 3,
        dropout_p: float = 0.5,
        input_size: int = 224,
    ):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
        )

        h = input_size // 8
        w = input_size // 8
        flatten_dim = 128 * h * w
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(flatten_dim, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_p),
            nn.Linear(128, 1),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


def build_resnet18_binary(
    pretrained: bool = True,
    freeze_backbone: bool = False,
    dropout_p: float = 0.2,
) -> nn.Module:
    """Construit ResNet18 avec une tete binaire (sortie 1 logit)."""
    weights = ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
    model = resnet18(weights=weights)

    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(dropout_p),
        nn.Linear(in_features, 1),
    )

    if freeze_backbone:
        for name, p in model.named_parameters():
            if not name.startswith("fc."):
                p.requires_grad = False

    return model
