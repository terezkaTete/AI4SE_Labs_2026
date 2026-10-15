"""
Task 2, step 2: evaluate the stored predictions and make the table and charts for the report.

Accuracy is computed exactly like in evaluate_retrieval_predictions.py (the predicted rows must
equal the expected rows as a multiset). The difference is that a query that can't be executed
is counted as wrong instead of stopping the whole evaluation.

Usage (paths are relative to this script, so it can be run from any folder):
    python evaluate_prompts.py

Output in results/:
    per_question.csv   correct / SQL error for every question and prompt
    summary.csv / summary.md   one row per prompt
    accuracy.png       accuracy per prompt with 95 % confidence interval
    inference_time.png distribution of inference times per prompt
"""

import argparse
import csv
import json
import math
import sqlite3
import statistics
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "data"))
import evaluate_retrieval_predictions as evaluator  # official database loader

csv.field_size_limit(1_000_000_000)

COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3dd"


def wilson(correct, n, z=1.96):
    """95 % confidence interval for a proportion (Wilson score interval)."""
    if n == 0:
        return float("nan"), float("nan")
    p = correct / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def to_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def evaluate_file(path, labels, connection):
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            idx = int(row["question_idx"])
            question, expected = labels[idx]
            if row["question"] != question:
                raise ValueError(f"{path}: question {idx} does not match the dataset")
            try:
                predicted = connection.execute(row["predicted_sql"]).fetchall()
                status = "correct" if Counter(map(tuple, predicted)) == Counter(map(tuple, expected)) else "wrong"
                error = ""
            except (sqlite3.Error, sqlite3.Warning, ValueError) as e:
                status, error = "sql_error", str(e)
            rows.append({
                "prompt_id": row["prompt_id"], "framework": row["framework"], "model": row["model"],
                "question_idx": idx, "question": question, "status": status,
                "correct": int(status == "correct"), "error": error,
                "inference_ms": to_int(row["inference_ms"]),
                "input_tokens": to_int(row["input_tokens"]), "output_tokens": to_int(row["output_tokens"]),
                "cache_read_tokens": to_int(row["cache_read_tokens"]),
                "cache_creation_tokens": to_int(row["cache_creation_tokens"]),
            })
    return rows


def summarize(rows, n_dataset):
    n = len(rows)
    correct = sum(r["correct"] for r in rows)
    low, high = wilson(correct, n)
    times = [r["inference_ms"] / 1000 for r in rows if r["inference_ms"] is not None]
    out_tokens = [r["output_tokens"] for r in rows if r["output_tokens"] is not None]
    in_tokens = [
        sum(r[k] or 0 for k in ("input_tokens", "cache_read_tokens", "cache_creation_tokens"))
        for r in rows if r["input_tokens"] is not None
    ]
    return {
        "prompt_id": rows[0]["prompt_id"],
        "framework": rows[0]["framework"],
        "model": rows[0]["model"],
        "answered": f"{n}/{n_dataset}",
        "correct": correct,
        "accuracy": correct / n,
        "acc_ci_low": low,
        "acc_ci_high": high,
        "sql_errors": sum(r["status"] == "sql_error" for r in rows),
        "time_mean_s": statistics.mean(times) if times else float("nan"),
        "time_median_s": statistics.median(times) if times else float("nan"),
        "time_total_min": sum(times) / 60 if times else float("nan"),
        "input_tokens_mean": statistics.mean(in_tokens) if in_tokens else float("nan"),
        "output_tokens_mean": statistics.mean(out_tokens) if out_tokens else float("nan"),
    }


