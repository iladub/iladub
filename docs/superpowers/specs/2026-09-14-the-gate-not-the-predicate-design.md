# Spec — the gate, not the predicate: R225's arm B and the clause that refuses a complete reading

**Serves:** prog:criterion:etkl:04 — `gov-stats/ons-index-of-services-2026-02.pdf`
(`tests/arc-manifest.ttl:265`; the document's manifest node is `tests/corpus-manifest.ttl:94`).
This spec is a **prerequisite** of that criterion, not a criterion of its own.

**Date:** 2026-09-14. **Branch:** `r225-arm-b-resolution-test`, cut from `10b09c5`.

**Doc impact: none.** This loop ships a spec and no released term. Nothing queues for a release
tag and nothing blocks one.

Every load-bearing claim below carries the command that produced it, per CLAUDE.md § Plan
authoring discipline rule 2. Figures are on this branch unless stated.

## 0. The ruling this spec executes

The maintainer ruled [[R225]]'s fork on 2026-09-14: **arm B — give the re-bucketing a resolution
test, and re-derive the fallback gate in the same change.** The row had costed both arms and named
the oracle: *ons must not lose its grid (571 cells) and bfs p5 must not regress from its adopted
404.*

The ruling's second clause is the whole of this spec's difficulty, and the measurements in § 1 show
why it is not a caution but a load-bearing requirement: **the resolution test alone reproduces the
collapse that refuted the naive guard**, on a predicate that is strictly better targeted. The
binding constraint was never the predicate. It is the gate.

## 1. What is measured

### 1a. The predicate fires in two documents, and cannot touch the five that carry pinned floors

`scripts/` carries no instrument for this; the probe wraps `compile._build_ruled_band` — the
production seam — and compares, at the exact site `compile.py:133` gates, the drawn resolution
`len(xs) - 1` against the band's own word structure. The word measure is taken on a **rules-free**
copy of the band: `infer_leaf_grid` short-circuits on `_rule_boundaries` (`grid.py:113`), so
passing the band as-is would compare the author's marks against themselves.

```
$ PYTHONPATH=src .venv/bin/python scratchpad/probe_all.py
document                    calls  border1  under
apple-fy2026q3-stateme         17        0      0
bfs-population-bilan-2         19        8     11
cbh-stem-2026-08-03             5        0      0
graincorp-capacity-202          3        0      0
graincorp-stem-2026-07          4        0      0
ons-index-of-services-         36       33     22
who-wfa-boys-zscore-0-         11        0      0

total _build_ruled_band calls: 95
border-only (drawn == 1):      41
under-resolved (drawn < word): 33
```

Three facts follow, and the third is the one that makes this safe to attempt:

1. **41 border-only bands corpus-wide** independently reproduces [[R225]]'s own census (ons 33,
   bfs 8), by a different instrument.
2. **33 under-resolved, not 41.** The refuted `len(xs) >= 3` guard would have refused all 41,
   including **8 genuinely single-column prose bands** (`drawn=1, word=1`) that are correctly
   fused today. The resolution test leaves those alone. This is the respect in which arm B is not
   the guard that was refuted.
3. **The five documents carrying adjudicated `cor:scoreFloor` pins have zero under-resolved
   bands.** The test cannot regress them — not because the figures happen to hold, but because it
   never fires there. bfs p6 also shows `drawn=6, word=9`: seven bands under-resolved *with real
   interior rules*, the [[R13]]-shaped "rules coarser than the columns" case, which the naive
   guard could not reach at all.

### 1b. The predicate alone reproduces the refuted collapse

D1 (§ 4) was applied and the whole corpus read twice, before and after, with
`scripts/corpus_verdict_snapshot.py` — the before-side taken on the unmodified tree.

