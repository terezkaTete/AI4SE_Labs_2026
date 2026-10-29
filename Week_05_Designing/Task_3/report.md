# Task 3 report: architecture tasks with and without the `architecture-decision` skill

**System:** RecipeCove (`Tasks/data/RecipeCove.txt`), the same in both runs.
**Without the skill:** `Task_1/notes.md`, `Task_2/*`. Metrics in `Task_3/baseline_without_skill.md`, recorded from the session transcript.
**With the skill:** `Task_3/run_with_skill/Task_1/notes.md`, `Task_3/run_with_skill/Task_2/*`. Skill: `.claude/skills/architecture-decision/` (at the repository root).

## 1. What the skill changed

Each problem from the first run became a rule in the skill. In the rerun, the user didn't have to fix any of them.

- **The decision was overturned late.** In the first run, team size was assumed (3–5 developers), and the user only asked what changes with a single developer after the hybrid decision, which forced the decision to be redone. **The skill** asks team size first, together with the other deciding assumptions, in one question set. **In the rerun**, team size was settled before any proposal, and the first recommendation stood.
- **Follow-up questions had to be asked one by one.** The "simple but seamless" question, the chatbot deep dive, whether A is ever wrong, and examples for B and C were four separate requests. **The skill** answers them proactively. **In the rerun**, they were all in the first answer.
- **The notes needed reorganizing and lost content.** The user asked twice to move questions earlier, and the full rewrite condensed away the *why* of the painful parts and the deployment lines. **The skill** organizes the notes by topic from the start (with a chronological log at the end), requires a *why* for every painful part, and forbids condensing reasoning when restructuring. **In the rerun**, the user didn't have to fix or reorganize the notes.
- **The ADR was built up by request.** The comparison table, deduplication, the GDPR section, the summary, the diagram and then a shorter GDPR section each took an iteration. **The skill's** ADR template includes all of them. **In the rerun**, the user accepted the first draft as is.
- **Errors slipped in.** The rationale contradicted the table, a function reference was left dangling, and a cross-reference was ambiguous ("see 9"). **The skill** runs a review checklist after every edit: recount claims about the table cell by cell, check references, number sections. **In the rerun**, the user had no errors to point out. One small error still slipped in: the ADR Summary (and the matching sentence in the notes) overclaimed why option 1 wins. The assistant found and fixed it in the final check of Task 3 (Task 2 notes, iteration 3).

**Overall:** the user's role changed from correcting and restructuring to answering one set of assumption questions, choosing the architecture and approving the ADR.

## 2. What the first drafts already contained

| Expected content (from the baseline) | Without the skill | With the skill, first draft |
|---|---|---|
| Assumptions with sensitivity | Assumptions, but no sensitivity | ✅ A1–A9; the recommendation is sensitive to A1 and A3 |
| Team-size question | Asked by the user late (turn 8) | ✅ asked before the proposals |
| Painful parts with the *why* | First had them; the rewrite lost them and they had to be restored | ✅ each with a one-sentence *why* |
| Deployment per architecture | Lost in the rewrite, then restored | ✅ |
| "Simple but seamless", when A is wrong, B/C examples, chatbot grounding | 4 separate user questions | ✅ all covered in the first answer (notes sections 5, 6 and 9) |
| ADR summary, numbered drivers, comparison table, diagram, short GDPR section | Each requested separately | ✅ all in the first draft |
| Rationale matching the table | ❌ mismatch caught by the user | ✅ recounted cell by cell before replying (Task 2 notes) |

## 3. Quality

- **The results were as good, not better.** Both runs ended with the same decision: a single Python (Django) modular monolith, with the chatbot as the first part to extract. Both ADRs compare the same four kinds of option (monolith, hybrid monolith + Python chatbot service, microservices, serverless/BaaS) and find the same requirement gap (no "delete my account" story); the rerun also lists data export as missing. The main design difference is chat history: the original stores none, the rerun keeps it for 30 days.
- **Weaker points of the rerun:** the ADR is slightly above its target length (1,890 words against 1,500–1,800). The Mermaid diagram hasn't been checked in a renderer, in either run.
- **Understanding:** the first run's value was the exploration. The user's own questions (whether A is ever the wrong choice, and what changes with only one developer) made the trade-offs visible. In the rerun, the same content is in the notes, but it was produced proactively, so the user asked almost nothing. The notes still show the reasoning (every pain point has its *why*, the rationale is derived step by step). Even so, a fast run shows less of the user's own understanding than the slow one. *User's view:* "The skill made the second run faster because everything was already set up. I already knew how to answer the model's questions, so they didn't take any extra time."

## 4. Caveats on the comparison

- **Same system, and a skill learned from it.** The skill was distilled from the RecipeCove session, so some of its defaults (a Python monolith for a solo developer with an LLM, LLM-grounding rules, the example systems) fit this system especially well. The rerun therefore overstates the gain. A fairer test would be another system from `Tasks/data/` (e.g. EventTicket or Teamify).
- **The user already knew the answers.** Knowing from the first run that team size matters, the user answered "1 developer" right away and accepted the recommendation. A new user would probably ask more follow-ups.
- **The evidence is the notes.** The without-skill transcript was used to record `baseline_without_skill.md` and was then deleted. The with-skill run was never exported. Both runs are documented by their notes.

## 5. Conclusion

The skill removed the rework, not the content. Every improvement the user had to request in the first session (up-front team size, *why* for every pain point, proactive follow-ups, the ADR structure, the rationale-vs-table check) happened by default. That cut the work from 20 user turns to 5 (counted the same way as the baseline, including the opening request), with no errors for the user to correct. The remaining risk is that a fast, mostly assistant-driven run shows less of the user's own understanding. The skill keeps the reasoning in the notes, but the user still has to read it.