def write_markdown(summaries, path):
    lines = [
        "| Prompt | Model | Answered | Accuracy (95 % CI) | Correct | SQL errors | Mean time (s) | Median time (s) | Mean input tokens | Mean output tokens |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in summaries:
        lines.append(
            f"| {s['framework']} | {s['model']} | {s['answered']} | {s['accuracy']:.1%} "
            f"({s['acc_ci_low']:.1%}–{s['acc_ci_high']:.1%}) | {s['correct']} | {s['sql_errors']} "
            f"| {s['time_mean_s']:.2f} | {s['time_median_s']:.2f} | {s['input_tokens_mean']:.0f} | {s['output_tokens_mean']:.0f} |"
        )
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def style(ax):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, length=0)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def make_charts(summaries, per_prompt_rows, out_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = [s["framework"].split(" (")[0] for s in summaries]  # short names for the axis
    x = list(range(len(names)))

    # accuracy with confidence interval
    fig, ax = plt.subplots(figsize=(6, 4))
    acc = [s["accuracy"] for s in summaries]
    ax.bar(x, acc, 0.55, color=COLORS[0])
    for i, s in enumerate(summaries):
        ax.errorbar(i, s["accuracy"], yerr=[[s["accuracy"] - s["acc_ci_low"]], [s["acc_ci_high"] - s["accuracy"]]],
                    color=INK, capsize=4, linewidth=1)
        ax.text(i, s["acc_ci_high"] + 0.02, f"{s['accuracy']:.0%}", ha="center", va="bottom", fontsize=9, color=INK)
    ax.set_xticks(x, names, color=INK)
    ax.set_ylim(0, 1.1)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_ylabel("Accuracy (exact match)", color=MUTED)
    ax.set_title("Accuracy per prompt (with 95 % confidence interval)", color=INK, loc="left", fontsize=11)
    style(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "accuracy.png", dpi=200)
    plt.close(fig)

    # inference time distribution
    fig, ax = plt.subplots(figsize=(6, 4))
    data = [[r["inference_ms"] / 1000 for r in rows if r["inference_ms"] is not None] for rows in per_prompt_rows]
    box = ax.boxplot(data, positions=x, widths=0.45, patch_artist=True, showfliers=True,
                     medianprops={"color": INK, "linewidth": 1.5},
                     flierprops={"marker": "o", "markersize": 4, "markerfacecolor": MUTED, "markeredgecolor": "none"},
                     whiskerprops={"color": MUTED}, capprops={"color": MUTED})
    for patch in box["boxes"]:
        patch.set_facecolor(COLORS[0])
        patch.set_alpha(0.35)
        patch.set_edgecolor(COLORS[0])
    ax.set_xticks(x, names, color=INK)
    ax.set_ylim(bottom=0)
    ax.set_ylabel("Inference time per question (s)", color=MUTED)
    ax.set_title("Inference time per prompt", color=INK, loc="left", fontsize=11)
    style(ax)
    fig.tight_layout()
    fig.savefig(out_dir / "inference_time.png", dpi=200)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--predictions", default=str(HERE / "predictions"))
    parser.add_argument("--out", default=str(HERE / "results"))
    args = parser.parse_args()

    with open(evaluator.LABELS_PATH, encoding="utf-8", newline="") as f:
        labels = [(row["question"], json.loads(row["result"])) for row in csv.DictReader(f)]

    connection = evaluator.load_database()
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)

    files = sorted(Path(args.predictions).glob("predictions_*.csv"))
    if not files:
        raise SystemExit(f"no predictions_*.csv files in {args.predictions}/")

    all_rows, per_prompt, summaries = [], [], []
    for path in files:
        rows = evaluate_file(path, labels, connection)
        if not rows:
            continue
        all_rows.extend(rows)
        per_prompt.append(rows)
        summaries.append(summarize(rows, len(labels)))
    connection.close()

    with open(out_dir / "per_question.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)
    with open(out_dir / "summary.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)
    write_markdown(summaries, out_dir / "summary.md")
    make_charts(summaries, per_prompt, out_dir)

    print((out_dir / "summary.md").read_text(encoding="utf-8"))
    print(f"Results written to {out_dir}/")


if __name__ == "__main__":
    main()