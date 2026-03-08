from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.transforms.functional import to_pil_image

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def make_transforms(
    img_size: int = 224,
    augment: bool = True,
    use_imagenet_norm: bool = True,
):
    """Create base/train/val transforms used in notebook 02."""
    mean = IMAGENET_MEAN if use_imagenet_norm else [0.5, 0.5, 0.5]
    std = IMAGENET_STD if use_imagenet_norm else [0.5, 0.5, 0.5]

    base_ops = [
        transforms.Resize(256),
        transforms.CenterCrop(img_size),
    ]

    train_ops = base_ops.copy()
    if augment:
        train_ops += [
            transforms.RandomRotation(5),
            transforms.RandomApply(
                [transforms.ColorJitter(brightness=0.10, contrast=0.10)],
                p=0.5,
            ),
            transforms.RandomAffine(
                degrees=0,
                translate=(0.03, 0.03),
                scale=(0.95, 1.05),
            ),
        ]
    train_ops += [
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ]

    eval_ops = base_ops + [
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ]

    base_tensor_ops = base_ops + [transforms.ToTensor()]
    return (
        transforms.Compose(base_tensor_ops),
        transforms.Compose(train_ops),
        transforms.Compose(eval_ops),
    )


def resolve_image_path(
    path_value: str | Path,
    base_dir: str | Path | None = None,
    project_root: str | Path | None = None,
) -> Path:
    """Resolve a potentially relative path against common roots."""
    p = Path(str(path_value))
    candidates = []

    if p.is_absolute():
        candidates.append(p)
    else:
        if base_dir is not None:
            candidates.append(Path(base_dir) / p)
        if project_root is not None:
            candidates.append(Path(project_root) / p)
        candidates.append(Path.cwd() / p)
        candidates.append(p)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    tried = " | ".join(str(c) for c in candidates)
    raise FileNotFoundError(f"Image file not found: {path_value}. Tried: {tried}")


class XRayDataset(Dataset):
    def __init__(
        self,
        df: pd.DataFrame,
        transform=None,
        base_dir: str | Path | None = None,
        project_root: str | Path | None = None,
    ):
        self.df = df.reset_index(drop=True)
        self.transform = transform
        self.base_dir = Path(base_dir) if base_dir is not None else None
        self.project_root = Path(project_root) if project_root is not None else None

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = resolve_image_path(
            row["path"],
            base_dir=self.base_dir,
            project_root=self.project_root,
        )
        img = Image.open(img_path).convert("RGB")
        y = int(row["label"])
        if self.transform is not None:
            img = self.transform(img)
        return img, torch.tensor([y], dtype=torch.float32)


@dataclass(frozen=True)
class LoaderConfig:
    batch_size: int = 32
    num_workers: int = 0
    pin_memory: bool = True
    seed: int = 42


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def create_loaders(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: Optional[pd.DataFrame] = None,
    train_transform=None,
    val_transform=None,
    base_dir: str | Path | None = None,
    project_root: str | Path | None = None,
    cfg: LoaderConfig | None = None,
) -> Dict[str, DataLoader]:
    """Create train/val/test loaders with deterministic seed handling."""
    cfg = cfg or LoaderConfig()
    seed_everything(cfg.seed)
    generator = torch.Generator()
    generator.manual_seed(cfg.seed)

    loaders: Dict[str, DataLoader] = {}
    loaders["train"] = DataLoader(
        XRayDataset(
            df=train_df,
            transform=train_transform,
            base_dir=base_dir,
            project_root=project_root,
        ),
        batch_size=cfg.batch_size,
        shuffle=True,
        num_workers=cfg.num_workers,
        pin_memory=cfg.pin_memory,
        generator=generator,
    )
    loaders["val"] = DataLoader(
        XRayDataset(
            df=val_df,
            transform=val_transform,
            base_dir=base_dir,
            project_root=project_root,
        ),
        batch_size=cfg.batch_size,
        shuffle=False,
        num_workers=cfg.num_workers,
        pin_memory=cfg.pin_memory,
        generator=generator,
    )

    if test_df is not None:
        loaders["test"] = DataLoader(
            XRayDataset(
                df=test_df,
                transform=val_transform,
                base_dir=base_dir,
                project_root=project_root,
            ),
            batch_size=cfg.batch_size,
            shuffle=False,
            num_workers=cfg.num_workers,
            pin_memory=cfg.pin_memory,
            generator=generator,
        )

    return loaders


def visual_inspect(
    train_df: pd.DataFrame,
    base_transform,
    normalized_transform=None,
    n: int = 5,
    seed: int = 42,
    random_sample: bool = True,
    save_path: str | Path | None = None,
    base_dir: str | Path | None = None,
    project_root: str | Path | None = None,
):
    """Show raw / preprocessed(no norm) / preprocessed(norm) samples."""
    n = min(n, len(train_df))
    sample = (
        train_df.sample(n=n, random_state=seed)
        if random_sample
        else train_df.iloc[:n]
    ).reset_index(drop=True)

    if normalized_transform is None:
        if isinstance(base_transform, transforms.Compose):
            normalized_transform = transforms.Compose(
                list(base_transform.transforms)
                + [transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)]
            )
        else:
            raise ValueError(
                "Provide normalized_transform, or pass base_transform as torchvision.transforms.Compose"
            )

    mean = torch.tensor(IMAGENET_MEAN).view(3, 1, 1)
    std = torch.tensor(IMAGENET_STD).view(3, 1, 1)

    fig, axes = plt.subplots(3, n, figsize=(3 * n, 9))
    if n == 1:
        axes = axes.reshape(3, 1)

    for j, row in sample.iterrows():
        img_path = resolve_image_path(
            row["path"],
            base_dir=base_dir,
            project_root=project_root,
        )
        img_pil = Image.open(img_path).convert("RGB")
        axes[0, j].imshow(img_pil)
        axes[0, j].set_title(f"Raw | y={int(row['label'])}")
        axes[0, j].axis("off")

        x_no = base_transform(img_pil)
        axes[1, j].imshow(x_no.permute(1, 2, 0).clamp(0, 1))
        axes[1, j].set_title("Preproc (no norm)")
        axes[1, j].axis("off")

        x_norm = normalized_transform(img_pil)
        x_vis = (x_norm * std) + mean
        axes[2, j].imshow(x_vis.permute(1, 2, 0).clamp(0, 1))
        axes[2, j].set_title("Preproc (with norm)")
        axes[2, j].axis("off")

    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, bbox_inches="tight")
    plt.show()


def export_preprocessed_from_loader_dataset(
    loader: DataLoader,
    out_dir: str | Path,
    save_tensor: bool = True,
) -> Path:
    """Export displayable PNG + optional exact normalized tensor for each sample."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dataset = loader.dataset

    mean = torch.tensor(IMAGENET_MEAN).view(3, 1, 1)
    std = torch.tensor(IMAGENET_STD).view(3, 1, 1)

    for i in range(len(dataset)):
        x, y = dataset[i]
        rel = Path(dataset.df.iloc[i]["path"]).with_suffix(".png")
        png_path = out_dir / rel
        png_path.parent.mkdir(parents=True, exist_ok=True)

        x_vis = (x * std + mean).clamp(0, 1)
        to_pil_image(x_vis).save(png_path)

        if save_tensor:
            torch.save({"x": x, "y": int(y.item())}, png_path.with_suffix(".pt"))

    return out_dir
