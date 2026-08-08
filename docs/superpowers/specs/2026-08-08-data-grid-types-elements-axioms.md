# The data grid — table types, their elements, and the axioms that identify them

**Date:** 2026-08-08 · **Status:** foundation draft — types and element definitions, with
the axiom families each needs. Pending adversarial review. ·
**Supersedes as the entry point:** `2026-08-08-concurrent-sensor-table-scan-design.md`
(BLOCKED) and `2026-08-08-header-boundary-locator-measurement.md` — both of which worked on
*metadata* (headers) before the data was established, which is the inversion this document
exists to correct.

**Doc impact:** increment — this defines owned `tab:` structure. No site page contradicted.

---

## 0. The governing principle

François, 2026-08-08:

> The data grid is data and all the rest metadata, so data about data. This is why the data
> *sensu stricto* must be identified and proven before tackling the metadata topic. And since
> spatial is a key dimension, we need spatial axioms.

> I want to see: *I found the data grid because this conforms to this, this, and this, and
> refuted this, this and this — so there is no doubt that the data grid is this.* This must be
> the conjunction of a lot of sensor signals and iterative reasoning.

> Once we have the grid safely identified we are left with residues that can be headers on the
> top, more or less complex indices on the left or on the right, and potentially annotations in
> all borders. We go in sequence, but the data grid is the origin of evidence.

Three consequences, and they are binding on everything below:

1. **Data before metadata.** No element may be defined in terms of a metadata element that has
   not itself been derived from the data. In particular: *if you need the header to find the
   grid, you have inverted it.*
2. **Identification is conjunctive and records its refutations.** A grid is not "found"; it is
   *admitted* when it conforms to every axiom of its type and every competing candidate is
   refuted — with both recorded. This is CLAUDE.md §3's epistemics applied to the grid itself.
3. **Spatial axioms are first-class**, not a tie-break. §6.3 shows by measurement that no
   amount of type or repetition evidence separates a unique-typed data row from a header row;
   only position does.

## 1. Why this document exists: there is no grid axiom today

Measured, not asserted:

```
src/iladub/etkl/grid.py:92
def infer_leaf_grid(band, gutter_pct: float = 0.98,
                    min_gutter_bins: int = 3, sample_target: int = 4) -> LeafGrid:
    ...
    Tuning guidance:
      - ncols too high (column split): raise min_gutter_bins (e.g. 5 or 6).
      - ncols too low (columns merged): lower gutter_pct (e.g. 0.95).
    confidence = min(1.0, len(band.lines) / float(sample_target))
```

- **Three tuned constants** and a docstring section headed *"Tuning guidance"*, in the most
  load-bearing decision in the pipeline. CLAUDE.md §8: a tuned constant is *prima facie*
  evidence the decision belongs in AXIOM or NEURAL, and unjustified procedural code is a defect.
- The confidence is **fabricated** — rows ÷ 4, capped at 1 — and carries no evidential meaning,
  yet it propagates downstream as a decidability ceiling.
- **No `tab:DataGrid` class exists.** Of tab.ttl's 58 classes, every grid-adjacent one
  (`tab:GridCell`, `tab:GridColumn`, `tab:ClassifyBand`) is documented *"transient … never
  asserted into a holon."* The grid has no identity, no provenance, and no decision record.
- Every downstream AXIOM consumes it unexamined: `classify-kind.rq`'s entire grid content is
  `?nc` = `tab:gridColumnCount` = `grid.ncols`; `stub-data-split.rq` presupposes the grid *and*
  the header/body split; `header-covers.rq` presupposes the columns.
- `grid-region.rq` is the only grid-adjacent axiom and it decides which *lines* fall inside a
  **ruled** grid — it requires interior vertical rules, so it is inert on every borderless
  document.

So the axiomatic work of the last several loops sits on top of an unexamined procedural
premise. That is the defect this document opens.

## 2. Anchor: established prior art, not invented vocabulary

