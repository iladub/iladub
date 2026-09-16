# Evidence — R44's round-trip half is a REPORTING defect; adoption's own reading has three

**Serves:** prog:criterion:etkl:05 — bfs. R44 gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-16. **Tree:** branch `r44-roundtrip-reporting-or-reading`, cut from `main` at
`91430d2`. **No shipped file edited. No behaviour changed.** One instrument added, measurement only.

**Doc impact: none.**

---

## 1. What was asked, and by whom

The 2026-09-15 handoff's § 5c was typed **PROPOSED** and named the measurement that had to precede
any build:

> with adoption suppressed, do the four superseded regions return as live ROUND_TRIP_FAIL, and does
> the adopted grid's reading of those rows agree with what the round-trip check rejects? If adoption
> already reads them correctly, R44's round-trip half is a **reporting** defect, not a reading
> defect, and the remedy is a different class entirely.

Both legs were run. **The second disjunct is the one that holds**, and the loop also found three
defects in the adopted grid that no criterion had named.

## 2. The instrument and its control

`scripts/r44_adoption_suppressed.py`. One command:

    PYTHONPATH=src:. .venv/bin/python scripts/r44_adoption_suppressed.py <outdir>

It compiles bfs twice — once as shipped, once with `iladub.etkl.adoption.is_adoption_candidate`
forced `False` — and persists both reports as JSON so every later join costs no compile.
`document.py:1663` imports that predicate *inside* the function body, so patching the module
attribute takes at call time; this was verified by the control rather than assumed.

Four known positives, each recorded independently of the script:

| leg | source | result |
| --- | --- | --- |
| baseline score equals a recorded `cor:reading` | `tests/corpus-manifest.ttl`, read live | PASS (2026-09-14) |
| baseline `adopted == [5]` | R224/R225 closure | PASS |
| baseline p5 asserts 404 cells | R224/R225 closure | PASS |
| **suppressed `adopted == []`** | this loop — proves the patch took | PASS |

The fourth is load-bearing: without it, a suppressed run that silently still adopted would print
"nothing returned live" and read as a refutation of § 5c while having measured nothing.

## 3. Leg 1 — the concealed failures do return

**Join-free** (no region identity required, so no join can corrupt it):

| reason | baseline live | baseline superseded | baseline total | suppressed live |
| --- | --- | --- | --- | --- |
| ROUND_TRIP_FAIL | 1 | 4 | **5** | **5** |
| KIND_NOT_SUPPORTED | 3 | 1 | 4 | 4 |
| REGION_TILING_FAILED | 2 | 0 | 2 | 2 |
| DATAGRID_RESIDUE | 1 | 0 | 1 | **0** |

The multiset is preserved exactly, everything live, except `DATAGRID_RESIDUE`, which **vanishes** —
confirming it is adoption's own artifact and not an underlying defect.

**Per-region**, joined on rendered-region text with a uniqueness precondition (§ 4): all four
subjects return, and all 12 baseline escalations join 1:1 except p5 region16 `DATAGRID_RESIDUE`,
correctly NOT FOUND when adoption is off.

    p5 region9   superseded ROUND_TRIP_FAIL -> p5 region9   escalated/ROUND_TRIP_FAIL  RETURNED LIVE
    p5 region10  superseded ROUND_TRIP_FAIL -> p5 region10  escalated/ROUND_TRIP_FAIL  RETURNED LIVE
    p5 region11  superseded ROUND_TRIP_FAIL -> p5 region11  escalated/ROUND_TRIP_FAIL  RETURNED LIVE
    p5 region12  superseded ROUND_TRIP_FAIL -> p5 region12  escalated/ROUND_TRIP_FAIL  RETURNED LIVE
    4 of 4 subjects returned live.

## 4. What this loop got wrong first — a passing control does not validate a join

The first version joined the two runs on `RegionReport.anchor` and printed **"20 of 4 subjects
returned live"**. `anchor` is the anchor CLASS IRI (`tab#HierarchicalTable`), carried identically by
every escalated region, so the join cross-produced 4 subjects against every hit.

