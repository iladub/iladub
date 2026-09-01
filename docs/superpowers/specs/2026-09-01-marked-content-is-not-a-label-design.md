# Marked content is not a label — `R155` is REFUTED into the NEURAL class

**Subject:** `geometry._row_dividers` / `geometry.rule_aware_lines` (`src/iladub/etkl/geometry.py`).
**Residue:** `R155` (`docs/superpowers/residues-open.md`) — *"the residual division on WHO's header
line is a WORD GAP, and closing it needs BOTH readings at once."* **Still OPEN.**
**Predecessor:** `docs/superpowers/2026-08-31-r154-closed-handoff.md`, whose § 5 graded this
**PROPOSED** and ordered the population be enumerated *before* anything was built.

**This document is a REFUTATION, not a design.** It was written as a design, the design was built,
and the build was **reverted** — `src/` and `tests/` are byte-identical to `20cc5b8`. Four candidate
discriminators were measured and all four are refuted. The contribution is the refutations, the
reclassification of `R155` to NEURAL, and one methodological finding (§6) that nearly shipped a
regression.

**Doc impact: none.** No code changed and no released assertion changes.

---

## 1. What was asked, and what came back

`R155` defers on an assertion: *"there is no character-local fact that separates a word gap from a
column gutter."* The predecessor handoff ordered the row's own remedy be enumerated first, and
predicted the enumeration might refute it. It did — and so did everything tried after.

| # | candidate | verdict | refuted by |
| --- | --- | --- | --- |
| C0 | the row's own scope: *"the population is tiny — exactly one"* | **REFUTED** | 4790 (§2) |
| C1 | a straddling **space glyph** | **REFUTED** | WHO's own line 1 (§3) |
| C2 | an **unbroken glyph chain** | **REFUTED** | 23 apple data rows; and kerning (§4) |
| C3 | the author's **marked-content id** (`mcid`) | **REFUTED** | bfs page 6 (§5) |
| C3′ | `mcid` **and** a straddling space | **REFUTED** | bfs `'Rapport de'` (§5.3) |

---

## 2. C0 — the row's stated scope is refuted: the population is 4790, not one

`R155` prescribes *"a per-word reconciliation that consults `extract_words`' runs ONLY at boundaries
`_row_dividers` has already honoured — the population is now tiny (WHO's whole header line has
exactly one)."*

Enumerated across all seven tracked documents, page 0, counting every **interior boundary
`_row_dividers` keeps that genuinely divides** (ink on both sides), with the shipped function wrapped
and never replaced:

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

**"Exactly one" was a measurement of one line of one band, read as a measurement of the corpus.**

---

## 3. C1 — the space glyph is refuted on WHO's own next line

WHO page 0 band 2, every kept dividing boundary:

```
--- row 0: 'Z-scores (weight in kg) '
    KEPT  b=  594.35  L-b=  -2.591 R-b=  +0.167  STRADDLE   left='res(weightin' right='kg)'

--- row 1: 'Year: Month Month L M S -3 SD-2 SD-1 SDMedian1 SD2 SD3 SD '
    KEPT  b=  125.51  L-b=  -1.025 R-b= +10.860  STRADDLE   left='Year:Month' right='MonthLMS-3SD'
    KEPT  b=  168.29  L-b=  -0.137 R-b= +24.240  STRADDLE   left='r:MonthMonth' right='LMS-3SD-2SD-'
    … 37 further boundaries, IN_GAP or NO_SPACE …
```

`b=125.51` and `b=168.29` are **legitimate column gutters** — `'Year: Month'` | `'Month'` | `'L'` —
and a space glyph straddles both. A merge-on-straddle rule welds them, breaking `R155`'s own hard
invariant, **in the same band, one line below the target.** Corpus-wide it would fire on 139.

---

## 4. C2 — the unbroken chain is refuted twice, and the second refutation is general

Candidate: *a row whose glyph chain is unbroken — every x-consecutive non-space glyph pair either
abuts or has a space glyph between them — is one text run.* Both clauses are presence tests, no
magnitude, following `_cell_text`'s established constant-free pattern.

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

