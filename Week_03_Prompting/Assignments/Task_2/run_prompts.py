"""
Task 2, step 1: run every prompt on every question with Claude Code and store the outputs.

Every question is sent as a separate `claude -p` call, so each answer comes from a fresh
session with no memory of the previous questions or prompts. Tools are switched off, so the
model only sees the prompt (it cannot read the database or the expected answers).

Usage (paths are relative to this script; defaults: ../Task_1/prompts.json, data/restaurants_dataset.csv,
model haiku):
    python run_prompts.py --limit 5        # quick test: first 5 questions per prompt
    python run_prompts.py                  # everything (3 x 155 calls)
    python run_prompts.py --prompts cot    # only one prompt

The script can be stopped and started again at any time. Questions that already have an
answer in the output file are skipped, so after hitting the usage limit just run it again later.

Output: predictions/predictions_<prompt_id>.csv, one row per question, plus
predictions/raw_<prompt_id>.jsonl with the complete JSON returned by Claude Code.
"""

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

csv.field_size_limit(1_000_000_000)

FIELDS = [
    "question_idx", "question", "predicted_sql", "raw_output",
    "prompt_id", "framework", "model", "agent", "agent_version",
    "inference_ms", "api_ms", "input_tokens", "output_tokens",
    "cache_read_tokens", "cache_creation_tokens", "is_error", "timestamp",
]

HERE = Path(__file__).resolve().parent

SYSTEM_PROMPT = "Follow the user's instructions exactly."


def extract_sql(text, prompt_id):
    """Get the SQL query out of the model's answer."""
    text = (text or "").strip()
    if prompt_id == "cot" or "SQL:" in text:
        # Chain of Thought ends with 'SQL: <query>'; take what follows the last marker
        matches = list(re.finditer(r"SQL:\s*", text))
        if matches:
            text = text[matches[-1].end():]
    text = re.sub(r"```(?:sql)?", "", text, flags=re.IGNORECASE).strip()
    if ";" in text:  # drop anything written after the end of the query
        text = text[: text.index(";") + 1]
    return " ".join(text.split())  # one line


def call_claude(claude_bin, model, prompt_text, workdir, timeout):
    command = [
        claude_bin, "-p", prompt_text,
        "--model", model,
        "--tools", "",                     # no tools: answer from the prompt only
        "--strict-mcp-config",             # no MCP servers
        "--system-prompt", SYSTEM_PROMPT,  # replace Claude Code's long coding prompt
        "--no-session-persistence",
        "--output-format", "json",
    ]
    started = time.perf_counter()
    completed = subprocess.run(command, capture_output=True, text=True, cwd=workdir, timeout=timeout)
    wall_ms = round((time.perf_counter() - started) * 1000)
    if completed.returncode != 0 and not completed.stdout.strip():
        raise RuntimeError(completed.stderr.strip() or f"claude exited with {completed.returncode}")
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"unexpected output from claude: {(completed.stdout or completed.stderr)[:500]}")
    data["_wall_ms"] = wall_ms
    return data


def model_name(data, requested):
    """The model that answered. modelUsage can also list small helper calls Claude Code makes
    in the background, so take the model whose token counts match the main answer."""
    usage = data.get("usage") or {}
    models = data.get("modelUsage") or {}
    for name, m in models.items():
        if (m or {}).get("outputTokens") == usage.get("output_tokens") and \
           (m or {}).get("cacheCreationInputTokens") == usage.get("cache_creation_input_tokens"):
            return name
    for name in models:
        if requested.lower() in name.lower():
            return name
    return next(iter(models), requested)


