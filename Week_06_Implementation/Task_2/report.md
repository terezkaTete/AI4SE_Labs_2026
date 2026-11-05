# Task 2 – Chunking the repository

**Files**
- `chunk_repo.py` – chunking script (stdlib only: `python3 chunk_repo.py [repo_root] [output]`)
- `chunks.json` – the resulting chunks (798 chunks, list of JSON objects)

## Splitting method: syntax-aware (AST) chunking

Instead of fixed-size character/token windows, every `.py` file is parsed with Python's
`ast` module and split along its natural code units:

| kind | content | count |
|---|---|---|
| `module` | module docstring, imports, top-level constants | 26 |
| `class` | class *skeleton*: header, docstring, class attributes / enum members, and the signatures + first docstring line of all methods (no bodies) | 99 |
| `method` | one complete method (with decorators), prefixed with its `class X(Base):` line | 664 |
| `function` | one complete top-level function | 9 |

Every chunk starts with a header line like `# file: playground/playground/models.py | class: Customer`,
so a chunk still says where it came from once it's cut out of its file. Each chunk also
stores metadata: `id`, `file`, `module`, `kind`, `name`, `class`, `start_line`/`end_line`,
`is_test`, `is_stub`, `n_tokens` (estimate), and `text`.

Why this split:

- **The tasks are method-shaped.** Every entry in `missing_code.json` asks for one
  method. The most useful context is other *complete* methods: the ones the target calls,
  sibling methods that show the class's conventions, and tests that call the target.
  Fixed windows would cut methods in half and mix pieces of unrelated ones, which
  makes both the embedding and the LLM prompt noisier.
- **Class skeletons give the "big picture" cheaply.** To implement e.g.
  `OrderStatus.is_terminal`, the model needs to know which enum members exist. To implement
  `Warehouse.stock_report`, it needs the attributes and helper methods of `Warehouse`. One
  skeleton chunk shows the whole interface of a class without paying for all its bodies.
- **Module chunks hold the imports**, so the model knows which names are available
  (`Money`, exceptions, enums, ...) and doesn't import things that don't exist.
- **Tests are included** (flagged `is_test: true`). They're part of the repository, and
  they're often the best spec of a method's behaviour (edge cases, expected exceptions).
  The flag lets later steps filter or down-weight them if needed.
- **Stub methods are flagged** (`is_stub: true`, i.e. the body is only `pass`/`...`/docstring).
  16 are flagged: the 10 target methods plus 6 legitimately abstract methods in `base.py`. A
  stub has no useful content to retrieve, so later steps can skip these chunks.

## Chunk size

There is no fixed chunk size. The size is "one code unit", capped at **80 lines**. A unit
longer than that would be split into 80-line windows with 10 lines of overlap. In this
repo the cap is never reached (the longest method, `Simulation.step`, is 56 lines), so the
cap only keeps the script general.

Resulting sizes (≈ 4 chars/token estimate):

| | value |
|---|---|
| median | 74 tokens |
| 90th percentile | 148 tokens |
| max | 493 tokens (`ProductTests` class skeleton) |
| whole repo | ~72.7k tokens (~20.4k without tests) |

Why this size works:

- **Small, focused chunks embed better.** One embedding per method stays close to that
  method's meaning. A 1000-token window covering five methods would average them into
  a vague vector.
- **The top-5 budget in Task 5 stays small.** 5 chunks × ~75–150 tokens is roughly
  0.5–1k tokens of context per prompt. That fits comfortably even in the small allowed
  models (gpt-5-nano, gpt-4.1-nano, ...), and cost stays negligible across 10 tasks.
- **No information is lost at the boundaries.** Cuts happen only between units, so no
  chunk starts or ends in the middle of a statement.
- The trade-off: with only 5 slots, small chunks mean the retrieved context is narrow
  (e.g. 5 methods from one class). Class skeletons make up for this partly, because one
  slot can describe a whole class.
