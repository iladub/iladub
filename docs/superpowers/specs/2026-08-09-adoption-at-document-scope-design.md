# Adoption at document scope (R73) — design

**Date:** 2026-08-09 · **Status:** design, approved · **Residue closed:** R73 ·
**Specimen:** `corpus/financial/apple-fy2026q3-statements.pdf` page 1 (the fourth transcribed
oracle, 28 entry rows), with `corpus/ag-trade/graincorp-stem-2026-07-31.pdf` as the control
and the adjudicated floor · **Builds on:** `2026-08-08-data-grid-types-elements-axioms.md`
(the data grid, closed), loop M (continuation carriage, R29), loop Q (section repair)

**Doc impact:** increment — `docs/wiki/concepts/data-grid.md` gains the adoption section
(it currently records only "`datagrid_adopt`, off by default"). No site page contradicted.

---

## 0. The claim, in one line

A page's total reading failure is **not final at page scope**: adoption is the document's
**last** reader, admitted only where carriage, section repair and stitching have all had
their turn and the page still asserted nothing — and what it withdraws is the escalation of
the ink it actually **read**, line by line, never the page's whole ledger.

## 1. What R73 said, and where it was wrong

The register's R73 row, and the docstring of `test_adoption_is_off_by_default`, state:

> `document.compile_document` compiles each page standalone BEFORE re-compiling continuation
> pages with carried headers, and stem p1/p2 escalate standalone BY DESIGN (R29) so that
> carriage can happen. Both would adopt.

**Measured, and the mechanism is false.** `compile_document` makes **one pass** over the
pages (`src/iladub/etkl/document.py:1152-1195`). Recognition reads only the band inventory
(`page_bands`), so it needs nothing from page p's compile; the carried reading is an
**input** to page p's single compile, not a re-compile after a standalone one. There is no
standalone compile of a continuation page anywhere in the driver.

The consequence is directly measured. With `datagrid_adopt` **forced True on every page** of
the driver's compiles, the stem document is byte-identical to its adjudicated floor:

```
document score = 0.9654553611484971      (floor: 0.9654553611484971)
chains         = 1 chain of 3
  page 0: score=0.9560 asserted=586 escalated=27
  page 1: score=0.9706 asserted=825 escalated=25
  page 2: score=0.9674 asserted=741 escalated=25
```

Adoption never fires on stem, because carriage makes p1/p2 assert **before** the gate
(`asserted_total == 0`) is ever reached. The floor was never at risk from the flag. R73's
row is corrected by this loop, not merely closed.

**What R73 does not name, and what is actually exposed** (both measured, §3).

- **The band-index contract breaks.** Adoption replaces the whole `reports` tuple with a
  single region (`src/iladub/etkl/compile.py:895-897`, `band_marks = [(0, 0)]`), destroying
  the pinned "region report index IS band index" contract the driver reads at
  `document.py:1176` (`regions[prev_idx].header_reading`), `:1201`, `:1244`, `:1262` and
  `:1310`. Apple survives only because it has no recognition and no section group; a
  document with both would index into a 1-tuple.
- **An adopted page can never join a chain.** The adopted region carries `table_uri=None`,
  so the driver silently takes the R29 "recognized, but one side asserted no table" branch.
- **The page score becomes a tautology.** Adoption sets `escalated_total = 0`
  unconditionally, so an adopted page scores exactly 1.0000 whatever the grid failed to
  read. The score can no longer falsify the adoption.

## 2. What proposes, what disposes, and why they are independent

Per R76, named before anything is designed.

**PROPOSER — `derive_data_grid` (`src/iladub/etkl/datagrid.py:319`).** The grid axioms over
the page's line and rectangle evidence propose a complete page reading: a set of admitted
row indices and their column placement. It knows nothing about bands, verdicts, carriage or
chains.

**DISPOSER — the document-scope outcome of the shipped pipeline.** A proposal is admitted
only where the page, after carriage (loop M), section repair (loop Q) and intra-page
stitching, still asserted **zero** cells while escalating some. The two share no code path:
the pipeline reads bands, rules, header blocks and carried readings; the grid reads lines and
rectangles.

**Independence is measured, not argued.** Forcing adoption at page scope leaves the stem
document byte-identical (§1) — because a *different* mechanism, carriage, had already
asserted those pages. The disposer refuses without ever consulting the proposer.

**The reading's correctness is disposed by a third, older artifact:** the hand transcriptions
(apple p1 at 28 entry rows, read 28 of 28 with nothing leaked; cbh p0 at 45 vessel rows plus
4 panel totals). They predate this design and were built before the data grid had one.

