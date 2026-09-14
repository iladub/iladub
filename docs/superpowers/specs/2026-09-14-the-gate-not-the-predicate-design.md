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
$ PYTHONPATH=src .venv/bin/python scripts/under_resolved_band_census.py
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

### 1e. The classification — and a DESIGN DEFECT in D1 that it exposes

```
$ .venv/bin/python -m pytest <the 11 failing node ids> --tb=line -q
tests/etkl/test_header_confirmed_refinement.py:45: assert ['ID','Total'] == ['ID','Qty','Total','Unit']
tests/etkl/test_run_merge_seam.py:85:  assert 369 == 267          # bfs p6 cells
tests/etkl/test_run_merge_seam.py:248: bfs p5: 0 < 16  (score 0.0, asserted 0, escalated 882)
tests/etkl/test_run_merge_seam.py:331: assert 14 == 12            # bfs p5 region count
11 failed in 181.59s
```

**`test_header_confirmed_refinement` is not a moved figure. It is D1 being placed at the wrong
site, and it falsifies part of § 1a's reasoning.**

When D1 refuses, `relines` is empty, so `_build_ruled_band` takes the early return at
`compile.py:151` — **before `refine_rule_columns` at `:155` is ever called.** That refinement, with
`confirmed_boundaries`, is [[R13]]'s closure: the mechanism that recovers columns in exactly the
case where the author's drawn rules are **coarser than the columns** (R13's closed row: GrainCorp
15 → 17 header labels). The fixture here collapses 4 recovered columns to 2.

So § 1a's third finding — that D1 also catches the "R13-shaped" `drawn=6, word=9` bands on bfs p6,
offered there as *reach the naive guard lacked* — has the sign wrong. Those bands are the ones
refinement exists to repair, and D1 as written **disables the repair instead of extending it**.

**What this implies for § 4's D1, and it is a change of design, not a tuning:** the resolution
comparison is being made against the RAW author marks (`xs`, `compile.py:111`), where
`_rule_boundaries` — the shipped separator test D1 was modelled on — deliberately prefers the
DERIVED boundaries (`band.column_xs`, `grid.py:71-74`). The comparison plausibly belongs *after*
refinement, against `col_xs`, so a band whose rules under-resolve is first **refined** and only
refused if it still under-resolves. **That is a proposition and is unbuilt** — it must be
constructed and run, not adopted from this paragraph.

**The rest, so far as this run shows them:** bfs p6 `267 → 369` and bfs p5 `12 → 14` regions are
pinned figures moving with a changed reading; `test_run_merge_seam.py:248` is a **page-scope**
regression (p5 asserts 0 of 16, escalating 882) which coexists with p5 adopting 404 at **document**
scope — the two scopes are different quantities, as `compile.py:1402-1408` already records. The
three `test_datagrid`, three `test_grid_donation_seam` and one `test_escalation_furnish` failures
are **named but not yet diagnosed**; nothing here says which D2 resolves.

**Those three** — the single failure and two errors in the two runs quoted at the top of this
section, not the twelve above — break on a **fixture-drift precondition**, never on their substance
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

### 1f. THE LEDGER CONTRACT — settled, 2026-09-14, by measurement with a control

**Question:** does `build_ledger`'s stated premise (`adoption.py:52-54` — *"an adopting page is by
definition one where `asserted_total == 0`"*) survive a widened adoption gate?

**Answer: NO.** The premise is load-bearing, and widening the gate falsifies it.

The ledger promises to account for every line "exactly once", but deliberately drops IGNORED
bands' prose, so a raw conservation test cannot tell prose from a defect. The exact identity is
`lost = (ink on UNADMITTED lines) − escalated_tokens`, so the unadmitted lines are split by the
booking class of the band holding them — the same thing `build_ledger` itself selects on:

