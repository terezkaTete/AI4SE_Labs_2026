"""Match a query embedding against the chunk store (Week 06, Task 4).

Exact nearest-neighbour search by cosine similarity. Stored vectors (Task 3) and query
vectors are both L2-normalised, so cosine similarity is a single matrix-vector product.

Usage:
    python retrieve.py "Return the number of line items in an Order" [-n 5]
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "Task_3"))

from embed_chunks import DEFAULT_CHUNKS, DEFAULT_OUTPUT as DEFAULT_STORE, embed_texts  # noqa: E402


class EmbeddingStore:
    """Chunk embeddings from Task 3 joined with chunk texts/metadata from Task 2."""

    def __init__(self, store_path: Path = DEFAULT_STORE, chunks_path: Path = DEFAULT_CHUNKS):
        data = np.load(store_path)
        self.embeddings = data["embeddings"]
        self.model = str(data["model"])
        by_id = {c["id"]: c for c in json.loads(Path(chunks_path).read_text(encoding="utf-8"))}
        self.chunks = [by_id[chunk_id] for chunk_id in data["ids"]]

    def top_n(self, query: np.ndarray, n: int = 5, exclude_files: set[str] = frozenset()) -> list[tuple[dict, float]]:
        """The ``n`` chunks most similar to ``query`` (a normalised vector), best first."""
        scores = self.embeddings @ query
        if exclude_files:
            mask = np.array([c["file"] in exclude_files for c in self.chunks])
            scores = np.where(mask, -np.inf, scores)
        n = min(n, int(np.isfinite(scores).sum()))
        best = np.argpartition(-scores, n - 1)[:n]
        best = best[np.argsort(-scores[best])]
        return [(self.chunks[i], float(scores[i])) for i in best]

    def search(self, text: str, n: int = 5, **kwargs) -> list[tuple[dict, float]]:
        """Embed ``text`` with the store's model and return its top ``n`` chunks."""
        return self.top_n(embed_texts([text], self.model)[0], n, **kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("query")
    parser.add_argument("-n", type=int, default=5)
    args = parser.parse_args()
    for chunk, score in EmbeddingStore().search(args.query, args.n):
        print(f"{score:.3f}  {chunk['kind']:<8} {chunk['id']}")


if __name__ == "__main__":
    main()
