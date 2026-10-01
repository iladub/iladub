# T3b measurements — the `_under_resolved` guard on the box band T1 (MEASUREMENT ONLY)

**Serves:** prog:criterion:etkl:03 — measurement for Task 3b of the box-split loop.
**Doc impact: none.** Copied from the SDD workspace so it is tracked; the scratch instruments it names live in a session scratchpad and are NOT durable — rerun from the commands below.

Branch `box-split`, HEAD `5ab01ad` (`git rev-parse --short HEAD` -> `5ab01ad`). Nothing under
`src/`, `tests/`, `docs/` was modified; nothing committed. All instruments are monkeypatches in
scratch scripts under
`/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/ef773e44-72f4-42e5-af80-7f2b655fc3f2/scratchpad/`
(`m1.py`, `m2.py`, `m2.sh`, `m2_report.py`, `guardoff.py`, `falsify.sh`; raw outputs `m1.out`,
`m2.jsonl`, `m2.log`, `m2_report.out`, `m2_extra.out`, `falsify.out`). Facts only; no fix is
proposed.

Guard under measurement (`src/iladub/etkl/compile.py`, `_build_ruled_band`):

```
_word_cols = _word_column_count(sub)          # infer_leaf_grid(rules-free copy of the PEELED sub).ncols
_under_resolved = (_word_cols is not None and len(xs) >= 2
                   and len(xs) - 1 < _word_cols)
```

and the second application after `refine_rule_columns`: `if _word_cols is not None and len(col_xs) - 1 < _word_cols: return band`.

---

## M1 — T1's 9 gutter columns vs its 7 rule columns

Command:

```
cd "/Volumes/WD Green/dev/git/iladub" && PYTHONPATH=src .venv/bin/python "$SP/m1_list.py"   # band list
cd "/Volumes/WD Green/dev/git/iladub" && PYTHONPATH=src .venv/bin/python "$SP/m1.py"          # the measurement
```

`m1_list.py` (identifies T1 = `page_bands(cbh, 0)[10]`, the only band with 8 `_rule_boundaries`):

```
10 lines 5 rules 8 rb 8 column_xs 0 | PORT WHEAT MAIN WHEAT GRADES BARLEY CANOLA OTHER TOTAL
11 lines 4 rules 3 rb 3 column_xs 0 | ALB 1 - 15 October
```

`m1.py` wraps `compile._build_ruled_band` and `compile._word_column_count` to capture the exact
(peeled) `sub` the guard measured. It matched exactly one build call to T1 by geometry
(`absorb_unit_markers` returns a new Band object, so identity does not match; lines are equal).
Raw output (`m1.out`):

