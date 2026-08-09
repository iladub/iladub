# The concurrent sensor bank — design

**Date:** 2026-08-08 · **Status:** **BLOCKED at adversarial review, 2026-08-08** — see §11 ·
**Specimen:** `corpus/financial/apple-fy2026q3-statements.pdf` pages 0–2 ·
**Succeeds:** `2026-08-08-reading-as-constraint-satisfaction-design.md` — its architecture
(§2, §2.1, §2.2, §3) stands unchanged; its §1.1 transcription and its §4 first slice are
replaced by the measured sensor bank below.

**Doc impact:** increment — new sensors and constraints in the owned `tab:` namespace. No new
table classes, no site page contradicted.

---

## 1. The discipline this slice implements

François, settling the architecture:

> Our discipline is to use multiple sensors simultaneously when starting the table scan — not
> only visual sensors, but the latter get priority, since they are supposed to highlight
> structure after the semantic table reshape.

Two rules, and they are not the same rule:

- **Concurrency.** Every sensor fires at the start of the scan. No sensor is sequenced behind
  another, and no sensor is deferred to a later loop. A sensor that finds nothing contributes
  nothing; it is never "not yet run."
- **Priority, not order.** Decoration-derived proposals outrank text-derived ones *when they
  disagree*. This is a ranking on evidence, not an ordering of execution.

The justification for the ranking is the surviving spec's §2.1 and is structural, not a
preference: the authoring order is compute → reshape → decorate → render, and decoration can
only be applied to dimensions that already exist. A rule spanning two columns exists because,
at decoration time, there were two columns to span. Text entangles content with position;
a rule carries no content at all.

The order in which judgements actually resolve on a given page is a **trace** recorded in the
decision holon — evidence about the reading, never the algorithm.

## 2. What is measured, and what was refuted

Everything below was run against the corpus during design. The refutations are recorded first
because two prior specs died by carrying plausible premises into design unmeasured.

### 2.1 Refuted during design — do not re-assert

| Claim | Source | Measured reality |
| --- | --- | --- |
| Grid gate separates at `gap > 2pt` | handoff | **False.** At 2pt it keeps 26/27 pages: justified prose word-gaps exceed 2pt, so bfs p0 (a press release) reads as mode 14. The real gate holds across `[3pt, 20pt]` — see §3.1 |
| `infer_leaf_grid` returns `224.1/433.6`, matching no ink | handoff | **True of band 2 only.** Bands 3–7 return `[50.0, 300.0, 364.4, 430.4, 496.4, 562.4]`, agreeing with rules and text edges. apple's column recovery works; its *header* recovery does not |
| The zebra's top edge is the header/body boundary | this design, hypothesised | **False on apple p2**, whose first data row (`Cash, cash equivalents … beginning balances $ 35,934 $ 29,943`) is unstriped and sits *above* the zebra |
| A stub-ink upward walk recovers the header block | this design, prototyped | **Recovers 0 lines on all three pages.** The walk halts at the first row with stub ink, which on every page is the row immediately above the zebra |
| The grid inferred from striped body rows is correct | this design, prototyped | **True on p0, false on p1/p2** — there it returns `[52.6, 418.6, 440.6, 492.6, 514.1, 562.3]`, splitting the `$` sign off as its own column |
| A measure-less row is an annotation outside the grid | this design, hypothesised | **False.** apple p0 has seven measure-less rows, all row-hierarchy parents on the indent lattice — see §3.4 |
| `classify` is a terminus; `nhw == ncols` is the escalation reason | superseded framing | **False, and re-confirmed here.** `classify` is a router (`compile.py:643`); the terminal reasons on apple p0 are `MATRIX_AMBIGUOUS` and `REGION_TILING_FAILED` |

### 2.2 The page under the microscope

`compile_tables("corpus/financial/apple-fy2026q3-statements.pdf", 0)`:

