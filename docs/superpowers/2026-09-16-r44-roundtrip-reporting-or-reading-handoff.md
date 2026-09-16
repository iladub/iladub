# Handoff — § 5c's fork resolved: reporting, not reading; and adoption has three defects of its own

**Topic:** [[R44]] § 5c resolved — with adoption suppressed all four concealed `ROUND_TRIP_FAIL`
return live, and the adopted grid reads 27 of 27 rows' values correctly, so the round-trip half is a
**reporting** defect and must not be built as the prior handoff proposed. The reading defects are in
adoption: [[R238]] and [[R239]].

**Serves:** prog:criterion:etkl:05 — bfs. R44 gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-16. **Tree:** branch `r44-roundtrip-reporting-or-reading`, cut from `main` at
`91430d2`. **No shipped file edited. No behaviour changed.** One instrument added, measurement only.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — R44's round-trip half is a REPORTING defect. Do not build the round-trip repair.

Measured, evidence § 5: with adoption suppressed all four concealed `ROUND_TRIP_FAIL` return live
(4 of 4, and the reason multiset is preserved exactly), **and** the adopted grid that supersedes
them reads **27 of 27** rows' values identically to the source. The numbers `region_round_trips`
rejects are already correct in the graph.

So the 2026-09-15 § 5c proposal — *"the next BUILD subject is probably p5's round-trip mechanism"* —
is **answered and should not be built as stated**. Repairing the round-trip check would move a
verdict, not a reading.

### 5b. ASSERTED — the reading defect is in ADOPTION, and it is [[R238]]

The adopted grid drops **the canton label column on all 27 rows** and **the final "Variation en %"
column**. 404 numeric cells assert with no row identity: nothing in the graph says which row is
Zurich. That is a reading defect, it is real, and no criterion names it.

### 5c. ASSERTED — column assignment is keyed on noise, and it is [[R239]]

25 rows put the intercantonal balance in col 9; Zurich and Bâle-Ville put it in col 8. The boundary
sits at x0 ≈ `374.44` and a **0.04 pt** difference decides it. The obvious cause (4-digit negatives)
was checked and **refuted** — `- 2 425` and `- 1 564` are 4-digit negatives in col 9.

The structural fault: these cells are right-aligned, x1 spread **0.1 pt**, x0 spread **12 pt** with
digit count. Keying the column on `x0` keys on the edge carrying no column information. [[R208]]
family.

### 5d. PROPOSED — the next build is probably [[R239]], and this loop did not test the remedy

**Rests on a judgement not measured here.** R239 is the most bounded of the three: one keying
decision, a visible structural argument, and a falsifiable prediction (re-key right-aligned numeric
columns on span or x1 and the two drifted rows join the other 25).

**Why it may be wrong, stated before anyone builds it:** nothing here measures what re-keying does
to columns that are *not* right-aligned numerics — a label column is left-aligned, and a rule keyed
on x1 would be exactly as wrong for it as x0 is here. If the fix must first classify a column's
alignment, that classification is itself a reading judgement and a § 8 call, not a one-line change.
**Measure first:** across the corpus, how many columns are right-aligned numerics, and does keying
on span rather than x0 change any assignment that is currently correct? If it regresses even one,
the remedy is a different class.

The **§ 8 classification for R238 and R239 remains the maintainer's** and is deliberately not made
here.

### 5e. ASSERTED — what NOT to do

- **Do not build a round-trip repair to fix bfs p5's numbers.** They are already right (§ 5a).
- **Do not assume what p5 region16 `DATAGRID_RESIDUE` contains.** It reports `cells=0` and empty
  `ascii`. That it holds the dropped labels and % column is plausible and **unverified**.
- **Do not read the escalated regions' `ascii` as the reading.** It is a truncating renderer;
  `Berne 05437` is really `1 051 437` (evidence § 5.1).
- **Do not pin a `cor:scoreFloor` for bfs.** The 2026-08-20 hold stands; this loop strengthens it
  again — the score is 0.8851 while the page asserts no row labels at all.
- **Do not trust the `tab` rung's `file:line` citations or `FIRES n` counts** — [[R236]], [[R237]],
  both still open.

---

## 1. Where the primaries are

- **This loop's evidence** — `2026-09-16-r44-roundtrip-reporting-or-reading-evidence.md` (§ 3 leg 1,
  § 4 the broken join, § 5 leg 2 and the 27/27 oracle, § 6 the three grid defects, § 7 what is not
  measured).
- **The instrument** — `scripts/r44_adoption_suppressed.py`, control inline, exits non-zero if the
  control fails. Persists both runs to JSON so later joins cost no compile:
  `PYTHONPATH=src:. .venv/bin/python scripts/r44_adoption_suppressed.py <outdir>`.
- **The prior loop** — `2026-09-15-r44-bfs-triage-handoff.md`, whose § 5c this loop ran.
- **The rows** — [[R44]] updated; [[R238]] and [[R239]] raised by this loop.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The four concealed ROUND_TRIP_FAIL do return live (4/4) | evidence § 3, R44's row |
| The adopted grid reads 27/27 rows' values correctly | evidence § 5, R44's row |
| R44's round-trip half is a REPORTING defect | this § 5a, R44's row |
| The grid drops the label column and the % column | [[R238]] |
| Column assignment keyed on x0 is decided by 0.04 pt | [[R239]] |
| "4-digit negatives shift column" — refuted | evidence § 6.1 |
| **What to build for R238/R239** | **UNDECIDED — a § 8 classification, the maintainer's** |

## 3. Unverified or assumed

- **§ 5d entirely** — that R239 is the next build, and that re-keying does not regress
  non-right-aligned columns.
- **What p5 region16 actually holds** (evidence § 7). One compile answers it.
- **Whether the three grid defects are general or bfs-p5-specific.** One document, one page.
- R44's two long-standing unreconciled figures (`RECORD_TABLE` 8 vs 7+2, `chains` 7 vs 6) are
  untouched.

## 4. What this session did, and what it cost

Took the subject from the strip's ready set on the maintainer's ruling, ran both legs of the prior
loop's § 5c, resolved its fork to the second disjunct, found three unnamed defects in adoption, and
raised two rows. Built no remedy, edited no shipped file.

**The cost worth carrying: the loop's first answer was wrong and its control passed anyway.** The
per-region join keyed on `anchor` — the anchor *class* IRI, identical on every escalated region —
and printed "20 of 4 subjects returned live". The control validates the two RUNS; nothing in it
reached the join laid over them. The repair was not a better key but a **stated precondition**: the
join now refuses itself unless every key is unique within each run, and it duly refused on its first
run (the masthead band, `ignored` identically on five pages).

That is the previous loop's repair #4 — *a positive result is not self-interpreting* — recurring one
loop later, written by someone who had just read it. **A second instance of the same class landed
inside this loop**: the escalated regions' `ascii` reads as corrupted digits and is merely a
truncating renderer, and the coordinate check refuted this loop's own first explanation of the
column drift. Three times in one session the first reading of a measurement was wrong; each time a
second, independent measurement caught it.
