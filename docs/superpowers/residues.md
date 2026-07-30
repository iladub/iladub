# Residue register

Deferred items from the ET(K)L loops, in one tracked place. Each row records what the residue is,
where it was **measured** (never assumed), why it was deferred, and what would close it.

**This register is canonical.** Loops append rows here; a loop that closes a residue deletes its row
in the same change. Specs may describe a residue in prose, but the list of open residues lives here.

Started 2026-07-29 (Loop D), collecting items previously scattered across four specs and the SDD
ledger.

| # | Residue | Measured | Why deferred | What would close it |
| --- | --- | --- | --- | --- |
| R1 | **Column 13 blob** — `Date Loading Completed\|Commodity\|Total` merged into one column | No rule drawn there; no gutter; `'CompletedCommodityTotal'` (x 716.3–818.4) is one extracted cell, as is the body's `'(blank)Chickpeas   2 0,000'` | Not recoverable from rules or whitespace at all | Character-level re-segmentation inside an extracted blob; same mechanism as R2 **Attempt 1 at R13 abandoned 2026-07-30 — R1 stays open with it.** |
| ~~R2~~ | **CLOSED for the ruled path (Loop F, 2026-07-29)** — padding space glyphs no longer split a contiguous number | Root cause was: source chars CONTIGUOUS (gaps −0.08…−0.03); padding space glyphs OVERLAPPING the digit run were joined in by `rule_aware_lines` | Fixed by a two-presence-test rule (a space glyph exists AND the glyphs it separates are apart). Two magnitude-based hypotheses were measured and REFUTED first — see the Loop F spec §2 | **Still open for the UNRULED path as R16** |
| R3 | **Nested-subset vote** in `recover_leaf_grid` | Loop D spec §2 Finding 3: the correct 15-column grid IS found by the longest suffix, then outvoted 35-to-16 by shorter suffixes that are nested subsets of it, not independent witnesses | Changes grid derivation for every table in the suite | A statistic that respects nesting, plus a fixture battery. **Ruled documents now route around this; the first ruleless document with a narrow gutter will hit it** |
| R4 | **Row-grouping + interleaved subtotals** — `Mackay Total`, `Jul 26 Total` | Measured 2026-07-29: a TWO-level hierarchy — Month (`c1`) suppressed after its first row, Port (`c2`) repeated, subtotal labels in the column of the key they aggregate. Today every subtotal compiles as an ordinary data record (a §7 violation: the source asserts no vessel called `Mackay Total`), and the shipped `subtotals_row_group_pdf` / `totals_table_pdf` fixtures do the same at score 1.0 | **BLOCKED BY R1+R2.** The only sound detector is arithmetic (a subtotal's measure == the sum of its siblings — decidable exact arithmetic, language-independent); a `" Total"` suffix test would be English-specific. The arithmetic reconciles (20,000+20,000+23,000+55,000 = 118,000) but there is no parseable measure to run it on | **New evidence (Loop F):** `logical_rows` also FUSES each subtotal line into the preceding data row's cell (measured pre-existing: `'(blank)Chickpeas 20,000 (blank)Sorghum 20,000 20,000'` is one cell), so R4 must separate the rows before it can sum them. Close R13, then: sum siblings, compare, emit `tab:AggregationRow`. The vocabulary already exists (used only in `denormalization.py`, never in the extraction path) **Still blocked on BOTH counts** — R13 attempt 1 was abandoned, so there is still no clean numeric `Total` column. |
| R5 | **Proposal inputs not recorded** in `emit_row_role_promotion` | Loop C.1 final review | Not a regression; best done alongside a live run | Record the context the proposer was shown, so an auditor can reproduce the proposal |
| R6 | **Centre-only merge candidate** for wide parents — a parent spanning cols 1–3 gets one candidate | Loop C.1 final review | Pre-existing in shape; needs a live run to judge | Report every covered column's candidate |
| R7 | **Live BAML path unreachable** — `BamlRowRoleProposer` is never constructed in `src/` | Loop C.1 final review | No live run attempted yet | Wire it behind `baml_proposer_available()` |
| R8 | **`ProposeHeaderSpan` missing** from `baml_src/` — B1.3's live path cannot run | Loop C | Pre-existing, unrelated to the loops since | Author the function |
| R9 | **Conservation shape unreachable** through the row-role driver | Loop C final review: no reachable role vector loses text | Sound as a regression backstop; covered directly by `test_conservation_shape.py` | Either a reading that genuinely loses text, or accept it as a backstop and say so |
| R10 | **`detect_bands` cuts one line too high** — the report date lands inside the table band | Loop C.1 §2 Finding 4: date x 398.3 ≈ page title x 399.0, matching no column | Segmentation is shared by every path; large blast radius | Title-block exclusion at segmentation |
| R11 | **Mixed header rows** cannot be expressed by a per-row role | Loop C §3.2 | No measured document exhibits one | Per-cell roles, when evidence demands it |
| R12 | **Split-table recurrence** — a solitary parent over a repeated layout | Loop C.1 §6.2; `stem.pdf` is a single page with no repeated block | No target document | Cross-block layout matching |
| R13 | **Rules coarser than the columns** are accepted and merge real columns — GrainCorp's `Date Loading Completed\|Commodity\|Total` compiles as one column at confidence 1.0. **R1 is the same defect.** | **ATTEMPT 1 ABANDONED 2026-07-30** (branch `iladub-rule-column-refinement`, unmerged, kept for reference). Approach: inside each rule interval, treat a persistent blank run with ink on both sides as an extra boundary. It DID reach the right answer on the target — 15→17 columns, all 17 labels correct, cells 447→509, score 0.947→0.9496 | **KILLED BY A COUNTER-EXAMPLE.** An ordinary monospaced ruled table whose values carry a COLUMN-ALIGNED internal space (`AB CDEFGH`, `12 500`, `01 JAN 2026` — GrainCorp's own genre) forms a persistent blank run with ink on both sides, so the rule manufactures a phantom column no header covers → `tab:CoverageShape` violation → **`compile_tables` RAISES**. Verified A/B on a synthetic 3-column PDF: `main` gives RECORD_TABLE/18 cells/score 1.0; the branch crashes. A 9pt Courier space is ~5 bins, so ONE aligned space suffices | Attempt 2 must survive that counter-example WITHOUT a width threshold (that is the tuned constant §8 forbids). Two honest directions: derive the required gutter width from the ink's OWN inter-glyph advance within the interval; or route the ambiguity to NEURAL propose→oracle instead of asserting at confidence 1.0 |
| R14 | **The collapse can delete an author-drawn boundary** when only a skipped line carried that column's ink | Loop D final review, pinned by `test_skipped_line_ink_loses_an_author_drawn_boundary_KNOWN_LOSS`: rule at x=90.0 discarded, two real columns merged, reported at confidence 1.0 with no escalation | Depends on R10 (a caption left in the band is what forces the suffix skip) | Close R10, or make the occupancy test span the whole band rather than the accepted suffix |
| R15 | **NEURAL residual: a wide label over blank/unclaimed columns** where the covering partition genuinely cannot decide | Loop B §7.4 / Loop C — still escalates honestly `MERGE_AMBIGUOUS` | No measured document needs it | The `span_proposer` seam, if a real document ever requires it |
| R16 | **The UNRULED path keeps the split-number defect** — pdfplumber's `extract_words` splits `2` from `0,000` on its own | Loop F: only `rule_aware_lines` (the ruled path) was fixed | Closing it means owning word segmentation for every document, not just ruled ones | Apply the same two-presence-test rule to a char-derived word segmenter for unruled bands |

