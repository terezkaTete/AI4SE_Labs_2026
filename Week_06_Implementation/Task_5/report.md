# Task 5 – Solving the tasks with the RAG pipeline

**Files:** `solve_tasks.py` (pipeline + test run), `results.json` (prompts, retrieved chunks,
replies per task), `test_output.txt` (full pytest output). The generated code is in
`../AI4SE_Playground/playground/playground/`.

**Pipeline:** task text (file, class, method, docstring) → top 5 chunks (Task 4) → prompt to
**`gpt-5-mini`** asking for only the complete method → the reply is parsed with `ast` and
replaces the stub in the target file (only if the result still parses).

## Results

All 10 methods were generated and written (~90 s in total).

| | passed | failed |
|---|---|---|
| before (stubs) | 429 | 52 |
| **after RAG pipeline** | **467** | **14** |

**38 of 52 failing tests fixed. 7 of 10 methods pass all of their tests:**
`OrderStatus.is_terminal`, `Warehouse.stock_report`, `OrderLog.by_status`, `Customer.can_afford`,
`Order.__len__`, `EventBus.__contains__`, `Money.__bool__`.

| failed method | tests | error |
|---|---|---|
| `OrderStateMachine.transition` | 5 | raised `ValueError` instead of the project's `InvalidTransitionError` |
| `BulkDiscountPricing.price` | 7 | multiplied `Money` by a float, but `Money.__mul__` only accepts `int` |
| `InventoryLedger.__contains__` | 2 | didn't catch `ValueError` for malformed SKUs; required stock `> 0` |

## Analysis

All 3 failures were **retrieval misses**: the needed fact sat in a chunk outside the top 5
(`exceptions.py`, `Money.__mul__`, `normalize_sku` in `util.py`). Embedding similarity
retrieved chunks that *look like* the target. For `price`, all 5 were small pieces of
`BulkDiscountPricing` itself, and those crowded out the dependencies. In one case the
docstring was also misleading: it says "positive on-hand stock", but a test expects `True`
for a SKU with 0 stock.

When the right chunk *was* retrieved, the LLM used it correctly every time. Test chunks were
in the top 5 for 5 of the 7 successes, so the tests act as the most useful spec.

*Note:* this is a single run. LLM output varies, so a rerun can differ by a method or two.
