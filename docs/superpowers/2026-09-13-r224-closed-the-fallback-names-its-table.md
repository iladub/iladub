# R224 closed — the fallback's region books its own ink and names its own table

**Serves:** prog:criterion:etkl:04 — this is a PREREQUISITE of that criterion, not the criterion.
The 2026-08-20 HOLD on `gov-stats/ons-index-of-services-2026-02.pdf` stands at loop close.

**Date:** 2026-09-13. **Branch:** `etkl-04-r224-repair`, cut from `main` at `2556b83`.
**Spec executed:** `docs/superpowers/specs/2026-09-13-the-fallback-that-names-no-table-design.md`,
§ 4 (I1/I2/I3 + the fixture) and § 5 (falsification). No plan was written; the spec's § 4 states
interfaces and invariants only, and the bodies are two statements.

**Doc impact: none.** No released term is declared or contradicted. Nothing queues for a release
tag and nothing blocks one.

---

## 1. What shipped

Two one-line repairs in one five-line branch, `src/iladub/etkl/compile.py:1351-1367`, the datagrid
fallback — introduced 2026-08-09 by `06c9f2bb`.

- **D1 — the returned URI is bound.** `:1359` now writes `_grid_uri = emit_data_grid(...)` and
  passes `table_uri=_grid_uri` to the `RegionReport`. The function was already declared
  `-> "URIRef"` (`datagrid.py:599-600`) and the adopt twin at `:1477` already captured it; only
  this site dropped it.
- **D2 — the branch's mark precedes its own ink.** `band_marks.append(...)` moved BEFORE
  `asserted_total += _tokens`. The ledger snapshots at the top of each band's turn and differences,
  so the mark appended here closes the LAST BAND's slot; appending it after the addition booked the
  grid's tokens onto that band.

Three oracles, and one fixture that did not exist:

- **I1 / I2** — `tests/etkl/test_fallback_region_books_and_names.py` (new). A region with
  `verdict == "asserted"` and `cells > 0` books ink, and names a table that is typed in the graph.
  Run over the synthetic fixture in CI and over all 7 corpus documents under `-m corpus`.
- **I3** — `tests/etkl/test_read_band_books_every_word.py`. Its helper now pairs report to band
  **by band index** instead of asserting `len(bands) == len(rep.regions)`, the assertion that
  *refused* this shape rather than checking it. A new test pins that no band books ink it does not
  hold on a fallback page, with the IGNORED clause load-bearing.
- **`border_only_grid_pdf`** — `tests/etkl/fixtures.py`. Draws only the two page-border verticals
  around column-aligned text, so `_build_ruled_band` re-buckets against a 2-element `xs`, fuses each
  row to one token, and the band classifies `NON_TABLE / "fewer than 2 columns"` — nothing asserts,
  nothing escalates, the gate opens, and `derive_data_grid` still reads 6×4 because it prefers
  alignment unless decoration resolves at least as finely (`datagrid.py:346`).

## 2. What was measured

All figures 2026-09-13, on this branch from `2556b83`.

**The fixture was required, not preferred.** A sweep of every single-argument fixture in
`tests/etkl/fixtures.py` found **ZERO** that trip the fallback gate (`errors: 0`, so the sweep ran
clean). The branch was reachable in CI by no synthetic page at all — which, with the three
blindnesses the spec's § 3 names, is why a 2026-08-09 defect survived to be found by measurement.

**ons, at document scope, before → after:**

| | before | after |
| --- | --- | --- |
| p7 #15 (ignored prose band, 6 words) | `a=285` | `a=0` |
| p7 #16 (grid, 276 cells) | `a=0`, `table_uri=None` | `a=285`, `…#p7-datagrid` |
| p8 #8 (ignored prose band) | `a=286` | `a=0` |
| p8 #9 (grid, 276 cells) | `a=0`, `table_uri=None` | `a=286`, `…#p8-datagrid` |

**No score moves, and this is measured on both sides rather than argued.** The full corpus sweep was
run with the repairs REVERTED (`git checkout` of the one file, then restored) and again with them
applied. All 7 documents are byte-identical:

```
cbh-stem 0.9095 · graincorp-capacity 1.0000 · graincorp-stem 0.9659 · apple 0.7188
bfs 0.4033 · ons 0.9719934102141681 · who-wfa 0.9156
tab:EntryCell 554 · tab:DataGrid 2   (ons, unchanged)
```

`tests/test_corpus.py -m corpus` passes 11/11 both ways.