```
$ PYTHONPATH=src .venv/bin/python scripts/ledger_contract_census.py
document                   pg              kind  lost  prose  escal ASSERT-ONLY outside
graincorp-stem-2026-07-31   1 CONTROL(adopting)    24     24     44           0       0
graincorp-stem-2026-07-31   2 CONTROL(adopting)    24     24     44           0       0
cbh-stem-2026-08-03         0        population   148      5    261         143       0
apple-fy2026q3-statements   0        population    68     22      0          46       0
apple-fy2026q3-statements   1        population    64     21      0          43       0
bfs-population-bilan-2023   5        population   215    143     75          39       0
bfs-population-bilan-2023   6        population    46     17     54          29       0
graincorp-capacity-2026-0   0        population    41     41      0           0       0
ons-index-of-services-202   4        population   101     82     36           0       0
who-wfa-boys-zscore-0-5   0/1/2      population    11     11     23           0       0

control pages with ASSERT-ONLY ink dropped:    0
population pages with ASSERT-ONLY ink dropped: 5
```

**The control is what makes this a finding rather than an anecdote:** on the two pages where the
premise is *stated* to hold, the ledger drops exactly the prose and nothing else. On five pages
whose bands assert, ink held by bands that assert and do **not** escalate is booked by nobody —
`escalated_bands = [i for i, r in enumerate(reports) if r.tokens_escalated > 0]` admits them to
neither the residue term nor the untouched term. The page would score higher than it read: the
failure the docstring says token-selection exists to prevent, from the direction it did not
consider.

**THE REVISION D2 MUST MAKE, and it is NOT one line.** Two terms are wrong once the gate widens,
and they need opposite treatments:

1. **Touched bands** (the grid admitted some of their lines): select the residue term by **any
   booked ink** (`tokens_asserted + tokens_escalated > 0`), not by escalated ink alone, so an
   assert-only band's *unread* lines become residue.
2. **Untouched bands** (the grid admitted nothing inside them): the band's own reading still
   stands and is not superseded, so its ink is **asserted, by the band** — it belongs in
   `asserted_tokens`, which today counts admitted lines only. Widening the residue term alone
   would book this ink as escalated and understate the page.

**Why the revision is safe to land BEFORE D2, and testable as inert:** on any page adopting under
today's gate, `asserted_total == 0` and `tokens_asserted` is non-negative, so **every** band has
`tokens_asserted == 0` and the widened predicate is *identically* the current one. The control row
above measures that: `ASSERT-ONLY = 0` on both adopting pages. So the revision can ship first and
be verified byte-identical on the whole corpus, which is the only way to separate it from D2's own
effects.

**Limits of this measurement, stated rather than left implied.** The corpus yields only **two**
control pages, so "0 of 2" is a thin control, not a strong one. Pages where no grid derives, or
where `len(reports) != len(bands)`, were **skipped and are unmeasured** — not clean. And on bfs p5
and ons p4 the identity leaves 33 and 19 tokens unexplained: bands that both assert *and* escalate
book fewer escalated tokens than they hold. That is a separate, smaller accounting question and is
**not** settled here.

### 1g. The second half: the graph, not the arithmetic

`document.py:1672-1674` withdraws only **superseded** bands and then merges `rep_a.graph`
wholesale. An asserting band is never superseded, so under a widened gate its table would survive
beside a grid region re-reading the same lines. Measured as contested lines — admitted lines lying
inside a band whose report asserted:

```
graincorp-capacity p0  27/27 admitted contested (475 tokens)    graincorp-stem p0  57/57 (747)
apple p0               31/31 (225)                              who-wfa p0         25/25 (321)
bfs p6                 29/32 (448)                              cbh p0              1/50 (16)
ons p4                  0/25 — disjoint, the one clean case
```