```
page score 0.11695906432748537   asserted 20   escalated 151
region0: NON_TABLE          ignored    cells=0   reason=fewer than 2 lines
region1: NON_TABLE          ignored    cells=0   reason=fewer than 2 columns
region2: UNSUPPORTED_TABLE  escalated  cells=0   tok_e=51   reason=MATRIX_AMBIGUOUS
region3: UNSUPPORTED_TABLE  escalated  cells=0   tok_e=16   reason=REGION_TILING_FAILED
region4: RECORD_TABLE       asserted   cells=20  tok_a=20   reason=None
region5: UNSUPPORTED_TABLE  escalated  cells=0   tok_e=22   reason=REGION_TILING_FAILED
region6: UNSUPPORTED_TABLE  escalated  cells=0   tok_e=31   reason=REGION_TILING_FAILED
region7: UNSUPPORTED_TABLE  escalated  cells=0   tok_e=31   reason=REGION_TILING_FAILED
```

Region 4's header row, per `classify`, is `Operating income | 35,695 | 28,202 | 122,432 |
100,623`. **The page's only assertion consumes a real data row as its header.** The 0.117 is
not a partial win; it is a misreading that happens to tile.

Meanwhile the area fills run **continuously from y=139.56 to y=746.28**, and the band gaps
that split them are 19.44 / 19.44 / 19.44 / 19.05 / 18.81 pt — ordinary leading.
`detect_bands(lines, gap_factor=1.8)` cut one table into eight. The `1.8` is a tuned constant
at the root of segmentation, and §8 names a tuned constant as prima facie evidence that the
decision belongs elsewhere.

## 3. The sensor bank

Six sensors, all fired at scan start. Each emits **candidate** facts into the page's evidence
graph. None decides.

### 3.1 Run-count sensor — is there a table on this page

An *ink run* is a maximal group of words whose consecutive x-gaps do not exceed a separation
`g`. The modal run count per text line is the signal: mode > 1 ⇒ grid, mode == 1 ⇒ prose.

The separation is not tuned. The verdict is **invariant across an order of magnitude**:

```
GAP  kept   pages called TABLE
  2    26   apple0-2 stem0-2 capacity0 cbh0 bfs0 bfs1 bfs2 bfs3 bfs5 bfs6 ons0..ons8 who0-2
  3    17   apple0-2 stem0-2 capacity0 cbh0 bfs4 bfs5 bfs6 ons4 ons7 ons8 who0-2
  4    17   (identical)
  ...
 20    17   apple0-2 stem0-2 capacity0 cbh0 bfs4 bfs5 bfs6 ons4 ons7 ons8 who0-2
```

`g` only has to fall between prose word-spacing and column gutters, and any value in `[3, 20]`
does. The gate discards bfs p0–p3 (press-release prose), ons p0–p3/p5/p6, and calls the
one-line `ons p6` furniture.

**Known false positive, measured:** bfs p4 passes on 3 in-region lines — a chart caption. The
gate has no floor on region size, and a floor is exactly where a tuned constant would enter.
Registered as a residue, not patched.

### 3.2 Fill sensor — table extent, and row structure where it exists

Maximal same-colour y-runs of area fills. The sensor reports whether the fill is
**row-structured** (roughly one fill row per text line — a direct measurement of the
post-reshape row count) or a **panel** (a background behind many rows).

```
doc       pg  fillrows lines-in  ratio   verdict
apple      0        42       37   1.14   ROW-STRUCTURED
apple      1        40       37   1.08   ROW-STRUCTURED
apple      2        39       34   1.15   ROW-STRUCTURED
stem     0-2    21/29/22   60/80/68  ~0.35 PANEL
capacity   0         3       30   0.10   PANEL
cbh        0        17       79   0.22   PANEL
who      0-2         3    28/27/15  ~0.11 PANEL
bfs      5,6      4/13     59/39   ~0.2  PANEL
ons      7,8         1    68/69    0.01  PANEL
bfs4 / ons4                              NO FILL
```

Row structure exists on apple's three pages and nowhere else in the corpus. Panel fills bound
the table but carry no row structure, and — measured — do **not** mark the header/body
boundary: the first line below the fill top is a title on stem and capacity, a section key on
cbh, a caption on who, and the header row itself on bfs.

### 3.3 Rule-span sensor — columns, header tree, and the frame

Horizontal rules grouped by y. Measured on all three apple pages:

```
apple p0  y=103.56/104.52  (302.7,365.1)(366.0,368.7)(369.6,431.1) | (434.7,497.1)(498.0,500.7)(501.6,563.1)
          y=125.16/126.12  (302.7,365.1) (368.7,431.1) (434.7,497.1) (500.7,563.1)