```
matched build calls: 1 ; T1 is the out object: [False] ; lines equal: [True]
T1 = page_bands(cbh,0)[10]; _rule_boundaries(T1) = [38.16, 75.98, 154.46, 216.5, 259.46, 302.42, 345.39, 449.09]
rule xs (len(xs)=8, rule cols=7): [38.16, 75.98, 154.46, 216.5, 259.46, 302.42, 345.39, 449.09]
_word_column_count(sub) = 9
peeled sub lines == T1 lines: True
infer_leaf_grid(rules-free).ncols = 9 boundaries = (50.88, 70.88, 101.38, 139.88, 216.38, 254.88, 298.88, 339.38, 377.88, 405.52)

LINES (index: text [x0,x1])
  L0 top=691.62: PORT[50.88,64.13]  WHEAT[106.58,124.86]  MAIN[158.54,172.60]  WHEAT[173.89,192.16]  GRADES[193.45,213.35]  BARLEY[229.34,247.62]  CANOLA[271.10,291.62]  OTHER[315.98,332.68]  TOTAL[389.81,405.52]
  L1 top=699.66: ALB[52.80,62.29]  129,183[77.30,96.79]  APW1/ASW9/AWW1[155.78,206.82]  27,023[219.14,235.62]  3,345[263.42,276.90]  1,293[306.38,319.86]  160,845[346.73,366.21]
  L2 top=707.70: ESP[53.04,61.99]  25,013[78.62,95.11]  APW1/H2/ASW9[155.78,196.50]  49,244[219.14,235.62]  5,596[263.42,276.90]  2,997[306.38,319.86]  82,850[348.05,364.53]
  L3 top=715.74: GER[52.44,62.53]  160,198[77.30,96.79]  AWW1/ASW9/ANW1[155.78,207.54]  3,406[220.46,233.94]  2,667[263.42,276.90]  4,460[306.38,319.86]  170,731[346.73,366.21]
  L4 top=724.14: KWI[52.44,62.68]  170,878[77.30,96.79]  AUH2/APWN/APW1[155.78,205.01]  33,996[219.14,235.62]  76,603[262.10,278.58]  3,418[306.38,319.86]  284,895[346.73,366.21]

ink extent x0=50.88 x1=405.52
GUTTER RUNS (bin-start x, bin-end x, centre=boundary) and rule xs inside the run:
  [64.88,76.88] centre 70.88: rules inside = [75.98]  -> RULE
  [96.88,105.88] centre 101.38: rules inside = []  -> EXTRA
  [124.88,154.88] centre 139.88: rules inside = [154.46]  -> RULE
  [213.88,218.88] centre 216.38: rules inside = [216.5]  -> RULE
  [247.88,261.88] centre 254.88: rules inside = [259.46]  -> RULE
  [291.88,305.88] centre 298.88: rules inside = [302.42]  -> RULE
  [332.88,345.88] centre 339.38: rules inside = [345.39]  -> RULE
  [366.88,388.88] centre 377.88: rules inside = []  -> EXTRA
rules with no gutter run containing them: [38.16, 449.09]

EXTRA gutter centre 101.38 run [96.88,105.88] inside rule interval [75.98,154.46]
   L0: words in interval=['WHEAT']; left-flank -; right-flank WHEAT[106.58,124.86]; splits-here=False
   L1: words in interval=['129,183']; left-flank 129,183[77.30,96.79]; right-flank -; splits-here=False
   L2: words in interval=['25,013']; left-flank 25,013[78.62,95.11]; right-flank -; splits-here=False
   L3: words in interval=['160,198']; left-flank 160,198[77.30,96.79]; right-flank -; splits-here=False
   L4: words in interval=['170,878']; left-flank 170,878[77.30,96.79]; right-flank -; splits-here=False
EXTRA gutter centre 377.88 run [366.88,388.88] inside rule interval [345.39,449.09]
   L0: words in interval=['TOTAL']; left-flank -; right-flank TOTAL[389.81,405.52]; splits-here=False
   L1: words in interval=['160,845']; left-flank 160,845[346.73,366.21]; right-flank -; splits-here=False
   L2: words in interval=['82,850']; left-flank 82,850[348.05,364.53]; right-flank -; splits-here=False
   L3: words in interval=['170,731']; left-flank 170,731[346.73,366.21]; right-flank -; splits-here=False
   L4: words in interval=['284,895']; left-flank 284,895[346.73,366.21]; right-flank -; splits-here=False

WHAT-IF ncols dropping one line at a time (rules-free):
  without L0: ncols = 7, boundaries = (52.44, 69.94, 126.44, 213.44, 248.94, 292.44, 333.44, 366.21)
  without L1: ncols = 9, boundaries = (50.88, 70.88, 101.38, 139.88, 216.38, 254.88, 298.88, 339.38, 377.88, 405.52)
  without L2: ncols = 9, boundaries = (50.88, 70.88, 101.38, 139.88, 216.38, 254.88, 298.88, 339.38, 377.88, 405.52)
  without L3: ncols = 9, boundaries = (50.88, 70.88, 101.38, 139.88, 216.38, 254.88, 298.88, 339.38, 377.88, 405.52)
  without L4: ncols = 9, boundaries = (50.88, 70.88, 101.38, 139.88, 216.38, 255.38, 298.88, 339.38, 377.88, 405.52)
ONLY L0 (header) ncols: 7
ONLY body lines L1.. ncols: 7 (52.44, 69.94, 126.44, 213.44, 248.94, 292.44, 333.44, 366.21)
```

Method note: a gutter run is classified RULE when a rule x lies inside the run's bin extent,
EXTRA otherwise (the run extents are recomputed with `infer_leaf_grid`'s defaults,
`gutter_pct=0.98`, `min_gutter_bins=3`, and reproduce its 10 boundaries exactly). The two outer
rules 38.16 / 449.09 are the box frame; the gutter grid's outer boundaries are the ink extremes
50.88 / 405.52, by construction of `infer_leaf_grid`.

**M1 facts.**

- 9 gutter columns = the 6 interior rules' gutters + **2 EXTRA gutters**, at x = 101.38 and 377.88.
- Both EXTRA gutters sit inside ONE rule interval each: [75.98, 154.46] (WHEAT) and
  [345.39, 449.09] (TOTAL).
- No single line has two words inside those intervals (`splits-here=False` on all 5 lines). In
  each interval the header word lies entirely to the RIGHT of the gutter
  (WHEAT x0=106.58, TOTAL x0=389.81) and every body word lies entirely to the LEFT
  (body x1 <= 96.79 and <= 366.21). The gutter is the x-gap between the header word and the
  body words of the same ruled cell.
- **Cause: both, jointly.** Header line alone -> 7 columns; body lines alone -> 7 columns;
  removing L0 -> 7; removing any single body line -> still 9. The extra gutters exist only when
  the header line and the body lines are profiled together, because within the WHEAT and TOTAL
  cells their words are x-disjoint.

---

## M2 — census, corpus-wide at HEAD

Instrument (`m2.py`): wraps `compile._build_ruled_band` (module global; `page_bands._build_sub`
calls it by global name and `boxsplit._box_band` does `from .compile import _build_ruled_band`
at call time, so both paths are caught) and `compile._word_column_count` (called unconditionally
once per build, on the peeled `sub`). Per call it records `len(xs)-1`, the captured word count,
`_under_resolved` recomputed with the source's own expression, whether the RETURNED band's
`column_xs` is non-empty, and, as a what-if, `infer_leaf_grid` ncols on the rules-free peeled
`sub` with its first line removed (`None` when the peeled `sub` has one line). Caller is
`box` when `_box_band` is on the call stack.

