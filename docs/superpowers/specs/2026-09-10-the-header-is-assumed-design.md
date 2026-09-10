# Spec — the header row is ASSUMED, not derived: R166 is a corpus-wide class

**Residue:** [[R166]] (`docs/superpowers/residues-open.md:119`), its surviving p2 half.
**Question inherited:** `docs/superpowers/2026-09-09-the-nil-glyph-handoff.md` § 5b, graded
PROPOSED — *"what decidable signal separates apple p2 band 6 from a year-headed table?"*
**Written 2026-09-10**, off `4905355`, branch `r166-the-header-is-assumed`.

**Doc impact: none.** No published term changes; the instrument and the census are evidence.

---

## 1. The subject, reproduced at HEAD — and R166 names only half the mechanism

apple p2 band 6 at `4905355`, `scripts/header_row_census.py`:

```
apple-fy2026q3-statements.pdf p2 band6 kind=RECORD_TABLE aligned=yes lines=2 contrast=NO corner=NO
    labels=['Increase in cash, cash equivalents, and restricted cash and cash equivalents', '3,610', '6,326']
    row1  =['Cash, cash equivalents, and restricted cash and cash equivalents, ending balances', '$ 39,544', '$ 36,269']
```

R166's row says *"the record-table reader takes the band's first line as the header row"*. That is
true, and it is not the whole mechanism. **The first line is named `tab:HeaderWord` in PYTHON,
before any query runs:**

```
src/iladub/etkl/classifygraph.py:52-57
    if grid is not None and band.lines:
        header = band.lines[0]
        for i, w in enumerate(sorted(header.words, key=lambda w: w.x0)):
            u = _EV["hw-%d" % i]
            g.add((u, RDF.type, TAB.HeaderWord))
```

`classify-kind.rq` then derives `tab:RecordTableKind` from `?nhw = ?nc && !?mis` — the count of
`tab:HeaderWord`s equals the leaf-column count, and each sits strictly in its own column. **The
evidence graph names the conclusion the query is asked to derive.** Nothing in the branch asks
whether line 0 is a header. `header_body_split` — the one derivation in this codebase that
locates a header/body boundary from evidence — **does not decide the label row here**:
`regions.classify` → `assign_cells` take row 0 by position, and `assert_record_region` turns every
`cell.row == 0` into a `tab:LabelCell`. (The split IS computed on a ruled band, at
`src/iladub/etkl/compile.py:172` inside `_build_ruled_band`, but it answers a different question —
whether a *candidate column boundary* falls in the header region — and its answer never reaches
the label row. Measured by reading that call site, not assumed: its result flows only into
`body_top`, the char filter for boundary confirmation.)

This is the failure `header-row-role.rq` corrected in its own review round 1, in that file's words:
a role reached by elimination rather than by *"a mark the author made"*. Here it is reached by
position.

## 2. The population, MEASURED corpus-wide 2026-09-10 at `4905355` — it is 12 bands, not 2

`PYTHONPATH=. .venv/bin/python scripts/header_row_census.py` over all 7 documents / 27 pages.
Twelve bands reach the **record-table branch** (`region.kind is RegionKind.RECORD_TABLE`) and
assert a `tab:RecordTable` with a label row: eleven upright, whose labels are band line 0, and one
**transposed** (bfs p5 band 13, `ttable13`), whose labels are grid column 0 after the axis flip —
the same `classify-kind.rq` gate, the same by-position choice, one axis over
(`src/iladub/etkl/compile.py:820-841`; the label column is `by_rc[(k, 0)]`, stated at `:874`). The judgement column is a READING,
made by comparing the asserted `labels` against the `row1` beneath it and against the page text
(`pdfplumber.extract_text`); the two rows are printed for every band so the reading can be checked.

| # | document | page | band | cols | the asserted label row | is it a header? |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | cbh-stem | 0 | 9 | 3 | `Stock at Port (Main Storage Area) as at 29/07/2026` / `PORT MAINTENANCE SHUTDOWN DATES - 2026` / `1,951,264` | **NO** — two page titles and a total. The REAL header is `row1`, joined into one cell: `PORT WHEAT MAIN WHEAT GRADES BARLEY CANOLA OTHER TOTAL` |
| 2 | graincorp-capacity | 0 | 3 | 16 | `2025/26` `August 2nd Half` `0` `N` `10,000` `Y` … | **NO** — a data row; `row1` is the next one (`September 1st Half` …) |
| 3 | apple | 2 | 6 | 3 | see § 1 | **NO** — R166's surviving half |
| 4 | bfs | 5 | 13 | 9 | `Tessin 354 023 2 390 3 488- 1 098 4 883- 145 357 720` … | **NO** — the TRANSPOSED one: its labels are column 0, whole data rows each joined into one cell. The census reports `aligned=no` here, correctly: line 0 is not where these came from |
| 5 | bfs | 6 | 2 | 9 | `Grandes régions` `Total` `0-19 ans` `20-39 ans` … | **YES** — but `row1` is `Cantons` / `dépendance` / `dépendance des`: the header's own wrapped continuation lines, asserted as a data row |
| 6 | bfs | 6 | 4 | 9 | `Région lémanique` `1 736 124` `365 836` … | **NO** — a regional subtotal row; `row1` = `Vaud` … |
| 7 | bfs | 6 | 5 | 9 | `Espace Mittelland` `1 944 753` … | **NO** — same |
| 8 | bfs | 6 | 6 | 9 | `Suisse du Nord-Ouest` `1 225 762` … | **NO** — same |
| 9 | bfs | 6 | 8 | 9 | `Suisse orientale` `1 237 469` … | **NO** — same |
| 10 | bfs | 6 | 9 | 9 | `Suisse centrale` `854 922` … | **NO** — same |
| 11 | who | 0 | 4 | 13 | `1:` `1` `13` `0.0563` `9.8749` … | **NO** — `row1` is `1:` `2` `14` `0.0487` …, the next month |
| 12 | who | 1 | 4 | 13 | `3:` `1` `37` `-0.0729` … | **NO** — same |

