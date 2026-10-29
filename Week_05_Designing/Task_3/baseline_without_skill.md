# Baseline: Tasks 1 and 2 without the skill

Recorded at the end of the original session (2026-10-27 → 2026-10-29), before the skill existed. Use it as the "before" side of the comparison report.

**System:** RecipeCove (`Week_05_Designing/Tasks/data/RecipeCove.txt`)
**Outputs:** `Week_05_Designing/Task_1/notes.md`, `Week_05_Designing/Task_2/{ADR-001-recipecove-architecture.md, privacy-gdpr.md, notes.md}`

## Task 1: architecture discussion

| Metric | Value |
|---|---|
| User turns until the notes were final (excluding commit) | **11** |
| Turns spent on content | 6: read + summary, 3 proposals, "simple but seamless", grounding deep dive, "when is A wrong", B/C examples |
| Turns spent on assumption changes / decision rework | 3: hybrid decision → "what if 1 developer?" → switch decision to single Python monolith |
| Turns spent fixing or reorganizing the notes | 3: "move this question earlier" (×2, combined with content), "redo the notes so they make sense", "fix these things" (ambiguous reference, condensed painful parts) |
| Problems the user had to point out | Wrong data file path in the request (assistant recovered on its own). The full rewrite of the notes **condensed away the *why* of the painful parts and the deployment lines**. An **ambiguous cross-reference** ("see 9"). |
| Late assumption change | Team size changed from 3–5 to **1 developer** after the decision, which overturned the hybrid decision. |

## Task 2: ADR

| Metric | Value |
|---|---|
| User turns until the ADR was final (excluding commit and branch rename) | **9** |
| Things the user had to ask for that are now skill defaults | comparison table, no repetition, GDPR section, summary at the top, architecture diagram, shorter GDPR section |
| Errors introduced by the assistant | **1 caught by the user:** the rationale didn't match the table. **1 caught in the final review:** dangling `suggest(...)` reference. |
| ADR iterations | 9 (draft → table → dedupe → GDPR → summary → diagram → rationale fix → GDPR shortening → final review) |

## What to measure in the run with the skill
- User turns until Task 1 notes are final, and until the ADR is final.
- Whether the first draft already contained: assumptions with sensitivity, team-size question, painful parts with *why*, deployment lines, B/C examples, summary, numbered drivers + table, rationale matching the table, diagram, short GDPR section.
- Errors the user had to point out.
- Subjective: was the result as good or better, and did the discussion still show understanding? (The task requires understanding, not just speed.)
