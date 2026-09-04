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

---

## 8. The band-index renumbering — MEASURED

The handoff's part 4 named this *"the one that could sink the design, and it has not been looked at
at all."* It was, 2026-09-04, in two halves: a static call-site inventory of what the index is used
for (§ 8.5), and runtime measurements of what would actually renumber (§ 8.1–8.4).

**Headline: the apple document score goes 0.1895 → 0.6289 under the merge, and on this corpus not
one band renumbers.** Neither of those is a licence to skip § 8.5 — the index turns out to be
load-bearing in three places nobody had listed.

### 8.1 Every merge the oracle ACCEPTS is a page tail — zero bands renumber

`page_bands`' index contract (`compile.py:279-296`) is *final position in append order*. Merging a
run `a..b` shifts every band after `b` down by `b − a`. So the whole question is: **is the run a
page tail?**

```
apple  p0 run 2.. 7 of 8 bands  [CONFIRMED merge     ]  page tail=True   bands after the run that would renumber=0
apple  p1 run 2.. 7 of 8 bands  [CONFIRMED merge     ]  page tail=True   bands after the run that would renumber=0
apple  p1 run 2.. 3 of 8 bands  [licence run         ]  page tail=False  bands after the run that would renumber=4
apple  p2 run 3.. 7 of 8 bands  [licence run         ]  page tail=True   bands after the run that would renumber=0
bfs    p6 run 3..10 of 12 bands  [licence run         ]  page tail=False  bands after the run that would renumber=1
ons    p7 run 2..14 of 16 bands  [licence run         ]  page tail=False  bands after the run that would renumber=1
ons    p8 run 1.. 7 of 9 bands  [licence run         ]  page tail=False  bands after the run that would renumber=1
cbh    p0 run 1.. 7 of 10 bands  [unruled-skip variant]  page tail=False  bands after the run that would renumber=2
```

Crossed with § 7's oracle results, the two lists are disjoint:

| run | page tail? | oracle | bands that renumber |
| --- | --- | --- | --- |
| apple p0 2..7 | **yes** | tiles, 124 entries | **0** |
| apple p1 2..7 | **yes** | tiles, 56 entries | **0** |
| apple p2 3..7 | yes | not a matrix candidate — refused | 0 |
| bfs p6 3..10 | no | not a matrix candidate — refused | 0 (never fires) |
| ons p7 2..14 | no | not a matrix candidate — refused | 0 (never fires) |

**On this corpus, under the § 7.3 design, no band renumbers at all.** Every merge the tiling oracle
accepts ends at the last band on its page; every non-tail run is refused before it can renumber
anything. Because the accepted runs are tails, indices are only ever *removed*, never *shifted onto
a different band*: bands 0 and 1 keep their positions and the merged band inherits the run's first
index — so on both pages it mints `#mtable2`, the IRI band 2 already mints today.

**This is a corpus fact, not a theorem.** Nothing forbids a non-tail run the oracle accepts, and the
design must be correct when one appears. § 8.5 is what would break then.

### 8.2 On the two pages where the merge fires, both index-keyed pass-2 inputs are EMPTY

```
pages with a non-empty section_repair_bands: 1 / 27
  cbh-stem-2026-08-03.pdf  p0: 10 bands, section_candidates=((1, 3, 5, 7),)

apple p0: bands minting a CarriedHeaderReading = NONE
apple p1: bands minting a CarriedHeaderReading = NONE
apple p2: bands minting a CarriedHeaderReading = NONE
```

`section_repair_bands` is non-empty on exactly **one** of the corpus's 27 pages, and it is not an
apple page. No apple band mints a `CarriedHeaderReading` at all (re-measured here; first measured
2026-09-03, `R165` row). So on apple p0 and p1 neither pass-2 input exists to be mis-targeted.

### 8.3 The one structural collision — and the oracle already absorbs it

cbh p0 is the single page where the two selections over `tab:ruleXsSignature` could collide:

```
  band 0: verdict=ignored    sig=None
  band 1: verdict=escalated  sig=37.92 38.16 75.74 154.22 216.26 259.22 302.18 …
  band 2: verdict=ignored    sig=None
  band 3: verdict=escalated  sig=37.92 38.16 75.74 154.22 216.26 259.22 302.18 …
  band 4: verdict=ignored    sig=None
  band 5: verdict=escalated  sig=37.92 38.16 75.74 154.22 216.26 259.22 302.18 …
  band 6: verdict=ignored    sig=None
  band 7: verdict=escalated  sig=37.92 38.16 75.74 154.22 216.26 259.22 302.18 …
  band 9: verdict=asserted   sig=37.92 38.16 75.74 76.1 154.22 216.26 259.22 30…
```

