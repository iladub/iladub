# A data grid's row-group labels, proposed by a reader and disposed exactly (design, 2026-10-28)

**Serves:** prog:criterion:tab:08 — DATAGRID_RESIDUE disposed. This design removes the largest
general class of residue ink. It does not by itself meet the criterion; §7 states what else must
happen and which parts are the maintainer's.

**Doc impact: increment.** An adopted grid gains printed row-group header nodes, one new `tab:`
class and one shape are added, a recordings directory is added, and the corpus baseline moves. No
released meaning changes.

**Status: DRAFT, for the maintainer's review.** §9 lists the decisions that are the maintainer's.

**Authoring cost, stated per the handoff rule.** This spec was written by a dispatched agent past the
originating floor (well over 50,000 working tokens; most of them were probe output). Every measured
fact in §2 carries its command and output, and a fresh session can re-run them. The design in §§3–5
is a **proposition**: it rests on predictions that are listed in §6 and must be run.

## 1. Goal

When the data grid adopts a page (`compile.py`, the `datagrid_adopt` branch), every unread line of a
touched band becomes residue, and the page emits one `DATAGRID_RESIDUE` candidate
(`compile.py:2210-2219`). The committed baseline shows **14** such regions over 6 documents. The
census in §2.2 sorts their **397** tokens into classes. The largest class that recurs across
documents is **row-group labels**: a printed line such as `Operating activities:`,
`Western Pacific Region`, `Percentage change, latest year on previous year` or `ZONE 4` that names
a run of the grid's rows and holds no entry of its own. That class holds 119 tokens and appears in 12
of the 14 regions and 5 of the 6 documents.

The goal is to carry those labels as structure: header nodes over the grid's rows, nested where the
author nested them. A label carried this way leaves the residue, and the grid's rows gain the path
the author printed (`Operating activities › Adjustments … › Depreciation and amortization`).

## 2. Measured before this spec (2026-10-28, `main` at `087c1ca`)

### 2.1 Where it fires, and which firings the criterion counts

```
$ grep -c DATAGRID_RESIDUE tests/corpus-baseline/*.json      (non-zero rows only)
apple-fy2026q3-statements.json:1   bfs-population-bilan-2023.json:1   caltrain-weekend-timetable.json:4
fed-h41-2025-01-02.json:5          ons-index-of-services-2026-02.json:2   who-covid-sitrep-41.json:1
```

Region positions, from the same JSON: apple p2 r9, bfs p5 r19, caltrain p0–p3 r2, fed p2 r6, p3 r9,
p5 r5, p8 r9, p10 r5, ons p7 r18, p8 r10, who-covid p3 r2.

**The criterion counts only three of them.** `tests/corpus_firings.py::_docs_by_pdf` keys the
manifest on `"corpus/" + cor:file`, so held-out documents produce no firing pair. The oracle's live
pairs, measured with a scratch script that calls `live_pairs(ADJUDICATED)` and `is_disposed`:

```
apple-fy2026q3-statements DATAGRID_RESIDUE False
bfs-population-bilan-2023 DATAGRID_RESIDUE False
ons-index-of-services-2026-02 DATAGRID_RESIDUE False
```

So tab:08 is 3 undisposed pairs: apple, bfs and ons. Caltrain, fed and who-covid are held out. The
design is measured on them because they are the overfitting check, not because the criterion
counts them.

**The arc-manifest comment above tab:08 is stale.** It reads "FIRES 1 — apple p1". apple p1 no
longer adopts (`adopted [2]` in the baseline), and the one apple firing is on p2.

### 2.2 The residue census — what the unread lines are