Runner (`m2.sh`), serial, ONE process per document, `page_bands(pdf, page)` for every page, no
full compile:

```
bash m2.sh > m2.log 2>&1     # loops `PYTHONPATH=src .venv/bin/python m2.py <pdf> m2.jsonl` over `find corpus -name '*.pdf' | sort`
grep -c "exit 0" m2.log      # -> 7
python3 m2_report.py > m2_report.out
```

Pages per document (`m2.log`): cbh 1, graincorp-capacity 1, graincorp-stem 3, apple 3, bfs 7,
ons 9, who 3 = **27 pages**, all 7 processes exit 0.

### Totals (`m2_report.out`, `m2_extra.out`)

```
TOTAL _build_ruled_band calls: 100
  section_repair=False: 100  True: 0
  _word_column_count fired inside every call: True
  by caller: {'page_bands/_build_sub': 98, 'box': 2}
_under_resolved=True: 36  False: 64
word_cols None: 0
returned column_xs non-empty (all calls): 18
returned column_xs non-empty among under_resolved: 12
rule_cols == word_cols: 19  rule_cols > word_cols: 45  rule_cols < word_cols: 36

PER DOC: calls / under_resolved / column_xs non-empty
  corpus/ag-trade/cbh-stem-2026-08-03.pdf: 6 / 1 / 0
  corpus/ag-trade/graincorp-capacity-2026-08-04.pdf: 3 / 0 / 0
  corpus/ag-trade/graincorp-stem-2026-07-31.pdf: 4 / 0 / 3
  corpus/financial/apple-fy2026q3-statements.pdf: 17 / 0 / 0
  corpus/gov-stats/bfs-population-bilan-2023.pdf: 22 / 14 / 8
  corpus/gov-stats/ons-index-of-services-2026-02.pdf: 37 / 21 / 4
  corpus/health/who-wfa-boys-zscore-0-5.pdf: 11 / 0 / 3

under_resolved rows whose what-if ncols (first line removed) <= rule_cols: 2
   cbh-stem-2026-08-03.pdf 0 7 7 PORT WHEAT MAIN WHEAT GRADES BARLEY CANO
   bfs-population-bilan-2023.pdf 5 1 1 Sources: OFS - BEVNAT, STATPOP
under_resolved rows with single line (what-if None): 12
NOT under_resolved rows where what-if ncols > rule_cols (len(xs)>=2): 0
rule_cols==0 rows (len(xs)<2): 0
under_resolved by rule_cols==1 (outer box only): 27  rule_cols>1: 9
under_resolved per (doc,page): {('cbh-stem-2026-08-03.pdf', 0): 1, ('bfs-population-bilan-2023.pdf', 5): 6, ('bfs-population-bilan-2023.pdf', 6): 8, ('ons-index-of-services-2026-02.pdf', 0): 1, ('ons-index-of-services-2026-02.pdf', 7): 14, ('ons-index-of-services-2026-02.pdf', 8): 6}
```

CONTROL: the instrument fired 100 times, and `_word_column_count` fired inside every one of them,
so a zero anywhere in this census is a zero, not a silent instrument.

Of the 36 `_under_resolved=True` rows: 27 have `rule_cols == 1` (the `len(xs) == 2` outer-box
shape R225 was about); **9 have `rule_cols > 1`** — cbh p0 T1 (7 vs 9) and 8 bfs p6 bands (6 vs 9).
cbh T1 is the ONLY under-resolved row from a box band, and the only under-resolved row whose
what-if (first line removed) count is `>= 2` and `<= rule_cols`.

### Every `_under_resolved=True` row

