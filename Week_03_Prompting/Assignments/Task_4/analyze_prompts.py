"""
Task 4: detailed comparison of the prompts, with statistical tests.

Uses only the files from Task 2 (nothing is run again):
    ../Task_2/results/per_question.csv      (made by evaluate_prompts.py)
    ../Task_2/predictions/predictions_*.csv (the stored SQL queries)

Usage (paths are relative to this script, so it can be run from any folder):
    python analyze_prompts.py

Everything is printed and also saved to results_task4/ (tables as .md, charts as .png).
"""
import csv
import json
import math
import random
import re
import sqlite3
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sys

HERE = Path(__file__).resolve().parent
TASK2 = HERE.parent / "Task_2"
sys.path.insert(0, str(TASK2 / "data"))
import evaluate_retrieval_predictions as evaluator

csv.field_size_limit(1_000_000_000)
OUT = HERE / "results_task4"
OUT.mkdir(exist_ok=True)
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
report = []  # all text output, also saved to results_task4/analysis.md


def say(text=""):
    print(text)
    report.append(text)


def table(header, rows):
    say("| " + " | ".join(header) + " |")
    say("|" + "---|" * len(header))
    for row in rows:
        say("| " + " | ".join(str(c) for c in row) + " |")
    say()


# ------------------------------------------------------------------ statistics (no extra packages)

def mcnemar_exact(b, c):
    """Exact McNemar test: b, c = questions only the first / only the second prompt got right."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def cochran_q(matrix):
    """Cochran's Q test for k paired yes/no results (rows = questions, columns = prompts)."""
    k = len(matrix[0])
    col = [sum(r[j] for r in matrix) for j in range(k)]
    row = [sum(r) for r in matrix]
    total = sum(row)
    denominator = k * total - sum(x * x for x in row)
    if denominator == 0:
        return 0.0, 1.0
    q = (k - 1) * (k * sum(x * x for x in col) - total ** 2) / denominator
    # chi-square survival function; for 2 degrees of freedom it is exactly exp(-q/2)
    p = math.exp(-q / 2) if k == 3 else float("nan")
    return q, p


def wilcoxon(x, y):
    """Wilcoxon signed-rank test for paired values (normal approximation, ties handled)."""
    d = [a - b for a, b in zip(x, y) if a != b]
    n = len(d)
    if n == 0:
        return 1.0
    order = sorted(range(n), key=lambda i: abs(d[i]))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(d[order[j + 1]]) == abs(d[order[i]]):
            j += 1
        for m in range(i, j + 1):
            ranks[order[m]] = (i + j) / 2 + 1
        i = j + 1
    w_plus = sum(r for r, v in zip(ranks, d) if v > 0)
    mean = n * (n + 1) / 4
    ties = Counter(abs(v) for v in d)
    var = n * (n + 1) * (2 * n + 1) / 24 - sum(t ** 3 - t for t in ties.values()) / 48
    z = (w_plus - mean) / math.sqrt(var)
    return math.erfc(abs(z) / math.sqrt(2))


def holm(pvalues):
    """Holm correction for several tests."""
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted, running = [0.0] * len(pvalues), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvalues) - rank) * pvalues[i]))
        adjusted[i] = running
    return adjusted


def fmt_p(p):
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


# ------------------------------------------------------------------ question types

NOISE = re.compile(r"\b(soup|pie|pancakes?|taco|muffin|noodles|toast|lunchbox|teacups|picnic|compass|umbrella|"
                   r"moon|armchair|chickpeas|omelets|dumplings|curry|cereal|sandwich|flowerpot|crackers|biscuits)\b", re.I)


def question_type(q):
    q = q.lower()
    if "illusion" in q:
        return "off-topic"
    if "the best" in q:
        return "best"
    if re.search(r"\bon (?!a |an |the |unrelated)[\w .#/&'-]+? in [a-z]", q):
        return "street"
    if " in the " in q:
        return "region"
    if q.startswith("where is") and "rating" not in q and " a " not in q[:12]:
        return "restaurant by name"
    if "rating above" in q:
        return "city + rating"
    return "city"


