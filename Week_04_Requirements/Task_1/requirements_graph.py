"""Agentic network for software requirements refinement (LangGraph).

Usage:
    python requirements_graph.py <input_dir> [-o requirements.md] [--max-rounds 4]

The OpenAI key is read from the env variable 'SCHOOL_OPEN_AI_API_KEY', optionally loaded from a .env file.

Graph:
    load_corpus (det.) -> extract (LLM, per document) -> categorize (LLM)
        -> consolidate_areas (LLM, per functional area) -> integrate (LLM)
        -> validate (det.) -> review (LLM)
             --approved / max rounds--> render (det.) -> END
             --issues--> integrate                      (feedback loop)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

TEXT_SUFFIXES = {".txt", ".md", ".eml", ".csv", ".json", ".html", ".xml", ""}
PRIORITIES = ["Must", "Should", "Could", "Won't"]
PRIORITY_SCALE = {
    "Must": "Essential for the system to be usable/acceptable; explicitly demanded "
    "by stakeholders, marked critical, or required by law/policy.",
    "Should": "Important and expected, but the system can go live without it "
    "(a workaround exists).",
    "Could": "Desirable nice-to-have that improves convenience; implemented if time allows.",
    "Won't": "Acknowledged but explicitly out of scope for the current release.",
}
AREA_CHUNK = 90           # max candidates per consolidation call
FALLBACK_AREA = "General"

MODELS = {
    "extract": "gpt-5-nano",
    "categorize": "gpt-5-mini",
    "consolidate": "gpt-5-mini",
    "integrate": "gpt-5-mini",
    "review": "gpt-6-luna",
}

STYLE_RULES = """Style and vocabulary rules (apply to every requirement):
- Name: short, Title Case, max ~8 words, names ONE capability.
- Description: one paragraph of 3-6 sentences starting with "The system shall", \
stating the behaviour, who uses it, the rationale, and how it can be verified.
- Use ONLY the canonical glossary terms (never synonyms of them).
- One requirement = one cohesive, independently testable capability. Do NOT bundle \
different features into one requirement just because they are related.
- Never mention internal ids (C###, R###) in names, descriptions or rationales; \
traceability is recorded separately in `candidate_ids`."""

GLOSSARY_RULES = """Glossary rules: one entry per concept (10-20 entries). Terms must be \
distinct, non-overlapping concepts: never create variants of a term (e.g. 'Template (Open)', \
'Template (Standard)') - describe subtypes inside the parent term's definition instead. \
Never define two terms for the same thing (e.g. 'Item' and 'Copy'); pick one canonical term \
and list the other as a synonym to avoid."""

BLACKLIST_RULES = """The discarded list (blacklist) is ONLY for candidates that are \
(a) in conflict with another requirement (name the winning requirement and why it wins), \
(b) nonsensical/unverifiable, or (c) not a software requirement (small talk, logistics, \
project management). Duplicates are NEVER discarded - merge them into the requirement \
they duplicate by listing their candidate id there."""


# --------------------------------------------------------------------------- #
# Structured LLM output schemas (strict-JSON compatible: no free-form dicts)
# --------------------------------------------------------------------------- #
class Candidate(BaseModel):
    name: str = Field(description="Short descriptive name (max ~8 words)")
    statement: str = Field(description="The requirement as one 'The system shall ...' sentence")
    evidence: str = Field(description="Short verbatim quote from the document supporting it")
    importance_hint: str = Field(description="Any urgency signal in the text (e.g. 'CRITICAL', 'nice to have') or ''")


class ExtractionResult(BaseModel):
    candidates: list[Candidate]


class GlossaryTerm(BaseModel):
    term: str = Field(description="Canonical term used consistently across requirements")
    definition: str
    avoid: list[str] = Field(description="Synonyms that must NOT be used instead of the term")


class Area(BaseModel):
    name: str = Field(description="Functional area name, Title Case, e.g. 'Circulation Reporting'")
    description: str


class Assignment(BaseModel):
    candidate_id: str
    area: str


class CategorizationResult(BaseModel):
    areas: list[Area]
    glossary: list[GlossaryTerm]
    assignments: list[Assignment]


class Requirement(BaseModel):
    name: str
    description: str
    type: Literal["Functional", "Non-functional"]
    priority: Literal["Must", "Should", "Could", "Won't"]
    priority_rationale: str
    candidate_ids: list[str] = Field(description="IDs of ALL candidates this requirement is derived from")


class Discarded(BaseModel):
    name: str
    kind: Literal["conflict", "nonsensical", "not-software"]
    reason: str
    candidate_ids: list[str]


class AreaResult(BaseModel):
    requirements: list[Requirement]
    discarded: list[Discarded]


class Merge(BaseModel):
    keep: str = Field(description="Key of the requirement that survives, e.g. 'R012'")
    absorb: list[str] = Field(description="Keys of duplicate requirements merged into `keep`")
    name: str
    description: str = Field(description="Rewritten paragraph covering the merged meaning")


class Rewrite(BaseModel):
    key: str
    name: str
    description: str
    type: Literal["Functional", "Non-functional"]
    priority: Literal["Must", "Should", "Could", "Won't"]
    priority_rationale: str


class DiscardRequirement(BaseModel):
    key: str
    kind: Literal["conflict", "nonsensical", "not-software"]
    reason: str


class Attach(BaseModel):
    key: str
    candidate_ids: list[str]


class Split(BaseModel):
    key: str = Field(description="Key of the bundled requirement to replace")
    parts: list[Requirement] = Field(description="Atomic requirements replacing it; together they must cover all its candidate_ids")


class Addition(BaseModel):
    area: str
    requirement: Requirement


class EditPlan(BaseModel):
    glossary: list[GlossaryTerm] = Field(description="Full (possibly updated) glossary")
    merges: list[Merge]
    splits: list[Split]
    rewrites: list[Rewrite]
    discard_requirements: list[DiscardRequirement]
    attach: list[Attach]
    additions: list[Addition]
    discard_candidates: list[Discarded]
    restore_candidates: list[str] = Field(description="Candidate ids wrongly blacklisted; they must also appear in attach or additions")


class ReviewResult(BaseModel):
    approved: bool
    issues: list[str] = Field(description="Concrete actionable problems referencing requirement keys (R###)")


# --------------------------------------------------------------------------- #
# Graph state
# --------------------------------------------------------------------------- #
class State(TypedDict, total=False):
    input_dir: str
    output_path: str
    max_rounds: int
    cache_path: str                     # extraction cache ('' = disabled)
    documents: dict[str, str]           # relative path -> text
    candidates: dict[str, dict]         # C001 -> candidate + source
    areas: list[dict]
    area_of: dict[str, str]             # candidate id -> area
    glossary: list[dict]
    reqs: dict[str, dict]               # R001 -> requirement (+ area)
    discarded: list[dict]
    validation_issues: list[str]
    review_issues: list[str]
    approved: bool
    round: int
    log: list[str]                      # per-round summary for the document


def llm(node: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=MODELS[node],
        api_key=os.environ["OPENAI_API_KEY_RESOLVED"],
        base_url=os.environ.get("OPENAI_BASE_URL") or None,
        timeout=900,
        max_retries=3,
    )


def log(msg: str) -> None:
    print(f"[graph] {msg}", file=sys.stderr, flush=True)


def glossary_text(glossary: list[dict]) -> str:
    return "\n".join(f"- {g['term']}: {g['definition']}"
                     + (f" (do not say: {', '.join(g['avoid'])})" if g["avoid"] else "")
                     for g in glossary)


ID_REF = re.compile(r"\s*\((?:see |e\.g\. )?C\d{3}(?:\s*[,–-]\s*C?\d{3})*\)")


def strip_ids(text: str) -> str:
    """Remove leaked internal candidate ids from reader-facing text."""
    return re.sub(r"\s+([.,;])", r"\1", ID_REF.sub("", text)).strip()


def clean_glossary(glossary: list[dict]) -> list[dict]:
    """Deterministic: a word that is itself (part of) a glossary term cannot be a forbidden synonym."""
    terms = [g["term"].lower() for g in glossary]
    return [{**g, "avoid": [a for a in g["avoid"]
                            if not any(re.search(rf"\b{re.escape(a.lower())}\b", t) or a.lower() in t for t in terms)]}
            for g in glossary]


def glossary_overlaps(glossary: list[dict]) -> list[tuple[str, str]]:
    """Deterministic: pairs of glossary terms that share a name variant or contain one another."""
    def variants(term):
        base = re.sub(r"\(.*?\)", " ", term.lower())
        inner = re.findall(r"\((.*?)\)", term.lower())
        return {v.strip() for v in re.split(r"[/,]", base) + inner if v.strip()}
    pairs = []
    for i, a in enumerate(glossary):
        for b in glossary[i + 1:]:
            va, vb = variants(a["term"]), variants(b["term"])
            if va & vb or any(re.search(rf"\b{re.escape(x)}\b", b["term"].lower()) for x in va) \
                    or any(re.search(rf"\b{re.escape(x)}\b", a["term"].lower()) for x in vb):
                pairs.append((a["term"], b["term"]))
    return pairs


def next_key(reqs: dict) -> str:
    return f"R{max((int(k[1:]) for k in reqs), default=0) + 1:03d}"


# --------------------------------------------------------------------------- #
# Nodes
# --------------------------------------------------------------------------- #
def load_corpus(state: State) -> State:
    """Deterministic: read every text file under input_dir (recursively)."""
    root = Path(state["input_dir"])
    docs = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES and not p.name.startswith("."):
            docs[str(p.relative_to(root))] = p.read_text(encoding="utf-8", errors="replace")
    if not docs:
        raise SystemExit(f"No text documents found in {root}")
    log(f"loaded {len(docs)} documents")
    return {"documents": docs, "round": 0, "log": []}


EXTRACT_PROMPT = """You are a requirements engineer. Extract EVERY software requirement \
(functional and non-functional) stated or clearly implied in the document below. \
The document is part of a corpus about one software system.

Rules:
- Be exhaustive: do not skip requirements, even minor ones (completeness matters).
- One atomic requirement per candidate; split compound wishes.
- Ignore content unrelated to the software (small talk, personal remarks, logistics).
- Do NOT deduplicate against other documents; another agent does that.
- Keep the stakeholders' meaning; do not invent features.

Document name: {name}
---
{text}
---"""


def extract(state: State) -> State:
    """LLM (cheap, parallel): per-document candidate requirement extraction."""
    cache = Path(state["cache_path"]) if state.get("cache_path") else None
    if cache and cache.exists():
        cached = json.loads(cache.read_text(encoding="utf-8"))
        if cached.get("documents") == sorted(state["documents"]):
            log(f"extract: reusing {len(cached['candidates'])} candidates from {cache}")
            return {"candidates": cached["candidates"]}
    model = llm("extract").with_structured_output(ExtractionResult)

    def run(item):
        name, text = item
        res = model.invoke(EXTRACT_PROMPT.format(name=name, text=text))
        log(f"extract: {name} -> {len(res.candidates)} candidates")
        return name, res.candidates

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(run, state["documents"].items()))

    candidates, n = {}, 0
    for name, cands in results:
        for c in cands:
            n += 1
            candidates[f"C{n:03d}"] = {**c.model_dump(), "source": name}
    log(f"extract: {len(candidates)} candidates total")
    if cache:
        cache.write_text(json.dumps({"documents": sorted(state["documents"]), "candidates": candidates},
                                    ensure_ascii=False, indent=1), encoding="utf-8")
    return {"candidates": candidates}


