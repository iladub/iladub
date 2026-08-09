# The aggregate witness as a row-admission axiom (R75) — design

**Date:** 2026-08-09 · **Status:** design, approved · **Residue closed:** R75 ·
**Residue amended:** R74 · **Specimen:** `corpus/ag-trade/cbh-stem-2026-08-03.pdf` page 0
(the fifth transcribed oracle), with `corpus/financial/apple-fy2026q3-statements.pdf` page 0
as the control · **Builds on:** `2026-08-08-data-grid-types-elements-axioms.md` (the data
grid, closed)

**Doc impact:** increment — `tab:AggregateWitness` gains a second consequence in
`tab-datagrid.ttl`; `tab:DetectedAggregationRow` is reused, not extended; one wiki page
increments. No site page contradicted.

---

## 0. The claim, in one line

A measure-only row whose printed value **equals the exact sum of the rows it stands over**
is an aggregate row of the grid, not a stray — and the same arithmetic that G8 already uses
to recognise an index *column* recognises an aggregate *row*.

## 1. What R75 said, and where it was wrong

The register's R75 row states that cbh's four per-panel volume totals (lines 20, 42, 63, 74:
374,904 / 737,289 / 660,363 / 178,708) "sit alone in the Volume column with no label, so
`tab:RowAddressability` refuses them."

**Measured, and the second half is false.** Each total is a *single* ink run in column 13.
`place_indexed` requires `len(hit) >= floor` with `floor = 2` when the row carries no ink in
the index block outside the rectangle, so the row returns `None` from placement and is
recorded `unplaceable`. It never reaches G2 at all:

```
line  20: refused='unplaceable'  runs=[(812.7, 832.2, '374,904')]  cols={13: ['374,904']}
line  42: refused='unplaceable'  runs=[(812.7, 832.2, '737,289')]  cols={13: ['737,289']}
line  63: refused='unplaceable'  runs=[(812.7, 832.2, '660,363')]  cols={13: ['660,363']}
line  74: refused='unplaceable'  runs=[(812.7, 832.2, '178,708')]  cols={13: ['178,708']}
```

The guard R75 exists to preserve — apple page 0 line 5, `2026 2025 2026 2025` — is refused at
a **different stage**:

```
line   5: refused='RowAddressability/no-key'  cols={1:'2026', 2:'2025', 3:'2026', 4:'2025'}
```

It places into four measure columns cleanly and dies on the missing key. This correction is
load-bearing for the design: because the two refusals are at different stages, **lowering the
placement floor cannot readmit apple's period header**, and conversely a relaxation written
against G2 would not have reached cbh's totals at all. The register row is amended by this
loop.

## 2. What proposes, what disposes, and why they are independent

Per R76, named before anything is designed.

**PROPOSER — placement geometry. Never reads a value.**
A page line is an aggregate candidate iff it places into **at least one measure column**,
carries **no ink in the key column**, and carries **no ink in the index block** left of the
rectangle. Every term is a containment test over already-derived column boundaries.

**DISPOSER — exact arithmetic. Never reads a position.**
The candidate is admitted iff **every** occupied cell parses as a number *and* equals the
exact `Decimal` sum of that same column over the candidate's **member rows**. At least one
member must exist; a vacuous `0 == 0` never confirms (`reconciles` already enforces this,
tested at `test_datagrid.py:73`).

**Member rows** = the already-admitted rows above the candidate, back to the previous
admitted aggregate row, exclusive.

They are independent in the sense R76 requires: the proposer cannot manufacture a sum and the
disposer cannot manufacture a placement. There is no round trip replaying its own recipe, no
field that selects then confirms itself.

### 2.1 The member rule is a reuse decision, not a fit

Two candidate member rules were measured:

| rule | corpus proposals | corpus admissions |
| --- | --- | --- |
| A — the maximal *contiguous* run of admitted rows immediately above | 86 | 4 |
| B — all admitted rows back to the previous admitted aggregate, exclusive | 86 | 4 |

They are **indistinguishable on the available evidence** — same four rows, same member counts.
Rule B is chosen because `rows.detect_aggregation_rows` (loop H) already uses that shape
("back to (exclusive) the previous CONFIRMED aggregation row whose label column <= L"), so the
repo carries one member rule rather than two. This is recorded as a reuse argument precisely
because the evidence does not choose; anyone who later finds a page that separates them should
treat the choice as open.