The instrument is a scratch probe that wraps `iladub.etkl.adoption.build_ledger` with a spy, runs
`compile_tables(pdf, page, validate_shapes=True, datagrid_adopt=True)`, and prints every
`led.residue` line: its index, its position relative to the admitted lines, `x0`, its word count,
its `datagrid.ink_runs` count, and the next admitted line. It runs at page scope. **Page-scope
escalated totals equal the baseline's page `escalated` on all 14 pages** (for example apple p2 27,
bfs p5 76, caltrain 41/48/48/48, fed 102/33/64/12/1, ons 32/44, who 11). The residue token sum per
page also equals the `DATAGRID_RESIDUE` region's `tokens_escalated`. Abridged output, with the
classification added:

```
apple p2  (6 lines / 27 tok)   7 Operating activities: | 9 Adjustments to reconcile net income …: |
          13 Changes in operating assets and liabilities: | 21 Investing activities: |
          28 Financing activities: | 39 Supplemental cash flow disclosure:          → all GROUP
bfs p5    (2 / 17)   2 "État de laComposantes de l'évolution … État de laVariation" (runs=2) → HEADER FRAG
                     15 "8 237 666 8 327 126" (runs=2, R294)                              → UNREAD ENTRY
caltrain p0 (8 / 41) 0,1 title lines (runs 5,7) → TITLE | 3 "6XX Local" → LEGEND |
          8,15,25,31 "4 ENOZ" … "1 ENOZ" (rotated ZONE n, x0≈16) → GROUP | 33 EFFECTIVE … (runs 3) → NOTE
caltrain p1–p3 (9 / 48 each)   the same shape plus a third title line (Northbound/Southbound …)
fed p2    (1 / 9)    7 Securities held in custody for foreign official and international → WRAPPED STUB
fed p3    (6 / 33)   6 U.S. Treasury securities2 | 9 Federal agency debt securities3 |
          12 Mortgage-backed securities4 → GROUP | 14 "Weekly changes 0 0 - 3 …" (runs=13) → UNREAD ENTRY |
          15,16 Loan participations held by MS / Facilities 2020 LLC (Main Street (next line 17
          is admitted) → WRAPPED STUB
fed p5    (4 / 26)   7 Assets → GROUP | 11, 25 (first lines of two-line row labels) → WRAPPED STUB |
          29 "Items in process of collection (0) 88 + 21 - 4" (runs=7) → UNREAD ENTRY
fed p8    (4 / 12)   6 Liabilities, 20 Capital → GROUP | 14, 17 → WRAPPED STUB
fed p10   (1 / 1)    14 Memo: → GROUP
ons p7    (5 / 32)   36, 43 "Percentage change, …" → GROUP | 9, 37, 44 "S2KU S2MV KI7B …" series-ID rows → HEADER FRAG
ons p8    (6 / 44)   10, 27 "Percentage change, …" → GROUP | 8 "Section G-T G and I …" boxhead line,
          11, 28, 45 series-ID rows → HEADER FRAG
who p3    (4 / 11)   5 Western Pacific Region, 15 European Region, 43 South-East Asia Region,
          48 Eastern Mediterranean Region → GROUP
```

| class | apple | bfs | caltrain | fed | ons | who | **total** | docs | regions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **row-group labels** | 27 | 0 | 32 | 13 | 36 | 11 | **119** | **5** | **12/14** |
| footnotes / notes below | 0 | 0 | 74 | 0 | 0 | 0 | 74 | 1 | 4 |
| titles above | 0 | 0 | 71 | 0 | 0 | 0 | 71 | 1 | 4 |
| header fragments in the body (spanner line, boxhead line, per-section series-ID rows) | 0 | 11 | 0 | 0 | 40 | 0 | 51 | 2 | 3 |
| wrapped row-label (stub) fragments | 0 | 0 | 0 | 43 | 0 | 0 | 43 | 1 | 4 |
| unread entry rows (values the grid did not admit) | 0 | 6 | 0 | 25 | 0 | 0 | 31 | 2 | 3 |
| legend | 0 | 0 | 8 | 0 | 0 | 0 | 8 | 1 | 4 |
| **total** | 27 | 17 | 185 | 81 | 76 | 11 | **397** | | |