## 3. What is measured

All figures produced this session on the shipped corpus, `validate_shapes` at its default
unless stated.

**M1 — the apple document, adoption off then forced on.**

```
adopt off:  document score = 0.06068601583113457
            p0: asserted=20  escalated=151  regions=8   (band 4 asserts, RecordTable)
            p1: asserted=0   escalated=97   regions=8   (5 bands escalate HierarchicalTable)
            p2: asserted=3   escalated=108  regions=8
adopt on :  document score = 0.3891509433962264
            p1: asserted=142 escalated=0    regions=1   score=1.0000  cells=84
recognized = ()   chains = two chains of one
```

**M2 — the stem document, adoption forced on: byte-identical to the floor.** See §1.

**M3 — the refusal branch, on real evidence.** stem p1 and p2 compiled *standalone* — the
only context in which the driver's own pages are adoption candidates:

```
stem p1 standalone, adopt off:   0 cells, escalated 850, score 0.0000, regions 3
stem p1 standalone, adopt on :  811 cells FLAT, escalated 0, score 1.0000, regions 1
stem p1 under the driver     :  825 cells hierarchical, chain member, score 0.9706
stem p2 standalone, adopt on :  726 cells FLAT, escalated 0, score 1.0000, regions 1
stem p2 under the driver     :  741 cells hierarchical, chain member, score 0.9674
```

Page-scope adoption would substitute a flat 811-cell grid for the 825-cell hierarchical,
chain-joined reading — **and report 1.0000 for the substitution against 0.9706 for the
correct reading**. The score, as adoption computes it today, prefers the worse reading. This
is the refusal branch this design exists to guarantee, and it is reachable on real evidence.

**M4 — what adoption's zeroing hides.** apple p1 has 43 lines / 206 tokens, of which the
pipeline escalates 97. The grid admits 28 rows carrying 142 tokens, so **15 lines / 64
tokens are never admitted** — this half is exact, both sides coming from the one
`text_lines` sequence:

```
[  0]  2  Apple Inc.                        [ 21]  4  LIABILITIES AND SHAREHOLDERS' EQUITY:
[  1]  5  CONDENSED CONSOLIDATED BALANCE …  [ 22]  2  Current liabilities:
[  2] 14  (In millions, except number of …  [ 29]  2  Non-current liabilities:
[  3]  4  June 27, September 27,            [ 34]  3  Commitments and contingencies
[  4]  2  2026 2025                         [ 35]  2  Shareholders' equity:
[  5]  1  ASSETS:                           [ 36] 11  Common stock and additional paid-in …
[  6]  2  Current assets:                   [ 37]  8  authorized; 14,608,963 and 14,773,260 …
[ 14]  2  Non-current assets:
```

Splitting those 64 tokens between the *ignored* bands (the title block) and the *escalated*
bands needs a band→page-line join, and the scratch measurement did it by line text. That
join is **approximate** — it attributes 21 tokens to band 7, which escalated only 18, because
a band may split a line differently from the page-level sequence. It puts roughly **40 of
the 64 tokens inside escalated bands**, i.e. apple p1 would score about **0.78** rather than
1.0000. The design does not depend on the exact figure, only on `0 < leftover < 97`, which
is robust to the join; the implementation derives it exactly from the shared line sequence
(§5.3) and V3 records the measured value rather than confirming a predicted one.

The unadmitted lines are the balance sheet's own structure — `ASSETS:`, `Current assets:`,
`Non-current assets:`, `Shareholders' equity:`, the column-header lines
`June 27, September 27,` / `2026 2025`, and the wrapped par-value prose. The bands escalated
as `HierarchicalTable`; the grid reads the 28 leaf rows and drops the hierarchy.

**M5 — band granularity is not available.** No escalated band on apple p1 is *fully* covered
by the grid (every one has at least one line outside — a conclusion the approximate join is
strong enough to support, since it only needs one such line per band). A band-granular
ledger — withdraw a band only when the grid admitted all of it — therefore withdraws nothing,
and the page scores 142/(142+97) = **0.594**: precisely the double count that made the first
wiring's 0.5941 meaningless, since the grid's 142 tokens include the very lines those bands
escalate. The ledger must be **line**-granular or it is wrong in one of two known directions.

## 4. The falsifiers

Two, both already built, plus one this loop adds.

1. **The transcriptions** (apple p1, cbh p0) — falsify the *reading*. Pre-existing.
2. **The stem floor** `0.9654553611484971` with 1 chain of 3 — falsifies any change that
   costs the only adjudicated document. Pre-existing, re-measured this session (M2).
