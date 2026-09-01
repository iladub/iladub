# The author drew one label — closing `R155` with marked content, not geometry

**Subject:** `geometry._row_dividers` / `geometry.rule_aware_lines` (`src/iladub/etkl/geometry.py`),
and `geometry.extract_chars`, which must carry one more raw field.
**Residue:** `R155` (`docs/superpowers/residues-open.md`) — *"the residual division on WHO's header
line is a WORD GAP, and closing it needs BOTH readings at once."*
**Predecessor:** `docs/superpowers/2026-08-31-r154-closed-handoff.md`, whose § 5 graded this
**PROPOSED** and ordered the population be enumerated *before* anything was built. It was.
§3 is that run, and it **refuted the row's own remedy** — three times, in three different ways.

**Doc impact: none.** No released assertion changes. The wiki's table-reading pages describe the
ruled re-extraction at a level this does not contradict.

---

## 1. What this closes, and what it does not

**Closes.** `R155`'s measured defect: WHO page 0 band 2 line 0 carries two top-level header nodes,
`'Z-scores (weight in'` and `'kg)'`, where the author wrote one label. After this change the
boundary at `b=594.35` does not divide that row, and the label is whole.

**Does NOT close.** `R154`'s wider claim that *"a header line needs BOTH readings at once"*. This
does not reconcile the ruled reading with the word reading. It does something narrower and stronger:
it reads the **author's own marked-content structure** and declines a boundary the author drew
*through* one label. Where a document carries no marked content, nothing changes — by construction,
not by tuning (§3.5).

**Does NOT license.** This is a **fidelity** repair on 8 boundaries corpus-wide. It is not a score
repair. §3.3's counts are the oracle's negative half; no score movement is claimed as justification.

---

## 2. The subject — stated once

`R154` established that `rule_aware_lines` assigns each character to a ruled column by its centre,
and gave `_row_dividers` the row-local predicate *a boundary divides this row only where the ink on
both sides clears it*. That predicate distinguishes **cuts ink** from **falls in a gap**.

It provably cannot distinguish **word gap** from **column gutter** — and `R155` records that as its
reason for deferral, asserting *"there is no character-local fact that separates them."*

**That assertion is half right, and the half it gets wrong is the whole loop.** There is no
*geometric* character-local fact (§3.1–§3.3 measure three candidates and refute all three). There is
a **non-geometric** one: the marked-content id (`mcid`) the author's own producer wrote into the
page. WHO's `'Z-scores (weight in kg)'` is **one** marked-content item spanning the boundary; the
twelve column labels on the line below are **twelve**.

**The change, in one sentence:** a boundary that falls strictly inside a single marked-content run
of this row's ink does not divide this row — the author drew one label there.

This is CLAUDE.md principle 0 in its most literal form: *ET(K)L recovers the author's structure; it
does not tokenise the source.* The structure here was never latent. It was written down.

---

## 3. The measurements

Every figure below was produced at `20cc5b8` with the shipped `_row_dividers`, wrapped and never
replaced. Probe scripts are named per subsection; each is reproducible from the description.

### 3.1 The row's stated scope is REFUTED — the population is 4790, not one

`R155`'s remedy is *"a per-word reconciliation that consults `extract_words`' runs ONLY at boundaries
`_row_dividers` has already honoured — the population is now tiny (WHO's whole header line has
exactly one)."* The predecessor handoff flagged this as never enumerated and ordered it run first.

Enumerated across all seven tracked documents, page 0, counting every **interior boundary
`_row_dividers` keeps that genuinely divides** (ink on both sides):

```
doc                   DECLINED   KEPT+SPACE_STRADDLE     KEPT+SPACE_IN_GAP         KEPT+NO_SPACE
apple                        6                    98                   194                    70
cbh                         53                     7                   132                   921
gcap                         0                     0                     0                  1154
gstem                        2                     0                   638                   930
who                         82                    34                   567                    45
TOTAL                      143                   139                  1531                  3120

POPULATION (kept AND dividing) = 4790   declined = 143
```

