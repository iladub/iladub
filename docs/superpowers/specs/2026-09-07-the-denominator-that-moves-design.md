# The denominator that moves — a read band must book every word it holds

**Residue:** [[R176]], raised 2026-09-07 by the loop `r172-the-cell-level-diff`.
**Written:** 2026-09-07, first third of the session, before any code.

**Doc impact: none.** MEASURED, not assumed: no page in `mkdocs.yml`'s nav (16 pages, `:47-63`)
states the score at all — grepped for `denominator`, `score =`, and the `asserted/(asserted+…)`
form, zero hits. The one document that does state it is `docs/wiki/concepts/table-holon-compilation.md:29`,
which is **Wiki** class — synthesis, freely rewritten, never published — and this loop updates it
in-band.

**And what it says there is that this loop restores the original design goal rather than changing
it:** *"score = validated% + escalated%; silent-wrong is impossible."* Those two are supposed to
SUM. § 1.1 measures them summing to 89.4% on an asserted band. The invariant in § 3.1 is not a new
definition of the score; it is the definition the wiki has recorded all along, which the
per-branch accounting drifted away from.

---

## 1. What was asked, and what is already measured

R176's row states the defect and prescribes a fork:

> either **(a)** COUNT label ink in the denominator … or **(b)** EXCLUDE it from both sides, so an
> escalated band stops counting it too. … **The prediction to run first is that apple p0 and p1
> stop reading `1.0`.**

Both halves are settled below **by measurement, before any design**. The row's own evidence was
two pages; this is the corpus.

### 1.1 The asymmetry is corpus-wide, not an apple artefact

`scripts/unbooked_ink_census.py` (written this loop) books each band's ink against the
`RegionReport.tokens_*` the compiler actually recorded. `reports[i]` IS `bands[i]` — the compile
loop appends exactly one report per band and derives `tokens_*` by differencing the running
totals around each band's turn (`src/iladub/etkl/compile.py:767-771`) — so the pairing is an
identity, not an alignment guess.

```
$ PYTHONPATH=src python3 scripts/unbooked_ink_census.py
verdict       bands        ink     booked   unbooked  unbooked%
asserted         24       2482       2220        262  10.6%
escalated        21       2996       2998         -2  -0.1%
ignored         146       2935          0       2935  100.0%
```

**Read the three rows together — that is the finding.** An *escalated* band books 100% of its ink
(the −2 is unit-marker ink, which is carried into the graph but is not a `band.lines` word:
`compile.py:261-267`). An *ignored* band books 0% **by design** — its ink is prose, and counting it
would be the C1 defect in reverse (`compile.py:801`). An *asserted* band — the one case where the
reader claims to have READ the band — books **89.4%**, and silently drops the rest. **17 of 24
asserted bands** are affected.

So the score's denominator is not a property of the page. It is a property of the *verdict*, and it
shrinks by ~10% of a band's ink at the exact moment the band starts being read.

### 1.2 R176's own prediction is REFUTED

`scripts/unbooked_ink_fate.py` (written this loop) asks where the unbooked ink WENT, by testing
each band word for containment in an emitted `tab:EntryCell` or `tab:LabelCell` bbox:

```
$ PYTHONPATH=src python3 scripts/unbooked_ink_fate.py corpus/financial/apple-fy2026q3-statements.pdf 0 1
page 0: score=1.0 asserted=124 escalated=0 | EntryCells=124 LabelCells=48 (no bbox: 0/0)
  b2  UNSUPPORTED_TABLE  ink=172   booked=124   unbooked=48   || entry=124   label=48    orphan=0
page 1: score=1.0 asserted=56 escalated=0 | EntryCells=56 LabelCells=42 (no bbox: 0/0)
  b2  UNSUPPORTED_TABLE  ink=98    booked=56    unbooked=42   || entry=56    label=42    orphan=0
```

**Every one of apple p0's 48 and p1's 42 unbooked words is covered by an emitted `LabelCell`.
Orphan count zero.** The reading recovered that ink and carried it into the graph; only the
*accounting* lost it. So under the repair below apple p0 and p1 read `1.0` **and go on reading
`1.0`** — R176 § 5a's headline prediction is **refuted**, and refuted in the direction that
matters: `score=1.0` on those pages was CORRECT, it was merely not provable from its own operands.