# ------------------------------------------------------------------ load data

with open(evaluator.LABELS_PATH, encoding="utf-8", newline="") as f:
    labels = [json.loads(r["result"]) for r in csv.DictReader(f)]

rows = list(csv.DictReader(open(TASK2 / "results" / "per_question.csv", encoding="utf-8")))
prompts = []  # keep the order of the file
for r in rows:
    name = r["framework"].split(" (")[0]
    if name not in prompts:
        prompts.append(name)

data = defaultdict(dict)  # data[prompt][question_idx] = row
for r in rows:
    data[r["framework"].split(" (")[0]][int(r["question_idx"])] = r
questions = sorted(set.intersection(*(set(d) for d in data.values())))
n = len(questions)
model = rows[0]["model"]

sql = defaultdict(dict)
for path in (TASK2 / "predictions").glob("predictions_*.csv"):
    for r in csv.DictReader(open(path, encoding="utf-8")):
        sql[r["framework"].split(" (")[0]][int(r["question_idx"])] = r["predicted_sql"]

correct = {p: [int(data[p][i]["correct"]) for i in questions] for p in prompts}
time_s = {p: [float(data[p][i]["inference_ms"]) / 1000 for i in questions] for p in prompts}


def tokens(r):
    return sum(float(r[k] or 0) for k in ("input_tokens", "cache_read_tokens", "cache_creation_tokens", "output_tokens"))


all_tokens = {p: [tokens(data[p][i]) for i in questions] for p in prompts}
out_tokens = {p: [float(data[p][i]["output_tokens"] or 0) for i in questions] for p in prompts}
qtext = {i: data[prompts[0]][i]["question"] for i in questions}
qtype = {i: question_type(qtext[i]) for i in questions}
noisy = {i: bool(NOISE.search(qtext[i])) for i in questions}

say(f"# Task 4 analysis\n\nModel: {model}, questions answered by every prompt: {n}\n")

# ------------------------------------------------------------------ 1. overview

say("## 1. Overview\n")
overview = []
for p in prompts:
    c = sum(correct[p])
    tpca = sum(all_tokens[p]) / c if c else float("nan")
    overview.append([p, f"{c}/{n}", f"{c / n:.1%}", f"{sum(time_s[p]) / n:.2f}",
                     f"{sum(out_tokens[p]) / n:.0f}", f"{tpca:,.0f}"])
table(["Prompt", "Correct", "Accuracy", "Mean time (s)", "Mean output tokens", "Tokens per correct answer"], overview)

# ------------------------------------------------------------------ 2. significance of accuracy

say("## 2. Is the difference in accuracy significant?\n")
matrix = [[correct[p][j] for p in prompts] for j in range(n)]
q, p_q = cochran_q(matrix)
say(f"Cochran's Q test (all three prompts at once): Q = {q:.2f}, p = {fmt_p(p_q)}\n")

pairs = list(combinations(prompts, 2))
raw, rows_mc = [], []
for a, b in pairs:
    only_a = sum(x and not y for x, y in zip(correct[a], correct[b]))
    only_b = sum(y and not x for x, y in zip(correct[a], correct[b]))
    p = mcnemar_exact(only_a, only_b)
    raw.append(p)
    rows_mc.append([f"{a} vs {b}", only_a, only_b, fmt_p(p)])
for row, adj in zip(rows_mc, holm(raw)):
    row.append(fmt_p(adj))
table(["Pair", "Only first correct", "Only second correct", "p (McNemar)", "p (Holm-corrected)"], rows_mc)

# ------------------------------------------------------------------ 3. significance of time and tokens