**What decides the design.** Titles, notes and the legend are 153 tokens, but they come from one
document, a timetable whose page furniture repeats on four pages. Wrapped stubs are fed only. Header
fragments are three unrelated shapes in two documents. Row-group labels are the only class present
in most documents and most regions. For the criterion's three documents they are 63 of 120 tokens:
apple 27 of 27, ons 36 of 76, bfs 0 of 17.

### 2.3 Facts the oracle rests on (same probe, second pass)

For every line classified GROUP above: `len(ink_runs(line)) == 1`, and in page order the line
is followed by an admitted grid line with **no other grid row between them**. The non-admitted lines
that do sit between are ons's series-ID rows, which are not grid rows. Examples:
`7 Operating activities: runs=1 next_admitted=8`, `36 Percentage change… runs=1 next_admitted=38
nonadmitted_between=[37]`. The exception is caltrain's rotated zone labels. Each one is printed
*beside* its stations, spanning their height, not above them (`4 ENOZ top=173.7 bottom=191.7`, first
member line 9).

**What these exact facts cannot separate.** WRAPPED STUB first lines (fed, `runs=1`, adjacent),
the caltrain legend `6XX Local` (`runs=1`, adjacent to line 4) and the who labels all pass the same
two tests. Multi-run lines do not pass: titles (5–7 runs), unread entry rows (7–13 runs), series-ID
rows (5 runs), the bfs spanner line (2 runs) and the caltrain notes (3 runs). So the exact legs
exclude every non-label class except wrapped stubs and the legend. Telling those apart from a group
label is the reading judgment, and §3.1 assigns it to the worker.

### 2.4 The criterion's blockers, re-measured (M8 binds them)

tab:08 is `prog:blockedBy "R79", "R83", "R84"` (`tests/arc-manifest.ttl:1393-1402`). M8 refuses
`met true` while any of them is open. Each was raised as **dormant**, so it was re-measured on all 14
pages with a second scratch probe. The probe reproduces `build_ledger`'s own `_covers` and
`booked_bands` and compares the report's escalated reasons with the `iladub:CandidateConcept` labels
in `rep.graph`:

```
apple p2   R84 admitted-outside-booked 3 tok 11 | R83 untouched escalated bands []
bfs p5     R84 3 tok 43 | R83 [(8,'REGION_TILING_FAILED',20),(15,'KIND_NOT_SUPPORTED',39)]
           report {REGION_TILING_FAILED:1, KIND_NOT_SUPPORTED:1, DATAGRID_RESIDUE:1}  graph {DATAGRID_RESIDUE:1}
fed p2     R84 0 | R83 [(4,'ROUND_TRIP_FAIL',93)]   graph {DATAGRID_RESIDUE:1}
fed p3     R84 4 tok 49 | fed p5 R83 [(1,'KIND_NOT_SUPPORTED',12),(3,'RULE_SEPARATED_INK',26)]
fed p8     R84 2 tok 32 | ons p7 R84 8 tok 43 | ons p8 R84 2 tok 5 | all others 0 / []
```

- **R83 is LIVE**, no longer dormant. Its own trigger has fired: on bfs p5 (a corpus page), fed p2 and
  fed p5, the page-scope report books untouched escalated bands that `rep.graph` does not escalate.
  The document path is unaffected, per the row.
- **R84 is LIVE** on 6 of 14 pages, including all three of the criterion's documents. Admitted grid
  lines that no booked band covers are counted as asserted.
- **R79** is unchanged: one candidate per page, with lines joined by newlines.

None of the three decides *whether DATAGRID_RESIDUE is disposed*. Two are ledger/graph accounting
and one is the candidate's granularity. §7 puts the edge question to the maintainer.

### 2.5 R80 re-measured (it blocks tab:04)

