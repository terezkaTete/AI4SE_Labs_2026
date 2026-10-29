# Week 05 – Task 2 (rerun with skill): ADR for RecipeCove

**Input:** `../Task_1/notes.md` (decision in section 8), `Week_05_Designing/Tasks/data/RecipeCove.txt`
**Output:** `ADR-001-recipecove-architecture.md`, `privacy-gdpr.md` (companion)

## Iteration log

### Iteration 1: first draft
**Request:** "go with A and write the ADR".

**What the assistant did:**
- Wrote the ADR on the skill's MADR-based template. The first draft already includes everything that took several iterations in the original session: a Summary at the top, numbered decision drivers (1–7), a comparison table whose rows are those drivers (one symbol per cell), a rationale derived from the table, a Mermaid diagram (instead of a module bullet list), a short GDPR section with only architecture-dependent points, Confirmation checks and revisit triggers.
- **Four options, not three:** the hybrid (a monolith in another stack + a Python chatbot service) is included because it's the extraction path and was discussed in Task 1 notes section 7. It's the closest competitor, so the rationale has to explain why it loses.
- **Requirement gap found:** there are no stories for account deletion or data export. Proposed as stories 15 and 16.
- Generic GDPR material (inventory, article-by-article table) moved to `privacy-gdpr.md`, so the ADR section has 4 bullets.

**Review checklist** (run before replying):
- Rationale vs table, recounted cell by cell: option 2 has ❌ on 1, 3, 6. Option 3 has ❌ only on 7 and ⚠️ on 2, 4, 5, 6. Options 1 and 4 have no ❌. Options 1 and 4 differ on exactly drivers 1 (✅/⚠️), 6 (✅/⚠️) and 7 (⚠️/✅), and match on 2–5. ✔
- Every Summary bullet is backed by the body. ✔
- One symbol per cell, legend present. ✔
- `suggest_recipes(...)` and `search_recipes(...)` are both defined in "Design in brief" before they're referenced in More Information. ✔
- The diagram matches the modules and stories of Task 1 notes section 3A. Not render-tested (no Mermaid CLI). ✔
- Length: 1,864 words by `wc -w`, including the Mermaid code and table syntax. That's slightly above the 1,500–1,800 target, and no duplicated content was found to cut.

### Iteration 2: accepted
**Request:** "it's final".

**What the assistant did:** nothing changed. The first draft was accepted as is, so the ADR took 1 iteration (the original session took 9).

### Iteration 3: final check of Task 3
**Request:** check the whole of Task 3 and fix all mistakes.

**What the assistant changed:**
- The Summary's "Why" overclaimed: option 4 also has the Python LLM ecosystem and joins. It now says what the table shows: option 1 is the only one with ✅ on drivers 1, 3, 4 and 5 (recounted: option 2 ❌ on 1 and 3, option 3 ⚠️ on 4 and 5, option 4 ⚠️ on 1).
- Fixed the same overclaim in Task 1 notes section 4.
- Quoted the label of the user node in the Mermaid diagram, to be safe with `/` and `:` inside the label. Still not render-tested.

### Iteration 4: last check of Task 3
**Request:** check everything one last time.

**What the assistant changed:**
- Rationale for option 3: cold starts were listed as part of the driver 4 ⚠️, but the table puts them under driver 2. Now worded to match the table.
- Privacy section: "the LLM provider is the only processor that sees user content" ignored the PaaS and the DB host, which `privacy-gdpr.md` lists as processors. Now says "apart from the hosting providers".
- Revisit section: extracting the chatbot from a Python monolith isn't exactly option 4 (whose main app is in another stack). Now says "a split like option 4, but with the main app staying in Python".
- These rewordings raised the ADR length from 1,864 to 1,890 words (`wc -w`); the report now gives the new number.
