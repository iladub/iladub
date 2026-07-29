# Residue register

Deferred items from the ET(K)L loops, in one tracked place. Each row records what the residue is,
where it was **measured** (never assumed), why it was deferred, and what would close it.

**This register is canonical.** Loops append rows here; a loop that closes a residue deletes its row
in the same change. Specs may describe a residue in prose, but the list of open residues lives here.

Started 2026-07-29 (Loop D), collecting items previously scattered across four specs and the SDD
ledger.

| # | Residue | Measured | Why deferred | What would close it |
| --- | --- | --- | --- | --- |
| R1 | **Column 13 blob** — `Date Loading Completed\|Commodity\|Total` merged into one column | No rule drawn there; no gutter; `'CompletedCommodityTotal'` (x 716.3–818.4) is one extracted cell, as is the body's `'(blank)Chickpeas   2 0,000'` | Not recoverable from rules or whitespace at all | Character-level re-segmentation inside an extracted blob; same mechanism as R2 |
| R2 | **Split-number cells** — `2 0,000` should be `20,000` | Loop B; visible in GrainCorp body rows | Data-side extraction, separate concern from structure | Intra-blob character-spacing evidence |
| R3 | **Nested-subset vote** in `recover_leaf_grid` | Loop D spec §2 Finding 3: the correct 15-column grid IS found by the longest suffix, then outvoted 35-to-16 by shorter suffixes that are nested subsets of it, not independent witnesses | Changes grid derivation for every table in the suite | A statistic that respects nesting, plus a fixture battery. **Ruled documents now route around this; the first ruleless document with a narrow gutter will hit it** |
| R4 | **Row-grouping + interleaved subtotals** — `Mackay Total`, `Jul 26 Total` | Loops B/C | Its own loop | First-class row-group structure |
| R5 | **Proposal inputs not recorded** in `emit_row_role_promotion` | Loop C.1 final review | Not a regression; best done alongside a live run | Record the context the proposer was shown, so an auditor can reproduce the proposal |
| R6 | **Centre-only merge candidate** for wide parents — a parent spanning cols 1–3 gets one candidate | Loop C.1 final review | Pre-existing in shape; needs a live run to judge | Report every covered column's candidate |
| R7 | **Live BAML path unreachable** — `BamlRowRoleProposer` is never constructed in `src/` | Loop C.1 final review | No live run attempted yet | Wire it behind `baml_proposer_available()` |
| R8 | **`ProposeHeaderSpan` missing** from `baml_src/` — B1.3's live path cannot run | Loop C | Pre-existing, unrelated to the loops since | Author the function |
| R9 | **Conservation shape unreachable** through the row-role driver | Loop C final review: no reachable role vector loses text | Sound as a regression backstop; covered directly by `test_conservation_shape.py` | Either a reading that genuinely loses text, or accept it as a backstop and say so |
| R10 | **`detect_bands` cuts one line too high** — the report date lands inside the table band | Loop C.1 §2 Finding 4: date x 398.3 ≈ page title x 399.0, matching no column | Segmentation is shared by every path; large blast radius | Title-block exclusion at segmentation |
| R11 | **Mixed header rows** cannot be expressed by a per-row role | Loop C §3.2 | No measured document exhibits one | Per-cell roles, when evidence demands it |
| R12 | **Split-table recurrence** — a solitary parent over a repeated layout | Loop C.1 §6.2; `stem.pdf` is a single page with no repeated block | No target document | Cross-block layout matching |
