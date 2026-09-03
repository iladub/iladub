# R161 measured — section repair cannot fire on apple, and the eight refusals are one coverage gap

**What this is:** the measurement `R161` deferred: *"why `sectiongraph.section_candidates` recognizes
no candidate section on apple p0 bands 3/5/6/7 and p2 bands 3/4/5/7 — dumping its own evidence graph."*
It is a diagnosis; it builds no remedy.

**Result in one line:** recognition runs on every apple page and the signature half of the section
identity agrees across every band, but the header-box half is emitted for at most one band per page
— and even if it were emitted, apple's sections print *different* headers, so `section-repeat.rq`
could never group them. The eight `REGION_TILING_FAILED` bands all refuse on **`CoverageShape`**:
they are body continuations of one statement table, carrying no column header of their own.

**Doc impact: none.**

---

## 1. The three causes the measurement had to separate

The repair driver (`document.py:1472-1490`) runs unconditionally; `section_repair=False` in
`sectiongraph`'s docstring names the per-band *build* flag, not the driver. So "never fires" had three
candidate mechanisms, in the order the driver consults them:

- (a) the page carries fewer than two ruled bands, and recognition is skipped;
- (b) recognition runs and derives no group;
- (c) a group is found but pass 2 still escalates.

## 2. Method

`scripts/section_repair_census.py`, committed by this loop. Per page: `page_bands` + `compile_tables`
for the band census and verdicts; `section_evidence` + `section_candidates` over the ruled bands (the
exact input and output of `section-repeat.rq`); and `tiling.region_tiles` wrapped read-only so each
refusal's SHACL report is kept. HEAD `4cfee38` (`main` after PR #152).

## 3. Readings

```
page 0: score=0.3243 bands=8 ruled=6 distinct rule-x signatures=1 groups=[]
  band lines rules hrules verdict    reason                header-box-y        header-box-text | first line
     0     1     0      0 ignored    fewer than 2 lines    None                'None'                         | Apple Inc.
     1     2     0      0 ignored    fewer than 2 columns  None                'None'                         | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)
     2    12   136    139 asserted   None                  126.1-139.6         'Net sales:'                   | Three Months Ended Nine Months Ended
     3     4    62     42 escalated  REGION_TILING_FAILED  285.7-286.9         'None'                         | Operating expenses:
     4     5    75     60 asserted   None                  357.0-358.0         'None'                         | Operating income 35,695 28,202 122,432 100,623
     5     6   102     65 escalated  REGION_TILING_FAILED  442.4-443.6         'None'                         | Earnings per share:
     6     7   121     79 escalated  REGION_TILING_FAILED  546.8-547.8         'None'                         | (1) Net sales by reportable segment:
     7     7   121     78 escalated  REGION_TILING_FAILED  660.8-661.8         'None'                         | (1) Net sales by category:
  tiling refused htable3: {'CoverageShape': 4, 'UnambiguousAccessShape': 4} — Leaf column is not covered by any header node of its table (coverage gap).
  tiling refused htable5: {'CoverageShape': 4, 'UnambiguousAccessShape': 4} — Leaf column is not covered by any header node of its table (coverage gap).
  tiling refused htable6: {'CoverageShape': 4, 'UnambiguousAccessShape': 4} — Leaf column is not covered by any header node of its table (coverage gap).
  tiling refused htable7: {'CoverageShape': 4, 'UnambiguousAccessShape': 4} — Leaf column is not covered by any header node of its table (coverage gap).
page 1: score=0.1667 bands=8 ruled=6 distinct rule-x signatures=3 groups=[]
     2    11    74     58 asserted   None                  135.2-136.2         'None'                         | June 27, September 27,
     3     7    65     44 escalated  REGION_TILING_FAILED  277.6-278.8         'None'                         | Non-current assets:
     4     8    73     50 escalated  ROUND_TRIP_FAIL       391.6-392.8         'None'                         | LIABILITIES AND SHAREHOLDERS’ EQUITY:
     5     5    49     32 escalated  REGION_TILING_FAILED  520.0-520.9         'None'                         | Non-current liabilities:
     6     1     7      0 ignored    fewer than 2 lines    None                'None'                         | Commitments and contingencies
     7     8    66     42 escalated  REGION_TILING_FAILED  634.0-647.6         'Common stock and additional ' | Shareholders’ equity:
  tiling refused htable3, htable5, htable7: {'CoverageShape': 2, 'UnambiguousAccessShape': 2} — same message
page 2: score=0.0270 bands=8 ruled=5 distinct rule-x signatures=1 groups=[]
     2     4     0     10 escalated  MATRIX_AMBIGUOUS      None                'None'                         | Nine Months Ended
     3    14   134     86 escalated  REGION_TILING_FAILED  176.5-177.5         'None'                         | Operating activities:
     4     7    65     40 escalated  REGION_TILING_FAILED  390.1-391.3         'None'                         | Investing activities:
     5     9    85     52 escalated  REGION_TILING_FAILED  504.1-505.3         'None'                         | Financing activities:
     6     2    18     10 asserted   None                  646.7-647.6         'None'                         | Increase in cash, cash equivalents, and restricted cash and cash equiv
     7     2    16      6 escalated  REGION_TILING_FAILED  689.4-690.4         'None'                         | Supplemental cash flow disclosure:
  tiling refused htable3, htable4, htable5, htable7: {'CoverageShape': 2, 'UnambiguousAccessShape': 2} — same message
```