CATEGORIZE_PROMPT = """You organise candidate software requirements (extracted from many \
stakeholder documents about ONE system) for consolidation.

1. Define 6-14 functional areas that partition the candidates (e.g. by feature/domain, \
plus one for non-functional qualities such as performance, security, usability). Areas \
must not overlap, so that duplicates of the same need land in the SAME area.
2. Build a glossary of canonical domain terms ({glossary_rules}). For each, list only genuine \
domain synonyms seen in the candidates that would make the specification ambiguous \
(e.g. 'copy' vs 'Item'). Do NOT list common English words that also have other \
meanings (e.g. 'user', 'library', 'account', 'activity', 'location') - leave `avoid` \
empty when unsure.
3. Assign EVERY candidate id to exactly one area (use the exact area name).

Candidates (id: name - statement [source]):
{candidates}"""


def categorize(state: State) -> State:
    """LLM: partition candidates into functional areas and define the glossary."""
    model = llm("categorize").with_structured_output(CategorizationResult)
    lines = "\n".join(f"{cid}: {c['name']} - {c['statement']} [{c['source']}]"
                      for cid, c in state["candidates"].items())
    res = model.invoke(CATEGORIZE_PROMPT.format(candidates=lines, glossary_rules=GLOSSARY_RULES))
    names = {a.name for a in res.areas}
    area_of = {a.candidate_id: a.area for a in res.assignments
               if a.candidate_id in state["candidates"] and a.area in names}
    areas = [a.model_dump() for a in res.areas]
    unassigned = [cid for cid in state["candidates"] if cid not in area_of]
    if unassigned:  # deterministic safety net: nothing is lost
        areas.append({"name": FALLBACK_AREA, "description": "Candidates not assigned to another area."})
        area_of.update({cid: FALLBACK_AREA for cid in unassigned})
    log(f"categorize: {len(areas)} areas, {len(res.glossary)} glossary terms, {len(unassigned)} unassigned")
    return {"areas": areas, "area_of": area_of, "glossary": clean_glossary([g.model_dump() for g in res.glossary])}