Two structurally different reads of the same fact:

* `sectiongraph.section_candidates` groups bands with equal signature **and** equal header-box text,
  **regardless of adjacency** — here `(1, 3, 5, 7)`.
* the merge licence takes **maximal contiguous runs** of equal signature — here **none**, because
  unruled (`sig=None`) bands 2, 4, 6 sit between them.

They do not collide today. **§ 7.2's needed relaxation makes them collide exactly:** apple p2
requires an unruled band to join a ruled run, and the same relaxation on cbh p0 selects bands 1..7 —
precisely the bands section repair claims. Measured:

```
cbh-stem-2026-08-03.pdf  p0 1..7: today=0 cells verdicts=['esc','ign','esc','ign','esc','ign','esc']
                           merged: cand=False classify=None entries=None tiles=None
```

`is_matrix_candidate` refuses it, so under § 7.3's design the merge never happens and section repair
keeps its bands. **The collision is real and the oracle absorbs it** — a second argument for § 7.3,
independent of bfs p6.

### 8.4 The full compile survives it, and the document score is 0.1895 → 0.6289

§ 2–3 ran `assert_matrix_region` on a scratch graph. This runs the **whole compile** with
`page_bands` returning the merged band (captions, unit markers, token accounting, the score):

```
--- apple p0   (merging bands 2..7)
  baseline: regions=8 score=0.3243 asserted=48 escalated=100 cells=48 triples=1749
  merged  : regions=3 score=1.0000 asserted=124 escalated=0 cells=124 triples=2618
    band 0: ignored   cells=  0 table=None      reason=fewer than 2 lines
    band 1: ignored   cells=  0 table=None      reason=fewer than 2 columns
    band 2: asserted  cells=124 table=mtable2   reason=None tok_a=124 tok_e=0

--- apple p1   (merging bands 2..7)
  baseline: regions=8 score=0.1667 asserted=14 escalated=70 cells=14 triples=1058
  merged  : regions=3 score=1.0000 asserted=56 escalated=0 cells=56 triples=1632
    band 2: asserted  cells= 56 table=mtable2   reason=None tok_a=56 tok_e=0
```

**Zero escalated tokens on both pages.** And at document scope:

```
baseline: score=0.1895  asserted=65 escalated=278  (32s)
    adopted=() repaired_bands=() recognized=()
    per-page regions=[8, 8, 8] page scores=[0.3243, 0.1667, 0.027]
merged  : score=0.6289  asserted=183 escalated=108  (25s)
    adopted=() repaired_bands=() recognized=()
    per-page regions=[3, 3, 8] page scores=[1.0, 1.0, 0.027]
```

Two things follow for **`R160`**, whose ruling the maintainer deferred until after this measurement:

* The apple document score is **0.6289**, against the 0.3587 pre-loop figure and the 0.1895 post-loop
  figure `R160`'s row records. The numbers that row is argued from are superseded.
* **`adopted=()` in BOTH runs.** The one-band reading does not restore datagrid adoption — it makes
  adoption unnecessary on p0 and p1 by asserting the ink outright. So `R160`'s conflict is not
  resolved in the fallback reader's favour; it is *dissolved*, because the page the fallback wanted
  no longer has escalated ink to claim. Whether that counts as closing `R160` or as changing its
  subject is the maintainer's call, and it is still open.

The document compile ran clean with two pages' band counts going 8 → 3 — but see § 8.2: that is
because section repair and carriage are both inactive on apple, not because the flows in § 8.5 are
safe.

### 8.5 What the index actually is — the static inventory

Measured by call-site inventory over `src/`, `scripts/`, `vocab/queries/` and `tests/`.

**(a) The index IS persisted into the shipped graph, and it reaches the grounded graph.** Every
table and every escalation candidate is minted from it — `#ttable{idx}` (`compile.py:672`),
`#rhtable{idx}` (`:739`), `#table{idx}` (`:781`), `#mtable{idx}` (`:829`), `#htable{idx}` (`:891`,
`:913`, `:951`), and `#region{idx}` at ten sites (`:624, 646, 684, 716, 767, 791, 858, 939, 967,
1006`). Every decision-log node inherits it (`decisionlog.py:103-104`, `:49`, `:59`), including the
`dec:regarding` edge (`:52`) that makes `why-escalated.rq` answerable, plus the index as a literal
in an `rdfs:label` (`decisionlog.py:108`). It then propagates *out of* the compile: `feed.py:141`
splits the fragment into a record discriminator, `feed.py:226`/`:284` into `SurfaceConcept.region`,
and `ground.py:100` mints `urn:iladub:region:<fragment>` as a **node IRI in the grounded graph**.
A renumbering changes node identity in shipped output — it is not an internal detail.