3. **The standalone/driver differential** (M3) — falsifies the *scope* claim. New, and the
   evidence for it is measured above before any code is written.

## 5. The design

### 5.1 Adoption becomes the document's last reader

`compile_tables(..., datagrid_adopt=…)` is **unchanged and stays off by default**: it remains
the page-scope API, and page-scope adoption remains a thing a caller may ask for explicitly
(M3 depends on being able to).

`compile_document` gains a final **adoption pass**, placed after the totals oracle and before
whole-graph validation — i.e. after carriage, after section repair, after §4.1 intra-page
stitching, after chain assembly and the chain arithmetic. Candidates are pages where, at that
point, `pages[p].asserted == 0 and pages[p].escalated > 0`.

Running last is load-bearing twice over. It is the decidability answer — *a total failure is
only final at document scope* — and it means no band-index consumer ever observes a rewritten
page, so §1's contract breakage cannot fire.

### 5.2 The gate is an AXIOM

"This page asserted nothing" is a **holon-scoped closed-world** question over the merged
graph: no `tab:EntryCell` carries `tab:onPage p`, and at least one escalation candidate does.
The holon is the closure boundary, so this is a legitimate query-local `NOT EXISTS` and the
gate belongs in a `.rq` (`vocab/queries/adoption-candidate.rq`), not in a Python condition.
It carries no numeric literal.

The **ledger arithmetic** of §5.3 is justified PROCEDURAL: exact counting over line-index
sets, decidable, with no tolerance and no threshold. It states so in the code.

### 5.3 The ledger is line-granular — every line counted exactly once

For an adopted page:

- `asserted` := tokens on lines the grid admitted (`grid.rows`);
- `escalated` := tokens on lines that an escalated band covered and the grid did **not**
  admit, plus the tokens of any escalated band the grid did not touch at all;
- no line contributes to both, and the two sets are asserted disjoint by a test, not by
  reasoning.

Target: apple p1 lands near **142 / ~40 ≈ 0.78** (M4 — the exact denominator is derived by
the implementation, not predicted here). Neither 1.0000 (§1's tautology) nor 0.594 (M5's
double count).

The join from a band's lines to page line indices must be an **exact** index-set operation.
Both sides derive from the same deterministic `text_lines(extract_words(pdf, page))`; the
implementation derives the band's line indices from that one sequence rather than comparing
coordinates. A coordinate comparison with a tolerance here would be a gate defect.

### 5.4 One reading per line in the graph, too

The graph must not carry a refusal and a reading over the same ink — the rule the adoption
comment already states (`compile.py:860-865`).

The unit of the graph is therefore the same as the unit of the ledger, which forces the
**overlap** rule — a band is not "covered" or "uncovered" but *touched* or *untouched*:

- A band the grid **overlapped at all** has its escalation record withdrawn (reusing loop Q's
  `_remove_escalation_record`). Its record no longer describes what happened: part of its ink
  has been read. On apple p1 that is every escalated band — M5 — which is exactly why a
  band-granular rule cannot work here.
- A band the grid **did not touch** keeps its escalation record and its tokens, unchanged.
- The lines of touched bands that the grid did **not** admit are re-escalated as **one
  page-level residue candidate** (an `iladub:CandidateConcept` carrying its line list and a
  reason naming the data grid as the reader that did not read them). Without it, those tokens
  count as escalated with nothing in the graph escalating them, and the ledger and the graph
  disagree.
- The grid's admission `dec:DecisionHolon` (already emitted by `emit_data_grid`) links
  `dec:supersedes` to each covered band's verdict decision — loop Q's precedent at
  `document.py:1283`, where the same link already makes a supersession queryable.

### 5.5 Reports keep the band-index contract

The adopted page's report keeps one entry per band:

- a band the grid **touched** gets verdict **`superseded`** (new string; every consumer is an
  equality test on `"asserted"`/`"escalated"`, verified by grep, so a third value is inert)
  and `tokens_escalated = 0` — its ink is now accounted for by the two appended regions;
- a band the grid did **not** touch keeps its report, its verdict and its tokens;
- the grid is **appended** as a region at index `len(bands)`, verdict `asserted`, carrying
  the `grid_uri` `emit_data_grid` already mints (`{doc}#p{page}-datagrid`) as its
  `table_uri`, anchor `tab:DataGrid`, `tokens_asserted` = the admitted lines' tokens;
