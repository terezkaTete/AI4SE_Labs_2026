"""Split the AI4SE_Playground repository into chunks for retrieval (Week 06, Task 2).

Chunking is syntax-aware: every Python file is parsed with ``ast`` and split along
its natural units instead of fixed-size character windows.

Chunk kinds produced per file:
  * ``module``  - module docstring, imports and top-level statements (constants, ...)
  * ``class``   - class "skeleton": header, docstring, class attributes and the
                  signatures (+ first docstring line) of all its methods
  * ``method``  - one full method, prefixed with its enclosing class header
  * ``function``- one full top-level function

Every chunk starts with a short ``# file: ... | class: ...`` header so the chunk is
self-describing once it is cut out of its file. Units longer than MAX_LINES are split
into overlapping windows (does not happen in this repo, but keeps the script general).

Usage:
    python chunk_repo.py [repo_root] [output_file]
"""

import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_REPO = HERE.parent / "AI4SE_Playground"
DEFAULT_OUTPUT = HERE / "chunks.json"

MAX_LINES = 80        # longer units get split into windows of this size
WINDOW_OVERLAP = 10   # lines shared by consecutive windows


def estimate_tokens(text: str) -> int:
    """Rough token count (~4 characters per token for code)."""
    return max(1, len(text) // 4)


def node_start(node: ast.AST) -> int:
    """First line of a node, including decorators."""
    decorators = getattr(node, "decorator_list", [])
    return min([d.lineno for d in decorators] + [node.lineno])


def source_lines(lines: list[str], start: int, end: int) -> str:
    """1-based inclusive line range of a file as text."""
    return "\n".join(lines[start - 1:end])


def is_stub(node: ast.AST) -> bool:
    """True for functions whose body is only a docstring and/or ``pass``/``...``."""
    body = list(node.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]
    return all(
        isinstance(stmt, ast.Pass)
        or (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis)
        for stmt in body
    )


def class_header(lines: list[str], cls: ast.ClassDef) -> str:
    """Decorators + ``class X(Base):`` line(s), up to the first body statement."""
    first_body_line = cls.body[0].lineno if cls.body else cls.lineno
    return source_lines(lines, node_start(cls), first_body_line - 1).rstrip()


def signature(lines: list[str], fn: ast.FunctionDef) -> str:
    """Decorators + ``def`` line(s) of a function, plus the first docstring line."""
    first_body_line = fn.body[0].lineno
    sig = source_lines(lines, node_start(fn), first_body_line - 1).rstrip()
    doc = ast.get_docstring(fn)
    if doc:
        indent = " " * (fn.col_offset + 4)
        sig += f'\n{indent}"""{doc.splitlines()[0]}"""'
    return sig


def class_skeleton(lines: list[str], cls: ast.ClassDef) -> str:
    """Class header, docstring, attributes and method signatures - no method bodies."""
    parts = [class_header(lines, cls)]
    for stmt in cls.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            parts.append(signature(lines, stmt) + "\n" + " " * (stmt.col_offset + 4) + "...")
        elif isinstance(stmt, ast.ClassDef):
            parts.append(class_header(lines, stmt) + "\n" + " " * (stmt.col_offset + 4) + "...")
        else:  # docstring, attributes, enum members, ...
            parts.append(source_lines(lines, node_start(stmt), stmt.end_lineno))
    return "\n".join(parts)


def module_overview(lines: list[str], tree: ast.Module) -> str:
    """Module docstring, imports and top-level statements that are not defs/classes."""
    parts = [
        source_lines(lines, node_start(stmt), stmt.end_lineno)
        for stmt in tree.body
        if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]
    return "\n".join(parts)


def split_long(text: str, start_line: int) -> list[tuple[str, int, int]]:
    """Split text longer than MAX_LINES into overlapping windows."""
    body = text.splitlines()
    if len(body) <= MAX_LINES:
        return [(text, start_line, start_line + len(body) - 1)]
    windows = []
    step = MAX_LINES - WINDOW_OVERLAP
    for offset in range(0, len(body), step):
        piece = body[offset:offset + MAX_LINES]
        windows.append(("\n".join(piece), start_line + offset, start_line + offset + len(piece) - 1))
        if offset + MAX_LINES >= len(body):
            break
    return windows


def chunk_file(path: Path, repo_root: Path) -> list[dict]:
    rel = path.relative_to(repo_root).as_posix()
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return []
    lines = text.splitlines()
    tree = ast.parse(text, filename=rel)
    module = rel.removesuffix(".py").replace("/", ".")
    is_test = "/tests/" in f"/{rel}" or path.name.startswith("test_")
    chunks = []

    def add(kind, name, body, start, end, class_name=None, stub=False):
        location = f"# file: {rel}" + (f" | class: {class_name}" if class_name else "")
        pieces = split_long(body, start)
        for part, (piece, p_start, p_end) in enumerate(pieces):
            chunk_id = f"{rel}::{name}" + (f"#part{part}" if len(pieces) > 1 else "")
            chunk_text = f"{location}\n{piece}"
            chunks.append({
                "id": chunk_id,
                "file": rel,
                "module": module,
                "kind": kind,
                "name": name,
                "class": class_name,
                "start_line": p_start,
                "end_line": p_end,
                "is_test": is_test,
                "is_stub": stub,
                "n_tokens": estimate_tokens(chunk_text),
                "text": chunk_text,
            })

    overview = module_overview(lines, tree)
    if overview.strip():
        add("module", "<module>", overview, 1, tree.body[-1].end_lineno if tree.body else 1)

    for stmt in tree.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            add("function", stmt.name, source_lines(lines, node_start(stmt), stmt.end_lineno),
                node_start(stmt), stmt.end_lineno, stub=is_stub(stmt))
        elif isinstance(stmt, ast.ClassDef):
            add("class", stmt.name, class_skeleton(lines, stmt),
                node_start(stmt), stmt.end_lineno, class_name=stmt.name)
            header = class_header(lines, stmt)
            for member in stmt.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    body = source_lines(lines, node_start(member), member.end_lineno)
                    add("method", f"{stmt.name}.{member.name}", f"{header}\n{body}",
                        node_start(member), member.end_lineno,
                        class_name=stmt.name, stub=is_stub(member))
    return chunks


def chunk_repository(repo_root: Path) -> list[dict]:
    chunks = []
    for path in sorted(repo_root.rglob("*.py")):
        if any(part.startswith(".") or part == "__pycache__" for part in path.parts):
            continue
        chunks.extend(chunk_file(path, repo_root))
    return chunks


def main() -> None:
    repo_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_REPO
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    chunks = chunk_repository(repo_root)
    output.write_text(json.dumps(chunks, indent=2), encoding="utf-8")

    sizes = sorted(c["n_tokens"] for c in chunks)
    kinds = {}
    for c in chunks:
        kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
    print(f"{len(chunks)} chunks written to {output}")
    print(f"  by kind: {kinds}")
    print(f"  source: {sum(not c['is_test'] for c in chunks)}, tests: {sum(c['is_test'] for c in chunks)}, "
          f"stubs: {sum(c['is_stub'] for c in chunks)}")
    print(f"  tokens per chunk: min {sizes[0]}, median {sizes[len(sizes) // 2]}, "
          f"p90 {sizes[int(len(sizes) * 0.9)]}, max {sizes[-1]}, total {sum(sizes)}")


if __name__ == "__main__":
    main()