*(bfs and ons contribute no rows: neither has a ruled band with ≥2 rule x's on page 0.)*

**The population is 4790.** "Exactly one" was a measurement of one line of one band read as a
measurement of the corpus. The row's scoping premise does not survive, and with it the claim that
the remedy is narrow.

### 3.2 The space glyph is REFUTED — on WHO's own next line

The natural character-local discriminator, and the only new *local* fact available: a space glyph.
If the renderer drew a space across the boundary, the two sides are one run.

WHO page 0 band 2, every kept dividing boundary, with the row's space glyphs:

```
--- row 0: 'Z-scores (weight in kg) '
    KEPT  b=  594.35  L-b=  -2.591 R-b=  +0.167  STRADDLE   left='res(weightin' right='kg)'

--- row 1: 'Year: Month Month L M S -3 SD-2 SD-1 SDMedian1 SD2 SD3 SD '
    KEPT  b=  125.51  L-b=  -1.025 R-b= +10.860  STRADDLE   left='Year:Month' right='MonthLMS-3SD'
    KEPT  b=  168.29  L-b=  -0.137 R-b= +24.240  STRADDLE   left='r:MonthMonth' right='LMS-3SD-2SD-'
    … 37 further boundaries, IN_GAP or NO_SPACE …
```

Row 1's `b=125.51` and `b=168.29` are **legitimate column gutters** — they separate `'Year: Month'`
from `'Month'` and `'Month'` from `'L'` — and a space glyph straddles both. A merge-on-straddle rule
welds them, breaking the byte-identical invariant `R155` declares hard, **in the same band, at the
same scale, one line below the target**. Corpus-wide the rule would fire on 139 boundaries.

### 3.3 The unbroken-chain predicate is REFUTED — twice, and the second refutation is the general one

Candidate: *a row whose glyph chain is unbroken — every x-consecutive non-space glyph pair either
abuts or has a space glyph between them — is one text run, so nothing divides it.* Both clauses are
presence tests, no magnitude, following `_cell_text`'s established constant-free pattern.

```
gstem  rows=   62  fired=    0  of-which-weld=   0  boundaries-dropped=    0
gcap   rows=   30  fired=    0  of-which-weld=   0  boundaries-dropped=    0
cbh    rows=   79  fired=    2  of-which-weld=   0  boundaries-dropped=    0
apple  rows=   41  fired=   30  of-which-weld=  23  boundaries-dropped=  253
         band2 row6 drops=11  'Total net sales (1)  109,417    94,036    364,357    313,695  '
bfs    rows=    0  fired=    0  of-which-weld=   0  boundaries-dropped=    0
ons    rows=   15  fired=   14  of-which-weld=   0  boundaries-dropped=    0
who    rows=   12  fired=    3  of-which-weld=   0  boundaries-dropped=    0
```

**First refutation:** it fires on 23 apple *data* rows and would drop 253 boundaries, dissolving
apple's table. Padding spaces make a legitimate data row an unbroken chain.

**Second refutation, and this is the one that generalises.** It does not fire on WHO row 0 — the one
row it was designed for. Why:

```
  GAP '-'->'s'  a.x1=513.528 b.x0=513.592 gap=0.064   spaces overlapping: []
  GAP 'e'->'s'  a.x1=537.970 b.x0=538.012 gap=0.042   spaces overlapping: []
  GAP 's'->'('  a.x1=542.283 b.x0=545.041 gap=2.758   spaces overlapping: [(542.281, 545.026)]
  GAP 'n'->'k'  a.x1=591.759 b.x0=594.517 gap=2.758   spaces overlapping: [(591.756, 594.501)]
```

Intra-word **kerning** gaps of 0.042–0.064pt and the inter-word gap of 2.758pt **differ only in
magnitude**. Any predicate separating them is a magnitude comparison — a tuned constant, forbidden
by CLAUDE.md §8, and prima facie evidence the decision does not belong in procedural geometry.

**`R155`'s own assertion is therefore upgraded from asserted to MEASURED**: at the level of character
geometry there is no constant-free fact separating a word gap from a column gutter. Three candidates,
three refutations. The row was right about the geometry and wrong to conclude the problem needs the
word reading.

### 3.4 Marked content separates them exactly — WHO band 2

WHO is a tagged PDF: 321 distinct `mcid` values on page 0, `tag` uniformly `'P'`.

```
--- row 0  (1 distinct mcid over 20 ink glyphs)
    mcid=7     x=[ 502.55, 609.76]  'Z-scores(weightinkg)'
    boundary b=  594.35  INSIDE mcid 7

--- row 1  (12 distinct mcid over 45 ink glyphs)
    mcid=8     x=[  63.11, 124.49]  'Year:Month'
    mcid=9     x=[ 136.37, 168.15]  'Month'
    …  mcid=10 'L' · 11 'M' · 12 'S' · 13 '-3SD' … 19 '3SD'
    all 39 boundaries: BETWEEN mcid runs
```

Row 2, the first data row, likewise: 12 mcids, every boundary between runs. The separation is
**exact and total** on the band that defines the defect.

### 3.5 The corpus census — the rule fires on 8 boundaries, and 4 of 7 documents cannot be touched

Across all seven documents, page 0, every kept dividing boundary classified by whether it falls
strictly inside one mcid run of its row's ink:

```
=== gstem:   0 mcids | INSIDE = 0 | BETWEEN =  726
=== gcap:    0 mcids | INSIDE = 0 | BETWEEN = 1154
=== cbh:   883 mcids | INSIDE = 7 | BETWEEN = 1053
      band9 row7 b=75.74 mcid=789 'DatesarebasedonDailyTransportcapacityandassumetotalcapacityisallocatedtogradet'
      band9 row8 b=75.74 mcid=790 'Theinformationprovidedisonlyanestimatebasedoninformationcurrentlytohandanddate'
      band9 row9 b=75.74 mcid=790 'Guidelines,PortQueuePolicyandmattersbeyondthecontrolofCBH.Relianceon,useordist'
=== apple:   0 mcids | INSIDE = 0 | BETWEEN =  362
=== bfs:    24 mcids | INSIDE = 0 | BETWEEN =    0
=== ons:     0 mcids | INSIDE = 0 | BETWEEN =    0
=== who:   321 mcids | INSIDE = 1 | BETWEEN =  318
      band2 row0 b=594.35 mcid=7   'Z-scores(weightinkg)'
```

**8 of 3613.** Every one is the same artefact `R154` named: a text run the renderer drew across the
grid. WHO's is the target label. cbh's three are **prose disclaimer notes** running under the grid —
the same strings `R156`'s row already records as garbled and partly repaired by `R154`
(`'ass ume total capacity is allocat ed'`, `'distribut ion of the informati on contained withi n'`).
Welding them is the remainder of that repair.

**And the inertness is structural, not tuned.** gstem, gcap, apple and ons carry **zero** marked
content on page 0. The rule has no evidence to fire on, so those four documents are byte-identical by
construction — not because a threshold happens to spare them. bfs has 24 mcids and no ruled band.
This is CLAUDE.md §8's open-world derivation form exactly: **a boundary is declined only where
positive evidence is present**, never inferred from absence.

---

## 4. Classification (CLAUDE.md §8) — and it is NOT ratified

**PROCEDURAL**, as a modification inside an existing justified PROCEDURAL step (raw extraction),
held to that step's own stated standard of *no tuned constant* — the identical argument `R154`'s spec
§4 made for `_row_dividers`, and it is stated here as *proposed*, not settled. That classification was
recorded as **not ratified by the maintainer**, and this one inherits the same status.

The argument for PROCEDURAL: the rule reads a raw PDF field and applies a containment test. It
derives nothing, infers nothing, and answers no reading judgement — the *author* answered it.

The argument that it is nonetheless the right side of the gate: there is **no constant**, no
tolerance, and no magnitude comparison anywhere in it. `COORD_EPS` is used only to make `<` mean `<`,
exactly as `_row_dividers` and `ruledroles._within` already use it.

**The argument a reviewer should press:** *"which columns does this label span"* is named in
CLAUDE.md §8 as the NEURAL class. This loop does not answer that question — it declines to ask it,
because the author already wrote the answer down. If the maintainer reads that as too fine a
distinction, the honest consequence is that both this and `R154` are misclassified together, and
that is a single ruling, not two.

---

## 5. The seams the implementer must measure

Named per plan-rule 3 — the fact to measure, not the answer.

1. **`geometry.Char` does not carry `mcid`** (`src/iladub/etkl/geometry.py:126-131`). It must, and
   `extract_chars` must populate it. **MEASURE every construction site of `Char` before adding the
   field** — tests build `Char` positionally (`tests/etkl/test_boundary_cuts_ink.py:20`,
   `test_padding_space_segmentation.py:12`, `test_border_grid.py:136`, `fixtures.py`). The field must
   default so no existing call site changes, and a `Char` with `mcid=None` must be inert.
2. **`_row_dividers` currently receives only `ink`.** The mcid runs must be built from that same
   list, in x-order, or the run spans will not correspond to the ink the predicate is judging. Do not
   pass a second list.
3. **`rule_aware_lines` filters spaces out before the call** (`geometry.py:341`). The runs must be
   built from **ink only**, as §3.4/§3.5 measured. A space glyph's mcid was never consulted; do not
   start now without re-measuring §3.5.
4. **There are TWO call sites** (`compile.py:133` and `compile.py:193`, the `col_xs` re-bucket).
   `R154`'s handoff records that their separate contributions were never separated. This loop does
   not separate them either — but MEASURE that the second call still receives chars carrying `mcid`.
5. **Re-derive §3.5 against the edited source**, not the wrapper. `R154`'s handoff records its own
   §3.3 battery as never re-run against the shipped function; do not repeat that.

---

## 6. The oracle — two-sided and NEGATIVE

The positive half is one assertion. The negative half is the whole rest of it.

| # | oracle | falsifies |
| --- | --- | --- |
| O1 | WHO page 0 band 2 line 0 is **one** word, `'Z-scores (weight in kg)'` | the loop did nothing |
| O2 | WHO page 0 band 2 line 1 is **byte-identical** to `20cc5b8` — twelve words, `'-3 SD'` intact | the `R155` hard invariant |
| O3 | cbh band 9 rows 7–9: the three prose notes are whole across `b=75.74` | the cbh half of §3.5 |
| O4 | gstem, gcap, apple, ons: **byte-identical** cells over every ruled band, page 0 | the inertness claim of §3.5 |
| O5 | corpus battery, both modes, `validate_shapes=False`, DOCUMENT scope: **no document regresses** | the general claim |
| O6 | a `Char` with `mcid=None` throughout produces byte-identical output to `20cc5b8` | the default-inert claim |

**O4 and O6 are the load-bearing ones.** O1 is satisfied by any number of wrong changes.

**Falsification (plan-rule 4) is mandatory per task.** For O1: invert the containment test and show
line 0 back at two words. For O6: the test must FAIL if the `mcid=None` guard is removed — and note
that with no mcids present the runs degenerate to one run per row, which would weld everything, so
this inversion is loud rather than subtle.

---

## 7. Score movement is expected, and is NOT the justification

`R154`'s closure row records that welding two chopped fragments removes an ink token and shrinks the
round-trip denominator, so scores rise for a reason that is not better reading. **The same applies
here and the same prohibition applies:** 8 boundaries weld, so a small rise on cbh and WHO is
expected and must be reported as a denominator effect, never cited as evidence.

**The oracle is O1–O6. Nothing else.**

---

## 8. What is NOT done (read this before writing any test — plan-rule 5)

- **Untagged documents are not helped at all.** apple, gstem, gcap and ons carry no marked content;
  any word-gap defect they have survives this loop untouched. This is a deliberate scope, not an
  oversight — §3.3 measures what happens when you try to help them geometrically.
- **Page 0 only.** Every figure in §3 is page 0. The rule is page-independent by construction but
  its census is not.
- **`mcid` is not validated against the PDF structure tree.** The rule reads the id as an opaque
  grouping token. It does **not** read `/StructTreeRoot`, does not know whether mcid 7 is a `<TH>`
  or a `<P>`, and must not be described as reading the tagged-PDF *semantics*. `tag` is uniformly
  `'P'` on both tagged documents in this corpus, so it carries no signal here.
- **No test may assert that a header spans N columns.** That is the NEURAL question §4 declines to
  ask. A test asserting it contradicts this section.
- **The `R156` type-triple question is untouched.** cbh band 9's `RECORD_TABLE` judgement is not
  revisited; this loop may repair three more of its cell strings and that is all.

---

## 9. Risk, stated once

**An author who tags a whole table ROW as one marked-content item would have every gutter in that
row declined, welding the row into one cell.** Measured: 0 occurrences in 3613 boundaries across two
tagged documents. Unmeasured for any document outside this corpus, and it is the failure this design
would suffer.

Its shape is benign in the direction that matters: the failure **merges**, and a merged row fails the
tiling/round-trip membrane, so it escalates rather than asserting something false (CLAUDE.md §7). It
does not fabricate.

---

## 10. Successors

- **`R157` (to raise): the untagged half.** §3.3 measured that no constant-free *geometric*
  predicate reaches a word gap. `R155` closes for tagged documents only; for untagged ones the
  question is genuinely the NEURAL one, and that is the row to write.
- **`R156` unchanged.** Neither half is addressed here.
