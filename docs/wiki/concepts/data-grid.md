---
title: The data grid — defining the data before detecting it
type: concept
sources:
  - docs/superpowers/specs/2026-08-08-data-grid-types-elements-axioms.md
  - docs/superpowers/specs/2026-08-09-aggregate-witness-row-admission-design.md
  - docs/superpowers/specs/2026-08-09-adoption-at-document-scope-design.md
  - vocab/ontology/tab-datagrid.ttl
  - src/iladub/etkl/datagrid.py
  - src/iladub/etkl/adoption.py
  - tests/etkl/test_datagrid.py
  - tests/test_corpus_stem.py
  - src/iladub/etkl/compile.py
  - src/iladub/etkl/document.py
related: ["[[table-holon-compilation]]", "[[decision-holon]]", "[[corpus-harness]]", "[[assert-propose-promote]]"]
confidence: high
updated: 2026-08-09
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
  reconcile exactly with the rows sharing a value in it; and, by the **same arithmetic**, a
  *measure-only row* is an aggregate row of the grid when every occupied cell equals the exact
  `Decimal` sum over the rows it stands over (the admitted rows above it, back to the previous
  aggregate, exclusive). One axiom, two uses. Measured on cbh page 0: the four label-less panel
  totals (374,904 / 737,289 / 660,363 / 178,708) are admitted over 10, 16, 14 and 5 members;
  corpus-wide 86 rows are proposed and exactly those 4 admitted. Such a row is typed with loop
  H's existing `tab:DetectedAggregationRow`, not a grid-side twin. *(confidence: high — five
  transcribed oracles, mutation-checked.)*
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

### The membrane does not validate against this module — decided, not overlooked

`compile._FULL_ONT` is built from `tab.ttl` + `dec.ttl` + `iladub.ttl`. **`tab-datagrid.ttl` is
deliberately absent** (R103, decided 2026-08-20), and it is worth knowing why, because the
absence looks like a gap and is not one.

`membrane.subclass_closure` reads *only* `rdfs:subClassOf` out of the ontology graph and never
mixes the ontology into the validated payload — the graph an engine sees is the page data plus
its own type closure, and **no ontology subject ever reaches an engine**. So adding a file to
that list can move a verdict by exactly one mechanism: an axiom `Sub ⊑ Super` materialising
`Super` on a node typed `Sub`, where a shape can reach `Super`. This module contributes six such
axioms and every one is inert — `datagrid.py` already emits `tab:DataGrid` *and* the grid's
subtype explicitly on the same node, two of the classes are emitted nowhere, and the universe
classes appear only as the object of `tab:universeSource`, never as an `rdf:type`.

Measured over all 7 corpus documents (27 pages): admitting the file produces a **closure delta of
0 triples** and leaves every verdict identical. Confidence: high — this is a measurement, and the
condition that would reverse it is pinned by
`test_tab_datagrid_axioms_are_unreachable_by_every_membrane_shape`.

The consequence to carry: this module's `rdfs:domain`/`rdfs:range` declarations are **documentation
of the emitter's contract, not constraints the membrane enforces**. Where the emitter and this
vocabulary disagree, only `scripts/probe_domain_range_agreement.py` can say so (see R61).

## Measured state

Four transcribed oracles, complete and sound — **162 of 162 entry rows, zero metadata admitted**:

| page | recall | leaked |
| --- | --- | --- |
| apple p0 | 31/31 | none |
| apple p1 | 28/28 | none |
| stem p0 | 57/57 | none |
| ons p7 | 46/46 | none |

Wired into `compile_tables` as a **fallback** where a page produces nothing at all (ons p7/p8,
0 → 276 cells each).

## Adoption — the document's last reader

**Adoption** is the exact withdrawal of a page's escalation in favour of the grid's reading. It
belongs to the **document**, not the page: `compile_document` asks only after the driver has had
its chance — after carriage, after section repair — so a page adopts only where the shipped
reader, with everything the document could give it, still read nothing at all.

