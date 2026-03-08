from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Mapping, Sequence

import pandas as pd
from PIL import Image

DEFAULT_LABEL_MAP: Dict[str, int] = {"NORMAL": 0, "PNEUMONIA": 1}
DEFAULT_SPLITS: Sequence[str] = ("train", "val", "test")
DEFAULT_IMG_EXTS = {".jpg", ".jpeg", ".png"}


def build_df(
    data_root: str | Path,
    split: str,
    label_map: Mapping[str, int] = DEFAULT_LABEL_MAP,
    img_exts: Iterable[str] = DEFAULT_IMG_EXTS,
    shuffle: bool = True,
    random_state: int = 42,
) -> pd.DataFrame:
    """Indexe un split dans un DataFrame (path, label, class_name, split)."""
    root = Path(data_root)
    allowed_exts = {ext.lower() for ext in img_exts}
    rows = []

    split_dir = root / split
    for class_name, y in label_map.items():
        class_dir = split_dir / class_name
        if not class_dir.exists():
            raise FileNotFoundError(f"Dossier manquant: {class_dir}")

        for p in class_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in allowed_exts:
                rows.append(
                    {
                        "path": str(p),
                        "label": int(y),
                        "class_name": class_name,
                        "split": split,
                    }
                )

    df = pd.DataFrame(rows)
    if shuffle and not df.empty:
        df = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return df


def build_all_dfs(
    data_root: str | Path,
    splits: Sequence[str] = DEFAULT_SPLITS,
    label_map: Mapping[str, int] = DEFAULT_LABEL_MAP,
    img_exts: Iterable[str] = DEFAULT_IMG_EXTS,
    shuffle: bool = True,
    random_state: int = 42,
) -> Dict[str, pd.DataFrame]:
    """Construit les DataFrames indexes pour tous les splits."""
    return {
        split: build_df(
            data_root=data_root,
            split=split,
            label_map=label_map,
            img_exts=img_exts,
            shuffle=shuffle,
            random_state=random_state,
        )
        for split in splits
    }


def find_corrupt_paths(df: pd.DataFrame, path_col: str = "path") -> list[str]:
    """Retourne les chemins que PIL ne peut pas ouvrir/verifier."""
    bad: list[str] = []
    for p in df[path_col]:
        try:
            with Image.open(p) as im:
                im.verify()
        except Exception:
            bad.append(str(p))
    return bad


def collect_sizes(df: pd.DataFrame, path_col: str = "path") -> pd.DataFrame:
    """Collecte les metadonnees image de base (width, height, mode, channels)."""
    shapes = []
    for p in df[path_col]:
        try:
            with Image.open(p) as im:
                w, h = im.size
                mode = im.mode
                channels = len(im.getbands())
                shapes.append(
                    {
                        "width": w,
                        "height": h,
                        "mode": mode,
                        "channels": channels,
                    }
                )
        except Exception:
            continue
    return pd.DataFrame(shapes)
