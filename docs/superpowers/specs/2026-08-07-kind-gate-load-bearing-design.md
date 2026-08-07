# The kind gate is load-bearing — why slice B cannot start yet — design

**Date:** 2026-08-07 · **Status:** closed 2026-08-07 ·
**Opens:** R71 · **Blocks:** slice B of the reading-as-differential-diagnosis
architecture (`2026-08-07-reading-decision-record-design.md` §7) ·
**Specimen:** `corpus/ag-trade/graincorp-stem-2026-07-31.pdf`, page 0 region 2 and
page 2 region 1

**Doc impact:** none — no vocabulary, no query, no `src/` change, no site page
touched. The deliverable is a measurement, a residue row, and a regression guard.

## 1. What this loop set out to do, and why it stopped

Slice B was to replace the three-value `RegionKind` enum with a carried set of
topology candidates narrowed by observation rather than by an early Python branch.
The agreed shape was a **vertical** slice: not a modelling change, but a capability
one — recover a table iladub currently misses, proven by a corpus score moving up.

**That goal has no target.** Measured across the whole corpus, there is no region
where the kind gate suppresses a topology that would have succeeded. In the only two
places it suppresses anything, it is *protecting a correct outcome*.

This loop therefore ships the measurement instead of the refactor. Building slice B
on the assumption that was refuted here would have cost 1,327 of stem's 2,152
asserted cells.

## 2. The conflation that motivated slice B — still real

`classify-kind.rq` asks exactly one question: *does the header line have exactly
`ncols` words, each strictly inside its own column?* That is **header regularity**.
Its binary outcome then decides which topologies are even considered:

```
kind
├── NON_TABLE          → ignore
├── RECORD_TABLE       → transposed? → coherent? → tiles?
│                      → row_grouped? → tiles?
└── UNSUPPORTED_TABLE  → matrix_candidate? → tiles?
                       → hierarchical? → tiles?
```

So `transposed` and `row_grouped` are unreachable for an irregular-header band, and
`matrix` is unreachable for a regular-header one — not because evidence refuted them,
but because a Python branch never offered them. The critique stands. What this loop
found is that *acting on it naively regresses the corpus*.

A second coupling makes it sharper. `regions.py:109` assigns `cells` **only** for
`RECORD_TABLE`. The gate does not merely skip the transposed test on an
irregular-header band — it withholds the evidence that test consumes. Carrying
candidates therefore means building the evidence for all of them *before* narrowing,
which is a larger change than the enum swap it looks like.

## 3. The measurement

For every band of every corpus document: classify it, assign cells regardless of kind
(the evidence the gate withholds), then run the oracles its branch would never reach.
A band is **suppressed-positive** when it is `UNSUPPORTED_TABLE` and `looks_transposed`
or `looks_row_grouped` returns True.

| document | suppressed-positive bands |
| --- | --- |
| apple (1p) | none |
| capacity (1p) | none |
| WHO (3p) | none |
| CBH (1p) | none |
| **stem (3p)** | **p0 region2, p2 region1** |

Both stem bands, examined:

| | p0 region2 | p2 region1 |
| --- | --- | --- |
| `kind` | UNSUPPORTED (`header has 2 words but 17 columns`) | UNSUPPORTED (`header has 1 words but 17 columns`) |
| `looks_transposed` | **True** | **True** |
| `transpose_is_coherent` | **False** | **False** |
| verdict today | **asserted**, 586 cells | **asserted**, 741 cells |
| "header" line | `['Friday, 31', 'July 2026']` | `['Date of Grain']` |

## 4. Why un-gating would regress, not recover

Both regions compile successfully today down the `UNSUPPORTED → hierarchical` path.
Un-gating `transposed` routes them instead into the transposed branch, where
`looks_transposed` is True and the coherence oracle then returns False. That branch
is not a fallback — `src/iladub/etkl/compile.py` (the `else:` after
`if is_coherent:`) calls `escalate_region(..., "TRANSPOSED", TAB.TransposedTable, 0.4)`,
adds every line's words to `escalated_total`, and appends
`RegionReport(..., "escalated", 0, "TRANSPOSED", ...)` — **zero asserted cells**.

