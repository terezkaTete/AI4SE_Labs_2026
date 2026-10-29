# ADR template (MADR-based, with the improvements from the original session)

File: `ADR-001-<system>-architecture.md`. Target length is about 1,500–1,800 words. Move long, architecture-independent material (e.g. a full GDPR analysis) to a linked companion file.

```markdown
# ADR-001: <Decision as an imperative title, e.g. "Build X as a single Python (Django) modular monolith">

- **Status:** Accepted | Proposed
- **Date:** YYYY-MM-DD
- **Deciders:** <who>
- **Source:** <phase 1 notes path (which section has the detailed analysis)>; <requirements path>

## Summary
5–6 one-line bullets: **Decision**, **Why**, **Main trade-off**, **<Risky component>**,
**Compliance** (incl. any requirement gap found), **Revisit**.
Conclusions only – this is the only intentional repetition in the ADR.

## Context and Problem Statement
What the system is + bullet list of story areas. "We need to choose the overall architecture."
The assumptions (the requirements don't state them) as bullets.

## Decision Drivers
Numbered 1..N, phrased as criteria (not restating facts from Context), e.g.:
1. Effort  2. Seamless UX  3. Data shape  4. <Risky component>  5. Privacy  6. Running cost  7. Evolvability

## Considered Options
Numbered list. Include the user's runner-up / earlier choice as its own option if there was one.

### Comparison against the decision drivers
| Decision driver | 1. … | 2. … | 3. … | 4. … |
Rows = the numbered drivers (same numbers). Cells = exactly ONE symbol ✅ / ⚠️ / ❌ + a short reason.
Put unique details from the phase 1 analysis in the cells (they replace a separate pros/cons section).
Last row: **Verdict** (Chosen / Rejected for now; future path / Rejected).
Legend line. No numeric scores or totals (drivers aren't equally weighted).

## Decision Outcome
**Chosen option: N — …**

**Rationale:** derived from the table, step by step:
- which options are eliminated by which ❌ (name the driver numbers),
- which options remain and exactly which drivers they differ on,
- why the chosen one wins that trade-off (driver weighting given the context; how its ⚠️ are mitigated).

**Architecture diagram:** Mermaid `flowchart LR` – user, app/services boxes (modules labelled with story numbers),
internal calls, data stores, external systems; label data-protection facts on edges/nodes
(e.g. "no user IDs", "EU region", "PII scrubbed"). One caption line explaining the arrows.

**Design in brief:** only what the diagram doesn't show – boundary rules (enforcement → see Confirmation),
frontend approach, risky-component design (e.g. grounding rules), isolation/safeguards, deployment.
Define any interface you'll refer to later (e.g. `suggest(messages)` → …).

### Privacy and <regulation>
One honest framing sentence ("architecture enables compliance, doesn't guarantee it") + link to companion file.
3–5 bullets – ONLY points that depend on this architecture (e.g. erasure/export simplicity from a single DB,
special-category data handling, what the risky component can see, processors/transfers) + any requirement gap.

### Consequences
**Good** (in addition to the ✅ in the table): only effects not already in the table.
**Bad:** concrete, including what the safeguards do NOT cover.

### Confirmation
Automatable checks: boundary linter in CI, evaluation set for the risky component, fallback test,
data-deletion test (no rows left), export-coverage test.

## More Information
**When to revisit:** triggers per alternative option; how the extraction would work (interface → HTTP contract).
```

## Companion file (if needed): `privacy-gdpr.md`
- Data inventory table: data | where | notes.
- Requirement → measure table: Art. 5, 6, 15/20, 17 (incl. backups and logs), 16, 25, 32, 28, 44+, 33.
- Residual risks.
