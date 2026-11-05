# Task 4 – Matching a task embedding to chunks

**File:** `retrieve.py`
- `EmbeddingStore()` loads `Task_3/embeddings.npz` and joins it by id with `Task_2/chunks.json`.
- `store.top_n(query_vector, n)` returns the *n* most similar chunks with their scores, best first.
- `store.search(text, n)` embeds the text with the store's own model, then calls `top_n`.
- CLI: `python retrieve.py "<task text>" -n 5`

## Design decisions

**Similarity: cosine.** It's the metric the embedding model (bge-small) was trained for,
and it ignores vector length, so a long test chunk doesn't win just by being long. All
vectors are L2-normalised, both when stored and when queried, so cosine similarity is just
a dot product: `scores = embeddings @ query`.

**Search: exact brute force, no approximate index.** With 782 × 384 vectors, scoring every
chunk is one matrix–vector product, and `top_n` takes **~0.1 ms per query** (measured
over 1000 queries). Approximate nearest-neighbour indexes (HNSW, IVF, FAISS, ...) trade a
little recall for speed on millions of vectors. Here there's no speed to gain, so exact
results are free.

**Top-n selection: `argpartition` + sort of the n winners.** This finds the n best
in O(N) and sorts only those n, instead of sorting all 782 scores. It's tested to give
the same order as a full `argsort`.

**Same model for queries as for chunks.** The store records the model it was built with,
and `search()` always embeds the query with that model. Mixing models would make the
vectors incomparable.

**Optional `exclude_files` filter.** It removes whole files from the candidates before
ranking, for example to run the pipeline without the test files, or to keep the target
file out of the results. It's off by default, so Task 5 retrieves from the whole repository.

**What it doesn't do (on purpose).** There's no score threshold, because the task asks for
exactly n chunks, and the scores (~0.8–0.9 here) aren't calibrated enough for a
meaningful cut-off. There's also no re-ranking or diversity step: plain similarity order
is the baseline that Task 5 is meant to evaluate. Ideas for improving on it go in the
bonus task.

## Example

```
$ python retrieve.py "# file: playground/playground/orders.py | class: Order
def __len__(self): Return the number of line items."
0.903  method   playground/playground/orders.py::OrderBuilder.__len__
0.898  method   playground/playground/orders.py::OrderLog.__len__
0.844  method   playground/playground/orders.py::OrderBuilder.__bool__
0.836  method   playground/playground/orders.py::Order.items
0.835  method   playground/playground/models.py::LineItem.quantity
```

These results are useful for the task: two sibling `__len__` implementations show the
convention, and `Order.items` shows how `Order` stores its line items.