**(b) Three two-pass flows use pass-1 indices against pass-2 results**, all in
`document.compile_document`:

1. **Section repair** — `document.py:1487-1541`. Pass-1 indices from `band_lists[p]` feed
   `section_candidates` (`:1490`), are filtered against `pages[p].regions[i]` (`:1496-1497`), handed
   to a second `compile_tables` (`:1507-1511`), then read back **by the pass-1 index** at `:1515`
   and written into a pass-1 slot at `:1537`. Every step is a valid list operation, so a mismatch is
   silent. Note pass 2 does **not** pass `carried_header_roles` while pass 1 does (`:1444-1448`).
2. **Adoption (R73)** — `document.py:1640-1740`, the sharpest exposure. `grid_idx =
   len(pages[p].regions)` (`:1657`) is the *driver's* band count used to index the *re-compile's*
   report list (`:1658-1659`), and `superseded` (`:1671-1672`) holds pass-2 positions applied
   against pass-1 IRIs at `:1683` and `:1738`. **This is the one the merge touches directly**:
   `len(pages[p].regions)` goes 8 → 3 on p0 and p1 (§ 8.4). The only guard is
   `grid_idx < len(rep_a.regions)` (`:1659`), which catches a shorter list, not a renumbered one.
3. **Carriage replay** — `carried_by_page[p]` is stored keyed by pass-1 indices (`document.py:1435`,
   `:1443`) and replayed into the adoption re-compile (`:1648`), resolved by
   `compile.py:898` `.get(idx)`. `compile.py:587-592` already records (finding F3, residue R34) that
   nothing in the signature enforces the alignment.

**(c) One SPARQL query reads the index**: `vocab/queries/section-repeat.rq:19-20` projects the two
`tab:bandIndex` values `sectiongraph.py:236` unions. The decision queries never see the integer —
they join on `dec:regarding ?region` with `?region` bound by the caller from the index.

**(d) The regression surface.** 20 test files pin a band index; 11 are corpus-document regressions.
The largest by far is `tests/etkl/test_typing_equiv.py:31-79` — a **positional list of 27 per-band
verdict tuples** across stem/cbh/capacity/apple p0, compared list-to-list against `page_bands`
output at `:87`. Also `tests/etkl/test_apple_statement_headers.py:18-21,35,49,58,75`,
`tests/etkl/test_decision_queries.py:26-28`, `tests/etkl/test_decisionlog.py:238-255`,
`tests/etkl/test_supersession_queries.py:17-18,41-42`, and
`tests/etkl/test_datagrid.py:1110-1133` (`test_adoption_keeps_the_band_index_contract`).
A merge on apple p0 changes at least the apple rows of `test_typing_equiv` and every apple assertion
in the other four.

**(e) One more index join, outside the driver**: `adoption.py:86` and `:92` use *report* positions
(`escalated_bands`, from `enumerate(reports)` at `:73`) to index the *band* list
(`touched`, from `range(len(bands))` at `:78-80`). `compile.py:1052-1054` is where the
report/band correspondence stops being total — the datagrid fallback appends a report at index
`len(bands)` that is not a band.

### 8.6 What § 8 does NOT settle

- **The design is still not built.** § 8.4 patches `page_bands` from outside with a hard-coded run;
  it does not show a licence can select that run, nor that the fallback path can be implemented
  cleanly inside `compile_tables`.
- **Nothing was measured for a non-tail accepted merge**, because the corpus has none. That is the
  case § 8.5 says would be dangerous, and it is exactly the case with no evidence.
- The document compiles in § 8.4 ran with `validate_shapes=False`. The membrane was not exercised.
- The 20 pinned tests were **not** run against a merged compile; (d) says which would change, from
  reading them, not from a failing run.
- `R160` is **not** ruled. § 8.4 supplies the numbers; the ruling is the maintainer's.
- p2 is untouched throughout (`R167` + `R162`), so `R166`'s p2 half is still open.
