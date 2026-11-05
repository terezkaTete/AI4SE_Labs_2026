# Task 3 – Embeddings and storage

**Files:** `embed_chunks.py` (`embed_chunk()` / `embed_texts()`, builds the store),
`embeddings.npz` (782 × 384 vectors, 1.1 MB), `compare_models.py` + `model_comparison.md`
(model selection experiment). Environment: `../requirements.txt`.

## Embedding mechanism: a local model

Embeddings are computed **locally** with `sentence-transformers` on the CPU. That makes them
free, offline and reproducible (a pinned model always gives the same vectors), and no code
leaves the machine. The whole repository embeds in under a minute.

**Model choice by experiment.** I compared three small models on the 10 real tasks: for each
task, a query built from the task, the top 5 chunks, and whether they come from the target
class or its tests.

| model | dim | embed time | hit@5 | precision@5 | skeleton@5 |
|---|---|---|---|---|---|
| `st-codesearch-distilroberta-base` | 768 | 65 s | 90% | 74% | 40% |
| **`BAAI/bge-small-en-v1.5`** | **384** | **48 s** | **100%** | **72%** | **80%** |
| `all-MiniLM-L6-v2` | 384 | 25 s | 100% | 76% | 50% |

**Chosen: `bge-small`.** It found relevant context for every task and the target class
skeleton (the most useful single chunk) for 8 of 10. Precision is about the same for all three.
Surprisingly, the code-specific model did worst: our queries match mostly through *names*
(`Warehouse`, `inventory.py`), and the general models handle those better. With only 10
queries, this is an indication rather than proof.

**What is embedded:** the full chunk text, including its `# file: ... | class: ...` header, so
file and class names end up in the vector. All chunks fit within the model's 512-token limit.
**Stubs are skipped**: their body is only `pass`, so they carry no information, and the target's
own stub would otherwise always be the top match.

## Storage: one NumPy `.npz` file

It holds `embeddings` (float32, L2-normalised rows), `ids` (aligned with the rows, joined back to
`Task_2/chunks.json`) and `model` (so queries always use the same model).

**No vector database:** 782 × 384 floats is 1.1 MB, and exact search is one matrix–vector
product taking well under a millisecond. Approximate indexes only pay off at hundreds of
thousands of vectors. Normalising the vectors when storing them makes cosine similarity a
plain dot product. If the repository grew a lot, the same layout would move directly into
FAISS.