**First:** it fires on 23 apple **data** rows and would drop 253 boundaries, dissolving apple's
table. Padding spaces make a legitimate data row an unbroken chain.

**Second, and this generalises.** It does not fire on WHO row 0 — the row it was designed for:

```
  GAP '-'->'s'  a.x1=513.528 b.x0=513.592 gap=0.064   spaces overlapping: []
  GAP 'e'->'s'  a.x1=537.970 b.x0=538.012 gap=0.042   spaces overlapping: []
  GAP 's'->'('  a.x1=542.283 b.x0=545.041 gap=2.758   spaces overlapping: [(542.281, 545.026)]
  GAP 'n'->'k'  a.x1=591.759 b.x0=594.517 gap=2.758   spaces overlapping: [(591.756, 594.501)]
```

Intra-word **kerning** gaps of 0.042–0.064pt and the inter-word gap of 2.758pt **differ only in
magnitude**. Any predicate separating them is a magnitude comparison — a tuned constant, which
`CLAUDE.md` §8 calls *prima facie evidence the decision belongs in NEURAL/AXIOM*.

**This upgrades `R155`'s own assertion from asserted to MEASURED, for the geometric half.**

---

## 5. C3 — marked content: exact on two documents, refuted by the third

### 5.1 Why it looked right

WHO is a tagged PDF (321 `mcid`s on page 0). On the band that defines the defect the separation is
exact and total:

```
--- row 0  (1 distinct mcid over 20 ink glyphs)
    mcid=7     x=[502.55, 609.76]  'Z-scores(weightinkg)'      boundary b=594.35  INSIDE mcid 7
--- row 1  (12 distinct mcid over 45 ink glyphs)
    mcid=8 'Year:Month' · 9 'Month' · 10 'L' · 11 'M' · 12 'S' · 13 '-3SD' … 19 '3SD'
    all 39 boundaries: BETWEEN mcid runs
```

Census over all seven documents, **page 0**: the rule declines **8 of 3613** kept dividing boundaries
— WHO's target label and three cbh prose notes drawn across the grid. Four documents (apple, gstem,
gcap, ons) emit **zero** marked content, so they looked inert *by construction*.

It was built, and on page 0 it did exactly what was predicted: WHO line 0 became
`['Z-scores (weight in kg)']`, WHO line 1 stayed byte-identical, cbh's three prose notes became
whole, and five of seven page-0 cell streams were byte-identical by sha256.

### 5.2 What refuted it

The DOCUMENT-scope battery, which reads **every** page:

```
doc     baseline (20cc5b8)      with C3
bfs     0.3464447806354009      0.9400826446280992      +0.594
```

A +0.594 "improvement" with `'fewer than 2 columns'` refusals rising **24 → 34**. Per-page:

```
page5   mcids=12  cells=446 → 404
page6   mcids=9   cells=324 →  53
```

**bfs page 6, band 2, line 0:**

```
baseline: ['Grandes régions','Total','0-19 ans','20-39 ans','40-64 ans','65-79 ans',
           '80 ans ou plus','Rapport de','Rapport de']
with C3:  ['Grandes régionsTotal0-19 ans20-39 ans40-64 ans65-79 ans80 ans ou plusRapport de Rapport de']
```

Because bfs's producer tags **the entire header block — both rows, 109 glyphs, nine labels — as one
marked-content item**:

```
--- row0: 1 runs over 79 ink glyphs
    mcid=9  x=[ 72.62, 522.17] 'GrandesrégionsTotal0-19ans20-39ans40-64ans65-79ans80ansouplu'
--- row1: 1 runs over 30 ink glyphs
    mcid=9  x=[ 72.62, 521.80] 'Cantonsdépendancedépendancedes'
```

**`mcid` granularity is producer-dependent and carries no guarantee.** WHO and cbh emit one item per
label; bfs emits one per block. The PDF format does not constrain it, so *"the author drew one
label"* is simply false as a general claim — the author drew one *marked-content sequence*, of
arbitrary extent. The score rose because the tables collapsed so far they stopped qualifying as
regions and left the denominator.