The corpus-wide fate is the same shape with one exception. Across every band the census flagged:

| document | page/band | unbooked | label-covered | ORPHAN |
| --- | --- | --- | --- | --- |
| apple | p0 b2, p1 b2, p2 b6 | 48, 42, 3 | 48, 42, 3 | 0 |
| graincorp-capacity | p0 b3 | 16 | 16 | 0 |
| cbh-stem | p0 b9 | 3 | 3 | 0 |
| bfs-population | p5 b13; p6 b2/b4/b5/b6/b8/b9 | 9 ×7 | 9 ×7 | 0 |
| who-wfa | p0 b4, p1 b4 | 13, 13 | 13, 13 | 0 |
| **who-wfa** | **p0 b2, p1 b2, p2 b1** | **21, 20, 20** | **20, 19, 19** | **1 each** |

**259 of the 262 unbooked words were recovered; 3 were dropped.** The three are one word per page,
the axis caption `Year: Month` — real ink the reading did not carry, and the case that proves the
repair's escalated branch is not dead code.

### 1.3 Fork (b) is not implementable — the reason is structural

Excluding label ink "from both sides" requires knowing which of an ESCALATED band's words are
labels. That is the reading the escalation declined to make. It is not a hard case; at several
sites there is nothing to consult:

| escalation site | what exists there |
| --- | --- |
| `compile.py:783` `MULTI_TABLE_AMBIGUOUS` | escalates **before `classify(band)` runs at all** — no region, no grid, no cells |
| `compile.py:1212` `KIND_NOT_SUPPORTED` | the `else` of the hierarchical-candidate test — no `hreg` was ever built |
| `compile.py:1064` `MATRIX_AMBIGUOUS` | reached when `mreg is None` **or** the region did not tile; in the first case there are no `data_cols` to complement |

Corpus escalation reasons, measured (`unbooked_ink_census.py`): `REGION_TILING_FAILED` n=12
(ink 2598), `ROUND_TRIP_FAIL` n=5 (345), `KIND_NOT_SUPPORTED` n=3 (31), `MATRIX_AMBIGUOUS` n=1 (22).

**Ruling: the fork is taken for (a), and not as a preference.** (b) asks the compiler to partition
ink it has just refused to partition. Any implementation would have to *guess* the label axis of a
band whose axis assignment was the very thing found ambiguous — a geometry heuristic answering a
"which rows/columns are labels" reading question, which CLAUDE.md § 8 forbids outright.

---

## 2. Classification under § 8 — argued for THIS subject

The subject is one decision: **for a word of an asserted band that the data accounting did not
book, is it `asserted` or `escalated`?**

**The decision is AXIOM in form — a derivation, open world, evidence-positive.** A word is booked
`asserted` **only when a cell holding it is PRESENT** in what the branch emitted; nothing is ever
inferred from absence, and the default for unsupported ink is `escalated`, which is the
conservative side. It is monotonic: emitting more cells can only move ink from `escalated` to
`asserted`, never back. That is precisely CLAUDE.md § 8's derivation form.

**It is NOT lowered to SPARQL, and the reason is stated rather than assumed.** The evidence a
SPARQL `SELECT` would read — the band's individual words — is not in RDF and has no reason to be:
serialising every word of every band into the graph purely so a `COUNT` can be run over it would
add triples that no consumer reads, to evaluate a predicate with **zero degrees of freedom**
(set membership; no threshold, no tolerance, no ordering). The lowering would buy no semantic
gain and would cost a per-word triple explosion. **This is a deliberate exception and a reviewer
should challenge it on those terms** — not on whether the predicate is declarative, which it is.