apple p1 no longer adopts (`adoption not_opened`, 98 asserted / 0 escalated). The band path now
carries all 7 of R80's labels as `tab:LabelCell`s (`mtable2-rhl0` `ASSETS:` … `mtable2-rhl30`
`Shareholders’ equity:`). The same probe dumps the row-header tree, and it is **flat**: 38 header
nodes, every one at `headerLevel 0` with no parent, and each label covering **only its own blank
row** (`mtable2-rh1 lvl 0 parent [] rows [1] | Current assets:`). R80's wording, *"escalated as
residue"*, is now false. Its substance, *"the indent hierarchy is read by nobody"*, is still true:
a group label is asserted as a leaf row with no values. This design does not touch the band path
(§5), so R80 stays open with its claim narrowed. The register edit is owed (§8).

## 3. Design

### 3.1 The row-group worker (NEURAL)

- **When it is asked.** Once per grid at the adoption site, after the boxhead and caption workers,
  and only if the grid has *candidate lines*. A candidate line is a line that a preliminary
  `build_ledger` call over the grid's current read lines would put in `residue`. That call is pure
  and cheap, and the site already calls it more than once. **Seam, measure before writing the
  call:** the candidate set must come from the same `_lines` / `bands` / `reports` that the final
  ledger uses (`compile.py:2066-2081`).
- **The question.** *Which of these unread lines are headings that name a run of the table's rows,
  and which rows does each one name?* The worker sees the grid crop (the same renderer as
  `read_grid_boxhead`), a numbered listing of the candidate lines, and a numbered listing of the
  grid's rows, each shown by its first ink run.
- **The answer.** A strongly typed, closed shape:
  `{groups: [{label_lines: int[], first_row: int, last_row: int}], refuses: bool}`. It contains
  indices only and never text, so it cannot return a value from the page. Nesting is **not** asked
  for; §3.3 derives it.
- **Recording.** Under `readings/row_group/`, keyed on `sha256("rowgroup\n" + candidate listing +
  "\n" + row listing)`. It replays offline and is disposed again on every compile, as
  `RecordedBoxheadReader` and `RecordedCaptionReader` do. The `refuses` default is NO CLAIM.

**Why NEURAL, and why not an AXIOM over existing evidence.** The decision is *which rows does X
span*, which CLAUDE.md §8 names as a NEURAL reading judgment. The one AXIOM witness that already
exists is a confirmed aggregation row, which `rowgroups.py` uses to derive `tab:DerivedRowGroup`
with exact Decimal arithmetic. It cannot cover this class **by construction**. ons's sections are
percentage changes, which do not sum. Caltrain's zones and who's regions head rows that are not
summed in the grid. A label with no arithmetic witness would never be read. The aggregation witness
is kept, but as an oracle leg (D7), not as the derivation. No geometric attempt is made: "a
one-run line directly above grid rows is a group label" would admit fed's wrapped stubs and
caltrain's legend (§2.3), which is the heuristic the 2026-09-17 ruling forbids.

### 3.2 The disposal (the oracle; PROCEDURAL; every check exact, no constant)

Per group, unless stated otherwise. A group that fails is dropped (NO CLAIM for it), and the other
groups stand. **D1 and D6 refuse the whole reading.**

- **D1 Address space.** Every `label_lines` index is a candidate index, and no index is used twice
  across groups. `0 <= first_row <= last_row < n_rows`. *Whole reading.*
- **D2 Label-only ink.** Every label line is exactly one ink run under `datagrid.ink_runs`. That is
  the shipped `GAP`, justified by its invariance plateau (`datagrid.py`), and no new number is
  introduced. A line holding a value in a value column has more than one run. §2.3 measured this
  refusing every unread-entry, title, series-ID, spanner and note line in the census.
- **D3 Label contiguity.** A multi-line label's lines are consecutive in page order, with no grid
  row between them.
