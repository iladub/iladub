# Residue register

Deferred items from the ET(K)L loops, in one tracked place. Each row records what the residue is,
where it was **measured** (never assumed), why it was deferred, and what would close it.

**This register is canonical.** Loops append rows here; a loop that closes a residue deletes its row
in the same change. Specs may describe a residue in prose, but the list of open residues lives here.

Started 2026-07-29 (Loop D), collecting items previously scattered across four specs and the SDD
ledger.

| # | Residue | Measured | Why deferred | What would close it |
| --- | --- | --- | --- | --- |
| ~~R1~~ | **CLOSED with R13 (Loop G attempt 2, 2026-07-30)** — it was the same defect | Loop F measured R1 IS R13; the header-confirmed split recovers `Date Loading Completed`/`Commodity`/`Total` as three columns | — | — |
| ~~R2~~ | **CLOSED for the ruled path (Loop F, 2026-07-29)** — padding space glyphs no longer split a contiguous number | Root cause was: source chars CONTIGUOUS (gaps −0.08…−0.03); padding space glyphs OVERLAPPING the digit run were joined in by `rule_aware_lines` | Fixed by a two-presence-test rule (a space glyph exists AND the glyphs it separates are apart). Two magnitude-based hypotheses were measured and REFUTED first — see the Loop F spec §2 | **Still open for the UNRULED path as R16** |
| R3 | **Nested-subset vote** in `recover_leaf_grid` | Loop D spec §2 Finding 3: the correct 15-column grid IS found by the longest suffix, then outvoted 35-to-16 by shorter suffixes that are nested subsets of it, not independent witnesses | Changes grid derivation for every table in the suite | A statistic that respects nesting, plus a fixture battery. **Ruled documents now route around this; the first ruleless document with a narrow gutter will hit it** |
| ~~R4~~ | **CLOSED for the ruled hierarchical path (Loop H, 2026-07-30)** — de-fusion + arithmetic subtotal detection | The hrule veto in `group_wrapped` (author rules are the row delimiters — presence test, no constant) de-fuses every suppressed-key/subtotal line; `rows.detect_aggregation_rows` (justified PROCEDURAL: decidable exact Decimal arithmetic) confirms a sparse candidate iff its all-numeric measure equals the token-sum of the non-aggregation rows back to the previous confirmed same-or-outer-level aggregation (the label's COLUMN encodes the level; label TEXT is never read). Measured on GrainCorp: fused cells **NONE** (was 3 source lines in one record); **17** `tab:DetectedAggregationRow` with correct members incl. the 2-level nesting (`Jul 26 Total` = 4 port groups; `Aug 26 Total` = 21 members; `2025/26 Total` = 32) — score/cells unchanged 0.9496/509. Candidate classification must be STRICT (every token numeric): `'Jul 26 Total'` carries the numeric token `26`, and lenient classification collapsed detection 17→4 (pinned by `test_a_label_containing_digits_is_still_a_label`) | — | **Open narrower forms (final review measured (c')–(e)):** (a) **blank-total subtotals** stay ordinary rows — `Port Kembla Total` (`'-'`) is arithmetically unverifiable and vacuous `0==0` confirmation would mark any sparse row over blanks (honest refusal, measured); (b) **unruled suppressed-key documents** keep the fusion defect — the hrule veto is inert without hrules; (c) **the row-hier path** (`assert_row_hier_region`) is unwired — `subtotals_row_group_pdf`'s reconciling `Total` rows (10+20=30, 15+25=40) still compile as data records via that path; (c') **the record path too** — `totals_table_pdf` compiles via `assert_record_region` and still mints `['Total','220','240','460']` as a data record (measured by the final review); worse, that Total row is **DENSE** (label + every measure column), so the 2-cell sparsity candidate bar makes the dense-total shape structurally unreachable by the detector on *any* path — closing (c)/(c') needs a widened candidate definition, not just wiring; (d) **the false-positive direction is inherent**: a sparse reference row whose number coincidentally equals the running sum (`see p.250` over 100+150) confirms — arithmetic-only detection has no defense, named honestly; (e) **single-member confirmation is degenerate but legitimate** — a row repeating the one measure above it confirms as a 1-member "sum" (`Mackay Total` over one data row is the measured real case; not fixable without losing that recall). The row-group *hierarchy* (Month > Port `coversRow` tree) is its own future loop, now unblocked |
| R5 | **Proposal inputs not recorded** in `emit_row_role_promotion` | Loop C.1 final review | Not a regression; best done alongside a live run | Record the context the proposer was shown, so an auditor can reproduce the proposal |
| R6 | **Centre-only merge candidate** for wide parents — a parent spanning cols 1–3 gets one candidate | Loop C.1 final review | Pre-existing in shape; needs a live run to judge | Report every covered column's candidate |
| R7 | **Live BAML path unreachable** — `BamlRowRoleProposer` is never constructed in `src/` | Loop C.1 final review | No live run attempted yet | Wire it behind `baml_proposer_available()` |
| R8 | **`ProposeHeaderSpan` missing** from `baml_src/` — B1.3's live path cannot run | Loop C | Pre-existing, unrelated to the loops since | Author the function |
| R9 | **Conservation shape unreachable** through the row-role driver | Loop C final review: no reachable role vector loses text | Sound as a regression backstop; covered directly by `test_conservation_shape.py` | Either a reading that genuinely loses text, or accept it as a backstop and say so |
| R10 | **`detect_bands` cuts one line too high** — the report date lands inside the table band | Loop C.1 §2 Finding 4: date x 398.3 ≈ page title x 399.0, matching no column | Segmentation is shared by every path; large blast radius | Title-block exclusion at segmentation **Interaction with loop G attempt 2 (latent):** a title/date line left inside the band above the header/body split contributes chars to the header-glyph evidence and could spuriously confirm a candidate; witness clauses are interval-bounded so out-of-band ink cannot, and no measured document reaches it today. |
| R11 | **Mixed header rows** cannot be expressed by a per-row role | Loop C §3.2 | No measured document exhibits one | Per-cell roles, when evidence demands it |
| R12 | **Split-table recurrence** — a solitary parent over a repeated layout | Loop C.1 §6.2; `stem.pdf` is a single page with no repeated block | No target document | Cross-block layout matching |
| ~~R13~~ | **CLOSED for the ruled path (Loop G attempt 2, 2026-07-30)** — rules coarser than the columns | Attempt 2: interior-gutter boundaries are CANDIDATES, confirmed only when the header region places char ink strictly on both sides within the author interval with no straddling glyph (`confirm-boundary.rq` AXIOM, no numeric literal). Measured: GrainCorp 15→**17** header labels (`Date Loading Completed` \| `Commodity` \| `Total` separate; cells 509, score 0.9496); attempt 1's counter-example compiles graph-ISOMORPHIC to main; the PLAIN-HIERARCHICAL crash class is closed by the membrane backstop (`REGION_TILING_FAILED` escalates in-band; the record/transposed paths remain direct-assert — see R17). **Honest cost:** candidates are *generated* by `refine_rule_columns`' inherited constants (`gutter_pct`/`min_gutter_bins`), so R13's **recall** is bounded by generation, not by the AXIOM — in one of the counter-example's three intervals it was the generation threshold, not header confirmation, that prevented a split | **Remaining narrow form, honest by construction:** a genuinely unlabeled sub-column (header ink one side only, yet truly two columns) is indistinguishable from the counter-example and stays merged — asserting it would be exactly attempt 1's defect. No measured document exhibits it | The attempt-1 post-mortem section below stands as history; attempt 2 resolved it |
| R14 | **The collapse can delete an author-drawn boundary** when only a skipped line carried that column's ink | Loop D final review, pinned by `test_skipped_line_ink_loses_an_author_drawn_boundary_KNOWN_LOSS`: rule at x=90.0 discarded, two real columns merged, reported at confidence 1.0 with no escalation | Depends on R10 (a caption left in the band is what forces the suffix skip) | Close R10, or make the occupancy test span the whole band rather than the accepted suffix |
| R15 | **NEURAL residual: a wide label over blank/unclaimed columns** where the covering partition genuinely cannot decide | Loop B §7.4 / Loop C — still escalates honestly `MERGE_AMBIGUOUS` | No measured document needs it | The `span_proposer` seam, if a real document ever requires it |
| R16 | **The UNRULED path keeps the split-number defect** — pdfplumber's `extract_words` splits `2` from `0,000` on its own | Loop F: only `rule_aware_lines` (the ruled path) was fixed | Closing it means owning word segmentation for every document, not just ruled ones | Apply the same two-presence-test rule to a char-derived word segmenter for unruled bands |
| R18 | **Groups without a confirmed total stay ungrouped — and an unconfirmed total POLLUTES the next group** | Loop I (2026-07-30), measured on the real document: `Geelong Total` (Aug) and `Portland Total` (Sep) refused because the unconfirmed totals above them (Port Kembla's blank total; a non-confirming Fisherman Islands total) stay ordinary rows, flow into the confirmed total's member walk, and break key uniqueness (conflicting port values → honest refusal). Also: a boxed source cell yields the faithful-but-doubled key `Mackay Mackay`. **Final review (M-3), a SECOND, distinct doubled-key mechanism**: nested groups whose key comes from the SAME source cell (an inner `Mackay Total` and an outer total over the same port, both `hasLabel`-pointing at that one `EntryCell`) double the key in the record PATH instead — `Mackay > Mackay > h0-r0` — even when the cell's own text is not itself doubled. Not covered by the boxed-cell case above | Refusal is the correct §7 behavior — the alternative (guessing group boundaries) is exactly what the loop forbids; the cascade is inherent to H-confirmed-only evidence. **Also (re-review m-3):** co-resident level-0 groups over the same rows (a month with its single port, admitted by the C-1 overlap exemption) reach the feed's deepest-cover tie-break, which keeps ONE key and silently drops the other (a §5 context loss, better than the pre-fix region loss but undocumented); the nested-same-cell case passes the membrane (source-faithful) and is merely noisy, not incorrect | Ditto-fill evidence (rowheaders' blank-below convention) cross-checked against H membership where both exist would recover the refused groups; a per-boxed-line key read would clean the doubled key. A path-dedup rule (collapse an immediate repeated segment, e.g. `X > X` → `X`) would clean the nested-same-cell case. All deferred until a document *needs* them |
| R17 | **The record and transposed region paths are still direct-assert** — `assert_record_region` / `assert_transposed_region` write into the output graph with no scratch+`region_tiles` gate, so a defective region there still RAISES at `compile_tables`' final validation instead of escalating in-band | Loop G attempt 2 final review: demonstrated by dropping one `tab:coversColumn` after `assert_record_region` → `AssertionError`, `tab:CoverageShape` at `#table0-c0` — the same crash class attempt 1 died of, through an ungated path | The backstop loop gated only the plain hierarchical path; these two need the same treatment | Give both paths the scratch → `region_tiles` → commit-or-escalate gate the hierarchical/matrix/row-hier paths have |

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
