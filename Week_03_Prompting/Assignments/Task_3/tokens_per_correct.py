"""
Task 3: Tokens per Correct Answer (TPCA).

TPCA = all tokens used by a prompt / number of correctly answered questions

It uses results/per_question.csv from Task 2 (made by evaluate_prompts.py), so nothing has to be run again.

Usage (paths are relative to this script, so it can be run from any folder):
    python tokens_per_correct.py
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def number(value):
    return float(value) if value not in ("", None) else 0.0


HERE = Path(__file__).resolve().parent

# add up tokens and correct answers for every prompt
totals = {}
with open(HERE.parent / "Task_2" / "results" / "per_question.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        name = row["framework"].split(" (")[0]
        t = totals.setdefault(name, {"questions": 0, "correct": 0, "input": 0.0, "output": 0.0})
        t["questions"] += 1
        t["correct"] += int(row["correct"])
        # input tokens = new + cached prompt tokens
        t["input"] += number(row["input_tokens"]) + number(row["cache_read_tokens"]) + number(row["cache_creation_tokens"])
        t["output"] += number(row["output_tokens"])

lines = [
    "| Prompt | Correct | Total tokens | Tokens per correct answer | Output tokens per correct answer |",
    "|---|---|---|---|---|",
]
for name, t in totals.items():
    t["tpca"] = (t["input"] + t["output"]) / t["correct"]
    t["output_tpca"] = t["output"] / t["correct"]
    lines.append(f"| {name} | {t['correct']}/{t['questions']} | {t['input'] + t['output']:,.0f} "
                 f"| {t['tpca']:,.0f} | {t['output_tpca']:,.0f} |")

out = HERE / "results_tpca"
out.mkdir(exist_ok=True)
(out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))

# chart: tokens per correct answer, split into input and output part
names = list(totals)
input_part = [totals[n]["input"] / totals[n]["correct"] for n in names]
output_part = [totals[n]["output"] / totals[n]["correct"] for n in names]

fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(names, input_part, 0.5, color="#2a78d6", label="Input tokens", edgecolor="white", linewidth=2)
ax.bar(names, output_part, 0.5, bottom=input_part, color="#eb6834", label="Output tokens", edgecolor="white", linewidth=2)
for i, n in enumerate(names):
    ax.text(i, totals[n]["tpca"] * 1.02, f"{totals[n]['tpca']:,.0f}", ha="center", va="bottom", fontsize=9)
ax.set_ylabel("Tokens per correct answer")
ax.set_title("Tokens per correct answer", loc="left")
ax.set_ylim(0, max(t["tpca"] for t in totals.values()) * 1.15)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2)
fig.tight_layout()
fig.savefig(out / "tokens_per_correct.png", dpi=200)
print(f"Saved {out.name}/summary.md and {out.name}/tokens_per_correct.png")