So the two regions would go from 586 + 741 = **1,327 asserted cells to 0**, out of
stem's 2,152 — and their words would be added to `escalated_total` on top. The exact
resulting score is not stated here because it was not run: what was measured is the
cell movement and the code path that produces it. That is already decisive, and an
estimated score would be a number this loop did not earn.

**`looks_transposed` is a false positive on these bands.** Its signature is "a
type-homogeneous structured row, and no type-homogeneous structured column." Both
bands carry a **multi-row wrapped column header**: `classify_evidence`
(`src/iladub/etkl/classifygraph.py`) reads header words from `band.lines[0]` only, so
a wrapped header's narrow top line (`['Friday, 31', 'July 2026']` / `['Date of
Grain']`) is what `classify-kind.rq` sees, and it is what drives the
`header has N words but 17 columns` mismatch to `UnsupportedTableKind` — the rest of
the header is never consulted for the kind decision. Because the `UNSUPPORTED_TABLE`
path runs no header/body split, `assign_cells` (`src/iladub/etkl/regions.py`) maps
every physical line after line 0 straight to a body row — including the wrapped
header's own remaining lines — which seeds Text cells into every column and destroys
the column type-homogeneity whose *absence* `looks_transposed` tests for.

Verified by ablation, dropping leading lines from each band and re-classifying:
removing only line 0 (the line `region.reason` names) leaves `looks_transposed=True`
on both bands; only stripping the *entire* wrapped-header block — 3 lines on p0, 2 on
p2 — flips both to `RECORD_TABLE` with `looks_transposed=False`. The coherence oracle
catches the resulting false positive regardless — which is the R55 lesson intact:
detection is not decision.

**The finding:** the kind gate is currently doing undocumented double duty as a guard
against this false positive. Nothing recorded that, and nothing would have caught it —
a "carry all candidates" refactor would have looked principled and lost the majority
of stem's asserted cells.

## 5. What ships

1. **This spec** — the measurement, so the next attempt starts from evidence.
2. **R71** in the register — the kind gate's load-bearing role and its closing condition.
3. **`tests/etkl/test_kind_gate_is_load_bearing.py`** — an executable guard pinning, on
   the two real stem bands: `looks_transposed` is True, `transpose_is_coherent` is
   False, and the band's kind is `UNSUPPORTED_TABLE`. If a future loop carries
   candidates without hardening the oracle first, this fires with the reason attached
   instead of the corpus silently dropping 1,327 cells.

   Most of it uses `page_bands` + `classify` on two pages directly, which costs seconds.
   One test, `test_page0_region2_still_compiles_through_the_unsupported_path` (added in
   fix round 1, recorded in §9), exercises the real routing via `compile_tables` on page
   0 and costs ~10s. Page 2 region1's 741-cell path is not guarded at that level — it
   requires `compile_document`'s cross-page header carry (~150s) — and that asymmetry is
   recorded in R71 rather than paid for in this file's runtime. It is a
   **characterisation** test: it pins behaviour that is currently *wrong but
   protective*, and its docstring must say so, or a later reader will mistake it for an
   endorsement of the false positive.

## 6. Success criteria

- The suppressed-positive scan is reproducible from the method in §3, and its result
  table is recorded here.
- The guard fails if either stem band's `looks_transposed` / `transpose_is_coherent` /
  kind triple changes — verified by inverting one assertion and observing the failure.
- **No `src/` change**, so no verdict can move; corpus scores unchanged.
- R71 states the closing condition precisely enough that slice B can be re-planned
  against it without re-deriving this measurement.

## 7. What slice B needs before it can start