The page-scope flag (`datagrid_adopt`) stays **off by default**, and the reason recorded before
this loop was wrong. It used to say the driver compiles each page standalone before re-compiling
continuation pages; measured, the driver makes **one pass** and page N-1's carried reading is an
*input* to page N's compile, so forcing adoption on every page leaves the stem document
byte-identical at `0.9654553611484971`.

The real reason is the **refusal branch**, and its first half is structural, not numeric: a
single-page compile is **incapable of chaining at all** — `CompilationReport` carries no chain
concept; chains exist only on `DocumentReport`. Whatever a page scores standalone, it can never
see the pages it continues onto.

The score corroborates it, **on the same page under both scopes**: stem p1 compiled standalone
with adoption reads *flat* and scores **`0.9588`**, while the driver's own reading of that same
page 1 scores **`0.9706`** (measured in Loop M, recorded at `residues.md` R29). Page scope is
refused not because the isolated reading would score deceptively higher, but because it scores
measurably **lower**. *(The two cell counts are not comparable and are not being compared: R29's
figure is 825 **tokens** asserted under the driver, the standalone figure is 811 **cells** —
only the two scores share a scale.)* At document scope the whole stem is one chain of 3, 2152
cells, at `0.9654553611484971`.

The withdrawal ledger is **line-granular**, and that is what keeps adoption honest: zeroing the
escalation would score any adopted page a perfect `1.0000` whatever the grid missed, and
withdrawing band-by-band would count the read lines on both sides. Only the line is a unit the
grid and the bands agree on. So an adopted page reaches `1.0000` **only if the grid read every
escalated line** — where it did not, the residue keeps escalating and the score cannot be
perfect. That is a property of the ledger's arithmetic, not a guarantee any shape or test
enforces: `build_ledger` sums residue-line tokens plus untouched escalated bands, and a page
with neither would score exactly `1.0000`. What is *measured* is apple p1 at `0.7802` and stem
p1 at `0.9588`; the only shipped pin is `< 1.0` for apple. On apple p1 the grid asserts 142
tokens and 40 tokens survive as one `DATAGRID_RESIDUE` candidate: `0.7802`, not perfection. The
bands the grid replaced are rewritten `superseded` in place (the
band index *is* the region index), and the admission decision carries `dec:supersedes` to the
verdicts it withdrew, so `effective-chain.rq` returns the live reading rather than the retracted
one.

Measured movement at document scope: **apple `0.06068601583113457` → `0.35560344827586204`**;
stem unchanged at `0.9654553611484971`, `adopted == ()` — carriage makes its continuation pages
assert before the gate can ask.

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

- **R73 is closed** (adoption at document scope, 2026-08-09) and its stated mechanism was
  measured false — see the section above. What it left behind is registered as **R79** (the
  unread structure is one page-level candidate, not a refusal per line) and **R80** (apple p1's
  indent hierarchy — 7 group labels among 11 unread lines — is read by nobody).
- **R81/R82** — the grid's admission decision is on the accountable-verdict query surface. The
  DOCUMENT driver's copy now carries `dec:decidedBy` (the reading compiler, the same agent that
  decided the verdicts it supersedes), but `emit_data_grid` itself still emits none, the
  `dec:chosen` grid still carries no `rdfs:label`, and a refusal-free grid emits only ONE
  `dec:optionSpace` against the shape's `minCount 2` — and `compile._validate` never applies
  `dec-shapes.ttl`, so SHACL green says nothing about any of it.
- **R83/R84** — two dormant accounting exposures on the adopted page, both measured at zero on
  the whole corpus: at PAGE scope the rebuilt graph escalates nothing for a band the grid never
  touched though the report books its tokens (the document path is unaffected), and the ledger
  counts an admitted line's tokens as asserted even if no band was scoring that ink.
- Five corpus pages remain untranscribed (cbh, capacity, who, bfs, apple p2), so their numbers
  are not yet evidence.
- The axioms are Python, not SPARQL. §8 says they belong in `.rq` over the evidence graph; the
  four oracles make that migration checkable as a differential.