- when the residue of §5.4 is non-empty it is appended as a **second** region at index
  `len(bands) + 1`, verdict `escalated`, anchor `tab:DataGrid`, `table_uri=None`,
  `tokens_escalated` = the unadmitted lines' tokens. The invariant
  `sum(r.tokens_*) == page.asserted/escalated` therefore holds by construction, as it does
  for every other path.

Region index ≡ band index therefore survives adoption. A `tab:DataGrid` is not a
`tab:Table`: it is **not** eligible to join a continuation chain, and the pass runs after
chain assembly so the question cannot arise.

## 6. Verification

| # | Check | Expected |
| --- | --- | --- |
| V1 | stem document score and chains | `== 0.9654553611484971` exactly, 1 chain of 3 |
| V2 | apple document score | rises from `0.06068601583113457`; the measured value is recorded, not predicted |
| V3 | apple p1 page score | `142 / (142 + leftover)`, leftover derived exactly (§5.3); expected ≈ 0.78, **recorded, never a floor to hit** |
| V4 | ledger disjointness | on every adopted page, no line index is on both sides; asserted+escalated tokens ≤ page tokens |
| V5 | the refusal branch (M3) | the driver's stem p1 keeps 825 cells and its chain membership; a test pins that the driver never consults a context-free compile for the adoption decision |
| V6 | the adopted page's reports | `len(regions) == len(bands) + 1` (+1 more when the residue is non-empty); the grid region carries a non-`None` `table_uri`; `sum(r.tokens_*)` equals the page aggregates |
| V7 | graph/ledger agreement | escalated tokens == residue candidate's line tokens + untouched escalated bands' tokens |
| V8 | corpus battery | every document still compiles; no floor lowered |

The three shipped page-level adoption tests are rewritten, not deleted:
`test_adoption_supersedes_an_escalation_exactly` asserts `escalated == 0` and `score == 1.0`
and both die with §5.3; `test_adoption_is_off_by_default`'s docstring premise is refuted by
§1 and is rewritten to the measured mechanism;
`test_adoption_never_touches_a_page_that_read_something` is unaffected.

## 7. What is NOT done here

- **The dropped hierarchy is not recovered.** apple p1's grid reads 28 leaf rows and does not
  read `Current assets:` / `Non-current assets:` as a row-group structure. That is a data-grid
  question (R-new, §8), not an adoption question.
- **`compile_tables`' page-scope adoption keeps its own ledger semantics** only in so far as
  §5.3 changes them; no other page-scope behaviour moves.
- **No SPARQL migration of the grid axioms** (the standing §8 debt of the data-grid spec).
  Only the adoption *gate* is authored as a `.rq`.
- **Nothing is done about R74/R77.** Untouched.

## 8. What this loop records

- **R73 deleted** from the register, with its mechanism corrected in the closing note (§1):
  the hazard as stated does not exist; the real exposures were the band-index contract, the
  chain-ineligible `table_uri`, and the score tautology.
- **New residue:** an adopted page's *unread* structure is escalated as one page-level
  residue candidate rather than per-line or per-band; a consumer wanting to know which
  structural lines were dropped reads the line list, not a typed refusal per line.
- **New residue:** apple p1's hierarchy (`Current assets:` and its siblings) is read by
  nobody — the pipeline escalates it as `HierarchicalTable` and the grid drops it. Measured
  at 15 unadmitted lines / 64 tokens, of which roughly 40 sit inside escalated bands.

## 9. Premise types (R76)

| Premise | Type |
| --- | --- |
| `compile_document` is one pass; carriage is an input (§1) | read-not-run, then measured (M2) |
| stem is byte-identical under forced adoption (M2) | measured on evidence |
| apple p1 escalates 97 tokens, grid admits 142 on 28 rows (M1, M4) | measured on evidence |
| 15 lines / 64 tokens are never admitted by the grid (M4) | measured on evidence |
| ~40 of those 64 tokens sit inside escalated bands (M4) | measured on evidence via an **approximate** text join — re-derived exactly by the implementation |
| every escalated band on apple p1 has at least one unadmitted line (M5) | measured on evidence; robust to the join's approximation |
| band-granular accounting reproduces 0.594 (M5) | proven arithmetically from M4 |
| stem p1/p2 standalone adopt at 811/726 flat cells (M3) | measured on evidence |
| apple p1 reads 28 of 28 entry rows | measured on evidence (transcription oracle) |
| `superseded` is inert to every verdict consumer | read-not-run (grep over `src`, `tests`, `scripts`) |
| the page-level gate is expressible as a holon-scoped `.rq` | proven by the gate's own rule; not yet run |