- **Route the transposition oracles' evidence through a header/body split, not the
  raw per-line cell grid.** `looks_transposed` and `transpose_is_coherent`
  (`src/iladub/etkl/orientation.py`) both treat `region.cells` row `0` as the header
  and every row `>= 1` as body — correct only when the header is exactly one
  physical line. For the two bands measured here the header is a multi-row
  *wrapped* column header (§4); `assign_cells` (`src/iladub/etkl/regions.py`) has no
  concept of that and maps every physical line straight to a row, so the wrapped
  header's own trailing lines are read as body, seed Text cells into every column,
  and manufacture the transposition signature. `vocab/queries/header-body-split.rq`
  already exists and is already consumed, via `header_body_split`
  (`src/iladub/etkl/headers.py`), by the RECORD_TABLE / matrix / hierarchical
  paths — the fix is routing the orientation oracles' body-cell evidence through
  that same split, not writing a new query. Per the gate (CLAUDE.md §8) this is an
  AXIOM change to the evidence a `SELECT`/`ASK` query consumes over an open-world
  grid, not a tuned threshold — the no-tuned-threshold constraint carries forward
  unchanged.
- **Then** the candidate set can be carried, because the evidence that narrows it will
  no longer contain a known false positive.
- **R10 was considered as the root cause and is refuted, not merely unproven, by
  this branch's own measurement.** R10 records that `detect_bands` cuts one line too
  high, leaving the report date inside the band, and this spec originally guessed
  the leading line these two regions read as a header was that same defect. The
  ablation in §4 rules it out: on p0, removing only the leading date line
  (`['Friday, 31', 'July 2026']`) leaves `looks_transposed=True`; on p2 the band
  carries **no report date at all** (`['Date of Grain']`) and fails identically. So
  even a full fix of R10 — deleting the report-date line from both bands — would not
  change either band's classification or oracle result. R10 remains open as its own
  residue (a real `detect_bands` defect on its own terms) but is not the cause of
  the kind-gate/`looks_transposed` interaction this spec measures; the wrapped-header
  / missing-header-body-split mechanism above is.

## 8. Global constraints (carried, per CLAUDE.md)

- **No `src/` change**, therefore no verdict change.
- No new vocabulary; no `.ttl` touched.
- §7 *only emit what the source supports* is why this loop ships a measurement rather
  than a refactor: the evidence refuted the plan, and reporting that is the result.
- The guard is a characterisation test, not an assertion that the current behaviour is
  correct. Its docstring carries that distinction.

## 9. Close-out: measured results (2026-08-07)

**Controller-run confirmation (Step 1 of Task 2), no `src/` file changed on this
branch:** `pytest tests/test_corpus_stem.py tests/test_cbh_e2e.py -q` → **13 passed in
278s** (stem 0.9655 / 2152 cells / chain [3]; CBH 0.9047). `git diff --stat` for `src/`
and `*.ttl` across the whole branch is **empty** — no source or ontology change, which
is why no verdict could move. Both figures match this document's own §6 expectation of
"corpus scores unchanged."

**The guard (Task 1), `tests/etkl/test_kind_gate_is_load_bearing.py`:** 10 tests, all
passing, none skipped. Six of the ten pin the `kind` / `looks_transposed` /
`transpose_is_coherent` triple — the first three test functions, each parametrized
over both stem bands (page 0 region2, page 2 region1). The other four pin different
facts: two parametrized instances (rename pending, see below) pin the header word
count and the `reason` string; one instance of `test_both_bands_carry_real_content`
pins both bands' cell counts (`> 100`); and
`test_page0_region2_still_compiles_through_the_unsupported_path` exercises the real
routing via `compile_tables(STEM, page_number=0)` and asserts
`regions[2].verdict == "asserted"` and `.cells == 586`. Both the oracle-fact assertions
and the routing assertion were demonstrated capable of failing (inverted, observed
FAILING, reverted) — see Task 1's report for the transcripts.

