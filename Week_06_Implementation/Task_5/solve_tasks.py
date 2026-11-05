"""Solve coding tasks with the RAG pipeline (Week 06, Task 5).

For every task in missing_code.json:
  1. turn it into a textual task,
  2. retrieve the top 5 chunks from the embedding store (Task 4),
  3. prompt an LLM with the task + the chunks,
  4. write the returned method into the target source file (replacing the stub).
Afterwards the playground unit tests are run and summarised.

The OpenAI key is read from the env variable SCHOOL_OPEN_AI_API_KEY (optionally from a
.env file); OPENAI_BASE_URL is honoured if set.

Usage:
    python solve_tasks.py [--model gpt-5-mini] [--skip-tests]
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import textwrap
import time
from pathlib import Path

from openai import OpenAI

HERE = Path(__file__).resolve().parent
WEEK = HERE.parent
sys.path.insert(0, str(WEEK / "Task_4"))
sys.path.insert(0, str(WEEK / "Task_3"))

from retrieve import EmbeddingStore  # noqa: E402

REPO = WEEK / "AI4SE_Playground"
TASKS = WEEK / "Assignments" / "missing_code.json"
RESULTS = HERE / "results.json"
TEST_OUTPUT = HERE / "test_output.txt"
DEFAULT_MODEL = "gpt-5-mini"
TOP_K = 5

SYSTEM_PROMPT = """You are an expert Python developer implementing a missing method in an existing code base.
You get the task and a few code snippets retrieved from the repository as context.
Reply with ONLY the complete method definition in a single ```python code block:
- include any decorators the method needs (e.g. @property) and the full signature with type hints,
- include the docstring from the task,
- do not add imports or code outside the method; use only names visible in the context,
- follow the conventions of the surrounding code."""


def task_to_text(task: dict) -> str:
    """Textual task description from a missing_code.json entry."""
    docstring = task["docstring"].strip().strip('"').strip()
    return (f"# file: {task['file']} | class: {task['class']}\n"
            f"Implement the method `{task['method']}` of class `{task['class']}` in `{task['file']}`.\n"
            f"Docstring: {docstring}")


def build_prompt(task_text: str, chunks: list[tuple[dict, float]]) -> str:
    context = "\n\n".join(f"### Context {i} ({chunk['id']})\n```python\n{chunk['text']}\n```"
                          for i, (chunk, _) in enumerate(chunks, 1))
    return f"## Task\n{task_text}\n\n## Retrieved context\n{context}"


def extract_code(reply: str) -> str:
    """Code from the first ```python block of the reply (or the whole reply)."""
    match = re.search(r"```(?:python)?\s*\n(.*?)```", reply, re.DOTALL)
    return textwrap.dedent(match.group(1) if match else reply).strip("\n")


def find_method(tree: ast.Module, class_name: str, method_name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name == method_name:
                    return member
    raise LookupError(f"{class_name}.{method_name} not found")


def write_method(path: Path, class_name: str, method_name: str, code: str) -> None:
    """Replace ``class_name.method_name`` (decorators included) in ``path`` with ``code``."""
    parsed = ast.parse(code)
    defs = [n for n in parsed.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if len(defs) != 1 or defs[0].name != method_name:
        raise ValueError(f"reply is not a single definition of {method_name}")

    source = path.read_text(encoding="utf-8")
    old = find_method(ast.parse(source), class_name, method_name)
    start = min([d.lineno for d in old.decorator_list] + [old.lineno])
    lines = source.splitlines(keepends=True)
    indent = " " * old.col_offset
    new = textwrap.indent(code, indent) + "\n"
    updated = "".join(lines[:start - 1]) + new + "".join(lines[old.end_lineno:])
    ast.parse(updated)  # never write a file that doesn't parse
    path.write_text(updated, encoding="utf-8")


def solve_task(task_text: str, target_file: Path, class_name: str, method_name: str,
               store: EmbeddingStore, client: OpenAI, model: str = DEFAULT_MODEL) -> dict:
    """Retrieve context for ``task_text``, ask the LLM, write the method into ``target_file``."""
    chunks = store.search(task_text, TOP_K)
    prompt = build_prompt(task_text, chunks)
    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
    )
    reply = response.choices[0].message.content or ""
    code = extract_code(reply)
    result = {
        "method": f"{class_name}.{method_name}",
        "file": str(target_file.relative_to(REPO)),
        "retrieved": [{"id": c["id"], "score": round(s, 3)} for c, s in chunks],
        "prompt": prompt,
        "reply": reply,
        "code": code,
        "seconds": round(time.perf_counter() - start, 1),
        "tokens": {"prompt": response.usage.prompt_tokens, "completion": response.usage.completion_tokens},
    }
    try:
        write_method(target_file, class_name, method_name, code)
        result["written"] = True
    except (SyntaxError, ValueError, LookupError) as error:
        result["written"] = False
        result["error"] = f"{type(error).__name__}: {error}"
    return result


def run_tests() -> dict:
    """Run the playground test suite and return the pytest summary counts."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rf"],
        cwd=REPO / "playground", capture_output=True, text=True,
    )
    TEST_OUTPUT.write_text(proc.stdout + proc.stderr, encoding="utf-8")
    summary = proc.stdout.strip().splitlines()[-1]
    counts = {key: int(n) for n, key in re.findall(r"(\d+) (passed|failed|error)", summary)}
    return {"summary": summary, **counts}


def make_client() -> OpenAI:
    try:
        from dotenv import load_dotenv
        load_dotenv(WEEK / ".env")
    except ImportError:
        pass
    key = os.environ.get("SCHOOL_OPEN_AI_API_KEY") or os.environ.get("school_open_ai_api_key")
    if not key:
        raise SystemExit("Set the env variable SCHOOL_OPEN_AI_API_KEY.")
    return OpenAI(api_key=key, base_url=os.environ.get("OPENAI_BASE_URL") or None)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()

    store, client = EmbeddingStore(), make_client()
    tasks = json.loads(TASKS.read_text(encoding="utf-8"))
    results = []
    for task in tasks:
        result = solve_task(task_to_text(task), REPO / task["file"], task["class"], task["method"],
                            store, client, args.model)
        results.append(result)
        status = "written" if result["written"] else f"NOT written ({result['error']})"
        print(f"{result['method']:<34} {status}  [{result['seconds']}s]")

    output = {"model": args.model, "top_k": TOP_K, "tasks": results}
    if not args.skip_tests:
        output["tests"] = run_tests()
        print(output["tests"]["summary"])
    RESULTS.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"details in {RESULTS}")


if __name__ == "__main__":
    main()