---

## R13 attempt 1 — what was learned (2026-07-30)

Branch `iladub-rule-column-refinement`, **abandoned, not merged, kept locally**. `main` is unaffected.
Recorded so attempt 2 does not re-derive any of it.

**What was right and is worth reusing**

- **The target is real and the answer is known.** GrainCorp's interval `[715.2, 829.92]` carries two blank
  runs, `744.2–763.2` and `789.2–808.2`, 19 bins each over 54 inked rows. Splitting at their centres
  (753.7, 798.7) gives **17** columns — the real header's count — with all 17 labels correct.
- **The architecture was sound and reviewer-verified.** A derived `Band.column_xs` field, kept separate
  from `Band.rules` (what the author drew), with `_rule_boundaries` preferring it. No `Rule` is ever
  synthesised. Additivity held under every adversarial input tried (unsorted / duplicate / near-duplicate
  boundaries, intervals narrower than the bin minimum, centres exactly on a boundary, space-only cells,
  chars wider than the interval). Interactions with the two preceding loops were clean.
- **`recover_leaf_grid` must carry EVERY boundary-bearing field onto its row-suffix sub-bands.** Dropping
  one silently disables everything downstream. This has now bitten **twice** — loop D for `rules`, attempt 1
  for `column_xs` (17 columns compiled as 15). Whatever attempt 2 adds, add it there too.

**What was wrong — do not repeat**

- **The interior condition is NOT what protects the shipped fixtures.** Measured: removing it *alone* leaves
  `ruled_tight_table_pdf` and `ruled_merged_table_pdf` at **+0**. The naive `+5`/`+2` requires removing the
  interior condition **and** flushing a run still open at the interval's end. Two independent mechanisms, and
  attempt 1's spec and source docstring both credited the wrong one.
- **Cells and score do not discriminate this change.** `509` / `0.9496` held *identically* at the broken
  15-column state and the correct 17-column one. The discriminating criterion is the **header-label count**
  (15 vs 17) — pin that, not the score.
- **`gutter_pct = 0.98` behaves discontinuously when `N` is per-interval.** A bin counts as blank iff inked in
  `≤ floor(0.02N)` rows — **zero** rows for `N ≤ 49`, **one** for `N ≥ 50`. Attempt 1 recomputed `N` per
  *interval* (GrainCorp ran at N = 4, 32, 33, 47, 54 in one table), where `infer_leaf_grid` uses a single
  per-*band* `N`. That change in meaning was undocumented and is the mechanism behind the crash.
- **The single-row case over-splits, it does not merge.** One row + 3 author rules yields **6** columns at
  confidence 1.0 (`['Date','Loading','Completed','Net','Weight','Tonnes']`), masked in the pipeline only
  because a one-line band classifies `NON_TABLE`.
- **A guard test that replicates production code instead of calling it is worthless.** Attempt 1's
  no-synthesised-`Rule` test copied `compile.py`'s band-construction block into the test body; patching
  `compile.py` to synthesise fake `Rule`s left every test green.

**The red test attempt 2 must start from**

A synthetic ruled table — 3 columns, Courier 9pt, header `ID | Date | Tonnes`, six rows of values carrying a
column-aligned internal space (`AB CDEFGH`, `01 JAN 2026`, `12 500`), vertical rules at the column edges only.
On `main` this compiles `RECORD_TABLE`, 18 cells, score 1.0. Any refinement that breaks it is wrong.