```
document                      score before   score after  cells b  cells a  sha
apple-fy2026q3-statements           0.7188        0.7188      183      183  IDENTICAL
bfs-population-bilan-2023           0.4033        0.8435      274      773  CHANGED
cbh-stem-2026-08-03                 0.9095        0.9095      763      763  IDENTICAL
graincorp-capacity-2026-08          1.0000        1.0000      406      406  IDENTICAL
graincorp-stem-2026-07-31           0.9659        0.9659     2152     2152  IDENTICAL
ons-index-of-services-2026          0.9720        0.5407      571      389  CHANGED
who-wfa-boys-zscore-0-5             0.9156        0.9156      654      654  IDENTICAL
```

§ 1a's prediction holds exactly: five documents are **byte-identical by canonical graph hash**,
not merely equal-scored. And **ons 0.5407 / 389 cells is the collapse [[R225]] measured for the
refuted guard** (0.5407, 571 → 389). Better targeting bought nothing here.

**bfs meets its half of the oracle and exceeds it:** p5 adopts at **exactly 404 cells**,
reproducing R225's document-scope figure to the digit, p6 gains 102, and `adopted` goes `[]` →
`[5]`.

### 1c. The collapse is one page, and its cause is an adoption clause

```
=== ONS page detail ===
 p7: cells  276 -> 94    asserted  285 -> 107   escalated    0 -> 226
 chains before: 3  after: 4
--- ons p8 AFTER: asserted=286 escalated=62
    #3,#4,#5,#7  UNSUPPORTED_TABLE  superseded   ROUND_TRIP_FAIL
    #9           RECORD_TABLE       asserted     cells=276
    #10          UNSUPPORTED_TABLE  escalated    DATAGRID_RESIDUE
```