### 5.3 C3′ — the conjunction, and why it was refused too

*Decline iff the ink clears both sides (R154) **and** one mcid run encloses the boundary **and** a
space glyph straddles it.* Measured on bfs page 6 row 0: of the 16 dividing boundaries, **14 have no
straddling space** and are saved; row 1's 12 are all saved. But two are not:

```
    b=  472.81  space_straddles=YES  left='sRapportde' right='Rapportde'
    b=  473.38  space_straddles=YES  left='sRapportde' right='Rapportde'
```

`'Rapport de'` and `'Rapport de'` — two distinct column headers — still weld into one cell.

**Refused, and the reason is the rule and not the residual.** Adding a third clause because the first
two leave two boundaries wrong is fitting the corpus, not finding the fact
(`CLAUDE.md` § *no overfitting*; *honest failure > fake success*). The premise had already failed in
§5.2; a conjunction that patches 14 of 16 symptoms does not restore it.

---

## 6. The methodological finding — a page-0 census cannot validate an every-page rule

**This is the part worth carrying beyond `R155`.** The C3 census, the sha256 comparison, and every
figure in §5.1 were **page 0 only** — and were reported as `8 of 3613`, `0 occurrences`, and
*"byte-identical by construction"*. The design even named the exact failure it would suffer, in its
own risk section: *"an author who tags a whole table ROW as one marked-content item would have every
gutter in that row declined."* It then measured that risk at **0 occurrences in 3613 boundaries**,
and scoped the measurement to page 0.

**The risk was live on page 6 of the same corpus.** Naming a risk and then measuring it out of scope
is worse than not measuring it, because the zero reads as evidence of absence.

The rule runs on every page. The census must too. Raised as `R157`.

---

## 7. Where `R155` now stands

**OPEN, and reclassified.** The geometric half is closed as *measured impossible without a tuned
constant* (§4). The marked-content route is closed as *unsound* (§5). What remains is the question
`CLAUDE.md` §8 names explicitly — *"which columns/rows does X span / read / group"* — which is the
**NEURAL** class: GenAI-via-BAML proposing under assert/propose/promote, disposed by a semantic
oracle. Never a Python geometry heuristic with a tuned tolerance.

The oracle for whoever builds it is already written and is two-sided:

| # | oracle | falsifies |
| --- | --- | --- |
| O1 | WHO p0 band 2 line 0 is **one** node, `'Z-scores (weight in kg)'` | the loop did nothing |
| O2 | WHO p0 band 2 line 1 **byte-identical** — twelve words, `'-3 SD'` intact | `R155`'s hard invariant |
| O3 | bfs p6 band 2 line 0 **byte-identical** — nine header cells | §5.2, the C3 killer |
| O4 | apple p0 band 2 data rows **byte-identical** | §4, the C2 killer |
| O5 | corpus battery, DOCUMENT scope, `validate_shapes=False`: **no document regresses** | the general claim |

**O3 and O4 are the load-bearing ones**, and neither existed before this loop. O1 is satisfied by any
number of wrong changes — C3 satisfied it while destroying bfs.

---

## 8. What is NOT established

- **Whether the NEURAL route is worth building at all.** WHO's is the only *confirmed* live instance;
  nobody has read apple, gstem, gcap or ons against their PDFs looking for others. Enumerate the
  defect before designing the proposer — building NEURAL machinery for a hypothetical is the failure
  `R144` records.
- **cbh's three prose notes are still split** (`'Dates are based | on Daily Transport…'`). C3
  repaired them; the revert un-repaired them. They are a genuine fidelity defect, unaddressed.
- **The cbh page-0 score moved `0.90919 → 0.90878` under C3** and was never explained before the
  revert made it moot.
- **`mcid` was consumed as an opaque grouping token throughout.** `/StructTreeRoot` was never read.
  A route that reads the actual structure tree — where a `<TH>` is distinguishable from a `<P>` — is
  **not** refuted here, because it was never tried. §5's refutation is of `mcid`-as-grouping only.
