# Locating the header/body boundary from decoration — measurement pass

**Date:** 2026-08-08 · **Status:** measurement only — no design, no plan ·
**Answers:** `2026-08-08-concurrent-sensor-table-scan-design.md` §11.6 item 1, the named
blocker ("replace the locator; measure it on WHO, cbh, stem, capacity before design closes") ·
**Pages measured:** apple 0/1/2, who 0/2, cbh 0, stem 0/1, capacity 0, bfs 6, ons 7

**Doc impact:** none — this file records measurements; it asserts no design.

---

## 0. Result in one line

**No single locator exists, and the reason is a property of the documents, not of the
locator:** decoration marks the header/body boundary only where the author gave the header
block a *different* border treatment from the body rows. Where every row is marked
identically, decoration is **silent** about which row is the header — and that silence is
itself measurable in advance.

## 1. First, a correction that removes a constant

Marks read from `page.rects` (one object per drawn mark) instead of `page.lines + page.edges`
(which reports the top *and* bottom edge of every filled rect, doubling every rule). With a
running-max abutment merge at tol=0 — and **no minimum segment width**, since the gutter
bridges that distinguish a parent rule from a leaf are 0.96–2.64pt wide — apple p0 reads:

```
RULE y=103.56  span=260.4 cov=98.6%  segs=2  [(302.68, 431.08), (434.68, 563.08)]
RULE y=125.16  span=260.4 cov=95.9%  segs=4  [(302.68, 365.08), (368.68, 431.08),
                                              (434.68, 497.08), (500.68, 563.08)]
```

Two parent spans and four leaf columns, **directly, with no Δy tolerance and no doubling
filter**. This closes review finding F2b/F2c: the blocked spec needed a 1.5pt constant only
because it was reading edges instead of marks.

It also separates two things `extract_hrules` conflates: apple's **zebra is fills**, and its
first genuine full-width *rule* is at y=168.12 — a subtotal rule, well inside the body — not
the y=139.56 the blocked spec treated as a row separator.

## 2. The locator tested

Stated plainly, so it can be judged: *full-width marks are those whose single merged segment
spans (a fraction of) the widest mark on the page; the header block is the text between the
last two full-width marks before the body.* Coverage fraction swept at 1.00 / 0.95 / 0.90 /
0.80 so the sensitivity is visible rather than hidden.

### 2.1 Where it works — exactly

```
########## who p0   widest mark span = 729.7
  frac=0.90:   6 full-width marks | 2 lines above first | lines between: [1, 1, 25, 0, 1, 0]
  --> header block = lines between y=115.38 and y=130.62:
        y= 118.71 :: Year: Month Month L M S -3 SD -2 SD -1 SD Median 1 SD 2 SD 3 SD

########## who p2   (identical structure)
  --> header block = y=118.71 :: Year: Month Month L M S -3 SD -2 SD -1 SD Median 1 SD 2 SD 3 SD
```

Exactly the header row, on both pages. **WHO is the document that destroyed the previous
locator** — it proposed a 26pt-wide grid of emblem strokes there — and it is the one document
this locator reads correctly. That inversion is the useful part of the result.

### 2.2 Where it fails, and the two distinct reasons

```
########## apple p0   frac=0.90:  44 full-width marks | lines between: [1,1,1,1,1,1,1,1,0,1,...]
########## capacity p0 frac=0.90: 31 full-width marks | lines between: [1,1,1,1,1,1,1,1,1,1,...]
########## cbh p0      frac=0.95: 61 full-width marks | lines between: [1,4,3,1,1,1,1,1,1,1,...]
```

**Reason A — row-uniform decoration.** Every row is delimited by a full-width mark (apple's
zebra stripes; capacity's and cbh's per-row rules), so there is no distinguished pair to find.
On cbh the "first large gap" fallback fires 540pt down the page and returns a data row.

```
########## stem p0   frac=0.90:  28 full-width marks | lines between: [1,1,3,1,2,2,2,1,1,2,4,5,...]
  --> header block candidate (WRONG): y=159.63 'Mackay Total 5 0,000' + 3 more data rows
```

