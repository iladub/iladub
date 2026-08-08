---
title: The data grid — defining the data before detecting it
type: concept
sources:
  - docs/superpowers/specs/2026-08-08-data-grid-types-elements-axioms.md
  - vocab/ontology/tab-datagrid.ttl
  - src/iladub/etkl/datagrid.py
  - tests/etkl/test_datagrid.py
  - src/iladub/etkl/compile.py
related: ["[[table-holon-compilation]]", "[[decision-holon]]", "[[corpus-harness]]", "[[assert-propose-promote]]"]
confidence: high
updated: 2026-08-08
---

# The data grid — defining the data before detecting it

**The data grid is data; everything else in a table is metadata — data about data.** So the
data *sensu stricto* must be identified and proven before any header, stub or annotation is
considered. This is Wang's distinction (entries versus categories) taken as an ordering
constraint rather than a taxonomy: *if you need the header to find the grid, you have inverted
it.*

## Why this exists

Every grid-adjacent class in `tab.ttl` is documented **"transient … never asserted into a
holon"**, and the grid itself was produced by `grid.py:infer_leaf_grid` — procedural Python with
**three tuned constants** and a docstring section headed *"Tuning guidance"*, plus a fabricated
confidence (`rows ÷ 4`, capped at 1). Every downstream AXIOM consumed it unexamined:
`classify-kind.rq`'s entire grid content is `?nc = grid.ncols`.

So the most load-bearing object in the pipeline had no definition, no identity, no provenance
and no decision record. Several loops of careful axiomatic work sat on top of an unexamined
procedural premise — and the sequence of failures that produced this page were all the same
failure: **detectors for an undefined object.**

## The definition

> A data grid is a **maximal rectangle whose rows and columns are admitted together**. Columns
> are admitted because the rows agree on their type; rows are admitted because the columns
> agree on their shape. Neither axis is derived first.

Two properties of the definition are load-bearing and were each earned by a measured failure:

- **The column universe is fixed once and never re-derived.** Re-deriving it from the growing
  row set changes the columns' identity between rounds, so the operators are not a closure and
  do not converge (measured: the union form collapsed cbh 49→3 rows, the intersection form
  collapsed apple to 1 of 44). It resembles formal concept analysis but is *not* a Galois
  connection — that claim was made in the ontology and retracted in it.
- **Candidate generation is free.** Rows sharing a structural signature necessarily share a run
  count, so their positional slots *are* the candidate columns. No gutter percentage, no minimum
  bin count, no sample target — the three constants that started this.

## Where the columns come from

| Term | What it is |
| --- | --- |
| `tab:DrawnRule` | a mark that **contains no glyph centre**. A fill contains the text it sits behind; a rule contains nothing. Presence test, no thinness ratio — apple page 0 reports 678 "vertical rules" when fill edges are counted and exactly **2** when they are not |
| `tab:DecorationUniverse` | columns between drawn rules, each ink-witnessed. Preferred **only when it resolves at least as finely as alignment** — an ordinal comparison. Preferring it unconditionally cost stem every row, since its three drawn marks are page borders |
| `tab:AlignmentUniverse` | columns from the gaps between seed rows' run extents. Carries the whole load on borderless documents |
| `tab:SeedFollowsUniverse` | the seed is the modal class in **whatever universe supplied the columns** — occupancy under decoration, signature under alignment. Getting this wrong cost capacity 19 of its 27 rows |

## The typology, decided from the data alone

No header is consulted, because on these definitions it cannot be — the header is not yet known.

- `tab:UniformGrid` / `tab:MixedGrid` — by the count of distinct column families.
- `tab:AggregatingGrid` — by **exact arithmetic**, not indentation. Indentation is measurably
  *inverted* for aggregates: apple's `Total current assets` sits at x=88.6, deeper than its own
  members at 70.6, while the stem's totals sit shallower. Indentation says a boundary is here;
  it does not say which side is the parent.
- `tab:StackedGrids` — two grids sharing a column extent.

## Index columns: repeated cells *are* indentation