apple p1  y=120.84/121.80  (419.8,489.4) (493.2,563.1)
apple p2  y=111.96/112.92  (419.8,489.4)(490.4,493.2)(494.2,563.1)
          y=133.56/134.52  (419.8,489.4) (493.2,563.1)
```

Three readings fall out, **each a presence or ordinal test, none a magnitude test**:

- **Row separators** are the single-segment rules of maximal span (`50.0–563.1` on p0) —
  argmax, not a threshold.
- **The leaf header rule** is the *lowest* multi-segment rule above the topmost row separator.
  Its segments are the columns: `302.7 / 365.1 / 431.1 / 497.1 / 563.1` on p0, agreeing with
  the body grid `50.0 / 300.0 / 364.4 / 430.4 / 496.4 / 562.4` and with the in-region text
  right-edge histogram (`~363 / 430 / 494 / 561`) — three independent measurements.
- **A parent header rule** is one carrying ink *inside the leaf rule's gutter intervals*. At
  y=103.56 there is ink at 366.0–368.7; at y=125.16 there is not. Purely presence-based, and
  it needs no segment-merging tolerance because the gutter intervals come from the leaf rule
  itself. On p0 this yields two parents (`Three Months Ended`, `Nine Months Ended`) over four
  leaves; on p1, one level, no parent; on p2, one parent over two leaves.

**Blast radius, measured.** The header-rule signature (a multi-segment rule above the topmost
row separator, drawn twice) fires on apple 0/1/2 and **zero of the other fourteen** gate-kept
pages. Emitting the evidence is therefore inert elsewhere by construction.

### 3.4 Indent-lattice sensor — row hierarchy, and which rows are in the grid

The leftmost ink x per body row, histogrammed. A position **two or more rows share** is a
lattice level; a position used **once** participates in no pattern.

```
apple p0 lattice:  52.6(x12)  59.2(x4)  70.6(x18)  88.6(x4)
apple p1 lattice:  52.6(x6)  70.6(x20)  79.6(x2)  88.6(x5)  106.6(x3)   |  211.5(x1)  287.3(x1)
apple p2 lattice:  52.6(x7)  70.6(x16)  88.6(x9)  106.6(x3)
```

apple p1 is the discriminating case, because there both kinds of measure-less row co-occur:

```
y=124.48 x0=287.3 :: ASSETS:                               <- occurs once, off-lattice
y=138.88 x0= 52.6 :: Current assets:                       <- shared by six rows, a real parent
y=381.04 x0=211.5 :: LIABILITIES AND SHAREHOLDERS' EQUITY: <- occurs once, off-lattice
```

Nothing about the rows themselves separates them — both are measure-less and `:`-terminated.
The repetition test does.

**And a measure-less row is not an annotation.** On p0 every measure-less row sits at 52.6
with deeper rows beneath it:

```
y=129.04  Net sales:              y=431.92  Earnings per share:
y=188.80  Cost of sales:          y=477.52  Shares used in computing earnings per share:
y=275.20  Operating expenses:     y=534.97  (1) Net sales by reportable segment:
                                  y=649.69  (1) Net sales by category:
