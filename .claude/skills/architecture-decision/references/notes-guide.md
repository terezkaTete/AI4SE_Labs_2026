# Discussion notes guide

The notes are a graded deliverable ("record of your conversation"). They must make sense to a reader who wasn't in the conversation.

## Structure: organized by topic, plus a chronological log

Organize the notes by **topic in logical order**, not by the order questions were asked. Put a **chronological discussion log** at the end that points into the sections. This avoids the original session's problem of asking the user to "move this question earlier so it makes sense" several times.

### Phase 1 notes (`Task_1/notes.md`)
```
# <Week> – Task 1: Architecture discussion for <System>
Intro: what these notes are (not verbatim), link to the requirements file.
Contents (numbered list)
1. Requirements summary (actors, area → stories table, open questions)
2. Assumptions (A1… table; mark any the user revised: "Originally X. **Revised: Y**")
3. Candidate architectures (A, B, C – full detail incl. deployment + painful parts with why)
4. Comparison table
5+. One section per follow-up topic, in logical order (e.g. "simple but seamless",
    "when the choice is wrong + examples", "team size", "deep dive: <risky component>")
N-1. Final decision (architecture, key design decisions, trade-offs accepted, future extraction path)
N. Discussion log (chronological, numbered, each item → "section X")
```
Put a deep dive on a component after the final decision if it describes how that component works in the *chosen* design.

### Phase 2 notes (`Task_2/notes.md`)
```
# <Week> – Task 2: ADR for <System>
Input/Output files
## Iteration log
### Iteration N — <short title>
**Request:** (user's ask, short)
**What the assistant did / changed:** bullets, with the reasoning for each choice
**Problem found / Observation / Lesson:** when relevant (especially errors, and who found them)
```

## Rules

- **Update the notes in the same turn as every answer.**
- **Not verbatim:** record key points, decisions, trade-offs, reasons and open questions.
- **Honesty:** if a question was asked after the decision but is placed earlier for logical flow, the log keeps the real order. If the user later replaces a decision, keep the old one, marked "superseded", and point to where it now lives (e.g. "future extraction path").
- **Errors:** when the user reports a mistake, record what was wrong, why it happened and how it was verified as fixed. An earlier note that claimed something was verified should be corrected, not hidden.
- **Unambiguous references:** "section 8" vs "item 9", never a bare "see 9".
- **Before rewriting the whole file:** copy it to the scratchpad, rewrite, then diff and make sure no explanation was lost (only true duplicates may go).
- **Don't log meta-requests** the user excludes ("do not create notes out of this prompt").
