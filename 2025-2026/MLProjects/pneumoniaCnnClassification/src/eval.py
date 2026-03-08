from __future__ import annotations

from pathlib import Path
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

IMAGENET_MEAN_TENSOR = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
IMAGENET_STD_TENSOR = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)


def load_model(model, ckpt_path: str | Path, device: str = "cpu"):
    """Load model weights from a checkpoint and set eval mode."""
    ckpt_path = Path(ckpt_path)
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device).eval()
    return model, ckpt


def load_val_tensors(
    val_dir: str | Path,
    class_names: Sequence[str] = ("NORMAL", "PNEUMONIA"),
):
    """Load exported .pt tensors from validation folders."""
    val_dir = Path(val_dir)
    xs, ys, names, classes = [], [], [], []

    for class_name in class_names:
        class_dir = val_dir / class_name
        if not class_dir.exists():
            continue

        for pt_file in sorted(class_dir.glob("*.pt")):
            sample = torch.load(pt_file, map_location="cpu", weights_only=False)
            xs.append(sample["x"])
            ys.append(sample["y"])
            names.append(pt_file.stem)
            classes.append(class_name)

    if not xs:
        raise FileNotFoundError(f"No .pt files found under: {val_dir}")

    X = torch.stack(xs)
    Y = torch.tensor(ys, dtype=torch.long)
    return X, Y, names, classes


@torch.no_grad()
def evaluate_model(model, X, Y, device: str, threshold: float = 0.5):
    """Evaluate one model on a full tensor batch."""
    model.eval()
    logits = model(X.to(device)).view(-1)
    probs = torch.sigmoid(logits).cpu().numpy()

    y_true = Y.numpy()
    y_pred = (probs >= threshold).astype(int)

    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
    }
    if len(np.unique(y_true)) > 1:
        metrics["roc_auc"] = roc_auc_score(y_true, probs)
    else:
        metrics["roc_auc"] = float("nan")

    return metrics, y_pred, probs


def _disable_inplace_relu(model) -> None:
    """Set every ReLU to inplace=False to avoid Grad-CAM hook issues."""
    for module in model.modules():
        if isinstance(module, nn.ReLU):
            module.inplace = False


class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None

        _disable_inplace_relu(model)
        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, inputs, output):
        self.activations = output.detach()

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(self, x, class_idx=None):
        self.model.eval()
        output = self.model(x)

        self.model.zero_grad()
        if class_idx is None:
            target = output.view(-1)
        else:
            target = output[:, class_idx]
        target.backward(retain_graph=True)

        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = F.interpolate(cam, size=x.shape[2:], mode="bilinear", align_corners=False)
        cam = cam.squeeze()
        if cam.max() > 0:
            cam = (cam - cam.min()) / (cam.max() - cam.min())
        return cam.cpu().numpy()


def tensor_to_display(
    x: torch.Tensor,
    mean: torch.Tensor = IMAGENET_MEAN_TENSOR,
    std: torch.Tensor = IMAGENET_STD_TENSOR,
) -> np.ndarray:
    """Denormalize one tensor image for plotting."""
    img = x.cpu() * std + mean
    return img.clamp(0, 1).permute(1, 2, 0).numpy()


def plot_gradcam_grid(
    model,
    target_layer,
    X: torch.Tensor,
    Y: torch.Tensor,
    names,
    classes,
    model_name: str,
    device: str,
    n: int | None = None,
    threshold: float = 0.5,
    fig_dir: str | Path | None = None,
):
    """Plot raw image, Grad-CAM heatmap and overlay for n samples."""
    if n is None:
        n = len(X)

    grad_cam = GradCAM(model, target_layer)
    fig, axes = plt.subplots(n, 3, figsize=(12, 4 * n))
    if n == 1:
        axes = axes.reshape(1, 3)

    for i in range(n):
        x_i = X[i].unsqueeze(0).to(device).requires_grad_(True)
        y_true = int(Y[i].item())

        with torch.no_grad():
            prob = torch.sigmoid(model(x_i)).item()
        y_pred = 1 if prob >= threshold else 0
        pred_label = "PNEUMONIA" if y_pred == 1 else "NORMAL"
        correct = "OK" if y_pred == y_true else "WRONG"

        heatmap = grad_cam.generate(x_i)
        img_display = tensor_to_display(X[i])

        axes[i, 0].imshow(img_display)
        axes[i, 0].set_title(f"[{classes[i]}] {names[i]}", fontsize=9)
        axes[i, 0].axis("off")

        axes[i, 1].imshow(heatmap, cmap="jet")
        axes[i, 1].set_title("Grad-CAM", fontsize=9)
        axes[i, 1].axis("off")

        axes[i, 2].imshow(img_display)
        axes[i, 2].imshow(heatmap, cmap="jet", alpha=0.4)
        axes[i, 2].set_title(
            f"Pred: {pred_label} (p={prob:.2f}) [{correct}]",
            fontsize=9,
        )
        axes[i, 2].axis("off")

    fig.suptitle(f"Grad-CAM - {model_name}", fontsize=14, fontweight="bold")
    plt.tight_layout()

    if fig_dir is not None:
        fig_dir = Path(fig_dir)
        fig_dir.mkdir(parents=True, exist_ok=True)
        out = fig_dir / f"gradcam_{model_name.lower().replace(' ', '_')}.png"
        plt.savefig(out, dpi=150, bbox_inches="tight")

    plt.show()


def plot_training_history(
    ckpt: dict,
    model_name: str,
    save_path: str | Path | None = None,
):
    """Plot train/val curves from checkpoint history."""
    history = ckpt.get("history", {})
    if not history or "train_loss" not in history:
        raise ValueError(f"No training history available for {model_name}")

    epochs = np.arange(1, len(history["train_loss"]) + 1)
    has_auc = "val_auc" in history and len(history["val_auc"]) == len(epochs)
    ncols = 3 if has_auc else 2
    fig, axes = plt.subplots(1, ncols, figsize=(6 * ncols, 4))

    axes[0].plot(epochs, history["train_loss"], label="Train", linewidth=2)
    axes[0].plot(epochs, history["val_loss"], label="Val", linewidth=2)
    axes[0].set_title("Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(epochs, history["train_acc"], label="Train", linewidth=2)
    axes[1].plot(epochs, history["val_acc"], label="Val", linewidth=2)
    axes[1].set_title("Accuracy")
    axes[1].set_xlabel("Epoch")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    if has_auc:
        axes[2].plot(epochs, history["val_auc"], color="purple", label="Val AUC", linewidth=2)
        axes[2].set_title("Validation AUC")
        axes[2].set_xlabel("Epoch")
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)

    fig.suptitle(f"Training curves - {model_name}", fontsize=13, fontweight="bold")
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()