CONSOLIDATE_PROMPT = """You are a senior requirements engineer. Consolidate the candidate \
requirements of the functional area "{area}" ({area_desc}) into final requirements.

Tasks:
1. MERGE candidates that express the same need into one requirement (list all their ids \
in `candidate_ids`). Keep genuinely different capabilities as separate requirements.
2. CONFLICTS: if candidates contradict each other, keep the better supported one (more \
sources, more authoritative/recent source, consistent with the rest) and blacklist the other.
3. PRIORITY (MoSCoW):
{scale}
   Base it on importance hints, number of stakeholders asking, and dependencies.
4. COMPLETENESS: every candidate id below must appear in exactly one requirement or \
discarded item.

{style}

{blacklist}

Glossary:
{glossary}

Candidates (JSON):
{candidates}"""


def consolidate_areas(state: State) -> State:
    """LLM (parallel per area/chunk): dedupe, resolve conflicts, prioritise."""
    model = llm("consolidate").with_structured_output(AreaResult)
    scale = "\n".join(f"   - {k}: {v}" for k, v in PRIORITY_SCALE.items())
    jobs = []
    for area in state["areas"]:
        ids = [cid for cid, a in state["area_of"].items() if a == area["name"]]
        for i in range(0, len(ids), AREA_CHUNK):
            jobs.append((area, ids[i:i + AREA_CHUNK]))

    def run(job):
        area, ids = job
        cands = {cid: {k: state["candidates"][cid][k]
                       for k in ("name", "statement", "evidence", "importance_hint", "source")} for cid in ids}
        res = model.invoke(CONSOLIDATE_PROMPT.format(
            area=area["name"], area_desc=area["description"], scale=scale, style=STYLE_RULES,
            blacklist=BLACKLIST_RULES, glossary=glossary_text(state["glossary"]),
            candidates=json.dumps(cands, ensure_ascii=False, indent=1)))
        log(f"consolidate: {area['name']} ({len(ids)} candidates) -> "
            f"{len(res.requirements)} requirements, {len(res.discarded)} discarded")
        return area["name"], set(ids), res

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(run, jobs))

    reqs, discarded = {}, []
    for area, ids, res in results:
        for r in res.requirements:
            r = r.model_dump()
            r["candidate_ids"] = [c for c in r["candidate_ids"] if c in ids]  # keep chunk-local refs only
            reqs[next_key(reqs)] = {**r, "area": area}
        for d in res.discarded:
            d = d.model_dump()
            d["candidate_ids"] = [c for c in d["candidate_ids"] if c in ids]
            discarded.append(d)
    log(f"consolidate: {len(reqs)} requirements, {len(discarded)} discarded in total")
    return {"reqs": reqs, "discarded": discarded}


