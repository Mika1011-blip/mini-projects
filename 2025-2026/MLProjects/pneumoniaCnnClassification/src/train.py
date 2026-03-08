from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score


@dataclass(frozen=True)
class TrainConfig:
    """Configuration d'entrainement."""

    epochs: int = 20
    lr: float = 1e-3
    weight_decay: float = 0.0
    early_stopping_patience: int = 6
    min_delta: float = 1e-4
    use_class_weights: bool = True
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


def accuracy_from_logits(logits: torch.Tensor, y: torch.Tensor) -> float:
    """Calcule l'accuracy binaire a partir des logits."""

    logits = logits.view(-1)
    y = y.view(-1)
    probs = torch.sigmoid(logits)
    preds = (probs >= 0.5).float()
    return (preds == y).float().mean().item()


def train_one_epoch(
    model,
    loader,
    loss_fn,
    optimizer,
    device: str,
) -> Tuple[float, float]:
    """Execute une epoch d'entrainement et retourne loss/accuracy moyennes."""

    model.train()
    losses, accs = [], []
    for x, y in loader:
        x = x.to(device)
        y = y.to(device).view(-1, 1)
        optimizer.zero_grad()
        logits = model(x)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()
        losses.append(loss.item())
        accs.append(accuracy_from_logits(logits.detach(), y))
    return float(np.mean(losses)), float(np.mean(accs))


@torch.no_grad()
def validate_one_epoch(
    model,
    loader,
    loss_fn,
    device: str,
) -> Tuple[float, float, float]:
    """Execute une epoch de validation et retourne loss/accuracy/AUC."""

    model.eval()
    losses, accs = [], []
    all_probs, all_targets = [], []

    for x, y in loader:
        x = x.to(device)
        y = y.to(device).view(-1, 1)
        logits = model(x)
        loss = loss_fn(logits, y)
        probs = torch.sigmoid(logits)

        losses.append(loss.item())
        accs.append(accuracy_from_logits(logits, y))
        all_probs.append(probs.detach().cpu())
        all_targets.append(y.detach().cpu())

    probs = torch.cat(all_probs).view(-1).numpy()
    y_true = torch.cat(all_targets).view(-1).numpy().astype(int)
    if len(np.unique(y_true)) > 1:
        val_auc = float(roc_auc_score(y_true, probs))
    else:
        val_auc = float("nan")

    return float(np.mean(losses)), float(np.mean(accs)), val_auc


def fit(model, loaders: Dict[str, torch.utils.data.DataLoader], cfg: TrainConfig):
    """Boucle complete d'entrainement avec early stopping sur la val loss."""

    device = cfg.device
    model.to(device)

    pos_weight = None
    if cfg.use_class_weights:
        train_dataset = loaders["train"].dataset
        if hasattr(train_dataset, "df") and "label" in train_dataset.df.columns:
            y_train = train_dataset.df["label"].astype(int).to_numpy()
            n_pos = int((y_train == 1).sum())
            n_neg = int((y_train == 0).sum())
            if n_pos > 0 and n_neg > 0:
                pos_weight = torch.tensor(
                    [n_neg / n_pos],
                    dtype=torch.float32,
                    device=device,
                )

    if pos_weight is None:
        loss_fn = nn.BCEWithLogitsLoss()
        print("Utilisation de BCEWithLogitsLoss sans ponderation de classes")
    else:
        loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
        print(f"Utilisation de BCEWithLogitsLoss avec pos_weight={pos_weight.item():.4f}")

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=cfg.lr,
        weight_decay=cfg.weight_decay,
    )

    history = {
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": [],
        "val_auc": [],
    }

    best_val_loss = float("inf")
    best_epoch = 0
    epochs_without_improvement = 0
    stopped_early = False
    best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    for epoch in range(1, cfg.epochs + 1):
        tr_loss, tr_acc = train_one_epoch(
            model,
            loaders["train"],
            loss_fn,
            optimizer,
            device,
        )
        va_loss, va_acc, va_auc = validate_one_epoch(
            model,
            loaders["val"],
            loss_fn,
            device,
        )

        history["train_loss"].append(tr_loss)
        history["train_acc"].append(tr_acc)
        history["val_loss"].append(va_loss)
        history["val_acc"].append(va_acc)
        history["val_auc"].append(va_auc)

        improved = va_loss < (best_val_loss - cfg.min_delta)
        if improved:
            best_val_loss = va_loss
            best_epoch = epoch
            epochs_without_improvement = 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            epochs_without_improvement += 1

        print(
            f"Epoch {epoch:02d}/{cfg.epochs} | "
            f"train_loss={tr_loss:.4f} acc={tr_acc:.4f} | "
            f"val_loss={va_loss:.4f} acc={va_acc:.4f} auc={va_auc:.4f}"
        )

        if (
            cfg.early_stopping_patience > 0
            and epochs_without_improvement >= cfg.early_stopping_patience
        ):
            stopped_early = True
            print(
                f"Arret anticipe a l'epoch {epoch}. "
                f"Meilleure epoch: {best_epoch} (val_loss={best_val_loss:.4f})"
            )
            break

    model.load_state_dict(best_state)
    history["best_epoch"] = best_epoch
    history["best_val_loss"] = best_val_loss
    history["stopped_early"] = stopped_early
    return history


