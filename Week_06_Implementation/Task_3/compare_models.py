"""Compare candidate embedding models on the 10 real tasks (Week 06, Task 3).

For every task in missing_code.json the query is built from the task description and
the top-5 chunks are retrieved by cosine similarity. A retrieved chunk counts as
*relevant* if it belongs to the target class (its skeleton or another method) or is a
test that mentions the target method. Reported per model:
  * hit@5       - share of tasks with at least one relevant chunk in the top 5
  * precision@5 - share of relevant chunks among all retrieved chunks
  * skeleton@5  - share of tasks whose target-class skeleton is in the top 5
"""

import json
import re
import time
from pathlib import Path

import numpy as np

from embed_chunks import embed_texts, load_chunks

HERE = Path(__file__).resolve().parent
TASKS = HERE.parent / "Assignments" / "missing_code.json"
OUTPUT = HERE / "model_comparison.md"
MODELS = [
    "flax-sentence-embeddings/st-codesearch-distilroberta-base",
    "BAAI/bge-small-en-v1.5",
    "sentence-transformers/all-MiniLM-L6-v2",
]
K = 5


def task_query(task: dict) -> str:
    """Natural-language description of a task, shaped like a chunk (file/class header)."""
    docstring = task["docstring"].strip().strip('"').strip()
    return (f"# file: {task['file']} | class: {task['class']}\n"
            f"def {task['method']}(self): {docstring}")


def is_relevant(chunk: dict, task: dict) -> bool:
    """Same class in the same file, or a test exercising the target class."""
    if not chunk["is_test"]:
        return chunk["file"] == task["file"] and chunk["class"] == task["class"]
    return re.search(rf"\b{re.escape(task['class'])}\b", chunk["text"]) is not None


def main() -> None:
    chunks = load_chunks()
    tasks = json.loads(TASKS.read_text(encoding="utf-8"))
    queries = [task_query(t) for t in tasks]
    rows = []
    for model in MODELS:
        start = time.perf_counter()
        matrix = embed_texts([c["text"] for c in chunks], model)
        seconds = time.perf_counter() - start
        top = np.argsort(-(embed_texts(queries, model) @ matrix.T), axis=1)[:, :K]
        hits = relevant = skeletons = 0
        for task, row in zip(tasks, top):
            flags = [is_relevant(chunks[i], task) for i in row]
            hits += any(flags)
            relevant += sum(flags)
            skeletons += any(chunks[i]["kind"] == "class" and chunks[i]["class"] == task["class"]
                             and chunks[i]["file"] == task["file"] for i in row)
        rows.append((model, matrix.shape[1], seconds, hits / len(tasks),
                     relevant / (K * len(tasks)), skeletons / len(tasks)))
        print(f"{model}: hit@5 {rows[-1][3]:.0%}, precision@5 {rows[-1][4]:.0%}, "
              f"skeleton@5 {rows[-1][5]:.0%}, {seconds:.0f}s")

    lines = ["| model | dim | embed time (782 chunks, CPU) | hit@5 | precision@5 | skeleton@5 |",
             "|---|---|---|---|---|---|"]
    lines += [f"| `{m}` | {d} | {s:.0f} s | {h:.0%} | {p:.0%} | {k:.0%} |" for m, d, s, h, p, k in rows]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"table written to {OUTPUT}")


if __name__ == "__main__":
    main()