The stem prints year and month once per group and **reprints the port on all 33 rows**. All
three are the same kind of thing — a row-axis category level, and therefore metadata. The
difference is typographic: *"Repeat item labels"* is a **per-field** PivotTable print option
([`PivotField.RepeatLabels`](https://learn.microsoft.com/en-us/office/vba/api/excel.pivotfield.repeatlabels)),
available only in tabular form. The mystery is a checkbox.

The discriminator is arithmetic, never vocabulary — reading the word "Total" would be
English-specific and is forbidden:

- **G8 `tab:AggregateWitness`** — a column is an index column when rows exist whose measures
  reconcile **exactly** with the rows sharing a value in it. `Mackay Total` is arithmetic
  nonsense unless `Mackay` names a group. Measured: 12 of 15 port-level totals reconcile.
- **G9 `tab:Groupability`** — equal values are **adjacent**, evaluated *within the parent group*.
  Adjacency not sortedness, so no order relation, collation or date parsing is needed. A global
  test is wrong: stem's ports are contiguous within each month and not across the page.
- **R6 `tab:SortedWithoutAggregate`** — groupable but never aggregated means the sort was
  presentational, so the column stays **data**. Conservative per §7, and it costs recall
  honestly: WHO's age index is a real category with no totals, because z-scores cannot be summed.

Excel's Subtotal command requires sorting by the grouping column first and then outlines the
list automatically — so *sort → group → aggregate* is the native authoring order, and outline
indentation is its by-product.

## The admission record

The grid is an **asserted object** carrying the record of its own admission, so *"why is this
the data grid?"* is answerable from the graph rather than from a Python dict:

```sparql
?d a dec:DecisionHolon ; dec:chosen ?grid ; dec:optionSpace ?candidate .
?grid tab:conformsTo tab:ColumnHomogeneity , tab:RowAddressability , … .
?rejected a tab:RefusedRow ; dec:rejectedBecause "HeterogeneousColumn/every-measure" ;
          prov:wasDerivedFrom <…#p0-line6> .
```

Every refused line is carried with its reason and provenance (§5). This is the **first
producer** for the differential half of `dec.ttl` — `optionSpace`/`chosen`/`rejectedBecause`
had never had one. The emitted graph crosses the closed-world membrane unchanged.

## Measured state

Four transcribed oracles, complete and sound — **162 of 162 entry rows, zero metadata admitted**:

| page | recall | leaked |
| --- | --- | --- |
| apple p0 | 31/31 | none |
| apple p1 | 28/28 | none |
| stem p0 | 57/57 | none |
| ons p7 | 46/46 | none |

Wired into `compile_tables` as a **fallback** where a page produces nothing at all (ons p7/p8,
0 → 276 cells each), with **adoption** — exact withdrawal of an escalation — implemented behind
`datagrid_adopt`, off by default. stem's document compile is unchanged at `0.9654553611484971`.

## The methodological lesson

Recorded because it cost several rounds and was caught twice by transcription, never by
reasoning: **row counts on unverified pages are not evidence.** A carve-out justified by row
counts on pages without an oracle turned out to be admitting ons's title and both footnotes as
data; and a rule that *dropped* cbh from 55 rows to 46 was a correction, not a regression — four
of the lost rows were reprinted headers and five belonged to a second table.

Relatedly: when two successive fixes trade one error for another, the defect is upstream of
both. Two refinements each fixed one failure mode and created another while the column universe
stayed wrong; fixing the universe moved four pages at once and cost nothing.

## Open

- **R73** — adoption is implemented and measured but not enabled: `compile_document` compiles
  pages standalone before carriage, and stem's continuation pages escalate standalone *by
  design* (R29) so carriage can happen. Both would adopt.
- Five corpus pages remain untranscribed (cbh, capacity, who, bfs, apple p2), so their numbers
  are not yet evidence.
- The axioms are Python, not SPARQL. §8 says they belong in `.rq` over the evidence graph; the
  four oracles make that migration checkable as a differential.
