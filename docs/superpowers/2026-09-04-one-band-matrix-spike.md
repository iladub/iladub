# The R165 one-band matrix spike — RUN, and CONFIRMED on two of three apple pages

**Date:** 2026-09-04 · **Branch:** `r165-one-band-matrix-spike` · **Baseline:** `main` at `c9e6941`

**Doc impact: none.**

The predecessor handoff
(`docs/superpowers/2026-09-03-r165-forced-carriage-spike-handoff.md` § 5) graded one prediction
**PROPOSED** and ordered it RUN before anything was designed on it:

> apple p0 compiles as **one matrix table** — under band 2's `Three Months Ended / Nine Months
> Ended` column header, with every section heading (`Operating expenses:`, `Earnings per share:` …)
> read as a row header the way `mtable2` already reads `Net sales:` as `rh0` — if bands 2–7 are
> handed to `compile_tables` as **one band** instead of six.

It was run on all three pages with `scripts/one_band_matrix_spike.py`. **Confirmed on p0 and p1;
refused on p2**, for two reasons neither of which is the one-band reading itself. Everything below
is that script's output, pasted.

---

## 1. The instrument

`scripts/one_band_matrix_spike.py` merges a contiguous run of `page_bands`' bands into one `Band`
(lines concatenated in document order; `top`/`bottom` the run's extent; `rules`/`hrules`/
`captions`/`unit_markers` concatenated; `column_xs` taken from the run's first band that carries
any — **never unioned**, because `column_xs` is a boundary vector and mixing two would invent
boundaries no band derived) and then calls `is_matrix_candidate` → `classify_matrix` →
`assert_matrix_region` → `region_tiles` on it, exactly the chain `compile.py:819-835` runs.

```
PYTHONPATH=. .venv/bin/python scripts/one_band_matrix_spike.py \
    corpus/financial/apple-fy2026q3-statements.pdf <page> <first band> <last band>
```

The merge is supplied on the command line, never inferred: the script decides nothing about any
document and carries no tuned constant (CLAUDE.md §8 — PROCEDURAL, an instrument).

## 2. Page 0 — CONFIRMED

Baseline census (what `compile_tables` reads today):

```
=== corpus/financial/apple-fy2026q3-statements.pdf page 0: baseline census (8 bands)
  band 0: ignored    cells=  0 table=None       lines= 1 rules= 0
           first_line='Apple Inc.'
  band 1: ignored    cells=  0 table=None       lines= 2 rules= 0
           first_line='CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)'
  band 2: asserted   cells= 28 table=mtable2    lines=12 rules=136
           first_line='Three Months Ended Nine Months Ended'
  band 3: escalated  cells=  0 table=None       lines= 4 rules=62
           first_line='Operating expenses:'
  band 4: asserted   cells= 20 table=table4     lines= 5 rules=75
           first_line='Operating income 35,695 28,202 122,432 100,623'
  band 5: escalated  cells=  0 table=None       lines= 6 rules=102
           first_line='Earnings per share:'
  band 6: escalated  cells=  0 table=None       lines= 7 rules=121
           first_line='(1) Net sales by reportable segment:'
  band 7: escalated  cells=  0 table=None       lines= 7 rules=121
           first_line='(1) Net sales by category:'
```

Merged 2..7:

```
=== merging bands 2..7 into one
    merged band: lines=41 rules=617 hrules=463
=== is_matrix_candidate(merged) -> True
=== classify_matrix(merged) -> MatrixRegion
    grid boundaries = [50.0, 300.0, 364.4, 430.4, 496.4, 562.4]
    data_cols = (1, 2, 3, 4)
    leaf_rows = 38
=== assert_matrix_region -> 124 entries, 2427 triples
=== region_tiles -> True
=== column tree (classify_matrix):
    [0] level=0 covers=(1, 2) parent=None text='Three Months Ended'
    [1] level=0 covers=(3, 4) parent=None text='Nine Months Ended'
    [2] level=1 covers=(1,) parent=0 text='June 27,'
    [3] level=1 covers=(2,) parent=0 text='June 28,'
    [4] level=1 covers=(3,) parent=1 text='June 27,'
    [5] level=1 covers=(4,) parent=1 text='June 28,'
    [6] level=2 covers=(1,) parent=2 text='2026'
    [7] level=2 covers=(2,) parent=3 text='2025'
    [8] level=2 covers=(3,) parent=4 text='2026'
    [9] level=2 covers=(4,) parent=5 text='2025'
    body_line=3 stub_cols=(0,)