So D2 must also **supersede the asserting bands whose lines the grid admits**, or refuse the
adoption where it would only partially cover one. Ink conservation in the ledger does not save the
graph: these are two separate obligations.

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
- **D2 — the gate, re-derived. THE FORM BELOW IS CORRECTED; the first draft of this bullet was
  refuted by measurement before it was implemented.** It said: *a page whose grid reads strictly
  more than its bands did may be adopted.* Measured at baseline, that predicate has a population
  of **12 pages spanning every corpus document**, including all five that carry an adjudicated
  `cor:scoreFloor`:

  ```
  cbh p0            13 -> 1000      graincorp-capacity p0   406 -> 432      (this page scores 1.0)
  graincorp-stem p0 586 -> 855      apple p0/p1/p2          124->155, 56->84, 3->87
  who-wfa p0/p1/p2  268->325 ...    bfs p5/p6               ons p4  19 -> 150
  ```

  **More cells is not a better reading, and the code already said so** before this spec was
  written: `compile.py:1334-1339` records that the two paths *segment* cells differently (on the
  stem, 441 shared, 59 old-only, 51 new-only) and that replacing wholesale "would churn the one
  document with an adjudicated floor for no measured gain". A cell-count comparison would fire on
  `graincorp-capacity` p0, which reads **perfectly today**.

  **The predicate must be about UNREAD INK, not cell counts** — which is what the existing gate
  actually asks ("did this page read *nothing*") and what `adoption.build_ledger` already computes
  exactly (`admitted` / `residue` / `asserted_tokens` / `escalated_tokens`).

  **D2 is therefore structurally TWO changes, not one clause.** `is_adoption_candidate` runs on
  the pass-1 graph, **before any grid exists**, so it cannot compare against grid ink at all: the
  closure in `vocab/queries/adoption-candidate.rq` can only be widened *narrowly*, and the actual
  comparison must be a new post-hoc refusal beside `document.py:1650` and `:1663`, where the grid
  and the ledger are both in hand. Neither existing refusal compares ink, so the comparison is new.

  **COST, which constrains how far the candidate gate may widen** (`document.py:1621-1625`): every
  candidate page pays one extra full `compile_tables`, *including pages that then refuse*, and an
  adoption switches on whole-graph SHACL (41.3 s on the stem). Widening the candidate gate to the
  12 pages above would add twelve page-compiles plus SHACL to every corpus run. The widening must
  stay as narrow as the defect it repairs.

  **AND IT BREAKS A PREMISE `build_ledger` STATES ABOUT ITSELF — read this before reusing it.**
  Its docstring (`adoption.py:52-54`) says: *"an adopting page is by definition one where
  `asserted_total == 0`, so any such band reached adoption with `n == 0` and carries real
  escalated ink under an 'asserted' label."* That premise is **why** it selects `escalated_bands`
  by `tokens_escalated > 0` rather than by the verdict string. Widening the candidate gate
  **falsifies the premise**: on a page whose bands genuinely assert, the grid's `admitted` lines
  and the bands' own asserted ink are the same ink counted on both sides — precisely the double
  count R73 exists to prevent, arriving from the other direction. **D2 must therefore revisit the
  ledger's contract in the same change, or state why it survives.** Not doing so is how this
  repair becomes the defect it is repairing.

  **Where each quantity comes from, since they are NOT in the same place.** `LineLedger` carries
  `asserted_tokens` for the **grid** only. The band-side quantity is `RegionReport.tokens_asserted`
  (`compile.py:491-507`), summed over the page's regions the way `document.py:1542` already does
  it. An implementer reaching for the ledger alone will not find the number the comparison needs.
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

## 9. D2 EXECUTED (2026-09-14) — four sites, two latent defects, and a refuted prediction

Appended, never rewritten: § 4's D2 bullet describes what was *designed*; this section records what
was *built and measured*, including where the design above was wrong.

### 9a. D2 is FOUR sites. § 1c names the third one without noticing it is a site