**Reason B — marks delimit records, not lines.** stem's rules bound *records*, and a record
spans 2–3 wrapped lines. Its true header block (y=67.83 / 74.43 / 81.03, between marks at
66.72 and 87.00) is three lines — **geometrically indistinguishable from a three-line wrapped
record**. No gap-size rule separates them, and a gap-size rule would be a tuned constant
anyway.

### 2.3 The discriminator is measurable in advance

Bijection test — does each full-width mark separate exactly one text line from the next?

```
doc        pg fwmarks  lines  gaps==1   frac  reading
apple       0      44     44       37   0.84  ROW-UNIFORM   (decoration silent on the boundary)
apple       1      41     43       34   0.83  ROW-UNIFORM
apple       2      40     41       34   0.85  ROW-UNIFORM
capacity    0      31     32       31   1.00  ROW-UNIFORM
cbh         0      61     85       54   0.89  ROW-UNIFORM
who         0       6     30        3   0.50  HEADER-DISTINGUISHED (boundary readable)
who         2       6     17        3   0.50  HEADER-DISTINGUISHED
stem        0      28     65       11   0.39  HEADER-DISTINGUISHED
stem        1      35     83       13   0.37  HEADER-DISTINGUISHED
bfs         6      15     43        7   0.47  HEADER-DISTINGUISHED
ons         7       9     68        5   0.56  MIXED
```

**Honest limit: the class does not predict locator success.** stem scores 0.39 — firmly
"header-distinguished" — yet the locator fails on it for reason B. The bijection test detects
*row-uniform marking*; it does not detect *record-level* marking. So it is a sound test for
"decoration is silent" and an unsound one for "decoration is sufficient".

## 3. What this measurement establishes

1. **The header tree is readable from decoration on apple and WHO, by different renderings of
   the same idea.** apple draws a merged header cell as a *rule span* over its children
   (2 parents over 4 leaves, §1). WHO draws it as a *filled box* over its children — fill
   y=102.78 is one box `(332.09, 780.29)` spanning the z-score columns, and the caption
   `Z-scores (weight in kg)` sits inside it at x 502.6–609.8, with the 5 left-hand columns as
   separate boxes at fill y=101.94. **A merged header cell is one drawn mark spanning its
   children** — in either rendering.
2. **The header/body boundary is a different question from the header tree**, and it is
   *not* generally answerable from decoration. It is answerable on WHO; it is not on apple,
   capacity, cbh, or stem.
3. Therefore the blocked spec's claim that this route gives a boundary "derived with no
   reference to cell datatypes" — its answer to R71's circularity — **holds only on WHO**,
   and must not be carried as general.
4. **Row-uniform marking is genuine silence, not a proposal.** This is the well-behaved
   counterpart to review finding F3 (where the zebra's explicit white stripes made NO-FILL a
   positive exclusion). A mark present on every row equally excludes nothing and proposes
   nothing about the boundary; a fill extent that stops *does* propose. The two must not be
   treated alike.

## 4. What is NOT established, and must not be assumed

- That any text-derived signal locates the boundary on the row-uniform documents. Not measured
  here. The obvious candidate — the first row at which the body's pattern begins repeating — is
  the natural next probe, and it is text-derived, so under the standing priority it applies
  only where decoration is silent.
- That the modal-run-count region start can serve. Measured and it cannot: it lands on
  apple p0's *second* data row (y=157.36, ground truth 129.04/143.20) and on stem p0's
  y=101.31 against a ground-truth body start of 88.35. It is a conservative interior estimate,
  never the boundary.
- Anything about pages this pass did not cover (apple p1/p2 header trees were read in §1 only;
  ons p7's located block `Section G-T G and I H and J K-N O-T` is the last of a five-line
  wrapped header, so the locator finds a *part* of the header block there, not the whole —
  counted MIXED above and not claimed as a success).

## 5. Probes

`locator1.py` (interleaved ground truth), `locator2.py` (rules vs fills, no width floor),
`locator3.py` (full-width profile + sensitivity sweep), in the session scratchpad. All read
the corpus directly; none writes to the repo.