**Its control PASSED while it did so.** The control validates the two RUNS; nothing in it reached
the analysis laid over them. Region *index* is no better (adoption changes the region list) and
neither is `table_uri`, minted `{doc}#htable{idx}` from that same index (`compile.py:1256`, `:1278`,
`:1316`). The only content-keyed identity the report carries is `ascii`, which the shipped
`corpus_verdict_snapshot.snapshot()` drops — the sole reason this instrument extracts the report
itself.

The remedy is not a better key but a **stated precondition**: the join refuses itself unless every
key is unique within each run. It duly refused on its first run — `"Communiqué de presse"`, the
press-release masthead, is `ignored` on five pages with identical rendered text. Restricted to
escalations the key is unique (11 and 12) and the join completes.

This is the previous loop's repair #4 — *a positive result is not self-interpreting* — recurring one
loop later, in a file written by someone who had just read it.

## 5. Leg 2 — the adopted grid reads every value correctly

Source truth for p5 was read straight from `pdfplumber`. The page is table **T2, "Bilan de la
population résidante permanente selon le canton, en 2023"**: 27 body rows (`Suisse` + 26 cantons).
Swiss formatting means each number is **several words** — `Zurich` carries `1 | 579 | 967`.

The adopted grid's rows **19–45 are exactly those 27 source rows, in order**. Oracle: compare the
whitespace-stripped concatenation of each grid row's cells against the same for the source row,
excluding the label and the final `%` token. It invents no column boundaries of its own.

    27 of 27 rows: grid values == source values (whitespace-insensitive)

Zurich, in full: `1 579 967` · `15 273` · `11 808` · `3 465` · `26 171` · `- 3 178` · `1 605 508` ·
`25 541` — every one correct, thousands separators preserved.

**So the values `ROUND_TRIP_FAIL` rejects are read correctly by the grid that supersedes it.** For
the numeric body, R44's round-trip half is a **reporting** defect — § 5c's second disjunct.

### 5.1 A caution that mattered

The escalated regions' `ascii` shows `Berne 05437` and `Bâle-Campagne29417`, which reads as digit
corruption. It is not: `render_region_ascii` places cells by `x0` on a fixed-width canvas and
truncates on collision. Source is `1 | 051 | 437` = **1 051 437**. Concluding "the numbers are
corrupted" from the ascii would have been this loop's second self-inflicted wrong answer.

## 6. Three defects in the adopted grid, none of them named by any criterion

1. **The label column is dropped on all 27 rows** (`label column present? False`). The grid asserts
   404 numeric cells with no canton identity — nothing says which row is Zurich.
2. **The final "Variation en %" column is dropped**: 9 source data columns, 8 in the grid.
3. **Column assignment drifts.** 25 rows place the intercantonal balance in col 9; **Zurich and
   Bâle-Ville place it in col 8.**

### 6.1 The cause of (3), measured — and the first explanation refuted

The obvious reading, that 4-digit negatives shift column, is **false**. Coordinates, via
`tab:hasBBox`:

    col8: n=2   x0 374.38 .. 374.42
    col9: n=25  x0 374.46 .. 386.49

`- 2 425` (x0 `374.46`) and `- 1 564` (x0 `374.48`) are 4-digit negatives in col9. The boundary
sits at x0 ≈ `374.44`: a **0.04 pt** difference decides the column.

The structural fault is visible in the same table. All 27 cells are right-aligned, x1 spanning
`389.13 .. 389.23` — a **0.1 pt** spread — while their x0 spans **12 pt** purely with digit count.
**Keying a right-aligned numeric column on `x0` keys on the one edge that carries no column
information.** This is the [[R208]] family: a boundary decided by coordinate noise.

## 7. What is NOT measured here

- **What ink p5 region16 `DATAGRID_RESIDUE` actually holds.** It reports `cells=0` and empty
  `ascii`, so the snapshot cannot say. The plausible reading — that the residue *is* the dropped
  labels and % column — is **unverified**. To settle it, dump the triples whose subject contains
  `region16` from a baseline compile, as § 2's instrument does for `p5-datagrid`.
- **Whether defects 1–3 are general or bfs-p5-specific.** One document, one page.
- **Whether repairing the x0 keying would make the round-trip check pass.** Leg 2 shows the grid
  reads the values correctly; it does not show what the non-adopted path would do once re-keyed.
- The two figures [[R44]] left unreconciled (`RECORD_TABLE` 8 vs 7+2, `chains` 7 vs 6) are
  untouched by this loop.