## 3. What is measured

All figures below are `measured-on-evidence` against the shipped corpus unless typed
otherwise. Reproduced by the probe scripts described in §6.

### 3.1 The premise: all four totals reconcile exactly

| line | printed | members | sum | exact |
| --- | --- | --- | --- | --- |
| 20 | 374,904 | 10 rows (10–19) | 374,904 | yes |
| 42 | 737,289 | 16 rows (26–41) | 737,289 | yes |
| 63 | 660,363 | 14 rows (49–62) | 660,363 | yes |
| 74 | 178,708 | 5 rows (69–73) | 178,708 | yes |

10 + 16 + 14 + 5 = 45, which is exactly the vessel-row count the cbh transcription records.

### 3.2 Corpus-wide soundness: 86 proposed, 4 admitted

Run over **every page of all six corpus documents (27 pages)**:

```
TOTAL proposed=86  admitted=4
```

The four are cbh page 0 lines 20, 42, 63, 74. **Zero false admissions on any page.** The
proposer is deliberately broad — it collects titles, boxhead fragments, ONS series-code rows,
WHO plate captions, bfs footnotes — and the arithmetic removes all of them.

### 3.3 THE WEAKNESS: the arithmetic refuses nothing on real evidence

This is the finding that shapes §4, and it is the reason this spec has a falsifier section.
Census of why each of the 86 proposals is decided:

| outcome | count |
| --- | --- |
| `ARITHMETIC/admit` | 4 |
| `NO-MEMBERS/non-numeric` | 69 |
| `NO-MEMBERS/numeric` | 3 |
| `NON-NUMERIC (members present)` | 10 |
| `ARITHMETIC/refuse` | **0** |

The three `NO-MEMBERS/numeric` rows are exactly the bare period headers this axiom must keep
refusing — apple page 0 line 5, page 1 line 4, page 2 line 5. **They are refused because they
sit above every data row on their page, not because their sum fails.** The exact-sum test, as
the corpus stands, would ship with an unexercised refusal branch.

Two prior lessons converge on this: the data-grid loop found two guards unreachable by
mutation testing, and R76 records five specs blocked for exactly the shape of a disposer that
cannot actually dispose. The axiom is not wrong — it is **unfalsified rather than
demonstrated**, and §4 fixes that before any wiring is written.

### 3.4 The grid is not on cbh's score path

```
compile_tables('corpus/ag-trade/cbh-stem-2026-08-03.pdf', 0)
  -> score=0.06984126984126984  asserted=66  escalated=879
```

`datagrid_fallback` fires only when `asserted == 0 and escalated == 0`; cbh asserts 66 cells,
so the data grid never runs on that page's score path. **This loop therefore moves no corpus
score, by construction.** Its closing number is the fifth oracle's recall (§5). The score-path
counterpart is escalated as a new residue rather than smuggled into this loop (§7).

### 3.5 Prior art in this repo: `tab:DetectedAggregationRow`

`rows.detect_aggregation_rows` (loop H, residue R4) already implements this arithmetic on the
extraction path, and `tab.ttl:379` already defines the class:

> "An aggregation row DETECTED by exact arithmetic in the extraction path (loop H): a sparse
> body row whose measure equals the token-sum of its member rows. … Detection never reads
> label text — sparsity, label column and arithmetic only."

Its candidate test requires **exactly two distinct occupied columns**, one numeric (the
measure) and one not (the label). cbh's totals carry no label, so loop H's detector misses
them for the *same reason* the grid does. The grid-side axiom is therefore not a duplicate
detector but the label-less case of one rule, and it **reuses the existing class and
properties** rather than minting new ones (§5.2).

### 3.6 An unasked-for finding, bearing on R74

cbh line 75 carries `1,951,264` in column 13, and

```
374,904 + 737,289 + 660,363 + 178,708 = 1,951,264   (exact)
```

R74 records line 75 as a leak from table B (stock at port) into table A's rectangle. The
arithmetic says its *measure* is table A's grand total, printed on the same text line as table
B's title — one text line carrying two tables' ink, not a stray table-B row. R74's row is
amended with this; deriving `tab:StackedGrids` remains its own slice and is out of scope here.

