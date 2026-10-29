# Week 05 – Task 2: Architecture Decision Record for RecipeCove

Running notes from the discussion with the coding assistant about creating and refining the ADR. Not a verbatim transcript; key requests, changes and reasoning.

- **Input:** Task 1 discussion (`Week_05_Designing/Task_1/notes.md`)
- **Output:** `Week_05_Designing/Task_2/ADR-001-recipecove-architecture.md`

---

## Iteration log

### Iteration 1 — first draft
**Request:** create an ADR based on the Task 1 discussion.

**What the assistant did:**
- Chose the **MADR** template (Markdown Architectural Decision Records). It is a common, well-structured format whose sections map directly onto what Task 1 produced:
  - Context and Problem Statement
  - Decision Drivers
  - Considered Options
  - Decision Outcome, with Consequences and Confirmation
  - Pros and Cons of the Options
  - More Information
- One ADR records the single, top-level decision: a **single Python/Django modular monolith**.
- **Considered options:**
  1. the chosen monolith,
  2. the monolith plus a separate chatbot service (the user's earlier choice, rejected for a solo developer),
  3. microservices,
  4. serverless.
- **Assumptions** from Task 1 are folded into the Context section, because the requirements didn't state them.
- **Chatbot grounding** is summarized in the design section, not repeated in full.
- **"When to revisit"** (More Information) turns the Task 1 extraction path and the "when A is not right" discussion into explicit triggers.
- **Deliberately left out of the first draft**, for the user to decide on:
  - an overview comparison table,
  - an architecture diagram,
  - a user-story → module mapping.
  
  MADR doesn't require them, and the task asks the user to judge whether they are needed.

**Open points for review:**
- Is the ADR the right length? It is currently about 2 pages.
- Should it have a comparison table and/or a diagram?
- Should the detailed design (modules, grounding) stay, or move to a separate design doc, with the ADR keeping only the decision?

### Iteration 2 — comparison table
**Request:** add a comparison table.

**What the assistant did:**
- Added **"Comparison against the decision drivers"** at the end of *Considered Options*, right before *Decision Outcome*. The reader sees the options side by side before reading the verdict.
- **Rows are the ADR's own decision drivers**, not generic criteria. Each driver can be traced to how every option performs, and the table justifies the decision instead of just decorating it.
- **Columns:** the 4 considered options. **Cells:** ✅ / ⚠️ / ❌ plus a short reason, so the ratings aren't unexplained symbols. A final **Verdict** row: chosen / rejected / future path.
- **No numeric scores or totals.** The drivers don't carry equal weight (for a solo developer, effort dominates), so summing them would be misleading.

**Observation:** option 2 scores as well as or better than option 1 on several rows (process isolation). The table makes it visible that the deciding factor is the *solo developer effort* row. That trade-off is honest and visible, not hidden.

### Iteration 3 — remove repetition
**Request:** make sure nothing in the ADR repeats.

**Problem found:** after the table was added, the same facts appeared up to four times:
- the table,
- "Why this option",
- Consequences → Good,
- the "Pros and Cons of the Options" section.

For example, "one codebase, one deploy", "SQL joins / transactions" and "low cost" were each stated 3–4 times.

**What the assistant changed:**
- **Removed the "Pros and Cons of the Options" section.** The table now holds the comparison on its own. The few unique details from that section were folded into table cells so nothing was lost: outbox / eventual search consistency, JWT logout, one security-rule mistake exposing all data, two CI pipelines. Full detail stays in Task 1 notes, section 3 (linked in the header).
- **"Why this option" → "Rationale".** Instead of restating the ✅ cells, it now reads the table: option 1 is the only option without a ❌, option 2 loses *only* on driver 1, and options 3 and 4 fail specific drivers.
- **Consequences → Good** now lists only effects *not* in the table: simple local dev, Django admin as a free admin UI, django-allauth handling OIDC.
- **Consequences → Bad:** merged "scales as one unit" and "can't deploy the chatbot separately". Clarified that the in-process safeguards cover the LLM failing, not the app itself, so it doesn't repeat the table's ⚠️.
- **Design → Module boundaries** no longer repeats the `import-linter` detail. It points to Confirmation.
- **Decision drivers are numbered,** and the table rows use the same numbers, so the rationale can reference them ("driver 1").
- **Corrected a rating:** option 1's chatbot cell changed from ✅ + ⚠️ to a plain **⚠️**, and option 4's effort and cost cells from ✅ + ⚠️ to **⚠️**. Mixed symbols in one cell were ambiguous, and the rationale ("only option without ❌, one ⚠️") must match the table exactly.

**Result:** about the same length (~1,250 words), because the table absorbed the unique details, but each fact now has one home: Context = facts/assumptions, Drivers = criteria, Table = evaluation, Rationale = conclusion, Design = how, Consequences = effects beyond the table, Confirmation = verification, More Information = revisit triggers.

### Iteration 4 — show how the design satisfies GDPR
**Request:** show how this (the architecture) satisfies GDPR.

**Assistant's framing (stated in the ADR):** an architecture can't make a system GDPR-compliant by itself. Compliance also needs organizational measures (privacy policy, records of processing, DPAs). The ADR shows what the architecture provides: the *technical capability* to comply, kept cheap.

**What was added** (new subsection *Privacy and GDPR* in *Decision Outcome*, after the design):
- **Personal-data inventory:** what is stored and in which module. Google `sub` / email / name / avatar, favorites, calendars, chat messages, session cookie / logs / Sentry.
- **Key finding: chat messages can contain special-category data** (Art. 9). Diet preferences can reveal health ("diabetic") or religion ("halal", "kosher"). **Decision:** conversations are per-session only, not linked to the account and not stored, so this data stays out of the DB.
- **GDPR requirement → design measure table:**
  - minimization (Art. 5)
  - lawful basis (Art. 6): no tracking, so only a strictly-necessary cookie and no consent banner
  - access and portability (Art. 15/20): each module's `services.py` exposes `export_user_data`
  - erasure (Art. 17): one-transaction cascade, and simple because there is one DB
  - erasure in backups and logs: fixed retention
  - rectification (Art. 16)
  - privacy by design (Art. 25): the chatbot never sees user data
  - security (Art. 32)
  - processors (Art. 28): DPAs, EU hosting, no identifiers sent to the LLM
  - international transfers (Art. 44+): DPF / SCCs for US providers
  - breach notification (Art. 33)
- **Gap in the requirements found:** there is **no "delete my account" user story**. Story 10 only deletes the calendar. The ADR says this must be added.
- **Residual risks:** users can type personal data into the chat, which then reaches the LLM provider. There is also no dedicated privacy role with one developer, so data actions must be self-service and automated.
- **Confirmation:** two new tests. Account deletion leaves no rows referencing the user, and the export covers every model with a user foreign key.

**Note:** this ties back to the comparison table (driver 5). The single database is what turns erasure and export into one transaction and one query, whereas microservices would need a saga.

### Iteration 5 — summary at the top
**Request:** add a summary of the file to the top.

**What the assistant did:**
- Added a **Summary** section directly under the metadata. It has six one-line bullets: decision, why, main trade-off, chatbot, GDPR and revisit trigger. A reader gets the whole ADR in about 30 seconds and can stop there.
- **Kept it deliberately short.** After Iteration 3 (no repetition), a summary is the one *intentional* repetition. It restates only conclusions, not the details or reasons that live in the table and sections below.
- Covers the two things added later in the process that a quick reader would otherwise miss: the **GDPR conclusion** and the **missing "delete my account" story**.

### Iteration 6 — architecture diagram
**Request:** add an architecture diagram.

**What the assistant did:**
- Added a **Mermaid flowchart** at the start of *Design in brief* (Decision Outcome). Mermaid is text in the Markdown file, so it is versioned and diffable alongside the ADR, and GitHub renders it natively. That suits an ADR better than an exported image, which goes stale.
- **What the diagram shows:**
  - The browser talking to one Django app box (ASGI, one container) over HTTPS with HTMX and SSE.
  - The **six modules** inside the box, each labelled with its **user stories**. This doubles as the user-story → module mapping offered in Iteration 1.
  - **Internal calls** go through `services.py`: the chatbot → `search_recipes()` → catalog, and favorites, calendars and importer → catalog.
  - **External systems:** Google Identity (login), the LLM API (labelled "chat text only, no user IDs"), the external recipe API, Sentry (personal data scrubbed), and managed Postgres (EU region, encrypted, backups). The GDPR measures are visible in the picture too.
- **Avoided repetition:** the diagram replaced the bullet list of modules in *Design in brief*, since the diagram now carries that information (module names, responsibilities, django-allauth, full-text + trigram search).
- Added one caption line: arrows inside the app are `services.py` calls, and nothing outside the box reaches the database.

**Note:** Mermaid renders on GitHub/GitLab. In VS Code the built-in Markdown preview needs a Mermaid extension (e.g. "Markdown Preview Mermaid Support").

### Iteration 7 — fix: rationale didn't match the table
**Reported by the user:** the rationale doesn't match the table.

**Errors confirmed by checking the rationale against the table, cell by cell:**
1. *"Option 1 is the only option without a ❌"* was **false**. Option 2 has no ❌ either (✅ ×5, ⚠️ on drivers 1 and 6).
2. *"Option 2 matches option 1 on every other driver … rejected only because of driver 1"* was **false**. Option 2 also differs on driver 6 (running cost: ✅ vs ⚠️).

These errors came in during Iteration 3, when the mixed ✅/⚠️ cells were cleaned up and the rationale was rewritten. The iteration-3 note claimed the rationale matched the table exactly, but that was not verified against the final table.

**Fix:** the rationale now follows the table step by step:
- Options 3 and 4 are ruled out by their ❌, naming the drivers (3: drivers 1, 5, 6; 4: drivers 3, 7).
- Options 1 and 2 are the only ones without a ❌, and they differ on exactly three drivers: option 1 is better on 1 (effort) and 6 (cost), option 2 on 4 (chatbot isolation).
- Option 1 wins because effort dominates for one developer, and its only ⚠️ is mitigated by the in-process safeguards.

**Checked:** every claim in the rationale and Summary against the table. The Summary's wording (effort, privacy, relational data, lock-in for options 3 and 4) is consistent.

**Lesson:** whenever the table changes, re-check every statement that counts or compares table cells.

### Iteration 8 — shorten the GDPR section
**User's question:** isn't the GDPR section too long now?

**Assistant's assessment:** yes. With a data-inventory table, an 11-row requirement table and residual risks, it was the longest part of the ADR and pushed the actual decision into the background. Most rows (lawful basis, rectification, HTTPS, breach notification, cookie banner) apply to *any* architecture, so they aren't consequences of this decision and don't belong in an ADR.

**What the assistant changed:**
- **The ADR keeps only the GDPR points that depend on the architecture** (5 bullets):
  - erasure and export are simple thanks to the single DB (vs. a saga in microservices),
  - chat messages are special-category data, so they aren't stored,
  - the chatbot never sees user data,
  - processors and international transfers,
  - the missing "delete my account" story.
- **Nothing was lost:** the full previous section (data inventory, requirement → measure table, residual risks) moved unchanged into a companion file, **`privacy-gdpr.md`**, linked from the ADR.
- The Summary and the GDPR tests in Confirmation stayed. They are still consistent with the shortened section.

### Iteration 9 — final review ("is it ready now?")
**The assistant re-read the whole ADR for consistency:**
- **Summary vs. sections:** consistent.
- **Rationale vs. table:** consistent (re-checked after the Iteration 7 fix).
- **Each fact has one home:** yes. The only intentional repetition is the Summary.
- **GDPR section vs. companion file and Confirmation tests:** consistent.

**Fixed:** a dangling reference. *More Information* mentioned `suggest(...)`, but that interface was no longer defined anywhere in the ADR (its description was removed with the module list in Iteration 6). It now says what it is: the `suggestions` module's public function, which returns streamed text + recipe IDs.

**Known, not changed:**
- The Mermaid diagram hasn't been render-tested (no Mermaid CLI available locally). It should render on GitHub; it needs a VS Code extension for preview.
- In the table, option 3's privacy cell also mentions "JWT logout not instant", which is a security point rather than GDPR deletion. It is minor and left as is.

**Verdict:** the ADR is ready to hand in.