INTEGRATE_PROMPT = """You are the lead requirements engineer integrating per-area \
requirement lists into ONE consistent specification. You do not rewrite the whole \
spec; you return a set of edit operations which will be applied to it.

{task}

Available operations:
- merges: merge semantic duplicates (possibly from different areas) into `keep`.
- splits: replace a requirement that bundles several distinct capabilities by atomic parts.
- rewrites: fix a requirement's name/description/priority (e.g. vocabulary, vagueness).
- discard_requirements: blacklist a requirement that conflicts with another (name the \
winner in the reason) or is nonsensical/not software.
- attach: add uncovered candidate ids to an existing requirement that covers them.
- additions: create a new requirement for uncovered candidates expressing a new need.
- discard_candidates: blacklist uncovered candidates (only conflict/nonsensical/not-software).
- restore_candidates: un-blacklist candidates that were wrongly discarded (then attach/add them).
- glossary: return the full glossary (update it if terms need clarifying or merging).

{glossary_rules}
Return empty lists for operations you do not need. Only reference existing keys.

{style}

{blacklist}

Priority scale (MoSCoW):
{scale}

Glossary:
{glossary}

Current requirements (key | area | priority | name | description | candidates):
{reqs}

Current blacklist:
{discarded}
{extra}"""

FIRST_ROUND_TASK = """Task for this round: find (1) duplicate requirements across areas and \
merge them, (2) requirements that conflict/contradict each other and blacklist the loser, \
(3) vocabulary inconsistent with the glossary and rewrite it, (4) bundled requirements and \
split them, (5) overlapping glossary entries and merge them."""


