# Review checklist: run it after every edit to the ADR or notes

Each item comes from a real defect in the original session.

## ADR
- [ ] **Rationale vs table, cell by cell.** For every sentence that counts or compares cells ("only option without ❌", "single ⚠️", "differs only on driver N", "matches on every other driver"), recount from the table *as it is now*. *(Original bug: after cells were edited, "option 1 is the only option without ❌" was false because option 2 had none either.)*
- [ ] **Summary vs body:** every Summary bullet is still true after the edit.
- [ ] **One symbol per table cell** (no "✅ … ⚠️ …" mixes); the legend is present.
- [ ] **One home per fact:** search for key phrases (e.g. "one codebase", "transaction", "low cost") and make sure each appears once outside the Summary. Delete a section that duplicates the table (e.g. Pros and Cons) after moving its unique details into the cells.
- [ ] **No dangling references:** every function, endpoint, section or file mentioned is still defined or present. *(Original bug: `suggest(...)` was referenced after its definition had been deleted.)*
- [ ] **Compliance section length:** only architecture-dependent points; generic obligations go to the companion file.
- [ ] **Diagram:** it matches the module list and stories; say honestly if rendering wasn't tested (no Mermaid CLI).
- [ ] **Length:** about 1,500–1,800 words; anything longer usually means duplication or misplaced detail.

## Notes
- [ ] Updated this turn.
- [ ] Cross-references are unambiguous ("section N" / "item N") and still valid after renumbering.
- [ ] Nothing condensed away when restructuring (diff against the scratchpad backup).
- [ ] Every painful part has its *why* and every architecture has a deployment line.
- [ ] The log keeps the real chronological order; superseded decisions are marked, not deleted.
- [ ] Claims about the edit (e.g. "shorter", "verified") are true. Check word counts or diffs before saying so.