| doc | page | caller | rule cols | word cols | _under_resolved | column_xs non-empty (n) | lines | what-if ncols w/o first line | first line |
|---|---|---|---|---|---|---|---|---|---|
| cbh-stem-2026-08-03.pdf | 0 | box | 7 | 9 | True | False (0) | 5 | 7 | PORT WHEAT MAIN WHEAT GRADES BARLEY CANOLA OTHER TOTAL |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 1 | 12 | True | True (13) | 5 | 12 | 2005 7 415 102 72 903 61 124 11 779 118 270 82 090 36 180 -  |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 1 | 12 | True | True (13) | 11 | 12 | 2010 2 7 785 806 80 290 62 553 17 737 161 778 96 839 64 939  |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 1 | 12 | True | True (13) | 4 | 12 | 2020 8 606 033 85 914 76 195 9 719 163 180 109 376 53 804 74 |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 1 | 10 | True | False (0) | 1 | None | Suisse 3 8 815 385 80 024 71 822 8 202 139 118 0 8 962 258 1 |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 1 | 10 | True | False (0) | 6 | 10 | Tessin 354 023 2 390 3 488 - 1 098 4 883 - 145 357 720 3 697 |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 1 | 2 | True | False (0) | 4 | 1 | Sources: OFS - BEVNAT, STATPOP |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | False (0) | 1 | None | Total 8 962 258 1 788 440 2 328 149 3 115 383 1 226 729 503  |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | True (13) | 4 | 9 | Région lémanique 1 736 124 365 836 471 307 595 287 212 487 9 |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | True (13) | 6 | 9 | Espace Mittelland 1 944 753 385 379 486 507 668 415 289 924  |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | True (13) | 4 | 9 | Suisse du Nord-Ouest 1 225 762 241 847 308 789 430 285 173 7 |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | False (0) | 1 | None | Zurich 1 605 508 317 627 451 829 558 149 193 666 84 237 31.4 |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | True (13) | 8 | 9 | Suisse orientale 1 237 469 245 111 314 009 427 846 181 342 6 |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | True (13) | 7 | 9 | Suisse centrale 854 922 169 763 216 904 304 027 118 629 45 5 |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | False (0) | 1 | None | Tessin 357 720 62 877 78 804 131 374 56 967 27 698 29.9 40.3 |
| ons-index-of-services-2026-02.pdf | 0 | page_bands/_build_sub | 1 | 4 | True | True (5) | 11 | 4 | Contact: Release date: Next release: |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 3 | True | False (0) | 2 | 2 | IOS1 IOS: Index of Services 1 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 2 | True | False (0) | 1 | None | Business Govern- |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 5 | True | False (0) | 3 | 5 | Total Distribution Transport, services ment and |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 6 | True | True (7) | 2 | 6 | Section G-T G and I H and J K-N O-T |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 6 | True | False (0) | 5 | 6 | S2KU S2MV KI7B KI7L KI7T |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 6 | True | False (0) | 1 | None | 2025 102.9 100.1 108.8 101.5 104.1 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 7 | True | False (0) | 1 | None | 2024 Q4 102 99.7 106 101.1 103.2 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 7 | True | False (0) | 1 | None | 2025 Q1 102.6 100.6 107.7 101.5 103.4 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 6 | True | False (0) | 1 | None | Q2 102.8 99.9 108.7 101.5 104 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 6 | True | False (0) | 1 | None | Q3 103 99.9 109.1 101.6 104.4 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 6 | True | False (0) | 1 | None | Q4 103 100 109.9 101.3 104.6 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 7 | True | True (8) | 15 | 7 | 2024 Dec 102.4 100.5 106.3 101.5 103.4 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 5 | True | False (0) | 7 | 6 | Percentage change, latest year on previous year |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 5 | True | False (0) | 17 | 7 | Percentage change, latest month on same month a year ago |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 1 | 2 | True | False (0) | 1 | None | Business Govern- |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 1 | 5 | True | False (0) | 3 | 5 | Total Distribution Transport, services ment and |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 1 | 6 | True | True (7) | 2 | 6 | Section G-T G and I H and J K-N O-T |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 1 | 5 | True | False (0) | 17 | 7 | Percentage change, latest month on previous month |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 1 | 4 | True | False (0) | 17 | 7 | Percentage change, latest 3 months on same 3 months a year a |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 1 | 7 | True | False (0) | 16 | 7 | S2BG S2DH KI7D KI7K KI7S |

### All 100 rows