def integrate(state: State) -> State:
    """LLM: cross-area integration (round 1) and fixing reviewer/validator issues (later rounds)."""
    model = llm("integrate").with_structured_output(EditPlan)
    rnd = state.get("round", 0) + 1
    issues = state.get("validation_issues", []) + state.get("review_issues", [])
    task = FIRST_ROUND_TASK if rnd == 1 else (
        "Task for this round: resolve ALL of these issues found by the validator and the reviewer:\n- "
        + "\n- ".join(issues))
    covered = {c for r in state["reqs"].values() for c in r["candidate_ids"]} | \
              {c for d in state["discarded"] for c in d["candidate_ids"]}
    uncovered = {cid: f"{c['statement']} [{c['source']}]"
                 for cid, c in state["candidates"].items() if cid not in covered}
    extra = ("\nUncovered candidates (must be attached, added or discarded):\n"
             + json.dumps(uncovered, ensure_ascii=False, indent=1)) if uncovered else ""
    req_lines = "\n".join(f"{k} | {r['area']} | {r['priority']} | {r['name']} | {r['description']} | "
                          f"{','.join(r['candidate_ids'])}" for k, r in state["reqs"].items())
    disc_lines = "\n".join(f"- {d['name']} ({d['kind']}): {d['reason']} [{','.join(d['candidate_ids'])}]"
                           for d in state["discarded"]) or "(empty)"
    plan = model.invoke(INTEGRATE_PROMPT.format(
        task=task, style=STYLE_RULES, blacklist=BLACKLIST_RULES, glossary_rules=GLOSSARY_RULES,
        scale="\n".join(f"- {k}: {v}" for k, v in PRIORITY_SCALE.items()),
        glossary=glossary_text(state["glossary"]), reqs=req_lines, discarded=disc_lines, extra=extra))

    reqs = {k: dict(r) for k, r in state["reqs"].items()}
    discarded = [dict(d) for d in state["discarded"]]
    applied = []

    for m in plan.merges:
        if m.keep not in reqs:
            continue
        for k in m.absorb:
            if k in reqs and k != m.keep:
                reqs[m.keep]["candidate_ids"] += reqs.pop(k)["candidate_ids"]
                applied.append(f"merge {k}->{m.keep}")
        reqs[m.keep].update(name=m.name, description=m.description)
    for s in plan.splits:
        if s.key in reqs and s.parts:
            old = reqs.pop(s.key)
            parts = [p.model_dump() for p in s.parts]
            missing = set(old["candidate_ids"]) - {c for p in parts for c in p["candidate_ids"]}
            parts[0]["candidate_ids"] += sorted(missing)  # never lose traces
            for p in parts:
                reqs[next_key(reqs)] = {**p, "area": old["area"]}
            applied.append(f"split {s.key} into {len(parts)}")
    for w in plan.rewrites:
        if w.key in reqs:
            reqs[w.key].update(w.model_dump(exclude={"key"}))
            applied.append(f"rewrite {w.key}")
    for d in plan.discard_requirements:
        if d.key in reqs:
            r = reqs.pop(d.key)
            discarded.append({"name": r["name"], "kind": d.kind, "reason": d.reason,
                              "candidate_ids": r["candidate_ids"]})
            applied.append(f"discard {d.key}")
    restore = set(plan.restore_candidates)
    if restore:
        for d in discarded:
            d["candidate_ids"] = [c for c in d["candidate_ids"] if c not in restore]
        discarded = [d for d in discarded if d["candidate_ids"]]
        applied.append(f"restore {len(restore)} candidates")
    for a in plan.attach:
        if a.key in reqs:
            reqs[a.key]["candidate_ids"] += [c for c in a.candidate_ids if c in state["candidates"]]
            applied.append(f"attach {len(a.candidate_ids)}->{a.key}")
    areas = {a["name"] for a in state["areas"]}
    for add in plan.additions:
        r = add.requirement.model_dump()
        r["candidate_ids"] = [c for c in r["candidate_ids"] if c in state["candidates"]]
        if not r["candidate_ids"]:  # never introduce untraceable requirements
            log(f"integrate: rejected untraceable addition '{r['name']}'")
            continue
        reqs[next_key(reqs)] = {**r, "area": add.area if add.area in areas else FALLBACK_AREA}
        applied.append("add")
    for d in plan.discard_candidates:
        d = d.model_dump()
        d["candidate_ids"] = [c for c in d["candidate_ids"] if c in state["candidates"]]
        if d["candidate_ids"]:  # an explicit discard wins: detach the candidates from requirements
            for r in reqs.values():
                r["candidate_ids"] = [c for c in r["candidate_ids"] if c not in d["candidate_ids"]]
            discarded.append(d)
            applied.append("discard candidates")
    for r in reqs.values():
        r["candidate_ids"] = sorted(set(r["candidate_ids"]))
    # A candidate that still supports a kept requirement is not blacklisted (the requirement
    # wins); blacklist entries keep their record even if all their candidates are shared.
    used = {c for r in reqs.values() for c in r["candidate_ids"]}
    for d in discarded:
        own = [c for c in d["candidate_ids"] if c not in used]
        d["related_ids"] = sorted(set(d.get("related_ids", [])) | (set(d["candidate_ids"]) - set(own)))
        d["candidate_ids"] = own

    summary = (f"Round {rnd}: {len(applied)} edit operations "
               f"({len(plan.merges)} merges, {len(plan.splits)} splits, {len(plan.rewrites)} rewrites, "
               f"{len(plan.discard_requirements)} requirement discards, {len(plan.attach)} attaches, "
               f"{len(plan.additions)} additions) -> {len(reqs)} requirements")
    log(f"integrate: {summary}")
    return {"reqs": reqs, "discarded": discarded,
            "glossary": clean_glossary([g.model_dump() for g in plan.glossary]) or state["glossary"],
            "round": rnd, "log": state["log"] + [summary]}