def already_done(path):
    if not path.exists():
        return set()
    with path.open(encoding="utf-8", newline="") as f:
        return {int(row["question_idx"]) for row in csv.DictReader(f)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prompts-file", default=str(HERE.parent / "Task_1" / "prompts.json"))
    parser.add_argument("--dataset", default=str(HERE / "data" / "restaurants_dataset.csv"))
    parser.add_argument("--out", default=str(HERE / "predictions"))
    parser.add_argument("--model", default="haiku", help="model alias or full name (default: haiku)")
    parser.add_argument("--prompts", nargs="*", help="only these prompt ids (default: all)")
    parser.add_argument("--limit", type=int, help="only the first N questions (for testing)")
    parser.add_argument("--timeout", type=int, default=300, help="seconds per call")
    parser.add_argument("--claude-bin", default="claude")
    args = parser.parse_args()

    if "/" in args.claude_bin or "\\" in args.claude_bin:
        args.claude_bin = str(Path(args.claude_bin).resolve())  # calls run in another folder
    else:
        # finds claude, claude.cmd or claude.exe on PATH (on Windows npm installs claude.cmd)
        found = shutil.which(args.claude_bin)
        if found is None:
            sys.exit(
                f"Could not find '{args.claude_bin}'. Check that Claude Code is installed and that "
                "'claude --version' works in this terminal, or pass the full path with --claude-bin."
            )
        args.claude_bin = found
    prompts = json.loads(Path(args.prompts_file).read_text(encoding="utf-8"))
    placeholder = prompts.get("placeholder", "{question}")
    with open(args.dataset, encoding="utf-8", newline="") as f:
        questions = [row["question"] for row in csv.DictReader(f)]  # only questions, never the answers
    if args.limit:
        questions = questions[: args.limit]

    version = subprocess.run([args.claude_bin, "--version"], capture_output=True, text=True).stdout.strip()
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)
    workdir = tempfile.mkdtemp(prefix="claude_run_")  # empty folder: no project files or CLAUDE.md

    for prompt in prompts["prompts"]:
        prompt_id = prompt["id"]
        if args.prompts and prompt_id not in args.prompts:
            continue
        csv_path = out_dir / f"predictions_{prompt_id}.csv"
        raw_path = out_dir / f"raw_{prompt_id}.jsonl"
        done = already_done(csv_path)
        new_file = not csv_path.exists()
        todo = [i for i in range(len(questions)) if i not in done]
        print(f"\n== {prompt_id}: {len(done)} done, {len(todo)} to go")

        with csv_path.open("a", encoding="utf-8", newline="") as out, raw_path.open("a", encoding="utf-8") as raw:
            writer = csv.DictWriter(out, fieldnames=FIELDS)
            if new_file:
                writer.writeheader()
            for n, idx in enumerate(todo, 1):
                question = questions[idx]
                prompt_text = prompt["prompt"].replace(placeholder, question)
                try:
                    data = call_claude(args.claude_bin, args.model, prompt_text, workdir, args.timeout)
                except Exception as error:  # usage limit, network problem, timeout ...
                    print(f"  stopped at question {idx}: {error}")
                    print("  run the script again later, it continues from here")
                    sys.exit(1)

                text = data.get("result", "")
                output_tokens = (data.get("usage") or {}).get("output_tokens") or 0
                if data.get("is_error") or output_tokens == 0:
                    # the model did not answer (not logged in, usage limit, ...): save nothing and stop
                    print(f"  Claude Code returned an error at question {idx}, nothing was saved for it:")
                    print(f"  {text[:500] or json.dumps(data)[:500]}")
                    if re.search(r"limit|quota", text, re.IGNORECASE):
                        print("  usage limit: run the script again after it resets, it continues from here")
                    else:
                        print("  fix the problem above (e.g. run `claude` and log in), then run the script again")
                    sys.exit(1)

                usage = data.get("usage") or {}
                writer.writerow({
                    "question_idx": idx,
                    "question": question,
                    "predicted_sql": extract_sql(text, prompt_id),
                    "raw_output": text,
                    "prompt_id": prompt_id,
                    "framework": prompt.get("framework", prompt_id),
                    "model": model_name(data, args.model),
                    "agent": "Claude Code (claude -p)",
                    "agent_version": version,
                    "inference_ms": data.get("duration_ms", data["_wall_ms"]),
                    "api_ms": data.get("duration_api_ms", ""),
                    "input_tokens": usage.get("input_tokens", ""),
                    "output_tokens": usage.get("output_tokens", ""),
                    "cache_read_tokens": usage.get("cache_read_input_tokens", ""),
                    "cache_creation_tokens": usage.get("cache_creation_input_tokens", ""),
                    "is_error": data.get("is_error", False),
                    "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                })
                out.flush()
                raw.write(json.dumps({"question_idx": idx, **data}, ensure_ascii=False) + "\n")
                raw.flush()
                print(f"  [{n}/{len(todo)}] q{idx} {data.get('duration_ms', data['_wall_ms'])} ms")

    print("\nDone. Next: python evaluate_prompts.py")


if __name__ == "__main__":
    main()