Per CLAUDE.md (align-don't-reinvent; the naming discipline), the type system anchors on the
existing table-model literature and on statistical-publishing vocabulary rather than on terms
we coin.

| Source | What it contributes | Confidence |
| --- | --- | --- |
| **Wang's abstract table model** (X. Wang, *Tabular Abstraction, Editing, and Formatting*, PhD, Waterloo, 1996) | A table is a mapping from the product of **category** (label) domains to **entries**. This is exactly the data/metadata split: entries are the data, categories are metadata. | High on the model; **verify the citation details before this leaves draft** |
| **Hurst's layered model** (M. Hurst, *The Interpretation of Tables in Texts*, PhD, Edinburgh, ~2000) | Separates graphical/physical from functional/structural from semantic layers — our sensor evidence is physical, our axioms are functional. | Medium; **verify** |
| **Statistical publishing vocabulary** (GPO/Chicago-style table anatomy) | `stub` (left label column), `boxhead` (column headers), `field`/`body` (the entries), `stub head`, `spanner` (a header over several columns), `cut-in heading` (a heading inside the body), notes. | High on the terms; **verify the style-guide attribution** |

This vocabulary is also *the author's language*, which
[[coarse-to-fine-human-reading]] requires: a statistician made a stub and a boxhead; nobody
ever made a "band".

**Mapping to François's words:** "headers on the top" = **boxhead**; "indices on the left or
right" = **stub**; "annotations in all borders" = **notes / captions**; "the data grid" =
**field** (Wang's *entries*).

> **Open item, must close before implementation:** every citation above is stated from
> knowledge, not from a fetched source. The naming discipline exists in this repo because a
> prior-art check was once skipped. Verify each before any of this is published under CC-BY.

## 3. The table types

Type is determined by **how entries are addressed** — Wang's criterion — not by appearance.
Each type is listed with the corpus instances that exhibit it, so no type is named that we
have not seen, and any type from the literature we have *not* seen is marked as such.

| # | Type | Addressing | Corpus instances |
| --- | --- | --- | --- |
| T1 | **Record / list table** | One category axis (columns = attributes); rows are records with no inherent order | stem 0–2, cbh 0, capacity 0 |
| T2 | **Matrix / cross-tabulation** | Two category axes; each entry addressed by (row category, column category); one measure | who 0–2 (age × z-score), ons 7–8 |
| T3 | **Hierarchical-stub table** | One category axis on top, a **tree** on the left (indentation or nesting), aggregates at internal nodes | apple 0–2, bfs 6 |
| T4 | **Stacked / multi-panel table** | Several grids of the same type sharing one boxhead, separated by cut-in headings | apple p0 (three panels; `Total net sales 109,417/94,036/364,357` appears three times) |
| T5 | **Transposed table** | Records run along columns instead of rows | **not exhibited by any corpus document** — R68 records that only synthetic fixtures reach this path |

T1–T4 are measured. T5 is carried from the literature and from the shipped
`tab:TransposedTable`, explicitly unexercised.

**Types are not exclusive.** apple p0 is T3 *and* T4; who is T2 with a small T1 region
(the L/M/S parameter columns). The type system must permit conjunction, so it is a set of
**properties of an addressing**, not a partition of documents.

## 4. The elements — data first, then metadata

### 4.1 `tab:DataGrid` (the field / Wang's entries) — the only DATA element

**Definition.** A `tab:DataGrid` is a maximal set of entry cells, spanning a set of columns and
a set of rows, such that every entry is addressed by exactly one path in each category axis of
its type, and every column is type-homogeneous under the shipped `tab:inDatatypeFamily`
lattice.

It is an **asserted holon object with identity and provenance** — not transient evidence. This
is the change from today, where no such object exists.

**Conformance axioms** (all must hold; the grid is admitted only on their conjunction):

| # | Axiom | Family | Status |
| --- | --- | --- | --- |
| G1 | **Column homogeneity** — every grid column has one datatype family, after dropping abstainers (`tab:Blank`, `tab:ParenthesizedNumber`) and excluding `tab:Text` | type | machinery shipped (`stub-data-split.rq` uses it, one level too late) |
| G2 | **Structural repetition** — each grid row instantiates a row signature shared by ≥2 rows | repetition | measured §6.2; presence test, no constant |
| G3 | **Rectangularity** — the grid is a rectangle in (row, column) space; every (row, column) pair inside it is an entry or a declared blank | **spatial** | to define |
| G4 | **Column alignment** — every entry of a column occupies that column's x-interval, and no entry straddles a column boundary | **spatial** | partially shipped (`confirm-boundary.rq`'s ink-witness idiom) |
| G5 | **Address completeness** — each entry has exactly one address on each axis of its type (constraint C1) | structural | to define |
| G6 | **Conservation** — no ink inside the grid's bbox is unaccounted for | membrane | **shipped** (conservation shape) |
| G7 | **Arithmetic coherence** — where aggregates exist, they reconcile exactly with the members they cover | arithmetic | **shipped** (exact `Decimal`, loop H) |
| G8 | **Round trip** — the reading regenerates the observed ink | membrane | **shipped** (`tab:ReshapeRecipe`) |

**Refutation axioms** — a candidate grid is *rejected*, and the rejection recorded, when:

| # | Refutation | Family |
| --- | --- | --- |
| R̄1 | A column is type-heterogeneous over non-abstaining cells | type |
| R̄2 | A row inside the rectangle spans it end-to-end with a single run (a cut-in heading, not an entry row) | **spatial** |
| R̄3 | An entry straddles a column boundary | **spatial** |
| R̄4 | A candidate grid is strictly contained in another that also conforms — maximality | **spatial** |
| R̄5 | The aggregate arithmetic fails | arithmetic |

**The record François asked for** — *"I found the data grid because it conforms to this, this
and this, and refuted this, this and this"* — is exactly a `dec:DecisionHolon` whose
`optionSpace` is the candidate grids, `chosen` the admitted one, `rejectedBecause` the
refutation axiom each loser tripped, and `consideredEvidence` the sensor facts. The
differential half of `dec.ttl` (`optionSpace`/`chosen`/`rejectedBecause`) was built for this
and, per the loop-decision-record spec, **has never had a producer**. This is its first real
use.

### 4.2 The metadata elements — the residue, classified by position

Derived **only after** the grid is admitted, and defined **relative to it**. Each is a residue
of ink that the grid does not account for, classified by its spatial relation to the grid.

| Element | Prior-art name | Spatial definition (relative to the admitted grid) | Type-specific? |
| --- | --- | --- | --- |
| `tab:BoxheadBlock` | boxhead | ink **above** the grid, x-contained in the grid's column span | all types |
| `tab:StubColumn` | stub | ink **left** of the grid, y-contained in the grid's row span | T1, T3 (a tree in T3) |
| `tab:RightIndex` | — | ink **right** of the grid, y-contained in its row span | not yet observed in corpus |
| `tab:StubHead` | stub head | ink above the grid **and** left of it — the corner | T1, T3 |
| `tab:Spanner` | spanner | a boxhead node covering ≥2 leaf columns | T2, T3, T4 |
| `tab:CutInHeading` | cut-in heading | a full-width single-run row **inside** the grid's row span | T3, T4 |
| `tab:Annotation` | notes / caption | ink outside the grid on any side, not x- or y-contained | all types |

Every one of these is a **spatial** predicate over the grid — which is precisely why the grid
must come first, and why spatial axioms are load-bearing rather than decorative.

**Note the earned correction:** a cut-in heading (`Net sales:`, `Operating expenses:`) is
*inside* the grid's row span and is metadata; an annotation is *outside*. The blocked spec
conflated these, and the measurement in §6.3 shows nothing but position separates them.

## 5. The axiom families

| Family | Answers | World | Form |
| --- | --- | --- | --- |
| **Type** | what kind of value is this cell | open | SPARQL over the shipped datatype lattice |
| **Repetition** | does this structure recur | open | SPARQL, count ≥ 2 — the minimal presence test for a pattern |
| **Spatial** | where is this, relative to what | open | SPARQL over interval/containment relations — **to be defined** |
| **Arithmetic** | do the aggregates reconcile | open | exact `Decimal`, justified PROCEDURAL |
| **Membrane** | may this cross into the clean holon | **closed** | SHACL, holon-scoped |

The spatial family is the gap. It needs a small, closed relation set over x- and y-intervals —
`contains`, `within`, `meets`, `overlaps`, `before`, `after`, `aligns` — and every one of those
is a **presence or ordinal** predicate, so the family can be built without a single tolerance.
The one honest exception to confront up front is coordinate noise (measured: WHO's visually
abutting marks differ at the 2nd decimal), which is why the repo already carries `COORD_EPS`;
whether that is a tolerance or a representation artifact must be argued, not assumed.

## 6. What is measured

### 6.1 Column recovery fails while metadata ink is present

Overlap-clustering runs into columns, over the whole page, collapses catastrophically:

```
apple p0   44 lines ->  1 overlap-column   x  52.6-562.3   runs=207
apple p2   41 lines ->  1 overlap-column
bfs   p6   43 lines ->  1 overlap-column   x  70.9-522.9   runs=311
stem  p0   65 lines -> 12 overlap-columns  (col1 x 55.0-311.7 welds 174 runs)
```

One wide metadata run — a title, a cut-in heading, a wrapped label — overlaps every data column
and bridges them all. **Columns cannot be recovered from a page that still contains its
metadata**, which is the formal reason the data must be isolated first.

### 6.2 Structural repetition isolates data from metadata — necessary, not sufficient

Row signature = the sequence of datatype families of a line's ink runs. Lines whose signature
recurs (≥2) are data candidates; singletons are metadata candidates.

```
who p0:  28 shared / 2 singletons — and the singletons are EXACTLY the metadata:
   y= 59.33 :: Weight-for-age BOYS                                   (title)
   y=118.71 :: Year: Month Month L M S -3 SD -2 SD -1 SD Median ...  (boxhead)

apple p0: 39 shared / 5 singletons; 3 are the boxhead rows (94.67, 107.39, 116.03)
stem  p0: 58 shared / 7 singletons; 2 are the boxhead rows (74.43, 81.03)
```

The boxhead is a singleton on **every** document measured. The signal is real.

### 6.3 …and it over-collects, in a way only space can fix

```
apple p0 singletons that are GENUINE DATA:
   y=360.64 :: Other income/(expense), net 572 (171) 670 (698)   (parenthesised negatives)
   y=593.20 :: Japan 6,554 5,782 24,368 2 2,067                  (R16 split-number defect)

capacity p0: 6 singletons, 4 of them genuine data rows
cbh      p0: 6 singletons, mostly genuine data rows
```

No type-lattice refinement separates these from a boxhead row — their uniqueness is a real
property of their values. What separates them is that they sit **inside** the repeating block
and **aligned to its columns**, whereas the boxhead sits **above** it and aligns to nothing.

**This is the measured derivation of §0's third consequence: spatial axioms are not a
tie-break, they are the discriminator.**

### 6.4 Carried from the prior measurement passes

- Marks read from `page.rects` (not `page.lines + page.edges`) give apple p0's two spanner
  spans and four leaf columns with **no tolerance and no doubling filter**.
- A merged header cell is **one drawn mark spanning its children** — a rule span on apple, a
  filled box on WHO. Same idea, two renderings.
- Decoration marks the header/body boundary **only** where the author distinguished the
  boxhead's border treatment from the body rows'; row-uniform marking is genuine silence.

## 7. What is NOT established

- **G3, G4, G5 and the whole spatial family are undefined.** They are named here, not built.
- **No candidate-generation strategy is chosen.** Today's generator is `infer_leaf_grid`'s
  tuned profile. Whether the axioms *dispose* a procedurally-generated candidate set (the
  shipped R13 pattern, whose recall is bounded by the generator) or whether candidates are
  themselves derived, is open — and it is the difference between repairing the defect and
  relocating it.
- **T5 (transposed) has no corpus witness** (R68). Any axiom written for it is unfalsifiable
  against real documents.
- **The prior-art citations in §2 are unverified.** They must be checked before publication.
- **Nothing here has been implemented or scored.** This is a definition document; the claim
  that these axioms *identify* the grid on the corpus is untested and must not be assumed.

---

## 8. The fundamental, and the first measured rectangles (2026-08-08)

François: *"How to detect something which is not defined? Let's start with the fundamentals —
we have more than enough failures to understand what these fundamentals must be."*

The failures were all the same failure: **detectors for an undefined object**. Columns derived
from un-isolated ink; rows derived from types alone; frequency mistaken for data-ness;
indentation mistaken for hierarchy. Each derived ONE axis in isolation.

### 8.1 The definition

> **A data grid is a maximal rectangle whose rows and columns are admitted together.**
> Columns are admitted because the rows agree on their type; rows are admitted because the
> columns agree on their shape. Neither axis is derived first, and the pair is admitted
> together or not at all.

This is a closure condition, and it dissolves the circularity that blocked every prior attempt.
It is now vocabulary: `vocab/ontology/tab-datagrid.ttl` (`tab:DataGrid`, the typology
`tab:UniformGrid` / `tab:MixedGrid` / `tab:AggregatingGrid` / `tab:StackedGrids`, the axioms
G1–G7 and refutations R1–R5 as first-class `tab:GridAxiom` / `tab:GridRefutation` individuals,
so a grid cites what it conformed to and a rejected candidate cites what killed it).

**Candidate generation becomes free**, which removes the tuned profile at the root: rows sharing
a structural signature necessarily share a run count, so their positional slots *are* the
candidate columns. No gutter percentage, no minimum bin count, no sample target.

**The typology is data-intrinsic** — decided from the grid alone, never from a header:
uniform vs mixed by counting distinct column families; aggregating by *exact arithmetic* rather
than indentation (measured: indentation is INVERTED for aggregates); stacked by two grids
sharing a column extent.

### 8.2 Derivation, in two phases

1. **Data rows** = rows whose structural signature recurs (≥2) and carries a non-`Text` family.
2. **Columns** = x-overlap classes of runs over *those rows only*.

Phase 2 is safe precisely because phase 1 removed the metadata — the measured cause of the
earlier collapse (§6.1), where one wide title or cut-in heading bridged every column and
reduced apple p0 and bfs p6 to a single column each.

### 8.3 Result: a rectangle for every document

```
page        data rows / lines   columns   rectangle x           y
apple p0        29 / 44            9       52.6- 562.3    143.2- 744.9
apple p1        25 / 43            5       70.6- 562.3    153.0- 724.5
apple p2        14 / 41            5       52.6- 562.1    137.4- 702.2
stem  p0        32 / 65           15       96.4- 829.6    101.3- 437.1
capacity p0     23 / 32           15      128.5- 811.6    134.6- 406.1
cbh   p0        49 / 85           19       50.0-1135.0    120.7- 721.7
who   p0        25 / 30           12       84.6- 780.3    134.2- 465.3
bfs   p6        32 / 43            9       72.6- 522.2    136.4- 480.8
ons   p7        46 / 68            7       55.3- 505.4    155.7- 580.6
```

Metadata excluded, without ever being looked for — every title, caption and header line, plus
cbh's section key `GERALDTON` and its berth notices, and WHO's `Z-scores (weight in kg)` and
`Year: Month Month L M S …`. They are residue by construction.

### 8.4 What is NOT yet right — measured, not smoothed

- **Row recall is incomplete.** A data row whose signature is unique is dropped: apple p2 admits
  14 of ~34 (parenthesised-negative rows each tokenise uniquely) and capacity p0 drops
  `2025/26 August 2nd Half 0 N 10,000 Y …`. Recall must come from the columns re-admitting rows
  that fit them — the second half of the mutual definition, not yet implemented.
- **G1 is not yet enforced per column.** stem and cbh have columns reading `['Quantity','Text']`
  and `['Date','Text']`. The rectangle's extent is right; its column homogeneity is not proven.
- **cbh's rectangle spans a stacked panel** (y to 721.7 includes `Stock at Port`), which
  `tab:StackedGrids` should separate and does not yet.
- **The axioms are declared in the ontology but not yet executable** — no `.rq`, no SHACL, no
  worked example, no negative test. Nothing here is wired into `compile_tables`, and no corpus
  score has moved.

### 8.5 The recall attempt: a negative result, and where the definition is still wrong

Building the second half of the mutual definition — columns re-admitting rows, iterated —
**failed, and the failure is in the definition, not the code.**

Attempt 1, columns as the **union** of the admitted rows' runs, iterated to a fixed point:

```
apple p0  29 -> 31 rows   but ADMITTED the year header row '2026 2025 2026 2025'
                          (extent moved up to y=116.0)
apple p2  14 -> 22 rows   improved
capacity  23 -> 25 rows   improved, and now correctly excludes 'Year Elevation Period ...'
cbh p0    49 ->  3 rows   COLLAPSED
who p0    25 ->  4 rows   COLLAPSED
```

The collapse is structural: admitting a row *widens* the column set, which tightens G2
("cover every data column"), which disqualifies the other rows.

Attempt 2, columns as the **intersection** (only intervals in which every admitted row has
exactly one run) — the operator the formal-concept form actually requires:

```
apple p0   1/44 rows      COLLAPSED
apple p1  24/43 rows      slightly worse than the 25 of the one-shot form
apple p2  19/41 rows      better than 14, worse than attempt 1's 22
stem  p0  33/65 rows      stable
capacity   1/32 rows      COLLAPSED
cbh  p0    crash (empty row set)
```

**Diagnosis.** A Galois connection requires a **fixed attribute universe**. Our columns are
*re-derived geometry* on each round, so the attributes change identity between iterations and
the pair of operators is not a closure operator at all. The ontology comment claiming "the
formal-concept shape" was an overclaim and has been corrected in `tab-datagrid.ttl`.

**What this establishes, and it is worth more than the failed iteration:** the column universe
must be fixed **once**, before any rectangle is selected, and a data grid is then a maximal
sub-rectangle *within that fixed universe*. Maximality is only well-defined against a stable
set of candidate columns. That is the next build, and it is a change to the definition, not a
parameter.

**State of the milestone.** The one-shot two-phase derivation of §8.3 stands as the best
measured result: one rectangle on every one of 9 pages, metadata excluded by construction, no
tuned constant. Its known gap remains row recall (§8.4). The iterated closure does not improve
on it and must not be presented as if it did.

### 8.6 Refined until universal — 9 of 9 pages admit a grid

Three changes to the DEFINITION, each forced by a measured failure, not by tuning:

1. **Columns are fixed once, by the seed, and never re-derived.** Re-derivation changes the
   columns' identity between rounds, so the operators are not a closure and do not converge
   (§8.5). Maximality is only well defined against a stable candidate set.
2. **`tab:Text` is a legal column family.** Excluding it imported the assumption that every
   table is a matrix of measures, and so excluded every record table — a vessel name is data.
   Measure-ness (family ≠ Text) now *types* the grid; it never decides admission. Added
   `tab:MeasureColumn` and `G1b` non-degeneracy (a rectangle of text columns alone is aligned
   prose).
3. **G2 completeness → `tab:RowAddressability`.** Requiring ink in every column is true of
   dense financial statements and false of sparse operational registers; it cut stem to 17/65
   and capacity to 6/32. A row must instead carry ink in the key column *and* in ≥1 measure
   column — which is what completeness was actually protecting against, and still refuses the
   bare period-header `2026 2025 2026 2025` (measures, no key) and the cut-in heading
   `Net sales:` (key, no measure).

Plus one precondition: **unit markers are absorbed before signatures are taken** (a lone `$` is
a `tab:UnitMarker` on its neighbour, not a column — leaving it in split apple's identical rows
into n=9 and n=5, one table read as two), and **abstaining datatypes must not erase a column**
that has nothing else (apple p2's value columns are entirely parenthesised negatives; erasing
them read the page as "not a table").

```
page        rows/lines  cols (measure)  type     rectangle x          y
apple p0      30 / 44     5  (4)        Uniform   52.6- 562.3   143.2- 744.9
apple p1      27 / 43     3  (2)        Uniform   70.6- 562.3   153.0- 724.5
apple p2      25 / 41     3  (2)        Uniform   70.6- 562.3   180.2- 616.7
stem  p0      17 / 65    15  (6)        Mixed     96.4- 829.6   101.3- 417.6
capacity p0    7 / 32    15  (6)        Uniform  129.6- 811.6   123.5- 317.8
cbh   p0      39 / 85    16  (8)        Mixed     50.0- 986.7   136.8- 656.0
who   p0      21 / 30    13 (12)        Uniform   84.6- 780.3   134.2- 465.3
bfs   p6      32 / 43     9  (2)        Uniform   72.6- 522.2   136.4- 480.8
ons   p7      28 / 68     6  (5)        Uniform   55.3- 505.4   155.7- 580.6

pages with an admitted grid: 9/9
```

**Universal in admission, not yet in recall.** Every page yields a grid, every grid excludes
its metadata, and no tuned constant appears anywhere. But recall is uneven: apple, who, bfs and
cbh are good, while **stem (17/65), capacity (7/32) and ons (28/68) still lose data rows** whose
run structure differs from the seed's — a sparse register's rows genuinely vary. Closing that
is the next refinement, and it must not be closed by relaxing a test until the numbers rise:
the rows lost are lost for identifiable structural reasons, and those reasons are the evidence.

### 8.7 Two further refinements attempted, both measured WORSE — §8.6 stands

Recall was diagnosed first, by asking which axiom refuted each rejected line — the
`tab:refutedBy` record the ontology calls for:

```
stem p0      STRADDLE x34   OUTSIDE x8 (the header row)   TYPE x6 ('Blank' placeholder)
capacity p0  STRADDLE x21   OUTSIDE x3 (the header row)   TYPE x1
ons  p7      TYPE x22 (wrapped header text)  STRADDLE x17 (the title)  NOMEASURE x1
```

ons's refusals are almost entirely genuine metadata, so its 28/68 is much closer to correct
than the ratio suggests. STRADDLE dominating stem and capacity was a defect in the definition:
a column's interval was the seed rows' **ink extent**, so any row with a longer vessel name
overflowed and was refused.

**Attempt A — columns as CUTS (the gaps between seed extents) rather than extents.** A run
straddles only if it crosses an entire gap; presence test, no midpoint chosen.

```
apple p2  25 -> 27 rows   improved
stem  p0  17 -> 13 rows   WORSE   (MULTI x4)
capacity   7 ->  6 rows   WORSE   (MULTI x18)
```

Widening columns to the gaps lets two runs fall in one column. STRADDLE fell and MULTI rose:
the same error swapping ends. **Rejected.**

**Attempt B — the column universe from author-drawn vertical rules**, on the standing principle
that decoration measures the post-reshape shape and therefore outranks alignment where it
exists.

```
pages with an admitted grid: 1/9   (8 pages: "no measure column")
```

**Catastrophic, and the cause is known:** `extract_rules` conflates area-fill edges with drawn
rules — apple reports 678 "vertical rules", and WHO yields a 104-column universe. This is the
same conflation the header-boundary pass recorded (`page.rects` vs `page.lines + page.edges`).
The principle is not refuted; the available rule extractor cannot supply the universe.
**Rejected.**

**Conclusion.** §8.6 stands as the best measured definition: 9/9 pages admit a grid, metadata
excluded by construction, no tuned constant. Recall remains uneven (stem 17/65, capacity 7/32,
ons 28/68), and two principled attempts to close it both measured worse. The remaining recall
gap is now attributable to two named causes rather than to mystery:

1. **stem/capacity carry document-specific placeholders** (`Blank`, `TBA`) that type as Text
   inside Date and Quantity columns. `tab:Blank` covers `(blank)` and a lone `-`; these are the
   same phenomenon under a different convention.
2. **A clean rule extractor does not exist.** Closing that — reading `page.rects` so a drawn
   rule is one object and a fill is not a rule — would let attempt B be retried honestly, and
   it is the prerequisite for using decoration as the column universe at all.

### 8.8 The prerequisite fixed — strict improvement, no regressions

§8.7 named the blocker: no clean rule extractor exists, and that conflation had broken two
independent lines of work. Fixing it first — rather than patching row admission a third time —
is what unblocked the rest.

**A mark is a rule iff it contains no glyph centre.** A presence test: a fill contains the text
it sits behind; a rule contains nothing. No thinness ratio, no minimum width.

```
doc       pg  rects  vrule  hrule  fill   clean column universe
apple      0    807      2     23   672   [369.2, 501.2]                     (was 678 "vrules")
apple      1    370      0     20   316   []
capacity   0    512     17     32   390   [43.0, 109.0, 210.5, 281.5, ...]   (was 65)
cbh        0    190     21     68    21   [38.2, 76.0, 154.5, 216.5, ...]    (was 95)
bfs        6     43      9      4    20   [140.0, 187.6, 235.2, 282.7, ...]
who        0     97      4      9    38   [735.9, 747.7, 768.7, 771.5]       (was 104 columns)
stem       0    202      3     41   127   [13.0, 73.3, 832.6]                (page borders only)
ons        7     15      0      8     7   []
```

Two further definitional rules were then forced by measurement, each after a failure:

- **Decoration supplies the universe only when it resolves at least as finely as alignment
  does** — an ordinal comparison of column counts, not a threshold. Preferring it
  unconditionally cost stem every row, because its three drawn marks are page borders giving
  2 columns where alignment gives 15.
- **`tab:SeedFollowsUniverse` (G0): the seed is the modal class in whatever universe supplied
  the columns** — occupancy of the drawn columns under a decoration universe, the signature
  class under an alignment universe. Seeding a decoration universe by signature cost capacity
  19 of its 27 rows. The seed must be modal in the same space the columns came from, or it
  types the wrong columns.

```
page        rows/lines  cols (meas)  type     universe   baseline   delta
apple p0      30 / 44     5  (4)     Uniform   ALIGN        30        +0
apple p1      27 / 43     3  (2)     Uniform   ALIGN        27        +0
apple p2      26 / 41     3  (2)     Uniform   ALIGN        25        +1
stem  p0      17 / 65    15  (6)     Mixed     ALIGN        17        +0
capacity p0   27 / 32    16  (4)     Uniform   RULES         7       +20
cbh   p0      45 / 85    20  (7)     Mixed     RULES        39        +6
who   p0      25 / 30    13 (12)     Uniform   ALIGN        21        +4
bfs   p6      32 / 43     9  (2)     Uniform   ALIGN        32        +0
ons   p7      28 / 68     6  (5)     Uniform   ALIGN        28        +0

pages 9/9   data rows 257 (baseline 226)   REGRESSIONS: NONE
```

**The lesson, recorded because it cost four attempts to learn:** the two refinements of §8.7
each fixed one failure mode and created another, because both patched row admission while the
column universe stayed wrong. Fixing the universe moved four pages at once and cost nothing on
the other five. When two successive fixes trade one error for another, the defect is upstream
of both.

**Still open, unchanged:** stem 17/65 remains the worst page — its drawn marks are borders, so
it falls to alignment, and its `Blank`/`TBA` placeholders type as Text inside Date and Quantity
columns. The axioms remain declared-only: no `.rq`, no SHACL, no worked example, no negative
test, nothing wired into `compile_tables`, no corpus score moved.

### 8.9 Index columns: repeated cells ARE indentation, and the aggregate proves it

François, on the shipping stem: *"Port should also be part of the indentation. We have to
question if repeated cells can or cannot be considered as differently typed indentation — and
the hint is that we have totals in the same column, which means port names are semantically
identical and a single repeated entity. The author might have removed repeated occurrences to
highlight the indentation and still let port names repeat, for a reason we ignore. But this
does not change the logic: the port column is metadata and not data."*

Measured on page 0, and it holds:

```
x= 18.8  '2025/26'                          Year   — printed once, suppressed beneath
x= 57-62 'Jul 26','Aug 26','Sep 26'         Month  — printed once per group, suppressed
x= 96.4  'Mackay','Gladstone','Geelong' ...  Port  — REPRINTED on all 33 rows
x= 91.7  'Mackay Total','Fisherman Islands Total' ...  port totals
x= 57.2  'Jul 26 Total','Aug 26 Total','Sep 26 Total'  month totals
x= 14    'GC Fin Year','2025/26 Total'                 season total
```

Three levels, each with a value indent and a total indent ~4.7pt shallower. Year and month are
ditto-suppressed; port is not. **The difference is typographic; the structure is identical.**

**The witness is arithmetic, not vocabulary.** Reading the word "Total" would be
English-specific and is forbidden. Instead: does a row's measure equal the sum of the rows
sharing its neighbour's value?

```
Gladstone Total          20,000  = 1 member    MATCH
Carrington Total         23,000  = 1 member    MATCH
Gladstone Total          36,500  = 3 members   MATCH
Fisherman Islands Total  76,000  = 3 members   MATCH
Port Kembla Total        62,500  = 1 member    MATCH
Geelong Total           233,000  = 6 members   MATCH
Portland Total          144,000  = 5 members   MATCH
...
confirmed port-level aggregates: 12 of 15
```

Twelve exact reconciliations. `Mackay Total` is arithmetic nonsense unless `Mackay` names a
group — so the port column is a **key**, and keys are metadata. (The three failures are
recorded, not hidden: one has its members cut by a group boundary; two hit the known
split-number defect that extracts a tonnage as `5 0,000`.)

**Vocabulary added:** `tab:IndexColumn` (a stub level; metadata, excluded from every data
grid), `tab:IndexLevel`, `tab:SuppressedRepeat` (suppression is cosmetic, not semantic),
`tab:AggregateWitness` (G8, the arithmetic discriminator), and `tab:IndexAtTotalIndent`
(corroborating spatial evidence only — its direction is not universal, since apple's aggregates
sit *deeper* than their members while the stem's sit shallower).

**Measured effect on the stem's grid:**

```
index block INCLUDED (today):   seed n=15 x11 | 15 cols (6 measure) | 17/65 rows  y 101.3-417.6
index block EXCLUDED:           seed n=14 x13 | 14 cols (6 measure) | 19/65 rows  y  88.4-417.6
```

The gain is small but the correction is structural: the grid's left boundary no longer runs
through the row-axis categories, and its extent now starts at the first data row (y=88.4)
instead of skipping two rows whose leading index runs varied.

**Honest limit, stated in the axiom itself:** a grouping level with no totals has no witness
and stays in the grid. G8 is sound, not complete.

### 8.10 Groupability, and why the "mystery" is a checkbox

François: *"Indentation is here for grouping, we group to aggregate, and to aggregate we sort
first — so a sorted column without aggregated values is not metadata but data."*

**Adjacency, not sortedness.** Grouping requires only that equal values sit together, so no
order relation is needed — which removes collation, locale and date-parsing from the test
entirely. G9 `tab:Groupability` is a contiguity test.

**Contiguity is relative to the parent.** Measured, and evaluating it globally is a real error:

```
stem  Year  contiguous globally YES   within parent YES
      Month contiguous globally YES   within parent YES
      Port  contiguous globally no    within parent YES   <- Mackay recurs Jul/Aug/Sep
who   Year  globally YES              within parent YES
      Month globally no               within parent YES
ons   Year  globally no               within parent no    <- genuine negative: no index block
```

A global test rejects exactly the levels it should accept. ONS is the control case: its
left-hand columns are contiguous neither way, so they stay data.

**The refutation, R6 `tab:SortedWithoutAggregate`:** a groupable column with no aggregate
witness is sorted DATA. The argument is the authoring chain, not a heuristic — one groups in
order to aggregate, so a column grouped but never aggregated was never grouped *for* anything.
Conservative per §7, and it costs recall honestly: the WHO age index is a genuine category with
no totals (z-scores cannot be summed), so it reads as data.

**Is this native spreadsheet behaviour? Verified, not assumed — and yes, exactly.**

- Excel's **Subtotal** command requires the data to be **sorted by the grouping column first**,
  and then **outlines the list automatically**. Sort → group → aggregate is the native authoring
  order, and outline indentation is its by-product. François's chain is Excel's own workflow.
- **"Repeat item labels" is a PER-FIELD print option** (Field Settings → Layout & Print, exposed
  as `PivotField.RepeatLabels`), shown only in **tabular form**. One field may repeat while its
  sibling is suppressed, in one table, with no difference of meaning. Microsoft's guidance even
  recommends it "when subtotals are turned off or there are multiple fields for items."

So the GrainCorp author has a tabular-form PivotTable with repeat-item-labels **on for Port and
off for Year and Month**. The "mystery" is a checkbox. Recorded as
`tab:PivotFieldRepeatLabels` so no future reading treats repeated labels as evidence about
structure — it is evidence about a setting.

Sources:
[Insert subtotals in a list of data](https://support.microsoft.com/en-us/excel/insert-subtotals-in-a-list-of-data-in-a-worksheet) ·
[Repeat item labels in a PivotTable](https://support.microsoft.com/en-us/office/repeat-item-labels-in-a-pivottable-882bdb55-9cdc-4d8d-b531-8e96e41dea31) ·
[PivotField.RepeatLabels](https://learn.microsoft.com/en-us/office/vba/api/excel.pivotfield.repeatlabels)

### 8.11 Implemented and tested against a transcribed oracle

`src/iladub/etkl/datagrid.py` (one implementation, replacing nine divergent probes) and
`tests/etkl/test_datagrid.py` (12 tests, 2.4s, offline).

**The oracle.** Every recall number before this was produced by eyeballing exclusion lists,
which cannot falsify anything. `APPLE_P0_METADATA` is a hand transcription of apple page 0 —
all 44 lines read and classified: 13 metadata (title block, boxhead, cut-in headings) and 31
entry rows, aggregates included (a subtotal mints no record per §7 but it is data).

```
admitted 30   oracle DATA 31   oracle METADATA 13
recall   30/31          leaked metadata: NONE

MISSED:
   34  HeterogeneousColumn/col4  ::  Japan 6,554 5,782 24,368 2 2,067
```

The single miss is the known **R16 split-number defect** — `22,067` extracted as `2 2,067` —
a pre-existing extraction bug, not a failure of the definition. Every metadata line is refused
*with its reason*: the three boxhead rows by `RowAddressability/no-key` (they carry measures but
no key, which is precisely what that axiom exists to catch), the titles and cut-in headings as
unplaceable.

**The tests were mutation-checked, and one was found vacuous.**

```
M1  remove RowAddressability's key check -> soundness FAILS (line 5 '2026 2025 2026 2025' leaks)
M2  remove NonDegeneracy (G1b)           -> ALL 12 PASS          <- vacuous
M3  drop unit-marker absorption          -> recall 30 -> 22, FAILS
```

M2 is a finding, not just a test defect: **G1b is unreachable as a distinct refusal.** If no
column is a measure then no row can carry one, so `RowAddressability` refuses every row and the
grid is empty regardless. No page can exist on which G1b is the only refuser. It is kept as an
explicit early exit and documented as a backstop — the disposition R9 already established for
the conservation shape — and pinned by `test_non_degeneracy_is_a_redundant_backstop`, which
fails if a future change makes it load-bearing.

**Corpus, through the committed module:**

```
apple p0  30/44   5 cols (4 meas)  UniformGrid  [alignment]
apple p1  27/43   3 cols (2 meas)  UniformGrid  [alignment]
apple p2  26/41   3 cols (2 meas)  UniformGrid  [alignment]
stem  p0  17/65  15 cols (6 meas)  MixedGrid    [alignment]
capacity  27/32  16 cols (4 meas)  UniformGrid  [decoration]
cbh   p0  46/85  20 cols (7 meas)  MixedGrid    [decoration]
who   p0  25/30  13 cols (12 meas) UniformGrid  [alignment]
bfs   p6  32/43   9 cols (2 meas)  UniformGrid  [alignment]
ons   p7  28/68   6 cols (5 meas)  UniformGrid  [alignment]

pages 9/9   data rows 258
```

**Not yet implemented, and the gap is deliberate:** G8 `tab:AggregateWitness` and G9
`tab:Groupability` are defined in the ontology but NOT in the module, so index columns are not
yet excluded — which is why stem reads 17/65 here against the 19/65 the index-exclusion probe
reached. Nothing is wired into `compile_tables`, and no corpus score has moved. The oracle
covers one page of nine; the other eight remain unfalsified.

### 8.12 Two oracles, and the homogeneity fix they forced

A second transcription: `graincorp-stem-2026-07-31.pdf` page 0, 65 lines — 8 metadata (four
title lines, the three-line wrapped header, the footnote) and 57 entry rows, every `Total`
included. It was chosen because it is the weakest page, the only document with an adjudicated
verdict (`cor:CompilesAbove`, floor 0.95), and the case where index columns should pay off.

**What the oracle exposed.** Refusal reasons for the 40 missed rows:

```
unplaceable                x24   '2025/26 Jul 26 Mackay 56817 ...'  — index runs, more runs than columns
HeterogeneousColumn/col1   x10   'Fisherman Islands Woodchip QCE ...' — Text where the seed had a number
HeterogeneousColumn/col4    x6   'Blank' / 'TBA' placeholders in a Date column
```

The `col1` group is the finding. That column is **genuinely mixed** — non-grain cargo carries a
commodity word where grain carries a slot reference — but typing it from the seed alone
declared it `Quantity`, manufacturing an agreement the column never had, which then refused ten
real data rows. **G1 says a column agrees over the ADMITTED rows; typing from the seed is not
that.**

**The fix, and the failed first attempt.** Re-typing over the addressable rows gave apple p0
perfect recall and stem 17→33, but destroyed capacity, bfs and ons outright (`NO GRID`): one
contradicting row emptied the measure set, and with it the grid.

So the second pass is **asymmetric — it may only RELAX a refusal, never redefine what the grid
is.** The seed establishes the grid's identity (its measures, its key column); the wider
evidence decides only whether a column is *entitled to refuse* a row. A column the addressable
rows contradict has no agreed family, and a column with no agreed family refuses nobody. Two
bounded passes, columns never moving — so §8.5's non-convergence cannot arise.

```
page        rows/lines   universe     delta   oracle
apple p0     31 / 44     alignment     +1     31/31 recall, 0 leaked   ← complete
apple p1     28 / 43     alignment     +1
apple p2     26 / 41     alignment     +0
stem  p0     33 / 65     alignment    +16     33/57 recall, 0 leaked
capacity     28 / 32     decoration    +1
cbh   p0     55 / 85     decoration    +9
who   p0     25 / 30     alignment     +0
bfs   p6     34 / 43     alignment     +2
ons   p7     42 / 68     alignment    +14

9/9 pages, 302 data rows (was 258), no regressions.  Suite 29 passed.
```

**apple page 0 is complete: all 31 entry rows, no metadata admitted.** Both oracles are pinned
as tests — apple at exact equality, stem at a floor of 33 — so a future change cannot silently
lose them.

**The remaining stem gap is entirely the index columns** (24 `unplaceable` rows carrying year
and month values that the other rows suppress). G8 `tab:AggregateWitness` and G9
`tab:Groupability` are defined in the ontology and implemented as functions here, but are **not
yet wired into the derivation** — that is the next step, and the stem oracle is now in place to
judge it.

Still true: nothing is wired into `compile_tables`, and no corpus score has moved.