def validate(state: State) -> State:
    """Deterministic: coverage, references, required fields, naming and style checks."""
    reqs, cands = state["reqs"], state["candidates"]
    issues = []
    in_req = {c for r in reqs.values() for c in r["candidate_ids"]}
    in_disc = {c for d in state["discarded"] for c in d["candidate_ids"]}

    missing = [c for c in cands if c not in in_req and c not in in_disc]
    if missing:
        issues.append("Uncovered candidates (attach, add or discard them): " + ", ".join(missing))
    both = sorted(in_req & in_disc)
    if both:
        issues.append("Candidates both used in a requirement and blacklisted (decide one): " + ", ".join(both))
    for k, r in reqs.items():
        if not r["candidate_ids"]:
            issues.append(f"{k} '{r['name']}' has no source candidates (untraceable); attach candidates or discard it.")
        if len(r["description"].split()) < 25:
            issues.append(f"{k} '{r['name']}': description is too short; write a full paragraph.")
        if not r["description"].lower().startswith("the system shall"):
            issues.append(f"{k} '{r['name']}': description must start with 'The system shall'.")
    by_name = {}
    for k, r in reqs.items():
        by_name.setdefault(re.sub(r"\W+", " ", r["name"].lower()).strip(), []).append(k)
    for keys in by_name.values():
        if len(keys) > 1:
            issues.append(f"Requirements {', '.join(keys)} have the same name; merge them or rename.")
    for g in state["glossary"]:
        for syn in g["avoid"]:
            hits = [k for k, r in reqs.items()
                    if re.search(rf"\b{re.escape(syn)}\b", r["name"] + " " + r["description"], re.I)
                    and not re.search(rf"\b{re.escape(syn)}\b", g["term"], re.I)]
            if hits:
                issues.append(f"Synonym '{syn}' used instead of glossary term '{g['term']}' in {', '.join(hits)}.")

    for a, b in glossary_overlaps(state["glossary"]):
        issues.append(f"Glossary terms '{a}' and '{b}' overlap; merge them into one entry "
                      "(describe variants in the definition).")

    log(f"validate: {len(issues)} issues, coverage {len(in_req | in_disc)}/{len(cands)}")
    return {"validation_issues": issues}