§ 1c already measured that *"the same `asserted_total == 0` precondition guards both page-scope
branches (`compile.py:1351` fallback, `compile.py:1428` adoption)"*. It draws the conclusion for the
fallback and not for adoption — but the document driver adopts by RE-COMPILING the page with
`datagrid_adopt=True`, so on a page whose bands assert anything, `compile.py:1428` refuses, no grid
region is appended, and `document.py:1650` refuses with *"no data grid region on the re-compile"*.
**Widening the `.rq` alone is a no-op.** The four sites are the `.rq`, that precondition, the ink
comparison, and § 1g's withdrawal.

### 9b. Where the ink comparison went, and why NOT beside `document.py:1650`

§ 4 D2 places it there. It is instead inside `compile.py`'s adoption branch, immediately after
`build_ledger`, because that is the one place where **both** quantities are already in hand —
`escalated_total` (what the bands leave unread) and `_led.escalated_tokens` (what the adopted page
would leave unread). Adopt iff the grid leaves **strictly** less; a tie refuses. One consequence is
load-bearing and was measured, not reasoned: with the test there, a page that refuses produces no
grid region, so the document driver's EXISTING refusal at `:1650` reports it and no second predicate
is needed. bfs p6 exercises exactly that path in the corpus run below.

### 9c. THREE LATENT DEFECTS, every one invisible until the gate widened

Neither is a regression introduced by `7f365ce`; both are couplings it left, which only a widened
gate can reach — every band on an adopting page had `tokens_asserted == 0` until now.

1. **`compile.py`'s supersession predicate had to move with `build_ledger`'s.** Its own comment
   says the two *"have to be"* the same predicate; the ledger's became `tokens_asserted +
   tokens_escalated > 0` while this one stayed `tokens_escalated > 0`. A touched band that ASSERTED
   would have kept its verdict and its `tokens_asserted` while the ledger had already handed that
   ink to the grid, breaking I5 from the side nothing tests.
2. **The grid region booked the PAGE's asserted total, not its own.** `RegionReport(...,
   tokens_asserted=_led.asserted_tokens)` was correct only while the ledger's asserted term was
   admitted-lines-only. Since the revision it also carries every UNTOUCHED booked band's asserted
   ink — which those bands' own reports still book — so the grid region would have counted it a
   second time. It now books `sum(len(_lines[j].words) for j in _led.admitted)`.
3. **`cells` and `table_uri` had to go with the tokens — found by the new fixture, not by reasoning.**
   A superseded band that asserted kept claiming its cells and naming its table, so `sum(r.cells)`
   counted them beside the grid's (the cell-level form of the same double count) and the report
   named a table that is in NO graph — the page rebuild discards it, and § 1g removes it at
   document scope. **Nothing catches this:** the shipped I1/I2 oracle filters
   `verdict == "asserted" and cells > 0` (`test_fallback_region_books_and_names.py:56`), so a
   SUPERSEDED region is outside its population entirely. It is why § 9e's cell figures read as they
   do: apple p2 reads **87**, not 90 (87 grid + 3 stale), and bfs p5 reads **404**, not 411 —
   landing exactly on [[R225]]'s stated oracle. **The graph was never wrong, and that is its own
   control:** sweeps taken before and after this change are byte-identical (6225 / 14197 triples,
   scores equal to 10dp), so this is a REPORT repair with the graph holding still beneath it.

Both are pinned by the sum identities I5 already names; `test_adoption_document.py`'s ledger test
passes on apple p2 (`sum(tokens_asserted) == asserted`, `sum(tokens_escalated) == escalated`), which
is the arithmetic those two defects would break.

### 9d. § 1g: withdraw-or-refuse, decided before any mutation

The rule built is: a superseded band that asserted a table has that table WITHDRAWN, but only when
**nothing outside its own subgraph points into it** and no multi-member chain names it; otherwise
the whole adoption is refused. The closure check replaces an enumeration of fact types (which would
rot as facts are added); the chain check exists because a chain is a report field, not a triple, and
the closure check cannot see it. The subgraph is computed from `pages[p].graph` — the page's own
pass-1 graph, where `_band_subgraph`'s reachability is bounded as designed — and never from the
merged graph, whose closure would reach the document node.

Measured on apple p2, the live case: 2 of 29 admitted lines lie inside asserting band 6; `#table6`
is the object of zero document-level triples and sits in a singleton chain; it is withdrawn and its
chain entry dropped.