```

A sensor treating these as furniture would discard the statement's entire section structure —
the error François blocked once already ("+76 cells that look like a win while discarding the
hierarchy").

### 3.5 Text-edge sensor — column boundaries from ink alone

Right and left edges of ink runs, histogrammed **in-region**. On apple p0 the right edges
cluster at ~363 / 430 / 494 / 561, independently confirming §3.3's leaf spans.

Measured in-region and never whole-page: who and stem read 3–15% single-run whole-page but
**0% in-region**, because title blocks bias the whole-page figure.

### 3.6 Measure-presence sensor — does a row carry values in the measure columns

A presence test per row against the column grid. Feeds the parent/data distinction of §3.4;
on its own it decides nothing, per the refutation in §2.1.

## 4. Priority and disposal

When two sensors propose incompatible structure, **§3.2 and §3.3 (decoration) outrank §3.1,
§3.4, §3.5 and §3.6 (text)**, for the reason in §1.

The one measured conflict on the specimen: on apple p2 the fill sensor leaves the first data
row unstriped while the lattice sensor places it on level 52.6 carrying measures. Here
decoration is **silent about that row rather than contradicting** — the fill's absence is not
a proposal — and the lattice's proposal stands unopposed. Priority applies to disagreement
between proposals, never to a proposal versus a silence.

**The grid's edge rows are carried, not asserted.** François, settling this:

> At that level we should live with the possibility that the top or bottom rows of a grid can
> have a potential offset. This will resolve only when we understand the meaning of the border
> columns. In a panel table we might have hierarchy, and therefore the first row can be
> ambiguous to interpret, since we might have no data in the grid per se — the row relates to
> the data parent. But still the indentation and the pattern will tell us if this first row is
> part of the grid or a simple annotation.

So the rule spans locate the frame **to within one row at each edge**, and that offset is a
first-class fact, not an error. It is resolved where the sensors agree, and the resolution is
recorded as a trace.

Disposal uses machinery already shipped and already enforced: `region_tiles`, the conservation
shape (C4), exact-Decimal aggregate reconciliation (C5), and the `tab:ReshapeRecipe` round trip
(C6). Where no assignment satisfies the constraints, the region escalates **naming the
constraint that failed** — strictly better than `UNSUPPORTED_TABLE`.

## 5. §8 classification

| Component | Class | Justification |
| --- | --- | --- |
| Rule/fill/word/char extraction | **PROCEDURAL** | Raw extraction, source → typed RDF facts. Irreducible: there is no declarative form of "parse the PDF content stream". Precedent: `extract_words`, `extract_chars` |
| Run-count, fill-row, rule-span, lattice, edge, measure-presence derivations | **AXIOM** | SPARQL `SELECT`/`CONSTRUCT` over the page evidence graph, open world, presence- and ordinal-based. Every threshold in §3 is either an argmax, a containment test, or a repetition count of two |
| Parent-vs-leaf rule classification | **AXIOM** | Presence of ink inside the leaf rule's own gutter intervals. No merging tolerance, no distance |
| Edge-row offset resolution | **AXIOM** | Lattice membership is a repetition test; the offset is carried as a candidate until sensors agree |
| Membrane / tiling / conservation | **SHACL, closed world** | The contract membrane, holon-scoped, unchanged |

**No NEURAL component in this slice.** Every judgement here is a presence or ordinal test over
ink. If a case arises where two sensors disagree and no constraint disposes it, that is where a
NEURAL proposal belongs — proposed under §3 epistemics and disposed by an oracle — and it is
out of scope until a document demands it.

**No tuned constant.** The one number that looks like a threshold — the run separation `g` of
§3.1 — is justified by a measured invariance plateau spanning `[3, 20]`, not by fit.

## 6. Premises

| # | Premise | Status |
| --- | --- | --- |
| P1 | The run-count gate separates table pages from prose | **MEASURED** — 17/27, invariant over `[3, 20]`pt (§3.1) |
| P2 | Row-structured fill exists on apple 0/1/2 and nowhere else in the corpus | **MEASURED** (§3.2) |
| P3 | The leaf rule's segments are the columns, on all three apple pages | **MEASURED** (§3.3) |
| P4 | Parent-vs-leaf is decidable by gutter-ink presence | **MEASURED** on p0 and p2; p1 is single-level so the test is vacuous there |
| P5 | The header-rule signature is inert on the other 14 gate-kept pages | **MEASURED** — zero occurrences (§3.3) |
| P6 | The indent lattice separates row-hierarchy parents from off-lattice annotations | **MEASURED** on p1, the only page where both co-occur (§3.4) |
| P7 | apple p0's only current assertion is a misread data row | **MEASURED** (§2.2) |
| P8 | Reading the frame this way moves apple's score above 0.11695906432748537 | **NOT MEASURED — this is the loop's success criterion, not a premise.** Region 4 currently asserts 20 cells by misreading; a correct reading of the same region could assert *fewer* cells while being right |
| P9 | stem / capacity / cbh / who / bfs / ons are untouched | **ARGUED from P5, NOT MEASURED end-to-end.** Inertness of the *evidence* does not by itself prove inertness of the *verdict*; the corpus must be re-run |

P8 and P9 are the two the loop must close. **P9 is the one to attack**: stem is 0.9655 over
2152 cells, and a regression there costs more than apple's gain is worth.

## 7. Success criteria

- The rule-span sensor recovers, on apple p0, two parent header nodes over four leaf columns
  matching §3.3, and on p1/p2 the two-column single-level header.
- The header/body frame is derived with **no reference to cell datatypes** — the property that
  makes it non-circular where `header_body_split` is circular (R71).
- The grid's edge-row offset is emitted as an explicit fact, and the decision holon records
  which sensor resolved it, or that none did.
- apple p0's eight whitespace bands resolve to one table, and the misread of region 4 is gone.
- **apple's document score moves above 0.0606860158, or the loop reports plainly that it did
  not and why.** A structural win with a flat score is a result; presenting it as success is
  not. If the score falls because a misreading was replaced by an honest escalation, that is
  a win and must be argued as one, with the token accounting shown.
- stem **0.9655 / 2152 / chain [3]**, CBH **0.9047**, capacity **1.0000**, WHO **0.5597**
  unchanged. Byte-identical, measured, not argued from P5.
- No tuned constant introduced. The run separation carries its plateau measurement in the code.

## 8. Out of scope

- **Producer-signature attribution.** Blocked at review and not revisited: stem and capacity
  have byte-identical PDF metadata and land in different signature classes.
- **`tab:RejoinSectionsOp` as a reshape inverse.** apple's fills run unbroken 139.56→746.28;
  iladub's own segmenter split that table. A segmentation repair is not the inverse of an
  authoring operation.
- **The stacked-table split.** apple p0's two footnote-marked rows (`(1) Net sales by
  reportable segment:`, `(1) Net sales by category:`) separate three decompositions sharing one
  header — confirmed by `Total net sales 109,417 / 94,036 / 364,357` appearing three times.
  Telling them apart from the four ordinary section headings needs a second signal that
  differs per document (arithmetic here, term grounding on CBH). That is R54, and it stays
  open.
- **Reading what a double rule means** (net result, section end). We detect the mark; naming it
  is domain interpretation.
- **A general solver over C1–C7.** This slice runs a small constraint set over six sensors.

## 9. Residues this slice opens

| Residue | What | Measured where |
| --- | --- | --- |
| bfs p4 false positive | The run-count gate has no floor on region size; bfs p4 passes on 3 lines of chart caption | §3.1 |
| Single-span region assumption | The table region is one y-span per page; a page with a table above and prose below would stretch it. None of the 17 obviously does — **unmeasured** | handoff, carried |
| Lattice repetition count | "Shared by two or more rows" is the minimal test for a pattern, but apple p1's 79.6 (a wrap continuation) has exactly two. The test's floor is untested against a document where a genuine annotation repeats | §3.4 |

## 10. Global constraints (carried, per CLAUDE.md)

- **§8 neurosymbolic gate.** Sensors emit evidence; every decision above is an AXIOM over it.
  No tuned constant; ratios, ordinals and presence tests within the table's own frame only.
- **§7 only emit what the source supports.** Where no assignment satisfies the constraints,
  escalate and name the failed constraint. Replacing a misreading with an honest escalation is
  a correct outcome even when the score falls.
- **§5 context is carried.** Section-heading rows are row-hierarchy parents, never furniture.
- **The decision holon records the trace** — which sensors fired, which proposals were pruned,
  by which constraint, and in what order. The order is evidence, not method.
- **Source ownership.** `tab:` is ours; no HGA term appears as a subject.

---

## 11. Adversarial review — BLOCKED (2026-08-08)

The review's job was to attack the premises before any plan was written. It did.
Three findings were independently re-measured by the controller and stand.

### 11.1 CRITICAL — P5 is refuted; the §3.3 locator fires on WHO

The claim *"the header-rule signature fires on apple 0/1/2 and **zero** of the other fourteen
gate-kept pages"* is false. It was produced by a design-time probe that filtered on
"drawn twice within 1.5pt with an identical segment list" — **two magnitude constants that
never reached §3.3's stated definition.** Under the definition as written, the signature
fires on **6 of 17** pages:

```
===== who p0: maximal single-seg span=729.72; topmost such rule y=101.22
  multi-segment rules ABOVE it: 5  -> SIGNATURE FIRES = True
     y=  89.22 segs=[(675.71, 687.77), (689.87, 701.99)]
  => LEAF rule (lowest multi-seg above) y=89.22
  real body x-extent: 63.11 .. 780.29
