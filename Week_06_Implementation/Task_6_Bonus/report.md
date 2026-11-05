# Task 6 (Bonus) – An ideal pipeline for repository-aware code generation

## Starting point: why Task 5 failed

The embedding pipeline solved 7/10 methods. All 3 failures were **retrieval misses**: the
LLM never saw a fact it needed. I looked up where the chunk holding that fact ranked
(out of 782):

| failed method | missing fact | rank | in the target file's imports? |
|---|---|---|---|
| `OrderStateMachine.transition` | raise `InvalidTransitionError` | 9 | ✅ |
| `BulkDiscountPricing.price` | `Money.__mul__` accepts only `int` | 95 | ✅ (`Money`) |
| `InventoryLedger.__contains__` | `normalize_sku` raises `ValueError` | 78 | ✅ |

The dependencies don't *look like* the task, but static analysis finds every one of them
directly.

## Answers

**Is embedding matching the best strategy?** Not on its own. Embeddings find code that
*looks similar*. Generating code needs what the target *depends on*, and the code states
that exactly: imports, type hints, calls, inheritance, and tests. Embeddings (plus BM25 for
exact identifiers) are best used to fill the remaining space with similar examples.

**A different number of chunks?** Use a token budget instead of a fixed k. A k of 10
would have rescued only one task, and the others needed 30–95. The real waste was
redundancy: for `price`, all 5 slots were small pieces of the same class. Fill the budget
by priority and drop chunks that are already covered.

**More sophisticated chunking?** The AST chunks worked well. What's missing are **links
between chunks** (calls, type refs, raises, test → method), so retrieval can follow the
dependency graph, plus signature-only views of dependencies.

## Proposed pipeline

```
offline:  AST chunks + code graph (imports, calls, types, tests) + BM25 + embedding index

per task: 1. Structural context: target class, imports + signatures of imported symbols,
             1-hop calls of sibling methods, base class, tests of the target
          2. Fuzzy context: hybrid search → rerank → dedupe, until the token budget is full
          3. Generate
          4. Verify: parse → lint/type-check → run the target's tests
          5. Repair: feed failing test + traceback back, max 2–3 rounds
```

- **Step 1** would have supplied all three missing facts in Task 5.
- **Steps 4–5** catch the rest. `TypeError: factor must be int` names the bug directly,
  and the tests settle cases where a docstring is wrong (as with `__contains__`).

**Scale decides the setup.** This repo is ~20k tokens of source, so it fits whole into any
allowed model. Here the simplest strong option is no RAG at all: the whole package plus the
target's tests, plus the repair loop. RAG pays off for repositories that don't fit. For very
large ones, an **agent with tools** (grep, go-to-definition, run tests) that fetches its own
context beats any one-shot retrieval.

*Caveat:* the rankings are measured. The claim that this pipeline would solve all 10 tasks
is an expectation based on them, not a tested result.