```

The 38 leaf rows are the whole statement, section headings included, each as a row header —
exactly as predicted:

```
      row: Net sales:
      row: Products | $ 78,678 | $ 66,613 | $ 272,629 | $ 233,287
      …
      row: Operating expenses:
      row: Research and development | 11,729 | 8,866 | 34,035 | 25,684
      row: Selling, general and administrative | 7,346 | 6,650 | 22,315 | 20,553
      row: Total operating expenses | 19,075 | 15,516 | 56,350 | 46,237
      row: Operating income | 35,695 | 28,202 | 122,432 | 100,623
      …
      row: Earnings per share:
      row: Basic | $ 2.03 | $ 1.57 | $ 6.91 | $ 5.64
      …
      row: (1) Net sales by reportable segment:
      row: Americas | $ 45,781 | $ 41,198 | $ 149,403 | $ 134,161
      …
      row: (1) Net sales by category:
      row: iPhone | $ 54,252 | $ 44,582 | $ 196,515 | $ 160,561
      row: Total net sales | $ 109,417 | $ 94,036 | $ 364,357 | $ 313,695
```

**`Operating income 35,695 28,202 122,432 100,623` is a leaf ROW of the merged table** — so the
one-band reading also disposes of `R166`'s p0 half: that line stops being a `tab:RecordTable`
header and becomes a row under `Three Months Ended` / `Nine Months Ended`.

**124 asserted entries where 48 entry-cells (28 + 20) are asserted today, and every escalated band
on the page disappears.**

## 3. Page 1 — CONFIRMED

```
=== merging bands 2..7 into one
    merged band: lines=40 rules=334 hrules=226
=== is_matrix_candidate(merged) -> True
=== classify_matrix(merged) -> MatrixRegion
    grid boundaries = [52.6, 418.6, 492.6, 562.3]
    data_cols = (1, 2)
    leaf_rows = 38
=== assert_matrix_region -> 56 entries, 1441 triples
=== region_tiles -> True
=== column tree (classify_matrix):
    [0] level=0 covers=(1,) parent=None text='June 27,'
    [1] level=0 covers=(2,) parent=None text='September 27,'
    [2] level=1 covers=(1,) parent=0 text='2026'
    [3] level=1 covers=(2,) parent=1 text='2025'
    body_line=2 stub_cols=(0,)
```

The whole balance sheet, `ASSETS:` through `Total liabilities and shareholders' equity`, in 38 leaf
rows — including band 6, the one-line `ignored` band `Commitments and contingencies`, which the
merge carries as a leaf row rather than dropping.

**56 entries where 14 are asserted today.** This is the page whose datagrid adoption `R160` records
as lost (score 0.3587 → 0.1895): the one-band reading is what makes the band reader's authority
claim on p1 worth honouring, so `R160`'s ruling has to be made against these numbers, not against
the 14.

## 4. Page 2 — REFUSED, for two reasons, neither of them the merge

```
=== merging bands 2..7 into one
    merged band: lines=38 rules=318 hrules=204
=== is_matrix_candidate(merged) -> True
=== classify_matrix(merged) -> None
```

### 4.1 A single em-dash cell moves the stub|data split — NEW, and merge-induced

`stub_data_split` and `matrix_body_start`, band 2 alone vs merged, all three pages:

```
p0 merged 2..7 : ncols=5 split=2 k=1 body_start=3
p0 band 2 alone: ncols=5 split=2 k=1 body_start=3
p1 merged 2..7 : ncols=3 split=1 k=1 body_start=2
p1 band 2 alone: ncols=3 split=1 k=1 body_start=2
p2 merged 2..7 : ncols=3 split=2 k=2 body_start=2      <-- k and body_start both wrong
p2 band 2 alone: ncols=3 split=2 k=1 body_start=3
```

The merge changed p2's `k` from 1 to 2. Per-column body-cell datatype census (rows >= split):

```
p2 col 0: 35 body cells, types=Textx35
p2 col 1: 30 body cells, types=ParenthesizedNumberx15, Numericx12, Currencyx2, Textx1
      Text: [(29, '—')]
p2 col 2: 30 body cells, types=Numericx14, ParenthesizedNumberx14, Currencyx2
```

**One cell.** Row 29 of column 1 holds `—` (U+2014), which `celltype._cell_datatype` types as
`tab:Text` because `is_blank` recognises only `''`, `(blank)` and the ASCII `-`
(`src/iladub/etkl/celltype.py:67-72`). A single `Text` body cell disqualifies column 1 as a data
column in `vocab/queries/stub-data-split.rq` (`SUM(IF(?ct = tab:Text, 1, 0)) = 0`), so `k` becomes
2; `matrix_body_start` then finds a "stub" cell (`2026`) on line 2 and returns 2 instead of 3.

