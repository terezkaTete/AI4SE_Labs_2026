| model | dim | embed time (782 chunks, CPU) | hit@5 | precision@5 | skeleton@5 |
|---|---|---|---|---|---|
| `flax-sentence-embeddings/st-codesearch-distilroberta-base` | 768 | 65 s | 90% | 74% | 40% |
| `BAAI/bge-small-en-v1.5` | 384 | 48 s | 100% | 72% | 80% |
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | 25 s | 100% | 76% | 50% |