def plot_training_curves(history, save_path: str | Path | None = None):
    """Trace les courbes loss/accuracy et AUC de validation (si disponible)."""

    epochs = np.arange(1, len(history["train_loss"]) + 1)
    has_auc = "val_auc" in history and len(history["val_auc"]) == len(epochs)
    ncols = 3 if has_auc else 2

    fig, axes = plt.subplots(1, ncols, figsize=(6 * ncols, 4))
    if ncols == 1:
        axes = [axes]

    axes[0].plot(epochs, history["train_loss"], label="Train Loss")
    axes[0].plot(epochs, history["val_loss"], label="Val Loss")
    axes[0].set_title("Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    axes[1].plot(epochs, history["train_acc"], label="Train Acc")
    axes[1].plot(epochs, history["val_acc"], label="Val Acc")
    axes[1].set_title("Accuracy")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    if has_auc:
        axes[2].plot(epochs, history["val_auc"], label="Val AUC", color="purple")
        axes[2].set_title("Validation AUC")
        axes[2].set_xlabel("Epoch")
        axes[2].set_ylabel("AUC")
        axes[2].grid(True, alpha=0.3)
        axes[2].legend()

    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, bbox_inches="tight")
    plt.show()


@torch.no_grad()
def evaluate_on_test(model, loader, device: str, threshold: float = 0.5):
    """Evalue un modele sur le loader de test avec un seuil configurable."""

    model.eval()
    model.to(device)
    loss_fn = nn.BCEWithLogitsLoss()

    losses = []
    all_probs = []
    all_targets = []

    for x, y in loader:
        x = x.to(device)
        y = y.to(device).view(-1, 1)
        logits = model(x)
        loss = loss_fn(logits, y)

        probs = torch.sigmoid(logits)
        losses.append(loss.item())
        all_probs.append(probs.cpu())
        all_targets.append(y.cpu())

    probs = torch.cat(all_probs).view(-1).numpy()
    y_true = torch.cat(all_targets).view(-1).numpy().astype(int)
    y_pred = (probs >= threshold).astype(int)

    metrics = {
        "test_loss": float(np.mean(losses)),
        "test_acc": float((y_pred == y_true).mean()),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }
    if len(np.unique(y_true)) > 1:
        metrics["roc_auc"] = float(roc_auc_score(y_true, probs))
    else:
        metrics["roc_auc"] = float("nan")
    return metrics


def save_checkpoint(
    model,
    cfg: TrainConfig,
    history: dict,
    test_metrics: dict,
    out_path: str | Path,
) -> Path:
    """Sauvegarde un checkpoint (poids, config, historique, metriques test)."""

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": asdict(cfg),
            "history": history,
            "test_metrics": test_metrics,
        },
        out_path,
    )
    return out_path