REVIEW_PROMPT = """You are an independent QA reviewer of a Software Requirements \
Specification. Check it strictly against these criteria:
- No semantic duplicates (two requirements meaning the same thing).
- No contradicting/conflicting requirements.
- Consistent vocabulary (glossary terms) and consistent style.
- Glossary: each concept defined exactly once; no overlapping, variant or near-synonymous terms.
- Each requirement is ONE testable capability with a short name and a full paragraph.
- Priorities are plausible under the MoSCoW scale.
- Blacklisted items are really conflicting/nonsensical/not-software (never mere duplicates), \
with a sound reason.
- Completeness: compare against the candidate list; no stakeholder need is lost.

Approve if the specification is good enough to hand to developers (minor stylistic \
nitpicks are not a reason to reject). Otherwise list at most 15 concrete, actionable \
issues, each referencing requirement keys (R###) or candidate ids (C###).

Glossary:
{glossary}

Requirements (key | priority | name | description | candidates):
{reqs}

Blacklist:
{discarded}

Candidates (id: statement [source]):
{candidates}"""


def review(state: State) -> State:
    """LLM (strongest, different model): critic in the feedback loop."""
    model = llm("review").with_structured_output(ReviewResult)
    req_lines = "\n".join(f"{k} | {r['priority']} | {r['name']} | {r['description']} | {','.join(r['candidate_ids'])}"
                          for k, r in state["reqs"].items())
    disc_lines = "\n".join(f"- {d['name']} ({d['kind']}): {d['reason']} [{','.join(d['candidate_ids'])}]"
                           for d in state["discarded"]) or "(empty)"
    cand_lines = "\n".join(f"{cid}: {c['statement']} [{c['source']}]" for cid, c in state["candidates"].items())
    res = model.invoke(REVIEW_PROMPT.format(glossary=glossary_text(state["glossary"]), reqs=req_lines,
                                            discarded=disc_lines, candidates=cand_lines))
    blocking = [i for i in state["validation_issues"] if not i.startswith("Synonym")]
    approved = res.approved and not blocking
    log(f"review round {state['round']}: approved={approved} (llm={res.approved}), {len(res.issues)} issues")
    for i in res.issues:
        log(f"  - {i}")
    return {"review_issues": res.issues, "approved": approved}


def route_after_review(state: State) -> str:
    if state["approved"] or state["round"] >= state["max_rounds"]:
        return "render"
    return "integrate"