Confirmed by construction — with `is_blank` extended to `—`/`–` and nothing else changed:

```
p2 merged with em-dash=Blank: split=2 k=1 body_start=3
```

`k` and `body_start` are then correct. **This is a new residue** (`R167` below). It is not the same
as `R78`, which is about genuinely ambiguous suppression markers (`..`, `n/a`) whose value is
unknown: the em-dash is US-GAAP's nil glyph, the typographically-correct spelling of the ASCII `-`
`is_blank` already accepts, and the reading is decidable from format alone.

### 4.2 The column tree still refuses — and that is `R162`, already ruled

With `k=1` and `body_start=3` restored, `classify_matrix` still returns `None`, at the next stage:

```
col_tree -> None
logical_rows -> 35
row_tree -> 35
```

p2's header band carries **0 rules** (see the p2 census: `band 2: escalated cells=0 lines=4
rules=0`), so `_build_ruled_band` never re-extracts its cells and pdfplumber's word split stands.
Its line 0 is three separate words over two data columns:

```
line 0: Nine@c1[454-471] | Months@c1[473-503] | Ended@c2[505-529]
boundaries [50.0, 417.2, 488.7, 562.4]
```

Data-column centres are 452.95 (c1) and 525.55 (c2). `Nine` wins c1, `Ended` wins c2, and `Months`
(centre 488.0, which `column_of` places in data column 1) wins nothing — so
`infer_column_tree_by_proximity`'s uncarried-ink guard refuses, correctly, rather than dropping its
ink.

**This is `R162` verbatim, at the site `R162` names** (`residues-open.md`: *"a multi-word spanner
like `Nine Months Ended` arrives as three separate `Line.words` entries on an unruled band"*,
measured on apple p2 band 2). `R162` is ruled **NEURAL** and out of scope; the spike confirms it at
a second entry point and adds nothing to it. p0 and p1 are unaffected because their header bands
are ruled, so `Three Months Ended` is one cell.

## 5. What this settles

| claim | verdict | evidence |
| --- | --- | --- |
| apple p0 compiles as one matrix under band 2's column header when bands 2–7 are one band | **CONFIRMED** | § 2 — 124 entries, `region_tiles -> True` |
| section headings read as row headers, the way `mtable2` reads `Net sales:` | **CONFIRMED** | § 2 — `Operating expenses:`, `Earnings per share:`, `(1) Net sales by …` are leaf rows |
| the same holds for p1 (balance sheet) | **CONFIRMED**, unpredicted | § 3 — 56 entries, tiles |
| `R166`'s p0 half is disposed of by the one-band reading | **CONFIRMED** | § 2 — `Operating income …` is a leaf row, not a header |
| the same holds for p2 (cash flows) | **REFUSED** | § 4 — two blockers, `R167` (new) and `R162` (ruled NEURAL) |
| the fix is in `page_bands`' band split, with no carriage seam involved | **supported, not proven** | the spike merges bands *after* `page_bands` returns; it does not show that `page_bands` can be made to produce the merged band from the author's evidence |

## 6. What this does NOT settle

- **How `page_bands` decides not to split.** The spike merges a run named on the command line. The
  licence `R165` proposes (*one `tab:ruleXsSignature` = one band*) was not derived, not queried, and
  not tested against any non-apple document. Nothing here shows it selects bands 2–7 and only 2–7.
- **Band indices move.** `page_bands`' index contract is load-bearing for `section_repair_bands`,
  the per-band decision log and every `#mtableN` / `#tableN` URI (`compile.py:270-297` states it at
  length). Merging six bands into one renumbers everything after it on the page. Not examined.
- **The corpus.** Only apple was run. `ons`, `who` and the other five documents were not, and a
  band-split change is global.
- **`R160`.** The p1 numbers above are the input to that ruling, not the ruling.
- **Document score.** Not measured, on any page. The entry counts above are `assert_matrix_region`'s
  return value on a scratch graph, not a compile.

---

## 7. The corpus census — **the licence R165 named is REFUTED**

`R165`'s remedy names one licence: *"do not split at section headings inside one
`tab:ruleXsSignature`"* — i.e. a maximal contiguous run of bands sharing one rule-x signature is
one band. That licence had never been run against the corpus. It was, 2026-09-04, on all 7
documents and all 27 pages (`sectiongraph._rule_xs_signature` over `page_bands`' own bands; the
census script is scratch, its output is below).

**Runs the licence would produce, and what merging each actually yields:**

