"""Turn repository chunks into embeddings and store them (Week 06, Task 3).

Embeddings are computed locally with a sentence-transformers model. Vectors are
L2-normalised, so cosine similarity is a plain dot product later on.

Storage: one ``.npz`` file holding
  * ``embeddings`` - float32 matrix, one row per chunk (n_chunks x dim)
  * ``ids``        - chunk ids, row i belongs to chunk ids[i]
  * ``model``      - name of the embedding model (queries must use the same one)
The chunk texts/metadata stay in Task 2's ``chunks.json`` and are joined by id.

Usage:
    python embed_chunks.py [chunks.json] [output.npz] [--model NAME]
"""

import argparse
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

HERE = Path(__file__).resolve().parent
DEFAULT_CHUNKS = HERE.parent / "Task_2" / "chunks.json"
DEFAULT_OUTPUT = HERE / "embeddings.npz"
DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"


@lru_cache(maxsize=None)
def load_model(name: str = DEFAULT_MODEL) -> SentenceTransformer:
    return SentenceTransformer(name, device="cpu")


def embed_texts(texts: list[str], model_name: str = DEFAULT_MODEL) -> np.ndarray:
    """Embed a list of texts into L2-normalised float32 vectors."""
    vectors = load_model(model_name).encode(
        texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False
    )
    return np.asarray(vectors, dtype=np.float32)


def embed_chunk(chunk: dict, model_name: str = DEFAULT_MODEL) -> np.ndarray:
    """Embed a single chunk (its text, including the ``# file: ... | class: ...`` header)."""
    return embed_texts([chunk["text"]], model_name)[0]


def load_chunks(path: Path = DEFAULT_CHUNKS, skip_stubs: bool = True) -> list[dict]:
    """Chunks to index; stubs (body is only ``pass``) carry no information and are skipped."""
    chunks = json.loads(Path(path).read_text(encoding="utf-8"))
    return [c for c in chunks if not (skip_stubs and c["is_stub"])]


def build_store(chunks_path: Path, output: Path, model_name: str) -> None:
    chunks = load_chunks(chunks_path)
    vectors = embed_texts([c["text"] for c in chunks], model_name)
    np.savez_compressed(
        output, embeddings=vectors, ids=np.array([c["id"] for c in chunks]), model=model_name
    )
    print(f"{len(chunks)} chunks embedded with {model_name} -> {output} "
          f"(dim {vectors.shape[1]}, {output.stat().st_size / 1e6:.1f} MB)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("chunks", nargs="?", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("output", nargs="?", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()
    build_store(args.chunks, args.output, args.model)


if __name__ == "__main__":
    main()