**11 of 12 label rows are not headers. The 12th has true labels and a false body. Zero of the
twelve are read correctly.** The whole population asserts **111 `tab:LabelCell`s, of which 73 are
numeric** (`headers.is_numeric` after removing the thin-space group separators) — 73 measured
values asserted as column labels, and excluded from the entry count by
`assert_record_region`'s `cell.row == 0` branch (`src/iladub/etkl/holon.py:129`, the
`tab:LabelCell` emission at `:139`).

R166's row says *"Not censused beyond apple"*. Censused: apple is 1 of 11, and bfs p6 alone is 5.

## 3. The question § 5b asked, ANSWERED: no in-band signal exists — one arm absent wherever it would have to fire, one impossible by construction

**(a) Type contrast — measured 0 of 12.** No band in the population has a single column where
row 0's normalised datatype family (`tab:inDatatypeFamily`, the family `header-body-split.rq`
itself reads) differs from the modal family of the rows below it. This is the census's
`contrast=` column, `NO` on all twelve. It is also the arm the R167 handoff refuted from an
argument (`is_numeric('2023')` is `True`, so a year header is `tab:Quantity` exactly as a data
row is); the census refutes it from the other side — the signal is not merely wrong, it is
**absent everywhere it would have to fire**.

**(b) The blank corner — IMPOSSIBLE, not absent, and refused TWICE OVER.**
`tab:RecordTableKind` is `?nhw = ?nc && !?mis`: as many header words as leaf columns, each
strictly inside the column of its own left-to-right order. A band whose row 0 leaves a column
empty fails **both** clauses, and the second alone is enough — measured on the fixture in
`tests/etkl/test_header_row_is_assumed.py`, a row 0 of `('', 'Value', 'Unit')` over a populated
first column gives `ncols=3 nhw=2 firstBad=0`, so weakening the count to `?nhw <= ?nc` leaves the
band `tab:UnsupportedTableKind` anyway (that weakening was RUN as a falsification and did not turn
the test red; disabling both clauses did). So *no* band on this path can ever carry the one mark
that most plainly evidences a header row — an empty stub corner over a populated stub column. The
census's `corner=` column is `NO` on all twelve, and it can never read otherwise.

**(c) The 1:1 alignment test is VACUOUS on a ruled band.** `Line.words` carries two granularities
([[R162]]): a pdfplumber WORD on an unruled band, a ruled CELL on a ruled one. Measured at
`4905355` on four of the population's bands: bfs p6 b4 (`vrules=15`, line 0 = 9 "words", the first
being `Région lémanique`), apple p2 b6 (`vrules=18`, 3), cbh p0 b9 (`vrules=26`, 3), graincorp
p0 b3 (`vrules=505`, 16). Where the author drew the columns, **every** row aligns 1:1 with them by
construction, so the only test standing between a data row and the `HeaderNode` cannot fail. (who
p0 b4 is the unruled counter-case, `vrules=0`: its 13 space-separated words happen to be one per
column, which is what a clean numeric data row looks like.)

**What that leaves.** For bfs p6 the true header is on **another band of the same page** (band 2,
row 5 of the table above); for apple p2 band 6 it is in another region entirely ([[R165]]). The
separating signal is therefore **not in the band**, and no amount of in-band format reading will
find it. The remedy is cross-band (carriage / one-band merge — [[R165]]'s family, whose p2 arm is
refused on [[R162]]) or NEURAL under an oracle (CLAUDE.md §8) — never an in-band axiom. § 5b
predicted this outcome as one of two and it is the one that measured true.

## 4. What this loop does NOT do, and why

**It does not change compiler behaviour.** The change the census argues for — refusing a
record-table reading whose label row carries no evidence — refuses **12 of 12** today, moves 111 label
cells plus every entry beneath them from asserted to escalated, and re-baselines every corpus
score and adoption pin in the suite. That is a design decision with a corpus-wide blast radius,
and it belongs to a plan written in a fresh session against this spec, not to the session that
measured it. § 5b of the handoff licenses this shape explicitly: *"saying so with the measurement
is a complete loop outcome, not a failure."*

**It does not close [[R166]].** R166's closure condition is that both named bands *"assert under a
non-numeric header or escalate"*, and neither has. The row is amended with the census instead: the
class is corpus-wide, the mechanism is `classify_evidence`, and the in-band arms are closed.

**It does not touch [[R162]], [[R165]] or [[R78]].** The cross-band remedy is R165's; the
word-granularity seam is R162's.