**One report figure DOES move, and it is not a score.** ons `chains` goes **[1] → [1, 1, 1]**. Chain
assembly lists `r.table_uri for … if r.table_uri is not None`, so the two grids were invisible to it
and are now three SINGLETON chains. No `tab:continuesTable` is added — it stays 0 — and singleton
chains never reach the multi-member arithmetic pass. Recorded here rather than buried because it is
a real consequence of D1 that the spec did not predict.

## 3. Falsification

Per CLAUDE.md § Plan authoring discipline rule 4. Each injection was applied, run, and reverted from
a pristine copy.

- **D2 restored (original statement order):** I3 and I1 **FAIL** — *"a region claiming 24 cells books
  no ink at all"*, `assert (0 + 0) > 0`. I2 **PASSES**.
- **D1 dropped (URI discarded):** I2 **FAILS** — *"a region claiming 24 cells names no table"*. The
  corpus arm fails on ons with the recorded signature: `p7 region#0 cells=276 booked=285 uri=None
  typed=False`, `p8 region#0 cells=276 booked=286 uri=None typed=False`. I1 and I3 **PASS**.
- **The shape guard:** the extended O1 helper still pairs band-only graincorp pages 1:1 (5/5, 4/4,
  3/3) with no asserted band booking zero, and `test_border_grid.py`,
  `test_boundary_cuts_ink.py`, `test_rule_column_refinement.py` pass 25/25. The extension loosened
  nothing.

Each test failing under its OWN defect and passing under the other is the point: it is what
distinguishes these from the plan-supplied test in CLAUDE.md's defect 5, which passed with its
subject deleted.

## 4. The § 5c prediction was RUN, and REFUTED

The handoff graded it PROPOSED and ordered it run before anything was built on it. That was correct.

**Predicted:** capturing the grid URI makes ons p7/p8 eligible for `tab:continuesTable`, because
`document.py:1554` stitches only regions whose `table_uri is not None`.

**Measured, with D1 applied:** `table_uri` IS bound on both grids, and `tab:continuesTable` is still
**0**. `recognized` is `()` — the continuation axiom never fired for any page pair.

**The mechanism is broader than the prediction's own escape hatch.** `_recognition_blocks` returns
`{}` for **all nine pages**, not merely the two R225 damaged: `leaf_block` needs a vertical rule, a
recoverable leaf grid of ≥ 2 columns and a header/body split, and even p4 — which asserts 19 cells —
evidences none. So `document.py:1404`'s guard never opens. Both stitch sites index regions by BAND
index anyway (cross-page at `:1454` via `blocks`, intra-page at `:1552` via `page_section_groups`),
and the fallback's appended region sits at index `len(bands)`, so neither could name it in principle.

Raised as [[R226]]. Note the prediction also cited the intra-page stitcher for a cross-page pair;
that misreading was visible from the code, but the reason it fails is not the reason reading
suggested, which is why it was run.

## 5. The register

- **[[R224]] CLOSED** — full row moved to `residues-closed.md` with the closure evidence above.
- **[[R226]] raised** — § 4's finding.
- **[[R202]]** keeps its open half (a shared pair-by-identity helper). This loop paired by
  *index*, which is not identity; the row is untouched.
- **[[R225]] untouched and still open.** Its fork is a maintainer's ruling, not a patch.

**The structural candidate count is unchanged at 91, and that stillness is a CANCELLATION.** Closing
R224 removed R202's only open neighbour and would have returned R202 to the set; R226's prose cites
[[R202]], which replaced it. A status move and a prose move cancelled exactly. Recorded in
`tests/test_residue_graph.py`'s docstring, because an unchanged count must not be read as evidence
that no row changed status. R225 stays out for an unrelated reason, checked rather than assumed: it
cites [[R44]], which is open.

No `prog:blockedBy` edge names R224, so `tests/arc-manifest.ttl` needs no edit (checked, not assumed).

## 6. What this loop does NOT do

- **It does not meet `etkl:04`.** The 2026-08-20 HOLD stands. Route steps 1 (author the
  `cor:contract` / `cor:terms` / `cor:shapes`) and 2 (exercise the grounding leg) are untouched.
- **It pins no floor and writes no adjudication.**
- **It does not touch band construction.** [[R225]]'s refuted remedy is not attempted; the grid
  reading still exists *because* the bands are broken.
- **It does not claim ONS should stitch.** [[R226]] records that the pair would still have to pass
  the continuation axiom and the R33 licence, and nothing here has measured whether it would.