(Page 1's and page 2's `ignored` title bands are elided; they read as page 0's.) Page scores here are
`compile_tables` page scores, not the 0.1895 document score.

Rule geometry, same run (`Counter` of vertical-rule heights, hrule widths, hrule y-gaps, p0 band 3):

```
vrule heights {14.2: 26, 13.2: 21, 14.4: 15} | hrule widths {3.6: 18, 62.4: 16, 252.7: 4} | hrule y-gaps {13.2: 2, 0.96: 2, 1.2: 1}
```

## 4. What the readings say

**(a) is refuted.** Every page carries 5–6 ruled bands; recognition runs on all three.

**(b) holds, and its mechanism is specific.** `section-repeat.rq` groups two bands only when BOTH
`tab:headerBoxText` and `tab:ruleXsSignature` agree verbatim. The signature half is satisfied
outright: all six ruled bands on p0 share one signature, all five on p2 share one. The header-box half
is emitted for exactly one band on p0 (band 2, `Net sales:`), one on p1 (band 7), none on p2 — so no
pair exists to match. Two facts stand behind that:

- **The "rules" are spreadsheet cell-rectangle edges, not drawn ruling.** Vertical rules are one row
  tall (13.2–14.4pt); horizontal rules come in three widths matching the label, `$` and number cell
  widths; consecutive hrules sit 13.2pt apart (row pitch) with **0.96pt** gaps between one cell's
  bottom and the next cell's top. `_leading_box_y` selects the first hrule pair an interior rule's
  y-extent overlaps, and on every escalated band that is a 0.96pt inter-cell gap (`285.7-286.9`,
  `442.4-443.6`, …). No line centre falls inside a 1pt box, so `_header_box_text` abstains. This is
  the degenerate-candidate class `R48` holds open; here it is described, not fixed, because of the
  second fact.
- **Apple's sections do not repeat a header.** `Operating expenses:`, `Earnings per share:`,
  `(1) Net sales by reportable segment:` are different printed headings. Loop Q's repair exists for
  the CBH shape — the SAME header box redrawn per section. With a perfect header-box candidate the
  texts would still differ and the query would still return no pair. **Section repair is the wrong
  instrument for this document by design, not by defect.** R161's framing, "silently declines to
  engage," described a tool applied outside its population.

**(c) is unreachable** — no group, so no pass 2.

**The refusal that actually costs the eight bands is one defect.** Every `REGION_TILING_FAILED` band
on all three pages is refused by `CoverageShape` + `UnambiguousAccessShape` on every leaf column:
*"Leaf column is not covered by any header node of its table."* The band has data columns and no
header row: the statement's single column header (`Three Months Ended … / June 27, June 28, …`) is
band 2 at the top of the page, asserted, and bands 3, 5, 6, 7 are body sections of that one table,
separated from it by whitespace and a section heading line. The rule-x signature agreeing across
every band on the page is the author's own evidence that they are one grid.

**The seam that would carry a header exists, page-to-page only.** Loop M (closing `R29`) carries page
N−1's confirmed header onto page N under `continuation-of.rq`, through
`compile_tables(carried_header_roles={band: reading})`. Clause (a) of that query requires both leaf
header rows to exist, so a header-less band can never be licensed by it, and nothing has ever driven
the seam from a band on the same page. That is the successor's subject, `R165`.

## 5. What this loop did NOT do

- No remedy; no `src/` change. The forced-carriage spike the handoff proposes was not run.
- p0 band 4 and p2 band 6 assert with no header line of their own; what they took as a header was
  not inspected (handoff § 4).
- **Positive control, run:** the same instrument on `corpus/ag-trade/cbh-stem-2026-08-03.pdf` page 0
  derives `groups=[(1, 3, 5, 7)]` over 5 ruled bands with 2 distinct signatures — recognition's
  evidence graph is sound where the repeated-header shape exists, so apple's empty result is a
  property of apple, not of the instrument.
