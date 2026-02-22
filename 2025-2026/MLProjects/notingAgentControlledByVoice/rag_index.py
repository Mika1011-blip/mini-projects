import json
import os
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = "rag_chunks.json"
EMB_FILE = "rag_embeddings.npy"

def _cosine_topk(
    query_vec: np.ndarray,
    mat: np.ndarray,
    top_k: int
) -> List[int]:
    # query_vec: (d,)
    # mat: (n, d)
    query_norm = np.linalg.norm(query_vec) + 1e-12
    mat_norms = np.linalg.norm(mat, axis=1) + 1e-12
    sims = (mat @ query_vec) / (mat_norms * query_norm)   # (n,)
    top_k = min(top_k, sims.shape[0])
    idx = np.argpartition(-sims, top_k - 1)[:top_k]
    idx = idx[np.argsort(-sims[idx])]
    return idx.tolist()

def chunk_vault_text(
    vault_text: str,
    min_len: int = 10
) -> List[str]:
    """
    Simple chunking: 1 chunk per non-empty line.
    (Works well if you store one memory per line / timestamped line.)
    """
    lines = []
    for line in vault_text.splitlines():
        s = line.strip()
        if len(s) >= min_len:
            lines.append(s)
    return lines

def build_rag_index(
    vault_text: str,
    embed_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    chunks_file: str = CHUNKS_FILE,
    emb_file: str = EMB_FILE
) -> int:
    """
    Builds embeddings for vault chunks and saves them to disk.
    Returns number of chunks indexed.
    """
    chunks = chunk_vault_text(vault_text=vault_text, min_len=10)
    if not chunks:
        # Save empty index
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        np.save(emb_file, np.zeros((0, 1), dtype=np.float32))
        return 0

    model = SentenceTransformer(embed_model_name)
    emb = model.encode(
        sentences=chunks,
        normalize_embeddings=False,
        convert_to_numpy=True,
        show_progress_bar=False
    ).astype(np.float32)

    with open(chunks_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    np.save(emb_file, emb)
    return len(chunks)

def load_rag_index(
    chunks_file: str = CHUNKS_FILE,
    emb_file: str = EMB_FILE
) -> Tuple[List[str], np.ndarray]:
    """
    Loads chunks + embeddings. If missing, returns empty.
    """
    if (not os.path.exists(chunks_file)) or (not os.path.exists(emb_file)):
        return [], np.zeros((0, 1), dtype=np.float32)

    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    emb = np.load(emb_file)
    return chunks, emb

def retrieve_context(
    query: str,
    embed_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    top_k: int = 5,
    chunks_file: str = CHUNKS_FILE,
    emb_file: str = EMB_FILE
) -> str:
    """
    Embeds the query, finds top-k similar chunks, returns them joined as context.
    """
    chunks, emb = load_rag_index(chunks_file=chunks_file, emb_file=emb_file)
    if not chunks or emb.shape[0] == 0:
        return ""

    model = SentenceTransformer(embed_model_name)
    q = model.encode(
        sentences=[query],
        normalize_embeddings=False,
        convert_to_numpy=True,
        show_progress_bar=False
    )[0].astype(np.float32)

    top_idx = _cosine_topk(query_vec=q, mat=emb, top_k=top_k)
    selected = [chunks[i] for i in top_idx]
    return "\n".join(selected)