## 4. The falsifiers — built FIRST

§3.3 says the disposer is inert on the corpus. Two artifacts make it reachable, and per R76
they are built before the axiom is wired.

**F1 — mutation on real evidence.** Tamper cbh's printed total by exactly 1
(374,904 → 374,905) and assert the row is refused with `AggregateWitness/no-reconciliation`.
This proves the sum is load-bearing for *admission* rather than decorative. The pattern is
already used in this repo at `tests/etkl/fixtures.py:1711` ("the tamper: off by exactly one,
never reconciles"). Type: `measured-on-evidence`, mutated.

**F2 — the negative fixture the conventions require.** A synthetic page that reprints a bare
period header (`2026 2025 2026 2025`) *below* admitted data rows, so the header has a
non-empty member run and position can no longer save the guard. The axiom must refuse it on
the arithmetic alone. Type: `measured-on-fixture`, and typed as such wherever it is cited —
it is not evidence that any real document does this.

Without F1 and F2 the axiom would be indistinguishable from one that admits any measure-only
row below a data block, and nothing in the corpus would detect the difference.

## 5. The design

### 5.1 A third pass, after the grid is closed

The witness runs in `derive_data_grid` **after `rows` is built**, not by relaxing
`place_indexed`'s floor.

Relaxing the floor would let single-cell candidates through into G2, where apple's period
header lives — coupling the fix to the guard it must not disturb. Running afterwards keeps
them decoupled: the column universe, the measure set and `key_col` are already fixed, so the
pass is **strictly additive** and cannot change the grid's identity. The §8.5
non-convergence hazard (columns re-derived from a growing row set) is therefore *structurally
excluded* rather than argued away.

Members always lie above their candidate, so a single top-down pass suffices — no iteration,
no fixed point. Admitting one aggregate can extend the member run available to a later one;
that is deterministic and is the intended reading of stacked totals.

Placement for a candidate reuses `place_indexed` with a **per-call** minimum-cell override
(`min_cells=1`) rather than a second placement implementation, so there remains exactly one
rule for reading runs into columns. The override is scoped to the witness pass alone: G2's own
placement is called exactly as it is today, so no line reaches `RowAddressability` that does
not reach it now. That is the whole of the decoupling — the floor is not lowered, it is
by-passed for candidates the arithmetic will then have to justify.

### 5.2 Emission — reuse, don't invent

`DataGrid` gains one field beside `refusals`:

```python
aggregates: dict[int, tuple[int, ...]] = field(default_factory=dict)
#   candidate line index -> member line indices
```

In `emit_data_grid` an aggregate row keeps its `tab:LeafRow` typing and additionally emits:

```turtle
?row a tab:DetectedAggregationRow ;
     tab:aggregationFunction "sum" ;
     tab:aggregates ?memberRow , ?memberRow , … .
```

This satisfies `tab:DetectedAggregationRowShape` exactly as that shape already stands
(`tab:aggregates` minCount 1, `tab:aggregationFunction` exactly 1) — **no shape edit and no
new class**. `Literal("sum")` matches the two existing producers (`document.py:925`,
`holon.py:455`), so the three sites stay one vocabulary.

`conforms` gains `"AggregateWitness"`. Safe: the emitted-graph test asserts membership
(`test_datagrid.py:383`), not set equality.

### 5.3 Refusals name the rule that actually decided

A refused candidate **keeps its existing refusal reason** (`unplaceable`,
`RowAddressability/no-key`) unless the arithmetic genuinely spoke — fully numeric, members
present, sum mismatched — in which case the reason becomes
`AggregateWitness/no-reconciliation`.

This is deliberate, not cosmetic. On this corpus the arithmetic speaks on exactly four lines
and admits all four, so stem page 0's carried-refusal count and apple's `no-key` reasons are
untouched (`test_datagrid.py:421` counts stem's refusals). The graph continues to answer
"why was this line refused?" with the rule that did the refusing rather than with the last
rule to look at it.

### 5.4 §8 classification: AXIOM

A presence-and-equality test over the evidence graph: **open world, evidence-positive** — a
row is admitted only when its supporting sum is *present*, never inferred from absence. Exact
`Decimal`, no tolerance, no tuned constant. It joins `reconciles` in `datagrid.py`'s AXIOM
section, whose module docstring already commits that section to migrating to SPARQL unchanged.

Loop H classified its own aggregation detector PROCEDURAL, justified as "decidable exact
arithmetic … a SPARQL formulation of nested running-sum windows would be obfuscation, not a
lift." That justification is about the **nested** form. The grid-side form is a single
unnested window (sum over a bounded run of rows), which is a plain `SUM` with an ordinal
bound and is expressible as written. The divergence is stated here rather than left for a
reviewer to trip over.

### 5.5 The honest limit, recorded not hidden

A multi-level total whose members are themselves totals will not reconcile against a member
run that contains both levels, and is refused. This is G8's own stated limit — "the axiom is
sound, not complete" — and matches loop H's "zero-member candidates … are never confirmed —
honest refusal." cbh line 75 is exactly this case and stays out of scope per §3.6.

## 6. Verification

**Closing evidence.** `test_cbh_p0_known_defects_are_pinned_not_hidden` currently pins
`assert not (admitted & CBH_P0_PANEL_TOTALS)`. That pin is what R75 removes; it inverts into a
positive test asserting all four admitted, each with its measured member count (10 / 16 / 14 /
5) and its exact sum. The table-B pin on line 75 stays unchanged. Fifth-oracle recall moves
**45/49 → 49/49 entry rows, with zero metadata admitted.**

**Regression surface — measured, not argued:**

- the other four oracles unchanged: apple p0 31/31, apple p1 28/28, stem p0 57/57, ons p7 46/46
- stem's document compile still `0.9654553611484971` (the only adjudicated floor)
- full corpus numbers unmoved — which follows from §3.4 but is measured rather than asserted
- `pytest` green, including `test_source_ownership.py` and `test_doc_governance.py`

**The two falsifiers of §4 must both fail before the wiring lands**, and both must pass after.

## 7. What is NOT done here

- **`rows.detect_aggregation_rows` is not touched.** cbh's four totals are missed on the
  *score* path too, for the identical no-label reason, and fixing that would move
  cbh p0 from 0.0698 to roughly 0.074 (4 cells of 945). Deliberately out of scope: it is a
  second detector with a second oracle, and loop H's nesting rule is the riskier thing to
  disturb. **Escalated as a new residue** so the next loop does not rediscover it.
- **Multi-level aggregation is not attempted** (§5.5). No transcribed oracle exists for it.
- **`tab:StackedGrids` is not derived** — R74 stays open, with its premise corrected (§3.6).
- **No new vocabulary class is minted.** `tab:DetectedAggregationRow` is reused (§3.5, §5.2).

## 8. What this loop records

- `docs/superpowers/residues.md` — R75's row **deleted** in the same change that closes it;
  R74's row **amended** with the grand-total arithmetic; a **new row** for the extraction-path
  counterpart named in §7.
- `vocab/ontology/tab-datagrid.ttl` — `tab:AggregateWitness`'s comment extended with its
  **second consequence** (row admission), keeping the `tab:IndexColumn` consequence intact.
  One axiom, two uses.
- `docs/wiki/concepts/data-grid.md` — increment.

## 9. Premise types (R76)

| premise | type |
| --- | --- |
| the four totals reconcile exactly (§3.1) | measured-on-evidence |
| the refusal is `unplaceable`, not G2 (§1) | measured-on-evidence — **corrects the register** |
| apple's period header is refused at G2 (§1) | measured-on-evidence |
| 86 proposed / 4 admitted corpus-wide (§3.2) | measured-on-evidence, 27 pages |
| the arithmetic refuses nothing on real evidence (§3.3) | measured-on-evidence — **the weakness** |
| member rules A and B are indistinguishable (§2.1) | measured-on-evidence |
| the grid is not on cbh's score path (§3.4) | measured-on-evidence |
| line 75 is table A's grand total (§3.6) | proven-algebraically from measured cells |
| loop H's detector requires a label (§3.5) | read-not-run — its own docstring and shape |
| the period header stays refused when position cannot save it | **measured-on-fixture (F2), to be built** |