### A correction this loop discovered, not stated in §3/§4 as originally written

Compiling stem **page 2 standalone** (`compile_tables(STEM, page_number=2)`) yields
`verdict=escalated, cells=0`. Its 741 asserted cells, reported in §3's table, exist
**only** under `compile_document`'s cross-page header carry (~150s) — not from a
standalone page-2 compile. So §3/§4's cell figures are **document-level**, not
per-page-standalone; a future reader re-deriving them by compiling page 2 alone would
get 0, not 741, and would wrongly conclude this spec was in error. Page 0's 586 cells,
by contrast, are reproducible standalone in ~10s — no document-level carry is needed.
This asymmetry is also why the guard's routing test (added in Task 1's fix round 1)
covers page 0 only: a `compile_document`-based test for page 2 would cost ~150s per
run, which was judged (François) not worth adding to this file. The cost, and the
resulting coverage gap, is recorded as part of R71 rather than closed here.

### §6 criterion-by-criterion pass

- **"The suppressed-positive scan is reproducible from the method in §3, and its result
  table is recorded here."** — **Met.** §3's table is present in this document, sourced
  from the corpus-wide scan described there.
- **"The guard fails if either stem band's `looks_transposed` /
  `transpose_is_coherent` / kind triple changes — verified by inverting one assertion
  and observing the failure."** — **Met, for the triple exactly as worded.** Both
  bands' triples are pinned (parametrized `key0`/`key1` in
  `tests/etkl/test_kind_gate_is_load_bearing.py`), and Task 1's falsifiability
  demonstration inverted `test_looks_transposed_is_a_false_positive_here`'s assertion
  and observed both `key0` and `key1` FAIL, then reverted to 10/10 passing. **A
  narrower claim this criterion does not, on its literal wording, cover: a routing
  change that leaves the triple untouched but drops asserted cells to zero.** Task 1's
  review found exactly that gap and closed it for page 0 only
  (`test_page0_region2_still_compiles_through_the_unsupported_path`, pinning
  `verdict == "asserted"`, `cells == 586`). Page 2 region1's 741 cells have **no**
  routing-level guard — only the oracle-fact triple is pinned for that band. A future
  refactor that changes routing (e.g. removing the `RECORD_TABLE`/`UNSUPPORTED_TABLE`
  branch in `compile.py`) while leaving `classify()`'s and the orientation oracles'
  outputs unchanged would pass all 10 tests in this file while silently dropping page
  2's 741 cells. This is recorded in R71's Measured column rather than silently
  accepted.
- **"No `src/` change, so no verdict can move; corpus scores unchanged."** — **Met.**
  Controller's `git diff --stat` for `src/` and `*.ttl` is empty across the whole
  branch; the corpus run above reproduces the same 13 passed / 0.9655 / 2152 cells /
  chain [3] / 0.9047 figures the brief expected.
- **"R71 states the closing condition precisely enough that slice B can be re-planned
  against it without re-deriving this measurement."** — **Met.** R71's *what would
  close it* column names routing the orientation oracles' evidence through a
  header/body split (`vocab/queries/header-body-split.rq`, already consumed
  elsewhere via `header_body_split`) as an open-world AXIOM change, explicitly not a
  tuned Python threshold, per §7 — and its *why deferred* column records that R10
  was checked first, as §7 required, and refuted rather than confirmed. It also
  carries a separate closing note for the routing-coverage gap this section
  describes.

**Summary: three of four §6 criteria are met without qualification; the second is met
exactly as worded (both bands' triples are pinned and demonstrated falsifiable) but
carries a narrower practical guarantee than "the corpus's 1,327 cells are protected" —
that stronger guarantee holds only for page 0's 586 cells at the routing level. Page
2's 741 cells remain protected at the oracle-fact level only, a gap this document and
R71 both now record rather than obscure.**