- **D4 Placement.** Exactly one of two forms holds. **Heading:** the label's last line precedes the
  `first_row` line in page order, and no grid row lies strictly between them. **Side label:** every
  label line's `[top, bottom]` lies within `[top(first_row), bottom(last_row)]`, and the label's
  `x1` is less than the `x0` of every grid column. This is the row-axis mirror of the shipped
  column-spanner disposal ("extent ⊆ group").
- **D5 Members.** `first_row..last_row` is a contiguous run of grid rows. The run is contiguous by
  construction, so the check is on the indices.
- **D6 Laminar.** Any two surviving groups are nested or disjoint, and two groups with identical
  extents are a violation. *Whole reading* — the same ruling the maintainer gave for spanners on
  2026-10-24 (laminar violation drops the class, keeps the rest of the grid).
- **D7 Arithmetic consistency.** For every `tab:DetectedAggregationRow` of the grid (exact
  Decimal), its operand set and each group's extent are nested or disjoint. A crossing refuses the
  group. This is the only leg that brings independent evidence about where a group *ends*.

**What the oracle cannot catch, stated plainly.** A group that ends too early, because coverage
may be partial, as for `tab:DerivedRowGroup`. A wrapped stub first line claimed as a one-row
heading. A legend claimed as a heading over the first row. All three carry printed text as
structure it does not have, and §6 lists them. None of them loses ink or invents a value.

### 3.3 Carriage (PROCEDURAL emission)

Level and parent are a deterministic function of the surviving laminar set: the parent is the
smallest strictly containing group, and the level is the depth. For each group:

- one `tab:HeaderNode`, also typed **`tab:PrintedRowGroup`** (new, `rdfs:subClassOf tab:HeaderNode`,
  sibling of `tab:DerivedRowGroup`), with `tab:headerLevel`, at most one `tab:parentHeader`, and
  `tab:coversRow` on each member grid row (the grid's `tab:LeafRow` URIs);
- `tab:hasLabel` pointing to one `tab:LabelCell` that carries `tab:cellText` (the label lines'
  words, in extractor order, exact to the extractor per R318), `tab:onPage` and `tab:hasBBox`;
- `grid tab:hasHeaderNode node` and `grid tab:hasCell labelcell`, which mirror `emit_boxhead`
  (`boxhead.py:437`, the column-axis twin).

**Membrane.** A new `tab:PrintedRowGroupShape` requires exactly one `hasLabel`, at least one
`coversRow` and at most one `parentHeader`. The shipped `tab:RowRefinementShape`
(`tab-shapes.ttl:191-202`) already refuses a child that covers a row its parent does not.
`tab:RowNoOverlapShape` (`:172-189`) already refuses two same-level nodes over one row. The
row-coverage and unambiguous-row-access shapes join on `tab:hasLeafRow` (`:158-170`, `:211-226`),
which a grid does not emit (it emits `tab:hasGridRow`), so partial coverage is not refused. **Seam,
measure before relying on it:** confirm on a real adopted page graph that neither shape targets
grid rows under `inference="rdfs"`.

**The ledger.** The label lines of the surviving groups join the grid's read lines in `_read`
(`compile.py:2077-2079`) before the final `build_ledger`, exactly as captions do. No ledger rule
changes.

### 3.4 Order at the adoption site

Boxhead, then spanners, then captions (all as shipped), then the preliminary residue, the row-group
worker, the disposal, the final `build_ledger`, and emission. Because the final ledger shrinks, **the
adoption gate's comparison (`_led.escalated_tokens < escalated_total`) can now pass on a page that
refuses today** (§6).

## 4. Gate classification (CLAUDE.md § 8)

| decision | class | why |
|---|---|---|
| which unread lines are row-group labels, and which rows each one names | **NEURAL** (new worker) | a *which rows does X span* judgment; no arithmetic witness exists for most groups (§3.1) |
| D1–D7 disposal | **PROCEDURAL**, disposal | index, ordinal, interval and set comparisons over the grid's own rows and the extractor's lines; the one number used is the shipped plateau-justified `GAP`; no new constant |
| level and parent | **PROCEDURAL**, emission | a deterministic function of the disposed laminar set |
| child ⊆ parent, no same-level overlap, group well-formedness | **AXIOM** (SHACL, closed world) | the membrane: two shipped shapes plus one new one |
| candidate lines | **PROCEDURAL** | set difference from a pure ledger call |

No tuned constant appears anywhere. The one geometric idea ("a one-run line above rows is a label")
is not attempted. §2.3 measured it as refuted before anything was built: it admits wrapped stubs and
the legend.

## 5. What is NOT done

- **The band path.** apple p1's flat label rows (R80, §2.5) are not re-read. The worker sits at the
  adoption site only. Pointing it at a hierarchical band is a later loop.
- **Titles, notes and the legend** (153 tokens, caltrain only). Whether the caption worker (R336)
  should be asked about lines *above a grid's first row* outside its header block is a separate
  question.
- **Wrapped row labels** (43 tokens, fed only), **unread entry rows** (31, incl. R294) and **header
  fragments in the body** (51: ons's per-section series-ID rows, bfs's spanner line).
- **Reading rotated text.** Caltrain's `4 ENOZ` is carried verbatim as the extractor gives it.
- **R79's per-run candidates**, **R83** and **R84.** They are measured live here (§2.4) and not
  repaired.
- **tab:04.** It stays unmet: R74 belongs to another lane, and R80 stays open (§2.5).

## 6. Unverified, and the predicted blast radius

**Predictions (proposed, each to be run by the plan before building on it):**

- apple p2: all 6 labels pass D1–D7, so the residue goes from 27 to 0 tokens and **apple stops firing
  DATAGRID_RESIDUE**. The labels nest: `Adjustments …` and `Changes in operating …` sit under
  `Operating activities:`. Falsifier: any one label refused leaves apple firing.
- who-covid p3 goes from 11 to 0 and fed p10 from 1 to 0 (both stop firing). ons goes from 76 to 40
  and still fires. bfs stays at 17 and still fires. fed p3/p5/p8 lose 9/1/2 tokens and caltrain
  loses 8 per page (if D4's side-label form admits the zones). Best case, live regions fall from 14
  to 11, and on the criterion's documents from 3 to 2.
- **Adoption flips (unmeasured, and the largest risk):** pages whose ledger is refused today may
  adopt once labels leave the residue. The plan's first task measures `rep.adoption` on every
  candidate page, with the recordings, before and after.
- **D7** may refuse a true group, for example where a subtotal's operands cross a nested heading.
  This has not been measured on any page.
- **Over-claiming:** whether the worker claims fed's wrapped stubs or caltrain's `6XX Local`
  (§3.2). Both pass the oracle.
- **feed.** Whether `feed._row_header_path` (`feed.py:859`) reads a grid's `coversRow` tree, which
  would change record identities on adopted pages. Measure it before emission lands.
- **Corpus baseline.** `src/`, `vocab/` and `readings/` change, so `scripts/corpus_baseline.py
  regenerate` is owed after the last input edit. Its diff is the blast radius (CLAUDE.md § Corpus
  baseline).

**Tests (each with a FALSIFICATION block, per plan rule 4):** one synthetic disposal test per leg
D1–D7, each showing NO CLAIM. A no-candidate identity test: a refusing reading gives a graph
byte-identical to `main`. apple p2 end to end, offline and recorded: no `DATAGRID_RESIDUE` region,
6 `tab:PrintedRowGroup` nodes with the nesting above, and a conforming page graph. ons p7, partial:
two groups, with the series-ID rows still in the residue.

## 7. How tab:08 becomes met (its own wording, plus M8)

The statement is met when *every firing document carries a dated `cor:adjudication` naming and
disposing of it*. The test is `cor:disposes "DATAGRID_RESIDUE"` on each live pair
(`tests/test_corpus.py:227`). Three steps:

1. **This design**, if §6 holds, removes the apple pair because apple stops firing.
2. **ons and bfs still fire** (40 and 17 tokens, none of them group labels). Each needs a dated
   adjudication with `cor:disposes "DATAGRID_RESIDUE"` that names the remaining ink: ons's series-ID
   rows and section boxhead line, and bfs's spanner line and R294's two figures. bfs's 2026-10-05
   note already describes its residue in prose but carries no `cor:disposes` for this reason. Writing
   these is an adjudication, which makes it the maintainer's act.
3. **M8:** R79, R83 and R84 must be closed, or their edges deleted with a recorded reason (precedent:
   the `DELETED …` blocks at `tests/arc-manifest.ttl:1832-1860`).

## 8. Register edits owed (not made by this spec)

R80: claim narrowed (§2.5). R83 and R84: dormancy refuted, with measurements (§2.4). tab:08's
arc-manifest comment: "apple p1" should read "apple p2", and the census is 14 regions / 3 counted
pairs. tab:04: its `prog:blockedBy "R77"` edge names a closed row, which the 2026-08-22 ruling says
should have been deleted when R77 closed.

## 9. Decisions for the maintainer

1. **Live recording budget.** Recording only apple would make the worker work on one document. The
   proposal is one live sample per grid that has candidate lines, across `corpus/` and `held-out/`,
   recorded once, as ruled for the caption worker on 2026-10-24. The plan measures the count first.
2. **tab:08's blockers.** (a) Delete the R79/R83/R84 edges as orthogonal to disposal, with a
   recorded reason, and keep the rows open, noting that R83 and R84 are now live. Or (b) close them
   first, which takes at least two more loops.
3. **The ons and bfs adjudications** (§7 step 2): whether to dispose of the remaining residue by
   adjudication, or to hold the criterion until more classes are read.
4. **D4's side-label form.** It is in scope for generality (the row mirror of a column spanner), but
   its only measured instance is held-out caltrain. Keep it, or cut it to the heading form.
5. **A new class `tab:PrintedRowGroup`**, rather than reusing `tab:DerivedRowGroup`, whose shape
   requires an aggregation witness (`tab-shapes.ttl:337-348`).

## 10. Adversarial pass on this spec's own premises

- *"Group labels are the general class."* They lead on breadth (5 of 6 documents, 12 of 14
  regions). They do not lead on tokens: titles and notes together hold more, but in one document.
  If the maintainer weights the criterion's three documents only, group labels are still the
  largest class there (63 of 120 tokens). That premise survives.
- *"The census classification is right."* It is my reading of extracted text, not of the rendered
  page. The fed WRAPPED STUB calls rest on the next line being admitted, and
  `Loan participations … (Main Street` was reclassified from GROUP to WRAPPED STUB on exactly that
  evidence. A human read of fed p3/p5/p8 and ons p7/p8 against the page should precede the plan.
- *"This serves tab:08."* Only partly. It retires one of three pairs. The criterion moves to met only
  through adjudications and an M8 ruling that this spec cannot make. A reviewer could fairly call
  this a maintenance loop with a criterion attached. The defence is that without it, apple's pair
  can only be closed by adjudicating away 27 tokens of real, readable structure.
- *"Page scope stands for document scope."* It does on the totals, which matched on all 14 pages.
  The document driver passes `carried_header_roles` on continuation pages (`document.py:1833-1838`),
  so a page with a cross-page header could differ. None of the 14 was observed to.
- *"D2's one-run test is not a heuristic."* It decides nothing on its own. It disposes a proposal and
  fails safe, refusing a true label rather than admitting a false one. If a real label carries a
  second run, such as a right-aligned footnote mark, it is refused and stays in the residue, which is
  today's state.