| document | page | run | cells today | merged band |
| --- | --- | --- | --- | --- |
| apple | 0 | **2..7** | 48 (`ass,esc,ass,esc,esc,esc`) | **124 entries, tiles** ✓ |
| apple | 1 | **2..3** | 14 (`ass,esc`) | 26 entries, tiles — but the § 3 reading of 2..7 gave **56** |
| apple | 2 | **3..7** | 3 (`esc,esc,esc,ass,esc`) | `is_matrix_candidate` → **False** |
| bfs | 3 | 3..5 | 0 (all `ign`) | not run |
| bfs | 5 | 3..5 | 0 (all `ign`) | not run |
| bfs | 6 | **3..10** | **216** (`ign,ass,ass,ass,ign,ass,ass,esc`) | `is_matrix_candidate` → **False** |
| ons | 0 | 0..1 | 0 (all `ign`) | not run |
| ons | 1 | 8..11 | 0 (all `ign`) | not run |
| ons | 5 | 9..12 | 0 (all `ign`) | not run |
| ons | 7 | 2..14 | 0 (all `ign`) | `is_matrix_candidate` → **False** |
| ons | 8 | 1..7 | 0 (all `ign`) | not run |
| who | 0,1,2 | — | — | **no runs at all** (4/4/3 ruled bands, 4/4/3 distinct signatures) |
| cbh, graincorp ×2 | all 5 pages | — | — | **no runs at all** |

Three things follow, and each one is a design constraint the spec has to answer:

### 7.1 The licence UNDERSHOOTS on apple p1 — the confirmed 56-entry reading is out of its reach

p1 has **3 distinct signatures across its 6 ruled bands**, so the licence stops the run at band 3:

```
  band 2: sig=49.96 52.6 417.16 419.8 488.68 489.64 493.24 562.36 563.08          'June 27, September 27,'
  band 3: sig=49.96 52.6 417.16 419.8 488.68 489.64 493.24 562.36 563.08          'Non-current assets:'
  band 4: sig=49.96 52.6 417.16 419.8 488.68 489.64 493.24 560.44 562.36 563.08   'LIABILITIES AND SHAREHOLDERS’ EQUITY:'
  band 5: sig=49.96 52.6 417.16 419.8 488.68 489.64 493.24 562.36 563.08          'Non-current liabilities:'
  band 6: sig=49.96 52.6 417.16 419.8 489.64 493.24 563.08                        'Commitments and contingencies'
  band 7: sig=49.96 52.6 417.16 419.8 488.68 489.64 493.24 562.36 563.08          'Shareholders’ equity:'
```

Band 4 carries **one extra** x (`560.44`); band 6 — the one-line `Commitments and contingencies`
band, which has no value cells — is **missing two** (`488.68`, `562.36`). Every other band on the
page is identical. Set *equality* of the distinct x positions is the wrong relation: band 6's set
is a strict **subset** of band 5's, band 4's a strict **superset** of band 3's. Loosening equality
to subsumption would join p1's 2..7 — and that loosening is precisely the kind of thing that needs
a stated oracle rather than a tolerance (CLAUDE.md §8).

### 7.2 The licence MISSES THE HEADER on apple p2

p2's header band 2 (`Nine Months Ended`) carries **no rules at all**, so its signature is `None`
and it can never join a run. The licence's run starts at band 3 — the merged band has no column
header, and `is_matrix_candidate` refuses it. Even with `R167` and `R162` fixed, p2 needs a rule
that can attach an UNRULED header band to a ruled run beneath it.

### 7.3 An unconditional split change would DESTROY 216 asserted cells on bfs p6

bfs p6's run 3..10 spans six `asserted` bands totalling 216 cells, and the merged band is **not a
matrix candidate**. The same shape appears at ons p7 (13 bands, run 2..14, not a candidate).

**So the merge cannot be an unconditional change to `page_bands`.** It has to be a *proposal
disposed by the existing oracle*: attempt the merged reading, keep it only when
`classify_matrix` + `region_tiles` both accept, and otherwise fall back to the bands as they are
today. That is the assert/propose/promote shape (CLAUDE.md §3) applied to a band split, and it is
what makes the change safe on bfs and ons without any per-document knowledge.

### 7.4 What the census does NOT show

- The five untested `ign`-only runs (bfs p3/p5, ons p0/p1/p5/p8) were not merged and not read.
  They assert nothing today, so the downside is bounded, but "bounded" is not "measured".
- The fallback design in § 7.3 is **not implemented and not run**. Nothing here shows the compile
  can be restructured to try a merged reading and fall back cleanly, nor what it costs in the
  band-index contract (`compile.py:270-297`) that `section_repair_bands`, the per-band decision
  log and every `#mtableN` / `#tableN` URI depend on.
- No document score was measured, on any page, under any of this.