**The arithmetic is PROCEDURAL and irreducible:** summing two integers over a partition is
decidable exact arithmetic (§ 8's second reserved case), and it is what the existing accumulators
already are.

**There is no tolerance anywhere in the repair.** The measurement scripts above use an
`EPS = 0.01` for bbox containment, derived from `holon.py`'s 2-dp `Decimal(str(round(v, 2)))`
rounding bound and not fitted to any document — but **the shipped code uses none**, because it
compares `Word` objects by identity against the cells the branch is holding, never geometry.
The scripts are instruments; the epsilon does not enter `src/`.

---

## 3. Design

### 3.1 The invariant

> **Every word of a band whose verdict is `asserted` is booked exactly once, in `tokens_asserted`
> if the reading recovered it into a cell and in `tokens_escalated` if it did not.**
>
> Equivalently: for every band with `verdict == "asserted"`,
> `tokens_asserted + tokens_escalated == sum(len(ln.words) for ln in band.lines)`.

The `escalated` and `ignored` verdicts are **unchanged**: an escalated band already satisfies the
first form with `tokens_asserted == 0` (§ 1.1), and an ignored band deliberately books nothing.

Once it holds, the denominator is a property of the *band's ink*, not of the verdict, and R176's
headline — "the score is not comparable between two readings of the same page" — is closed.

### 3.2 What changes, and only there

The repair is **strictly additive to the existing data accounting**. No branch's current
`asserted_total`/`escalated_total` arithmetic is edited; each affected branch gains one call that
books the ink it was dropping. This keeps every currently-correct number correct by construction
and confines the diff to the sites the census names.

Affected sites are exactly those whose asserted branch books a *subset* of the band. They are
**named by measurement, not by reading**: every asserted branch mints a distinct `table_uri`
prefix (`compile.py:830, 853, 895, 943, 1005/1027/1065`), so the census' `uri` column identifies
the site that booked each band with no inference at all.

| site | mint | books | corpus asserted bands | unbooked |
| --- | --- | --- | --- | --- |
| transposed | `:786` `#ttable` | `:821`, cells with `c.col >= 1` | 1 | **9** |
| row-hierarchical | `:853` `#rhtable` | `:872`, cells whose col is in `data_cols` | **0** | — |
| record | `:895` `#table` | `:923`, cells with `c.row > 0` | 11 | **102** |
| matrix | `:943` `#mtable` | `:963`, cells whose col is in `data_cols` | 5 | **151** |
| ruled / hierarchical | `:1005/:1027/:1065` `#htable` | `:1019/:1045/:1102`, **all** `tokens` | 7 | **0** |

`102 + 151 + 9 = 262`, which is § 1.1's total exactly — so the four subset-booking sites account
for all of it and nothing else does.

**The `#htable` branches are already total and MUST NOT be touched.** They book `tokens` — every
word of the band — splitting it `n_ruled` / `tokens - n_ruled`. Measured: who-wfa p0 b3/b5,
`ink == booked == 76`, unbooked 0 on all 7 corpus bands that reach them. Adding the helper there
would double-book.

**The row-hierarchical site (`:853`/`:872`) is reached by NO corpus band.** It books a subset by
the same `data_cols` shape as the matrix site, so it is in scope on the code, and it is the one
site whose repair no corpus page can verify — § 5's O1 is blind to it. It needs a synthetic
fixture or an explicit written ruling that it is left alone; **the plan must say which.**

### 3.3 The helper

One shared function, called by each affected branch after its existing accounting:

```
def _book_recovered_ink(band, booked, recovered) -> tuple[int, int]
```

- `booked` — the `Word`s the branch's existing arithmetic already counted.
- `recovered` — the `Word`s the branch carried into the graph as label/header structure.
- returns `(asserted_delta, escalated_delta)` for the band ink in neither operand yet.

`Word` is a frozen dataclass (`src/iladub/etkl/geometry.py:25-31`), so set membership is exact
value identity — text plus all four bounds. **This is why there is no epsilon:** two distinct
words cannot share a bbox, so identity is total and geometry never enters.

The implementer states the body. **The invariant it must preserve** is that
`asserted_delta + escalated_delta` equals the count of band words outside `booked`, exactly — the
helper partitions, it never re-derives what was already counted, and it must be impossible for it
to double-book.

**Seam to MEASURE before writing the call at each site** (do not assume it from this spec): for
each affected branch, *which object holds the label ink*. § 3.2's table names what each branch
books, which is the complement — but the complement of "books `c.row > 0`" is not automatically
"the `row == 0` cells cover the rest", and a matrix band's header block is not in `leaf_rows` at
all. Confirm per site by re-running `unbooked_ink_fate.py` on that site's own corpus page and
checking the helper's returned counts against the `label=` / `orphan=` columns. Where they
disagree, the helper is wrong, not the probe.

---

## 4. What is NOT done — deliberately

1. **The escalated and ignored verdicts are not re-accounted.** Both are already coherent (§ 1.1).
2. **The data-cell round-trip predicate is not changed.** A data cell that fails `cell_round_trips`
   goes on booking `escalated`; this loop adds ink, it does not re-judge any ink already judged.
3. **`assert_hier_region`'s bbox-less `LabelCell` is NOT fixed here.** Measured this loop: that
   emitter (`src/iladub/etkl/holon.py:529-531`) writes `cellText` with **no `tab:hasBBox`**, unlike
   all five sibling emitters (`:134`, `:184`, `:246`, `:278`, `:330`), so 24 LabelCells on who-wfa
   p0 carry no provenance-to-the-page. It is a real defect against core principle 6 and it is
   **raised as a residue** (§ 7), not repaired: it sits on a branch § 3.2 must not touch, and
   folding it in would make one diff answer two questions.
4. **The `Year: Month` orphan is not repaired.** This loop makes it *visible* by booking it
   `escalated`; making the reading carry it is a different question.
5. **No re-definition of the document-level score.** The document driver aggregates the same two
   operands; it inherits the repair and needs no change of its own.

---

## 5. The oracle — falsifying, two-sided

**O1 (the invariant, and the only one that can fail silently).** For every band of every corpus
page with `verdict == "asserted"`, `tokens_asserted + tokens_escalated == band ink`. Falsified by
reverting any one site's new call: the census' `unbooked%` for `asserted` returns above 0.

**RUN, and satisfied on the whole corpus:**

```
verdict       bands        ink     booked   unbooked  unbooked%
asserted         24       2482       2482          0  0.0%      (was 2220 / 262 / 10.6%)
escalated        21       2996       2998         -2  -0.1%     (unchanged)
ignored         146       2935          0       2935  100.0%    (unchanged, by design)

ASSERTED bands with unbooked ink : 0 of 24                      (was 17 of 24)
```

**O2 (the refutation, pinned).** apple p0 and p1 still score exactly `1.0`, and now with
`asserted == 172` and `98` rather than `124` and `56`. This is the two-sided form: a repair that
booked label ink as *escalated* instead would drop them to 0.72 and 0.57, and O2 catches it.

**O3 (the movement, predicted before it was run — and then RUN).** Predictions were computed from
§ 1's measurements and were falsifiable to the digit. The right column is the census re-run after
the repair, not a restatement:

| page | score before | PREDICTED | MEASURED after |
| --- | --- | --- | --- |
| apple p0 | 1.0 | 1.0 (asserted 124 → 172) | **1.0, asserted 172** ✓ |
| apple p1 | 1.0 | 1.0 (56 → 98) | **1.0, asserted 98** ✓ |
| apple p2 | 0.027027… | 6/114 = 0.052631… | **0.05263157894736842** ✓ |
| graincorp-capacity p0 | 1.0 | 1.0 (390 → 406) | **1.0, asserted 406** ✓ |
| cbh-stem p0 | 0.057110… | 54/896 = 0.060267… | **0.060267857142857144** ✓ |
| bfs p5 | 0.018817… | 16/381 = 0.041994… | **0.04199475065616798** ✓ |
| bfs p6 | 0.898785… | 276/301 = 0.916943… | **0.9169435215946844** ✓ |
| who p0 | 0.911564… | ~~288/315~~ | **0.9176829268292683 (301/328)** ✗ |
| who p1 | 0.908127… | ~~276/303~~ | **0.9145569620253164 (289/316)** ✗ |
| who p2 | 0.908450… | 148/162 = 0.913580… | **0.9135802469135802** ✓ |

**8 of 10 exact; the two misses are an arithmetic error in THIS spec, not a surprise from the
code, and the distinction matters.** who p0 and p1 each have **two** dirty bands — band 2 (matrix,
20/19 words) *and* band 4 (record, 13 words) — and the prediction summed only the first. `268 + 20
+ 13 = 301` and `257 + 19 + 13 = 289` are the corrected figures, and they are exactly what the
re-run reports. who p2 has only one dirty band, which is why its prediction survived. The lesson
is § 1.1's own table read one row too narrowly: the per-band census lists bands, and a page can
appear in it twice.

**O3 also pins what did NOT move.** The census reports the identical band population before and
after — `asserted 24 / escalated 21 / ignored 146` — so the repair changed the accounting and
touched no reading.

**O4 (the orphan is booked, not swallowed).** who-wfa p0 band 2 books its `Year: Month` word into
`tokens_escalated`. Falsified by making the helper return `(n, 0)` unconditionally: O4 fails while
O1 still passes, which is why O4 exists separately.

**O5 (no synthetic pin is collateral damage).** Every `assert report.score == 1.0` in
`tests/etkl/test_closing_slice.py` and its siblings must survive **unchanged**: a fixture that
asserts its whole band with no escalation stays at `1.0` because label ink lands on the asserted
side. Any that does NOT survive is a finding to report and rule on, **not a number to re-baseline**
— it means that fixture drops ink the accounting was hiding.

---

## 6. Interfaces

`_book_recovered_ink(band, booked: set[Word], recovered: set[Word]) -> tuple[int, int]` —
module-private in `src/iladub/etkl/compile.py`, beside `_marker_word_count`. Pure; no graph, no
I/O, no geometry.

`RegionReport`, `CompilationReport` and every public signature are **unchanged**. The score's
operands keep their names and their arithmetic; only what feeds them grows.

---

## 7. Residues to raise

- **`assert_hier_region` emits `LabelCell` without `tab:hasBBox`** (§ 4.3) — 24 instances on
  who-wfa p0 alone; the five sibling emitters all write one. Breaks provenance-to-the-page for
  every hierarchical table's header labels.
- **who-wfa's `Year: Month` axis caption is dropped by the reading** (§ 4.4) — after this loop it
  is booked `escalated`, so it is visible in the score; carrying it is unbuilt.

---

## 8. Unverified or assumed

- **The `Doc impact` check was a grep over the 16 nav pages, not a read of them.** Patterns:
  `denominator`, `score *=`, `asserted *[/(]`, `escalated)`. A page that describes the score in
  prose without any of those tokens would not have been caught.
- **The `#htable` exclusion is guarded in CI at ONE of its three sites, not three.** Found by
  falsification, not by reading: injecting the forbidden double-booking at `compile.py:1110` left
  `test_a_wholesale_branch_is_left_alone` GREEN. All five `#htable`-producing fixtures book at
  `:1193`; `:1110` and `:1136` are reached by corpus documents only. Re-aimed at `:1193` the
  injection fails the test loudly, so the test pins its own branch and only its own. Recorded in
  that test's docstring.
- **The corpus is 7 documents, 45 non-ignored bands.** Every number in § 1 is that corpus. The
  row-hierarchical site (`compile.py:906`/`:872`) is reached by **no** corpus band, so its
  diagnosis is read off the code and its repair cannot be falsified by O1 — see § 3.2's last
  paragraph, which makes that a decision the plan must take rather than a gap it may inherit.
  (An earlier draft of this spec named the *transposed* site as the unexercised one. That was
  wrong: bfs-population p5 b13 reaches it, mints `#ttable13`, and is dirty by 9 words. The census'
  `uri` column is what corrected it — the point of measuring rather than reading.)
- **The score-movement table (O3) is arithmetic on § 1's measurements, not a run.** It is the
  prediction; a plan that pastes it instead of running it has verified nothing.
- **`Word` equality is assumed total** — that no two distinct words in one band share text and all
  four bounds. Physically it cannot happen; it is not asserted by any test.