| doc | page | caller | rule cols | word cols | _under_resolved | column_xs non-empty (n) | lines | what-if ncols w/o first line | first line |
|---|---|---|---|---|---|---|---|---|---|
| cbh-stem-2026-08-03.pdf | 0 | page_bands/_build_sub | 23 | 16 | False | False (0) | 18 | 16 | GERALDTON |
| cbh-stem-2026-08-03.pdf | 0 | page_bands/_build_sub | 23 | 16 | False | False (0) | 21 | 16 | KWINANA |
| cbh-stem-2026-08-03.pdf | 0 | page_bands/_build_sub | 23 | 16 | False | False (0) | 20 | 16 | ALBANY |
| cbh-stem-2026-08-03.pdf | 0 | page_bands/_build_sub | 23 | 16 | False | False (0) | 10 | 16 | ESPERANCE |
| cbh-stem-2026-08-03.pdf | 0 | box | 2 | 2 | False | False (0) | 4 | 2 | ALB 1 - 15 October |
| cbh-stem-2026-08-03.pdf | 0 | box | 7 | 9 | True | False (0) | 5 | 7 | PORT WHEAT MAIN WHEAT GRADES BARLEY CANOLA OTHER TOTAL |
| graincorp-capacity-2026-08-04.pdf | 0 | page_bands/_build_sub | 5 | 1 | False | False (0) | 2 | 1 | ELEVATION CAPACITY TABLE |
| graincorp-capacity-2026-08-04.pdf | 0 | page_bands/_build_sub | 21 | 9 | False | False (0) | 1 | None | Year Elevation Period Mackay Gladstone Fisherman Islands Car |
| graincorp-capacity-2026-08-04.pdf | 0 | page_bands/_build_sub | 49 | 16 | False | False (0) | 27 | 16 | 2025/26 August 2nd Half 0 N 10,000 Y 0 N 0 N On Application  |
| graincorp-stem-2026-07-31.pdf | 0 | page_bands/_build_sub | 4 | 1 | False | False (0) | 1 | None | SHIPPING STEM |
| graincorp-stem-2026-07-31.pdf | 0 | page_bands/_build_sub | 19 | 17 | False | True (22) | 61 | 17 | Friday, 31 July 2026 |
| graincorp-stem-2026-07-31.pdf | 1 | page_bands/_build_sub | 18 | 18 | False | True (21) | 80 | 18 | Date of Grain |
| graincorp-stem-2026-07-31.pdf | 2 | page_bands/_build_sub | 18 | 16 | False | True (21) | 71 | 16 | Date of Grain |
| apple-fy2026q3-statements.pdf | 0 | page_bands/_build_sub | 14 | 5 | False | False (0) | 12 | 9 | Three Months Ended Nine Months Ended |
| apple-fy2026q3-statements.pdf | 0 | page_bands/_build_sub | 14 | 5 | False | False (0) | 4 | 5 | Operating expenses: |
| apple-fy2026q3-statements.pdf | 0 | page_bands/_build_sub | 14 | 9 | False | False (0) | 5 | 9 | Operating income 35,695 28,202 122,432 100,623 |
| apple-fy2026q3-statements.pdf | 0 | page_bands/_build_sub | 14 | 9 | False | False (0) | 6 | 9 | Earnings per share: |
| apple-fy2026q3-statements.pdf | 0 | page_bands/_build_sub | 14 | 9 | False | False (0) | 7 | 9 | (1) Net sales by reportable segment: |
| apple-fy2026q3-statements.pdf | 0 | page_bands/_build_sub | 14 | 9 | False | False (0) | 7 | 9 | (1) Net sales by category: |
| apple-fy2026q3-statements.pdf | 1 | page_bands/_build_sub | 8 | 5 | False | False (0) | 11 | 6 | June 27, September 27, |
| apple-fy2026q3-statements.pdf | 1 | page_bands/_build_sub | 8 | 5 | False | False (0) | 7 | 5 | Non-current assets: |
| apple-fy2026q3-statements.pdf | 1 | page_bands/_build_sub | 9 | 6 | False | False (0) | 8 | 5 | LIABILITIES AND SHAREHOLDERS’ EQUITY: |
| apple-fy2026q3-statements.pdf | 1 | page_bands/_build_sub | 8 | 3 | False | False (0) | 5 | 3 | Non-current liabilities: |
| apple-fy2026q3-statements.pdf | 1 | page_bands/_build_sub | 6 | 1 | False | False (0) | 1 | None | Commitments and contingencies |
| apple-fy2026q3-statements.pdf | 1 | page_bands/_build_sub | 8 | 5 | False | False (0) | 8 | 5 | Shareholders’ equity: |
| apple-fy2026q3-statements.pdf | 2 | page_bands/_build_sub | 8 | 3 | False | False (0) | 14 | 3 | Operating activities: |
| apple-fy2026q3-statements.pdf | 2 | page_bands/_build_sub | 8 | 3 | False | False (0) | 7 | 3 | Investing activities: |
| apple-fy2026q3-statements.pdf | 2 | page_bands/_build_sub | 8 | 3 | False | False (0) | 9 | 3 | Financing activities: |
| apple-fy2026q3-statements.pdf | 2 | page_bands/_build_sub | 8 | 5 | False | False (0) | 2 | 5 | Increase in cash, cash equivalents, and restricted cash and  |
| apple-fy2026q3-statements.pdf | 2 | page_bands/_build_sub | 8 | 5 | False | False (0) | 2 | 5 | Supplemental cash flow disclosure: |
| bfs-population-bilan-2023.pdf | 3 | page_bands/_build_sub | 1 | 1 | False | False (0) | 5 | 1 | Accès aux résultats |
| bfs-population-bilan-2023.pdf | 3 | page_bands/_build_sub | 1 | 1 | False | False (0) | 3 | 1 | Les offices de statistique des cantons et des villes ont eu  |
| bfs-population-bilan-2023.pdf | 3 | page_bands/_build_sub | 1 | 1 | False | False (0) | 3 | 1 | Le Secrétariat d’État aux migrations (SEM), le Secrétariat d |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 12 | 7 | False | False (0) | 3 | 11 | État de laComposantes de l'évolution de la population État d |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 1 | 12 | True | True (13) | 5 | 12 | 2005 7 415 102 72 903 61 124 11 779 118 270 82 090 36 180 -  |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 1 | 12 | True | True (13) | 11 | 12 | 2010 2 7 785 806 80 290 62 553 17 737 161 778 96 839 64 939  |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 1 | 12 | True | True (13) | 4 | 12 | 2020 8 606 033 85 914 76 195 9 719 163 180 109 376 53 804 74 |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 1 | 1 | False | False (0) | 4 | 1 | Sources: OFS - BEVNAT, ESPOP, STATPOP |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 10 | 7 | False | False (0) | 3 | 8 | Cantons État de la Composantes de l'évolution de la populati |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 1 | 10 | True | False (0) | 1 | None | Suisse 3 8 815 385 80 024 71 822 8 202 139 118 0 8 962 258 1 |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 1 | 10 | True | False (0) | 6 | 10 | Tessin 354 023 2 390 3 488 - 1 098 4 883 - 145 357 720 3 697 |
| bfs-population-bilan-2023.pdf | 5 | page_bands/_build_sub | 1 | 2 | True | False (0) | 4 | 1 | Sources: OFS - BEVNAT, STATPOP |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 17 | 9 | False | False (0) | 4 | 3 | Grandes régions Total 0-19 ans 20-39 ans 40-64 ans 65-79 ans |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | False (0) | 1 | None | Total 8 962 258 1 788 440 2 328 149 3 115 383 1 226 729 503  |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | True (13) | 4 | 9 | Région lémanique 1 736 124 365 836 471 307 595 287 212 487 9 |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | True (13) | 6 | 9 | Espace Mittelland 1 944 753 385 379 486 507 668 415 289 924  |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | True (13) | 4 | 9 | Suisse du Nord-Ouest 1 225 762 241 847 308 789 430 285 173 7 |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | False (0) | 1 | None | Zurich 1 605 508 317 627 451 829 558 149 193 666 84 237 31.4 |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | True (13) | 8 | 9 | Suisse orientale 1 237 469 245 111 314 009 427 846 181 342 6 |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | True (13) | 7 | 9 | Suisse centrale 854 922 169 763 216 904 304 027 118 629 45 5 |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 6 | 9 | True | False (0) | 1 | None | Tessin 357 720 62 877 78 804 131 374 56 967 27 698 29.9 40.3 |
| bfs-population-bilan-2023.pdf | 6 | page_bands/_build_sub | 3 | 2 | False | False (0) | 3 | 1 | Source: OFS - STATPOP |
| ons-index-of-services-2026-02.pdf | 0 | page_bands/_build_sub | 1 | 1 | False | False (0) | 4 | 1 | Statistical bulletin |
| ons-index-of-services-2026-02.pdf | 0 | page_bands/_build_sub | 1 | 4 | True | True (5) | 11 | 4 | Contact: Release date: Next release: |
| ons-index-of-services-2026-02.pdf | 1 | page_bands/_build_sub | 1 | 1 | False | False (0) | 4 | 1 | Index of Services time series |
| ons-index-of-services-2026-02.pdf | 1 | page_bands/_build_sub | 1 | 1 | False | False (0) | 3 | 1 | Monthly Business Survey turnover of services industries |
| ons-index-of-services-2026-02.pdf | 1 | page_bands/_build_sub | 1 | 1 | False | False (0) | 4 | 1 | Index of Services, main components and sectors to four decim |
| ons-index-of-services-2026-02.pdf | 1 | page_bands/_build_sub | 1 | 1 | False | False (0) | 3 | 1 | Index of Services revisions triangles |
| ons-index-of-services-2026-02.pdf | 5 | page_bands/_build_sub | 1 | 1 | False | False (0) | 4 | 1 | GDP monthly estimate, UK: February 2026 |
| ons-index-of-services-2026-02.pdf | 5 | page_bands/_build_sub | 1 | 1 | False | False (0) | 4 | 1 | GDP quarterly national accounts, UK: October to December 202 |
| ons-index-of-services-2026-02.pdf | 5 | page_bands/_build_sub | 1 | 1 | False | False (0) | 4 | 1 | Index of Production, UK: February 2026 |
| ons-index-of-services-2026-02.pdf | 5 | page_bands/_build_sub | 1 | 1 | False | False (0) | 4 | 1 | Producer price inflation, UK: February 2026 |
| ons-index-of-services-2026-02.pdf | 5 | page_bands/_build_sub | 1 | 1 | False | False (0) | 2 | 1 | Office for National Statistics (ONS), released 16 April 2026 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 3 | True | False (0) | 2 | 2 | IOS1 IOS: Index of Services 1 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 1 | False | False (0) | 1 | None | Industry sections (SIC2007) |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 2 | True | False (0) | 1 | None | Business Govern- |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 5 | True | False (0) | 3 | 5 | Total Distribution Transport, services ment and |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 6 | True | True (7) | 2 | 6 | Section G-T G and I H and J K-N O-T |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 6 | True | False (0) | 5 | 6 | S2KU S2MV KI7B KI7L KI7T |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 6 | True | False (0) | 1 | None | 2025 102.9 100.1 108.8 101.5 104.1 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 1 | False | False (0) | 1 | None | " |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 7 | True | False (0) | 1 | None | 2024 Q4 102 99.7 106 101.1 103.2 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 7 | True | False (0) | 1 | None | 2025 Q1 102.6 100.6 107.7 101.5 103.4 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 6 | True | False (0) | 1 | None | Q2 102.8 99.9 108.7 101.5 104 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 6 | True | False (0) | 1 | None | Q3 103 99.9 109.1 101.6 104.4 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 6 | True | False (0) | 1 | None | Q4 103 100 109.9 101.3 104.6 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 7 | True | True (8) | 15 | 7 | 2024 Dec 102.4 100.5 106.3 101.5 103.4 |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 5 | True | False (0) | 7 | 6 | Percentage change, latest year on previous year |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 1 | 5 | True | False (0) | 17 | 7 | Percentage change, latest month on same month a year ago |
| ons-index-of-services-2026-02.pdf | 7 | page_bands/_build_sub | 4 | 2 | False | False (0) | 8 | 2 | 1 The IOS output is designated as a National Statistic. |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 2 | 1 | False | False (0) | 1 | None | Industry sections (SIC2007) |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 1 | 2 | True | False (0) | 1 | None | Business Govern- |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 1 | 5 | True | False (0) | 3 | 5 | Total Distribution Transport, services ment and |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 1 | 6 | True | True (7) | 2 | 6 | Section G-T G and I H and J K-N O-T |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 1 | 5 | True | False (0) | 17 | 7 | Percentage change, latest month on previous month |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 1 | 4 | True | False (0) | 17 | 7 | Percentage change, latest 3 months on same 3 months a year a |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 1 | 1 | False | False (0) | 1 | None | Percentage change, latest 3 months on previous 3 months |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 1 | 7 | True | False (0) | 16 | 7 | S2BG S2DH KI7D KI7K KI7S |
| ons-index-of-services-2026-02.pdf | 8 | page_bands/_build_sub | 4 | 2 | False | False (0) | 8 | 2 | 1 The IOS output is designated as a National Statistic. |
| who-wfa-boys-zscore-0-5.pdf | 0 | page_bands/_build_sub | 34 | 2 | False | False (0) | 1 | None | Weight-for-age BOYS |
| who-wfa-boys-zscore-0-5.pdf | 0 | page_bands/_build_sub | 27 | 1 | False | False (0) | 1 | None | Birth to 5 years (z-scores) |
| who-wfa-boys-zscore-0-5.pdf | 0 | page_bands/_build_sub | 47 | 11 | False | True (49) | 9 | 12 | Z-scores (weight in kg) |
| who-wfa-boys-zscore-0-5.pdf | 0 | page_bands/_build_sub | 3 | 1 | False | False (0) | 1 | None | WHO Child Growth Standards |
| who-wfa-boys-zscore-0-5.pdf | 1 | page_bands/_build_sub | 34 | 2 | False | False (0) | 1 | None | Weight-for-age BOYS |
| who-wfa-boys-zscore-0-5.pdf | 1 | page_bands/_build_sub | 27 | 1 | False | False (0) | 1 | None | Birth to 5 years (z-scores) |
| who-wfa-boys-zscore-0-5.pdf | 1 | page_bands/_build_sub | 47 | 11 | False | True (49) | 8 | 12 | Z-scores (weight in kg) |
| who-wfa-boys-zscore-0-5.pdf | 1 | page_bands/_build_sub | 3 | 1 | False | False (0) | 1 | None | WHO Child Growth Standards |
| who-wfa-boys-zscore-0-5.pdf | 2 | page_bands/_build_sub | 57 | 1 | False | False (0) | 2 | 1 | Weight-for-age BOYS |
| who-wfa-boys-zscore-0-5.pdf | 2 | page_bands/_build_sub | 47 | 11 | False | True (49) | 8 | 12 | Z-scores (weight in kg) |
| who-wfa-boys-zscore-0-5.pdf | 2 | page_bands/_build_sub | 3 | 1 | False | False (0) | 1 | None | WHO Child Growth Standards |

