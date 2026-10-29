---
name: architecture-decision
description: Propose and compare software architectures from a requirements document, choose one with the user, and write an Architecture Decision Record (ADR). Use when the user asks for architecture proposals, wants to discuss or compare architectures (monolith, microservices, serverless, ...), asks for an ADR, or points at a requirements/user-story file (e.g. a file in a `data/` folder) and wants a design. Keeps running discussion notes throughout.
---

# Architecture proposals → decision → ADR

This skill runs a guided architecture discussion in two phases and keeps notes the whole time:

1. **Proposals** (ends with a decision): read requirements → assumptions → 3 architectures → comparison → follow-up discussion → decision.
2. **ADR** (ends with a reviewed ADR): write the ADR from the phase 1 notes → iterate with the user → final consistency review.

The user may start at phase 2 if phase 1 notes already exist. Read them first.

It was distilled from a real session in which the user had to ask for the same improvements again and again. Those improvements are now the **defaults** below, so do them without being asked.

## Before anything else

1. **Find the requirements file.** If the given path doesn't exist, search for it (`find . -iname '*name*'`), say where it actually is, and continue. Don't stop on a wrong path.
2. **Decide where outputs go.** Default: `<week folder>/Task_1/notes.md` for phase 1, and `<week folder>/Task_2/{notes.md, ADR-001-<system>-architecture.md}` for phase 2. If the user names paths, use theirs. **Never overwrite existing notes or ADRs.** If a target file already exists (e.g. from an earlier run), ask the user, or write to a new folder such as `<week folder>/Task_3/run_with_skill/`.
3. **Create the notes file immediately**, before discussing anything. Follow [references/notes-guide.md](references/notes-guide.md). Update it **in the same turn** as every answer. Never batch updates for later.

## Phase 1 — Proposals

Follow [references/proposals-guide.md](references/proposals-guide.md). In short:

1. **Summarize the requirements**: actors, a table of functional areas mapped to story numbers, and the ambiguities found.
2. **Settle the assumptions that decide the architecture, up front, in one go.** The most important one is **team size and skills**. In the original session, changing it from "3–5 devs" to "1 dev" late in the discussion overturned the decision and forced rework. Ask the user with one `AskUserQuestion` call (at most 4 questions: team size, data source, the riskiest special component such as AI/real-time, and scale + compliance combined). If they say "just assume", make the assumptions, number them (A1, A2, …), put them in a table, and **state which ones the recommendation is sensitive to**.
3. **Propose 3 genuinely different architectures** (default: modular monolith, microservices, serverless/BaaS, unless the requirements clearly call for others, e.g. event-driven or offline-first). For each one, give: idea, ASCII diagram, mapping of stories to modules, data model sketch (for the first), pros, cons, **deployment**, and **painful low-level parts, each with a one-sentence explanation of *why* it is painful**. A bare list of pain points doesn't show understanding; the explanation does.
4. **Comparison table** (criteria × architectures) + a recommendation + the likely evolution path (e.g. "monolith now, extract component X later").
5. **Answer follow-ups proactively.** The original user asked all of these, so cover them in the first answer or offer them as next steps:
   - Which option fits "simple but works seamlessly"? What does "seamless" mean concretely?
   - When is the recommended option **not** right? Give **concrete example systems** where each alternative is the clear choice, and say why this system is neither.
   - How does the recommendation change with team size (especially a **solo developer**)?
   - A deep dive into the riskiest component (e.g. LLM grounding, real-time sync, payments).
6. **Record the decision** in the notes, with what was traded away and the future extraction path.

## Phase 2 — ADR

Use the structure in [references/adr-template.md](references/adr-template.md). The **first draft must already include** everything the original user had to ask for over several iterations:
- a **Summary** at the top,
- **numbered decision drivers**,
- a **comparison table whose rows are those drivers**,
- a **Rationale derived from the table**,
- a **Mermaid architecture diagram** (it replaces the module bullet list),
- a **short compliance/privacy section** containing only points that depend on the architecture (details in a companion file),
- **Confirmation** checks,
- **revisit triggers**.

Then ask the user what to change. After **every** edit, run the checklist in [references/review-checklist.md](references/review-checklist.md) before replying. Above all:
- **Every claim that counts or compares table cells ("the only option without ❌", "differs only on driver 1") must be re-verified cell by cell.** This was a real bug in the original session.
- **Each fact has exactly one home.** The Summary is the only intentional repetition.
- **No dangling references** (functions, sections, files that no longer exist after an edit).

## Rules that apply throughout

- **Never condense away reasoning when restructuring a document.** If the user asks to "redo" or "reorganize" notes, keep every explanation. Back up the file to the scratchpad first and diff after.
- **Number sections, and refer to them as "section N" or "item N" unambiguously.** Re-check all cross-references after renumbering.
- **Don't record meta-requests in the notes** when the user says not to (e.g. "fix these things, do not create notes out of this prompt").
- **Be honest about limits:** e.g. "an architecture doesn't make a system GDPR-compliant by itself", "the Mermaid diagram hasn't been render-tested".
- **Committing:** only when asked. If on the default branch, create a descriptively named branch first (e.g. `weekNN-<topic>`), and commit only the task's files.