say("## 3. Is the difference in time and tokens significant?\n")
rows_w = []
raw_t, raw_o = [], []
for a, b in pairs:
    raw_t.append(wilcoxon(time_s[a], time_s[b]))
    raw_o.append(wilcoxon(out_tokens[a], out_tokens[b]))
for (a, b), pt, po, at, ao in zip(pairs, raw_t, raw_o, holm(raw_t), holm(raw_o)):
    dt = sorted(x - y for x, y in zip(time_s[a], time_s[b]))[n // 2]
    do = sorted(x - y for x, y in zip(out_tokens[a], out_tokens[b]))[n // 2]
    rows_w.append([f"{a} vs {b}", f"{dt:+.2f}", fmt_p(at), f"{do:+.0f}", fmt_p(ao)])
table(["Pair", "Median time difference (s)", "p (time)", "Median output token difference", "p (tokens)"], rows_w)
say("Wilcoxon signed-rank test on the paired values per question, Holm-corrected.\n")

# tokens per correct answer: paired bootstrap of the difference
random.seed(0)
rows_b = []
for a, b in pairs:
    diffs = []
    for _ in range(5000):
        idx = [random.randrange(n) for _ in range(n)]
        ca, cb = sum(correct[a][i] for i in idx), sum(correct[b][i] for i in idx)
        if ca and cb:
            diffs.append(sum(all_tokens[a][i] for i in idx) / ca - sum(all_tokens[b][i] for i in idx) / cb)
    diffs.sort()
    low, high = diffs[int(0.025 * len(diffs))], diffs[int(0.975 * len(diffs)) - 1]
    real = sum(all_tokens[a]) / sum(correct[a]) - sum(all_tokens[b]) / sum(correct[b])
    rows_b.append([f"{a} vs {b}", f"{real:+,.0f}", f"{low:+,.0f} to {high:+,.0f}",
                   "yes" if low > 0 or high < 0 else "no"])
table(["Pair", "Difference in tokens per correct answer", "95 % bootstrap interval", "Significant"], rows_b)

# ------------------------------------------------------------------ 4. where the prompts fail

say("## 4. Accuracy by question type\n")
types = [t for t in ["city", "city + rating", "street", "region", "best", "restaurant by name", "off-topic"]
         if any(qtype[i] == t for i in questions)]
rows_t = []
for t in types:
    ids = [j for j, i in enumerate(questions) if qtype[i] == t]
    rows_t.append([t, len(ids)] + [f"{sum(correct[p][j] for j in ids)}/{len(ids)}" for p in prompts])
for label, flag in (("with distracting text", True), ("without distracting text", False)):
    ids = [j for j, i in enumerate(questions) if noisy[i] == flag]
    rows_t.append([label, len(ids)] + [f"{sum(correct[p][j] for j in ids)}/{len(ids)}" for p in prompts])
table(["Question type", "Questions"] + prompts, rows_t)

say("## 5. How many prompts got each question wrong\n")
wrong_count = Counter(sum(1 - correct[p][j] for p in prompts) for j in range(n))
table(["Wrong in", "Questions"], [[f"{k} prompt(s)", wrong_count.get(k, 0)] for k in range(len(prompts) + 1)])

say("Questions that every prompt got wrong:\n")
for j, i in enumerate(questions):
    if all(correct[p][j] == 0 for p in prompts):
        say(f"- [{qtype[i]}] {' '.join(qtext[i].split())[:160]}")
say()

# ------------------------------------------------------------------ 6. kind of mistake

say("## 6. What kind of mistakes\n")
connection = evaluator.load_database()


def mistake(query, expected):
    try:
        got = Counter(map(tuple, connection.execute(query).fetchall()))
    except (sqlite3.Error, sqlite3.Warning, ValueError):
        return "SQL error"
    exp = Counter(map(tuple, expected))
    if not got:
        return "returned nothing"
    if not exp:
        return "should return nothing"
    if not (got & exp):
        return "completely different rows"
    if got - exp and not exp - got:
        return "too many rows"
    if exp - got and not got - exp:
        return "too few rows"
    return "partly overlapping rows"


kinds = ["returned nothing", "should return nothing", "too many rows", "too few rows",
         "partly overlapping rows", "completely different rows", "SQL error"]
mistakes = {p: Counter() for p in prompts}
examples = []
for p in prompts:
    for j, i in enumerate(questions):
        if not correct[p][j] and i in sql[p]:
            kind = mistake(sql[p][i], labels[i])
            mistakes[p][kind] += 1
            if len(examples) < 6 and qtype[i] != "off-topic":
                examples.append((p, kind, " ".join(qtext[i].split())[:120], sql[p][i][:220]))
table(["Kind of mistake"] + prompts, [[k] + [mistakes[p][k] for p in prompts] for k in kinds if any(mistakes[p][k] for p in prompts)])

say("Some example mistakes:\n")
for p, kind, qq, s in examples:
    say(f"- **{p}**, {kind}: *{qq}*  \n  `{s}`")
say()

Path(OUT / "analysis.md").write_text("\n".join(report) + "\n", encoding="utf-8")

# ------------------------------------------------------------------ charts


def style(ax):
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.yaxis.grid(True, color="#e4e3dd")
    ax.set_axisbelow(True)


# accuracy by question type
fig, ax = plt.subplots(figsize=(8, 4))
w = 0.8 / len(prompts)
for k, p in enumerate(prompts):
    vals = []
    for t in types:
        ids = [j for j, i in enumerate(questions) if qtype[i] == t]
        vals.append(sum(correct[p][j] for j in ids) / len(ids))
    ax.bar([x + (k - (len(prompts) - 1) / 2) * w for x in range(len(types))], vals, w * 0.92, color=COLORS[k], label=p)
ax.set_xticks(range(len(types)), [f"{t}\n(n={sum(qtype[i] == t for i in questions)})" for t in types], fontsize=8)
ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
ax.set_title("Accuracy by question type", loc="left")
ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=len(prompts))
style(ax)
fig.tight_layout()
fig.savefig(OUT / "accuracy_by_type.png", dpi=200)
plt.close(fig)

# kind of mistakes
used = [k for k in kinds if any(mistakes[p][k] for p in prompts)]
fig, ax = plt.subplots(figsize=(6.5, 4))
bottom = [0] * len(prompts)
for k, kind in enumerate(used):
    vals = [mistakes[p][kind] for p in prompts]
    ax.bar(prompts, vals, 0.5, bottom=bottom, color=(COLORS + ["#008300", "#e87ba4", "#6b6a64"])[k], label=kind,
           edgecolor="white", linewidth=2)
    bottom = [a + b for a, b in zip(bottom, vals)]
ax.set_ylabel("Wrong answers")
ax.set_title("What kind of mistakes each prompt made", loc="left")
ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
style(ax)
fig.tight_layout()
fig.savefig(OUT / "mistakes.png", dpi=200)
plt.close(fig)

# accuracy vs cost
fig, ax = plt.subplots(figsize=(6, 4))
for k, p in enumerate(prompts):
    acc = sum(correct[p]) / n
    ax.scatter(sum(time_s[p]) / n, acc, s=120, color=COLORS[k], zorder=3)
    ax.annotate(p, (sum(time_s[p]) / n, acc), textcoords="offset points", xytext=(8, 6), fontsize=9)
ax.set_xlabel("Mean inference time per question (s)")
ax.set_ylabel("Accuracy")
ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
ax.set_title("Accuracy vs. time (top left is best)", loc="left")
ax.set_xlim(0, max(sum(time_s[p]) / n for p in prompts) * 1.4)
ax.set_ylim(max(0, min(sum(correct[p]) / n for p in prompts) - 0.1), 1)
style(ax)
fig.tight_layout()
fig.savefig(OUT / "accuracy_vs_time.png", dpi=200)
plt.close(fig)

print(f"\nSaved results_task4/analysis.md and 3 charts")