def render(state: State) -> State:
    """Deterministic: assign final IDs, derive traces, write the Markdown document."""
    cands = state["candidates"]
    area_order = [a["name"] for a in state["areas"]]
    ordered = sorted(state["reqs"].items(), key=lambda kv: (
        area_order.index(kv[1]["area"]) if kv[1]["area"] in area_order else len(area_order),
        PRIORITIES.index(kv[1]["priority"]), kv[1]["name"]))
    final = []
    for i, (key, r) in enumerate(ordered, 1):
        r = {**r, **{f: strip_ids(r[f]) for f in ("name", "description", "priority_rationale")}}
        sources = sorted({cands[c]["source"] for c in r["candidate_ids"] if c in cands})
        final.append({**r, "id": f"REQ-{i:03d}", "key": key, "sources": sources})
    key_to_id = {r["key"]: r["id"] for r in final}
    counts = {p: sum(r["priority"] == p for r in final) for p in PRIORITIES}

    L = [
        "# Software Requirements Specification",
        "",
        f"*Generated {date.today()} by the requirements-refinement agentic network from "
        f"{len(state['documents'])} input documents: {len(cands)} extracted candidate requirements "
        f"→ {len(final)} requirements and {len(state['discarded'])} blacklisted items after "
        f"{state['round']} integration/review round(s). Reviewer approved: "
        f"{'yes' if state['approved'] else 'no (see section 8)'}.*",
        "",
        "## 1. Priority Scale (MoSCoW)",
        "",
        "| Priority | Meaning | Count |",
        "|---|---|---|",
        *[f"| **{k}** | {v} | {counts[k]} |" for k, v in PRIORITY_SCALE.items()],
        "",
        "## 2. Glossary",
        "",
        *[f"- **{g['term']}**: {g['definition']}" for g in sorted(state["glossary"], key=lambda g: g["term"].lower())],
        "",
        "## 3. Requirements Overview",
        "",
        "| ID | Name | Area | Type | Priority |",
        "|---|---|---|---|---|",
        *[f"| [{r['id']}](#{r['id'].lower()}) | {r['name']} | {r['area']} | {r['type']} | {r['priority']} |"
          for r in final],
        "",
        "## 4. Requirements",
    ]
    current = None
    for r in final:
        if r["area"] != current:
            current = r["area"]
            L += ["", f"### {current}"]
        L += [
            "",
            f"#### {r['id']}",
            "",
            f"**{r['name']}** · *{r['type']} · Priority: {r['priority']}*",
            "",
            r["description"],
            "",
            f"*Priority rationale:* {r['priority_rationale']}",
            "",
            f"*Sources:* {', '.join(f'`{s}`' for s in r['sources'])}",
        ]
    L += ["", "## 5. Discarded Requirements (Blacklist)", ""]
    if state["discarded"]:
        L += ["| # | Name | Kind | Reason | Sources |", "|---|---|---|---|---|"]
        for i, d in enumerate(state["discarded"], 1):
            reason = strip_ids(re.sub(r"\bR\d{3}\b", lambda m: key_to_id.get(m.group(), m.group()), d["reason"]))
            name = re.sub(r"\s*\bcandidate\s+C\d{3}\b|\s*\bC\d{3}\b", "", d["name"]).strip()
            src = sorted({cands[c]["source"] for c in d["candidate_ids"] + d.get("related_ids", []) if c in cands})
            L.append(f"| D-{i:03d} | {name} | {d['kind']} | {reason} | {', '.join(src)} |")
    else:
        L.append("No requirements were discarded.")
    L += ["", "## 6. Traceability Matrix (Document → Requirements)", "", "| Document | Requirements |", "|---|---|"]
    for doc in state["documents"]:
        ids = [r["id"] for r in final if doc in r["sources"]]
        L.append(f"| `{doc}` | {', '.join(ids) or '—'} |")
    L += ["", "## 7. Refinement Log", "", *[f"- {line}" for line in state["log"]]]
    def fix(i):
        return re.sub(r"\bR\d{3}\b", lambda m: key_to_id.get(m.group(), m.group()), i)
    vocab = [i for i in state.get("validation_issues", []) if i.startswith("Synonym")]
    open_issues = [i for i in state.get("validation_issues", []) if not i.startswith("Synonym")] + \
        ([] if state["approved"] else state.get("review_issues", []))
    if open_issues or vocab:
        L += ["", "## 8. Open Issues", ""]
        L += [f"- {fix(i)}" for i in open_issues]
        if vocab:
            L += ["", "Vocabulary warnings (non-blocking):", "", *[f"- {fix(i)}" for i in vocab]]

    Path(state["output_path"]).write_text("\n".join(L) + "\n", encoding="utf-8")
    log(f"wrote {state['output_path']}: {len(final)} requirements")
    return {}


# --------------------------------------------------------------------------- #
def build_graph():
    g = StateGraph(State)
    for name, fn in [("load_corpus", load_corpus), ("extract", extract), ("categorize", categorize),
                     ("consolidate_areas", consolidate_areas), ("integrate", integrate),
                     ("validate", validate), ("review", review), ("render", render)]:
        g.add_node(name, fn)
    g.set_entry_point("load_corpus")
    g.add_edge("load_corpus", "extract")
    g.add_edge("extract", "categorize")
    g.add_edge("categorize", "consolidate_areas")
    g.add_edge("consolidate_areas", "integrate")
    g.add_edge("integrate", "validate")
    g.add_edge("validate", "review")
    g.add_conditional_edges("review", route_after_review, {"integrate": "integrate", "render": "render"})
    g.add_edge("render", END)
    return g.compile()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input_dir")
    ap.add_argument("-o", "--output", default="requirements.md")
    ap.add_argument("--max-rounds", type=int, default=4)
    ap.add_argument("--cache", default="extraction_cache.json",
                    help="extraction cache file; pass '' to always re-extract")
    for node, model in MODELS.items():
        ap.add_argument(f"--{node}-model", default=model)
    args = ap.parse_args()

    load_dotenv()
    key = os.environ.get("school_open_ai_api_key") or os.environ.get("SCHOOL_OPEN_AI_API_KEY")
    if not key:
        raise SystemExit("Set the env variable school_open_ai_api_key (or put it in .env).")
    os.environ["OPENAI_API_KEY_RESOLVED"] = key
    for node in MODELS:
        MODELS[node] = getattr(args, f"{node}_model")

    build_graph().invoke(
        {"input_dir": args.input_dir, "output_path": args.output, "max_rounds": args.max_rounds,
         "cache_path": args.cache},
        {"recursion_limit": 50},
    )


if __name__ == "__main__":
    main()