### 9e. The corpus, before and after (`scripts/corpus_verdict_snapshot.py` + the new differ)

```
$ PYTHONPATH=src .venv/bin/python scripts/corpus_snapshot_diff.py snap-base snap-d2g
apple-fy2026q3-statements      0.7187500000 -> 0.9302325581  triples   5157 ->   6225  CHANGED
    adopted  [] -> [2]        chains 3 -> 2
    p2: score 0.0526 -> 0.8537   cells     3 ->    87   asserted     6 ->  210   escalated 108 ->  36
bfs-population-bilan-2023      0.4033149171 -> 0.8890554723  triples   9333 ->  14197  CHANGED
    adopted  [] -> [5]        chains 7 -> 6
    p5: score 0.0420 -> 0.9183   cells     7 ->   404   asserted    16 ->  910   escalated 365 ->  81
    + note: page 6: adoption refused — no data grid region on the re-compile
cbh-stem / graincorp-capacity / graincorp-stem / ons / who-wfa        IDENTICAL (canonical sha)
2 of 7 documents changed
```

**§ 1g's own effect, isolated by a second sweep taken with it reverted:** apple 6318 → 6225 triples
(−93) and bfs 14451 → 14197 (−254), **with every score, cell count and verdict unchanged**. That is
the double-read being removed and nothing else — the five untouched documents are the control.

### 9f. THE PREDICTION THIS LOOP RAN FIRST WAS REFUTED, and the refutation is the finding

The handoff graded one claim PROPOSED and ordered it run before anything was built on it: *D2 alone
is inert on the corpus.* **It is not.** Two documents move, and they move the way the row's oracle
asked:

- **bfs p5 adopts at 411 cells — R225's oracle is `≥ 404` — with D1 REVERTED.** The row costed this
  gain as D1's; it is the gate's.
- **ons is byte-identical**, so I2 holds without D1 having to be judged at all.

§ 1b's title says *the predicate alone reproduces the refuted collapse*; § 9 completes the sentence:
**the gate alone delivers the gain.** That is the strongest available form of this spec's claim, and
it was available only by running the experiment in the order the maintainer ruled.

**A second correction, small and worth not burying:** § 1a says five documents carry adjudicated
`cor:scoreFloor` pins. Measured against the manifest, **three** do — graincorp-stem 0.95,
graincorp-capacity 0.99, who-wfa 0.90 — and all three are byte-identical above. apple, which moved,
carries no floor (its own manifest note says so explicitly), so no floor is at risk in either
direction.

### 9g. What is NOT done, stated rather than implied

- **The 87 cells apple p2 now reads, and bfs p5's 411, are unverified against a transcript.** The
  oracle here is ink conservation and the ledger identities, both of which hold; cell-level
  correctness is unmeasured — as it was for the 3 cells apple p2 read before.
- **D1 stays reverted.** Its placement is now judgeable on readings rather than on gate accidents,
  which is what the maintainer's ruling asked for, and it is the next loop's subject.
- **apple furnishes 0 requests** where it furnished 5 (`test_escalation_wiring`): all five escalating
  decisions are now superseded. The residue candidate mints no decision (R69), so it furnishes
  nothing — consistent, but whether a DATAGRID_RESIDUE should furnish is not settled here.
- **[[R202]] bounds § 1g's instrument, not the repair**: where `len(reports) != len(bands)` the
  contested-line probe abstains. The shipped code indexes `pages[p].regions[idx]` by the band index
  the adoption contract already pins, so it does not depend on that probe.