**p8 did not survive through the fallback — it went through ADOPTION** (four superseded bands and
a residue candidate are adoption's own products, `document.py:1661`), recovering the same 276
cells by a different route. **p7 did not**, and the reason is exact: its unfused bands assert
**94 cells** (7 + 1 + 86), and the adoption gate asks whether the page is a *total* reading
failure —

```
$ cat vocab/queries/adoption-candidate.rq        # the closure clause, verbatim
  FILTER NOT EXISTS { ?cell a tab:EntryCell ; tab:onPage ?page . }
```

One asserted cell disqualifies the page. So a **94-cell partial reading blocks a 276-cell complete
one**. The same `asserted_total == 0` precondition guards both page-scope branches
(`compile.py:1351` fallback, `compile.py:1428` adoption), which is why neither opens.

**p7's grid is intact and is not the problem:**

```
$ PYTHONPATH=src .venv/bin/python -c "...derive_data_grid(ONS, 7)"
p7: {'rows': 46, 'columns': 6, 'universe': 9, 'conforms': 6, 'refusals': 22}
p8: {'rows': 46, 'columns': 6, 'universe': 9, 'conforms': 6, 'refusals': 23}
```

46 × 6 = 276, the count both pages carried before. The reading p7 loses is still derivable; only
the gate stands between it and the page.

### 1d. What D1 costs in test coverage

Two runs, quoted as they were actually issued — no combined figure was taken:

```
$ .venv/bin/python -m pytest tests/etkl/test_border_grid.py \
      tests/etkl/test_boundary_cuts_ink.py tests/etkl/test_rule_column_refinement.py \
      tests/etkl/test_read_band_books_every_word.py -q
FAILED tests/etkl/test_read_band_books_every_word.py::
       test_no_band_books_ink_it_does_not_hold_on_the_fallback_page
1 failed, 31 passed in 15.47s

$ .venv/bin/python -m pytest tests/etkl/test_fallback_region_books_and_names.py -q
ERROR ...::test_the_fallback_region_books_the_ink_it_claims
ERROR ...::test_the_fallback_region_names_the_table_it_asserted
7 passed, 2 errors in 442.28s
```

**CORRECTED — the three described below are NOT the only breakage, and the paragraph that stood
here asserted that on no evidence.** The first full-suite attempt passed `--timeout=1200`, which
this repo has no plugin for: pytest answered `unrecognized arguments` and **exited 0 having run
nothing** — a phantom green that would have shipped the understatement as verified. The clean
re-run says:

```
$ .venv/bin/python -m pytest tests/etkl -q
FAILED test_datagrid.py::test_fallback_fires_only_where_the_page_produced_nothing_at_all
FAILED test_datagrid.py::test_fallback_output_passes_full_shacl_through_the_production_path
FAILED test_datagrid.py::test_an_unread_table_page_no_longer_scores_perfect
FAILED test_escalation_furnish.py::test_corpus_census_every_live_escalating_decision_is_furnished
FAILED test_grid_donation_seam.py::test_bfs_p6_reads_267_entries_under_band_2s_labels
FAILED test_grid_donation_seam.py::test_donation_moves_no_ink_between_the_ledgers
FAILED test_grid_donation_seam.py::test_an_accepted_donation_is_a_recorded_decision
FAILED test_header_confirmed_refinement.py::test_confirmed_split_reaches_the_grid_end_to_end
FAILED test_read_band_books_every_word.py::test_no_band_books_ink_it_does_not_hold_on_the_fallback_page
FAILED test_run_merge_seam.py::test_o2_the_fallback_is_what_saves_the_ink
FAILED test_run_merge_seam.py::test_o3_no_page_loses_asserted_ink_to_a_merge
FAILED test_run_merge_seam.py::test_o5_document_scope_completes_with_a_forced_non_tail_merge
ERROR  test_fallback_region_books_and_names.py  (x2 — the preconditions described below)
12 failed, 994 passed, 2 skipped, 1 xfailed, 2 errors in 3080.13s (0:51:20)
```

**At least two are substantive rather than preconditions**, and neither is a surprise — both agree
with § 1b's own figures: `test_run_merge_seam.py:331` pins bfs p5 at **12** regions where D1 yields
**14**, and `test_grid_donation_seam.py` pins bfs p6 at **267** donated entries where § 1b measured
p6 moving to **369**. D1 therefore reaches [[R210]]'s grid-donation ink ledgers and the run-merge
seam, not only ONS.

**Per-failure classification is NOT done.** Until it is, nothing here says which of these D2
resolves and which are pinned figures that must be re-derived and re-justified — and § 4's task
list is incomplete by exactly that amount.

All three break on a **fixture-drift precondition**, never on their substance
(`test_read_band_books_every_word.py:103`, `test_fallback_region_books_and_names.py:68`, both of
the form *"this page must reach the datagrid fallback"*). The invariant underneath — no band books
ink it does not hold — still passes.

The cause is structural and worth stating plainly: **`border_only_grid_pdf` reaches the fallback
gate by being R225's defect reproduced synthetically.** Its own docstring cites `datagrid.py:346`
— the very ordinal comparison D1 applies at `compile.py:133` — as the reason the grid path still
reads the table. D1 makes the band path agree with the grid path, so the fixture's mechanism
evaporates: the page now reads completely through bands (`RECORD_TABLE`, 20 cells, score 1.0) and
has no need of a fallback. On the fixture D1 is the cure; on ONS p7 the same mechanism is the
injury.

## 2. The defect, stated once

A page may hold a **partial** band reading and a **complete** grid reading at the same time. Every
gate in the reader tests for *absence* — no asserted cell, no escalation — so the partial reading,
merely by existing, excludes the complete one. Absence was an adequate proxy for "the bands failed"
only while the bands failed *totally*; D1 makes partial failure common, and the proxy stops
holding.

## 3. Why nothing caught it

The three instruments that could have are blind here by construction: the fallback branch had
**no synthetic fixture at all** until [[R224]] authored one (a sweep of every single-argument
fixture found zero reaching the gate), the corpus tests that would show it are `corpus`-marked and
do not run in CI, and totals are preserved on both sides of the gate, so no sum identity moves.

## 4. What the loop builds

**No function bodies here** (CLAUDE.md § Plan authoring discipline rule 1) — interfaces,
invariants, and the falsifying oracle.

- **D1 — the resolution test at `compile.py:133`.** The author's marks may re-bucket a band only
  when they resolve **at least as finely** as the band's own word structure. Ordinal, not a
  threshold; no tuned constant; `datagrid.py:346`'s shape applied at the one site that never
  consulted it. Already applied and measured throughout § 1. Classification under the § 8 gate:
  this is a comparison of two already-derived measures in procedural code, mirroring a shipped
  precedent — **the plan must state that classification explicitly and justify it against the
  AXIOM default**, or move it.
- **D2 — the gate, re-derived.** The admission question becomes comparative rather than absolute:
  a page whose grid reads **strictly more** than its bands did may be adopted, and the existing
  post-hoc refusals at `document.py:1650` (no grid region) and `:1663` (superseded no band) stay
  as they are. **Neither of those compares completeness**, so the comparison is new and must be
  added beside them, not assumed from them. The clause to change is the closure in
  `vocab/queries/adoption-candidate.rq`, which keeps the decision an **AXIOM, holon-scoped** —
  the § 8 default — rather than moving it into Python.
- **D3 — a replacement fixture for the fallback branch,** since D1 destroys R224's. **Measured
  constraint, recorded because the obvious design is impossible:** a page whose bands are *all*
  one line cannot be built — `detect_bands` splits where a gap exceeds `1.8 ×` the **median** gap
  (`bands.py:37-52`), and gaps cannot all exceed their own median. The replacement must instead
  keep every multi-line band single-column in gutter terms while page-wide alignment still
  resolves ≥ 2 columns. **This is a proposition, not a plan: it must be built and run before
  anything depends on it.**

**The invariants, each stated once:**

| | invariant | how it falsifies |
| --- | --- | --- |
| I1 | the five pinned documents stay byte-identical by canonical graph hash | any sha in § 1b changing |
| I2 | ons carries ≥ 571 cells and ≥ 0.9720 | the § 1b figure |
| I3 | bfs p5 stays adopted at ≥ 404 cells | `adopted` losing `5` |
| I4 | no band books ink it does not hold | `test_read_band_books_every_word.py`'s surviving assertion |
| I5 | no token is counted on both sides | the two sum identities `test_datagrid.py:1149`, `test_adoption_document.py:141` |

**The oracle is I1–I3 together**, run as the before/after corpus sweep of § 1b. I2 is the one D1
alone fails.

## 5. Falsification, mandatory per task

Every task reports a `## FALSIFICATION` block: remove or invert what the new test pins, show it
**failing**, restore, show green. D3's fixture additionally must be shown to *reach the gate* — the
precondition R224's fixture can no longer satisfy — or it pins nothing.

## 6. What this loop does NOT do

- **It does not stitch ONS.** [[R226]] measured that recognition cannot fire there at all, and the
  prior loop's probe settled that `is_continuation(p7, p8)` is `False` on origin disagreement. No
  task here depends on a chain forming.
- **It does not author ONS's contract triple** (etkl:04's route step 1). That is independent and
  unblocked; meeting the criterion still needs it, plus an adjudication that accepts the score.
- **It does not touch the five pinned documents**, by § 1a's construction.

## 7. Residues

[[R225]] closes only when D1 **and** D2 land together; D1 alone is the refuted state, measured in
§ 1b. [[R226]] and [[R202]] are untouched. [[R13]] is closed for the ruled path and § 1a shows its
shape recurring on bfs p6 — noted, not reopened. If D3 ships without a fixture that provably
reaches the gate, the fallback branch loses the CI coverage R224 created, and that must be raised
as a residue rather than left silent.

## 8. An honesty note on the ruling

Arm B, completed, **converges on arm A's framing**: a page ends up carrying both a band reading
and a grid reading, with one adjudicated against the other and `dec:supersedes` recording the
judgement. The difference that remains is real — arm A would have widened the gate while leaving
41 bands misread, where arm B repairs the misreading and lets adoption's existing exact-withdrawal
machinery do the adjudication — but the two are not the opposites the fork presented. That was not
visible when the fork was written, and it is recorded here rather than quietly resolved.