Scope caveat: `page_bands` is called with its default `section_repair_bands=None`, so the census
covers the `section_repair=False` builds only (as asked); the section-repair rebuilds a full
`compile_document` performs are not in it.

---

## M3 — history and the tests that pin the guard

```
$ git log -S _under_resolved --oneline
d588412 R225 closed: the resolution test ships, and the fallback it retires is recorded (#221)
$ git log -S _word_column_count --oneline
d588412 R225 closed: the resolution test ships, and the fallback it retires is recorded (#221)
523e00b The gate asks about unread ink, and the lineage chains (R225 arm B)
```

- **`d588412`** (2026-09-14, PR #221) introduced both into `src/iladub/etkl/compile.py`
  (`git show d588412 | grep -n "^[+].*_under_resolved\|^[+].*def _word_column_count"` -> diff
  lines 879 `+def _word_column_count`, 924/927/944 `_under_resolved`). Commit subject: *"R225
  closed: the resolution test ships"*; body: *"D1 (the RELOCATED placement) gives
  `_build_ruled_band` a resolution test ... Relocated (after `refine_rule_columns`) because that
  is the only placement that keeps R13's closure intact. Ruled by the maintainer 2026-09-14."*
- **`523e00b`** (2026-09-14, R225 arm B / D2) matches `-S _word_column_count` only in DOCS:
  `git show 523e00b | grep -n "^[+-].*_word_column_count"` -> two `+` lines, both prose
  (*"`54c0edf`, verified: `_word_column_count` gone"*, *"D1 is ... a new `_word_column_count`
  helper"*) — D1 was reverted on that branch and recoverable from `3ee9495`. It is an ancestor of
  HEAD but did not ship the helper.
- **Residue:** R225 (closed) — `docs/superpowers/residues.md:396` / `residues-closed.md:132`:
  *"A band whose only intersecting rules are the page BORDERS is re-bucketed into one column,
  fusing every row into a single token."*
- **Spec:** `docs/superpowers/specs/2026-09-14-the-gate-not-the-predicate-design.md` (R225 arm B;
  D1 in § 4; the placement defect and relocation in § 1e, cited by the source comment as
  "spec § 1e").

### Tests that pin the guard

```
$ grep -rn "_under_resolved\|_word_column_count\|under-resol\|under_resol" tests/
(no output)
$ grep -rniE "under.?resol" tests/
(no output)
```

**Zero test files name `_under_resolved`, `_word_column_count` or "under-resol".** Tests that
cite the guard as "R225 D1" / "resolution test" in prose
(`grep -rn -e R225 -e "resolution test" -e "resolves at least" -e border-only tests/ | grep '\.py:'`,
enclosing function located by awk):

| file:line | enclosing test / fixture |
|---|---|
| `tests/etkl/test_read_band_books_every_word.py:101,113` | `test_no_band_books_ink_it_does_not_hold_on_the_fallback_page` (docstring: "RETIRED 2026-09-14 (R225 D1)") |
| `tests/etkl/test_fallback_region_books_and_names.py:81` | fixture `adopting_doc` (I1/I2 re-pointed at adoption, R225 D1); tests `test_the_adopted_grid_region_books_the_ink_it_claims`, `test_an_untyped_grid_is_not_adopted`, `test_the_adopted_grid_region_names_the_table_it_asserted` added in d588412 |
| `tests/etkl/test_datagrid.py:901` | `test_fallback_fires_only_where_the_page_produced_nothing_at_all` |
| `tests/etkl/test_datagrid.py:992` | `test_fallback_output_passes_full_shacl_through_the_production_path` |
| `tests/etkl/test_datagrid.py:1034` | `test_an_unread_table_page_no_longer_scores_perfect` |
| `tests/etkl/test_run_merge_seam.py:215-240, 325` | module constant `D1_MOVES` (bfs p5 16->180, ons p7 0->112, ons p8 0->12), read by `test_o3_no_page_loses_asserted_ink_to_a_merge` |
| `tests/etkl/fixtures.py:2176, 2227` | fixtures `border_only_grid_pdf`, `isolated_rows_grid_pdf` |

Spec § 1e also names `tests/etkl/test_header_confirmed_refinement.py::test_confirmed_split_reaches_the_grid_end_to_end`
as the R13 test the unrelocated D1 broke (spec lines 162, 181) — i.e. it pins that the guard does
NOT refuse after refinement, not that it refuses.

### Falsification run (guard disabled)

To find out which of the grep-listed tests actually fail when the guard is gone, a scratch pytest
plugin `guardoff.py` sets `compile._word_column_count = lambda sub: None`. That makes
`_under_resolved` False AND skips the post-refinement `len(col_xs) - 1 < _word_cols` check, so
both applications of D1 are off. `falsify.sh` ran each target serially, guard on and then off:
`PYTHONPATH="src:$SP" .venv/bin/python -m pytest -q -x -p no:cacheprovider [-p guardoff] <target>`.

```
                                                                         guard ON          guard OFF
tests/etkl/test_header_confirmed_refinement.py                            4 passed          4 passed
tests/etkl/test_read_band_books_every_word.py                             7 passed          7 passed
tests/etkl/test_fallback_region_books_and_names.py                       10 passed (561s)  10 passed (485s)
test_datagrid.py::test_fallback_fires_only_where_the_page_produced_nothing_at_all   1 passed   1 passed
test_datagrid.py::test_fallback_output_passes_full_shacl_through_the_production_path 1 passed  1 passed
test_datagrid.py::test_an_unread_table_page_no_longer_scores_perfect                 1 passed  1 passed
```

CONTROL, showing the plugin is live and that it changes T1 (`$SP/test_guardoff_ctl.py`, run with and without `-p guardoff`):

```
=== plugin: '-p guardoff'
T1 line0 cells: ['PORT', 'WHEAT', 'MAIN WHEAT GRADES', 'BARLEY', 'CANOLA', 'OTHER', 'TOTAL']
2 passed
=== plugin: ''
T1 line0 cells: ['PORT', 'WHEAT', 'MAIN', 'WHEAT', 'GRADES', 'BARLEY', 'CANOLA', 'OTHER', 'TOTAL']
E  AssertionError: assert '_word_column_count' == '<lambda>'   (and the T1 assertion fails)
```

**Fact:** none of the 24 tests above fails with the guard disabled, and the control confirms the
patch took effect. With the guard off, T1's header re-buckets to exactly the 7 cells
`PORT | WHEAT | MAIN WHEAT GRADES | BARLEY | CANOLA | OTHER | TOTAL`. **NOT RUN:**
`tests/etkl/test_run_merge_seam.py::test_o3_no_page_loses_asserted_ink_to_a_merge` (it holds
`D1_MOVES` and is corpus-gated with 27 pages) and the full suite. If any test pins the refusal, it
is outside the set measured here and nothing names it by symbol.