```

The sensor proposes a **26pt-wide, two-column grid** — WHO emblem strokes in the top-right
corner — for a table 717pt wide. And by §4 that is a *decoration-derived* proposal, which
**outranks** the text-edge sensor's correct one.

WHO currently scores 0.5597 and escalates 3× `MATRIX_AMBIGUOUS` (R45). This sensor could
convert an honest escalation into a **wrong assertion** — strictly worse than the status quo
and a direct §7 violation. **P9 was "ARGUED from P5"; with P5 refuted, P9 has no support.**

Root cause: the ordinal *"above the topmost maximal-span row separator"* is not
document-general. On apple that rule is the first zebra edge, with the header above it; on
WHO it is the table's **box top**, with the header *inside*. WHO's real header rules sit at
y=101.94 (5 leaf segments) and y=102.78 (one parent span 332.1–780.3) — **below** the
locator, so the sensor simultaneously proposes garbage and misses the real tree.

### 11.2 CRITICAL — §3.3's "none a magnitude test" is false, and §7's output is unreachable

- *"Row separators are the single-segment rules of maximal span (50.0–563.1 on p0)"* — that
  rule is **9 raw segments**, not one. A running-max abutment merge is load-bearing at step
  one and is not stated. (A naive pairwise merge fails: the nested segment `(52.6, 300.04)`
  fabricates a 2.64pt gap.)
- Under the stated parent test, apple p0 yields **4 parent nodes, not the 2 §7 requires** —
  every rule is drawn twice. Collapsing them needs the same undisclosed Δy ≤ 1.5pt constant.
- **A constant-free fix exists** and should be adopted: the doubling is an artifact of
  `extract_hrules` reading `page.lines + page.edges`, which reports the top and bottom edge of
  each filled rect separately. Reading `page.rects` gives one object per drawn mark, and under
  a tol=0 abutment merge apple p0's parent rect collapses to exactly `(302.68, 431.08)` and
  `(434.68, 563.08)` — two spans, no constant. It does **not** rescue §11.1.

### 11.3 HIGH — §4's "proposal versus silence" collapses on its only worked example

Re-measured on apple p2:

```
color=(1.0,1.0,1.0):  152 rects, y 162.12..689.40      <- white stripes painted EXPLICITLY
color=(0.937,...):    162 rects, y 148.92..703.56
rects covering the first data row (y~137.4-151): 0
```

The zebra is three-valued — GREY / WHITE / NO-FILL — so NO-FILL is a **positive proposal of
exclusion**, not an absence of opinion. §2.1 already treats the zebra's extent as a boundary
proposal when refuting it, then §4 calls the same fact a silence. Decoration and text
therefore **disagree** on that row, with decoration outranking — and under §4 the correct row
would be discarded. §5's "no document demands a NEURAL disposal yet" is false: the specimen
demands one today.

### 11.4 HIGH — §7's score criterion cannot fail, and §3.4 overclaims

- §7 accepts score-up, score-flat and score-down. No outcome is a failure. Worse, it is not
  checkable: region 4 today asserts 20 cells (4 data rows × 5 columns, row 0 eaten as
  header), and a *correct* reading of the same region is 5 data rows × 4 measure columns =
  **20 cells again**. Right and wrong readings are numerically indistinguishable at the
  headline score. The criterion must become cell-level against a committed ground-truth
  transcription for apple p0 — which this spec removed when it replaced the predecessor's §1.1.
- **§3.4's "row hierarchy" is wrong about direction.** Re-measured on apple p1: `Total current
  assets 149,818` sits at x0=**88.6**, *deeper* than its six members at 70.6
  (39,544+22,855+31,398+27,509+11,092+17,420 = 149,818), and `Total assets` deeper still at
  106.6. Indent yields **levels**, not containment direction; direction needs the arithmetic
  (C5). Also `Commitments and contingencies` (p1, measure-less, on-lattice at 52.6, no
  children) is a **third row class** the §3.4 + §3.6 pair cannot express, so §2.1's
  "all seven are parents" is true of p0 and false of p1.
- §3.4's floor is not "untested" as §9 claims — it is **measurably wrong on p1**: the 79.6
  level has exactly two members and both are wrap continuations, a 20% false-level rate on
  the page §3.4 calls discriminating.

### 11.5 Confirmed without qualification

The review reproduced, exactly: §2.2's compile output including
`score=0.11695906432748537 asserted=20 escalated=151` and every region reason; §2.1's whole
refutation table; §3.1's plateau (and strengthened it — tie-break-invariant, tables surviving
to g=33–60 against prose dying at g=3, a ~10× margin); §3.2's apple ratios with a 3× margin
over every other page; §3.3's rule listings; §3.5's in-region figures. **P1, P2, P4, P7
stand.** No contradiction with `residues.md` was found, and §7's "derived with no reference to
cell datatypes" is a genuinely correct answer to R71's circularity.

### 11.6 What would unblock

1. **Replace the locator.** It must be relative to the table's own frame (predecessor §2.2)
   and be **measured on WHO 0/1/2, cbh, stem, capacity before design closes** — not argued
   from apple. This is the real work; everything else is repair.
2. **Re-derive P5 honestly** under whatever locator survives, and demote P9 from "argued" to
   measured, adding WHO to the byte-identity criterion with the same force as stem.
3. Adopt the rect-based reader (§11.2) and state both merge rules explicitly.
4. Drop §4's silence distinction; a sensor proposes across the y-extent its evidence covers.
   Then dispose apple p2's row honestly, or name the deferral.
5. Make §7 cell-level against a committed transcription.
6. Correct §3.4 per §11.4; restate §3.2's verdict as a bijection test rather than a ratio.

**The architecture is not what failed.** Concurrency, the decoration-over-text priority, the
constraint set, and the non-circular answer to R71 all survive. What failed is one ordinal
locator, generalised from a single document.
