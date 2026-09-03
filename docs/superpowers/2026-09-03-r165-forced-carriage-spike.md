# R165's forced-carriage spike — RUN, and refuted: loop M's seam cannot carry a header onto apple's section bands

**What this is:** the prediction the R161 handoff's part 5 graded PROPOSED and ordered run before
anything was designed: *"on apple p0, handing band 3 the header reading band 2 asserted — through
`compile_tables(..., carried_header_roles={3: <band 2's reading>})` — makes band 3 pass `CoverageShape`
and assert."* It was run, on all three apple pages, with a committed instrument. It is a refutation of
the **mechanism** R165's remedy named; it **confirms** R165's diagnosis. It builds no remedy.

**Result in one line:** band 3 stays `escalated / REGION_TILING_FAILED` under forced carriage on every
page, asserted tokens unchanged (48 → 48, 14 → 14, 3 → 3), for three independent reasons — the
reading the prediction wanted to carry does not exist, the seam refuses the band that would receive it,
and on p2 the header band itself escalates. The diagnosis stands: every escalated section band's only
header row is its own section heading in the stub column.

**Doc impact: none.**

---

## 1. Method

`scripts/forced_carriage_spike.py`, committed by this loop. Per page: `compile_tables` for the band
census (verdict, cells, table URI, whether a `CarriedHeaderReading` was produced, and for every
asserted table the label text of its first column header, `-lc0`); for every escalated band, what
`headers.header_rows_of` finds as its header rows; then the forced compile. Because band 2 produced no
reading (§ 2.1), the script hand-builds one from band 2's first three lines over band 3's leaf grid —
signatures keyed by `regions.column_of`, exactly `ruledroles._row_signature`'s notion — with the roles
`continuation, continuation, leaf`, the most permissive block the seam accepts (a carried vector may not
contain `level`). Its two pure pieces are pinned in `tests/test_forced_carriage_spike.py`, with the
falsifying twin: the same seam **matches** a receiving band that redraws the whole block.

```
PYTHONPATH=. .venv/bin/python scripts/forced_carriage_spike.py corpus/financial/apple-fy2026q3-statements.pdf {0,1,2}
```

Measured 2026-09-03 on `main` at `5d7e47d`.

## 2. Readings, verbatim

```
=== corpus/financial/apple-fy2026q3-statements.pdf page 0: baseline census
  band 0: ignored   cells=  0 table=None header_reading=None | Apple                                            I
  band 1: ignored   cells=  0 table=None header_reading=None |       CONDENSED   CONSOLIDATED   STATEMENTS   OF O
  band 2: asserted  cells= 28 table=mtable2 header_reading=None lc0=[] |                                           Three Mo
  band 3: escalated cells=  0 table=None header_reading=None header_rows=[['Operating expenses:']] | Operating expenses:
  band 4: asserted  cells= 20 table=table4 header_reading=None lc0=['Operating income'] | Operating income                           35,695 
  band 5: escalated cells=  0 table=None header_reading=None header_rows=[['Earnings per share:']] | Earnings per share:
  band 6: escalated cells=  0 table=None header_reading=None header_rows=[['(1) Net sales by reportable segment:']] | (1) Net sales by reportable segment:
  band 7: escalated cells=  0 table=None header_reading=None header_rows=[['(1) Net sales by category:']] | (1) Net sales by category:
=== band 2 header_reading: None
=== band 3 leaf grid boundaries: [50.0, 300.0, 364.4, 430.4, 496.4, 562.4]
=== band 3 header_rows_of: [['Operating expenses:']]
    synthetic row role='continuation' signature=((2, 'Three Months Ended'), (4, 'Nine Months Ended'))
    synthetic row role='continuation' signature=((1, 'June 27,'), (2, 'June 28,'), (3, 'June 27,'), (4, 'June 28,'))
    synthetic row role=None signature=((1, '2026'), (2, '2025'), (3, '2026'), (4, '2025'))
=== carried_roles_for(synthetic, band 3 header rows, band 3 grid) -> None
=== forced compile: band 3 verdict=escalated cells=0 reason=REGION_TILING_FAILED
=== asserted tokens: baseline=48 forced=48
=== corpus/financial/apple-fy2026q3-statements.pdf page 1: baseline census
  band 0: ignored   cells=  0 table=None header_reading=None | Apple                                            I
  band 1: ignored   cells=  0 table=None header_reading=None |         CONDENSED     CONSOLIDATED     BALANCE   S
  band 2: asserted  cells= 14 table=mtable2 header_reading=None lc0=[] |                                                   
  band 3: escalated cells=  0 table=None header_reading=None header_rows=[['Non-current assets:']] | Non-current assets:
  band 4: escalated cells=  0 table=None header_reading=None header_rows=[['LIABILITIES AND SHAREHOLDERS’ EQUITY:']] |                         LIABILITIES AND SHAREHOLDE
  band 5: escalated cells=  0 table=None header_reading=None header_rows=[['Non-current liabilities:']] | Non-current liabilities:
  band 6: ignored   cells=  0 table=None header_reading=None | Commitments and contingencies
  band 7: escalated cells=  0 table=None header_reading=None header_rows=[['Shareholders’ equity:']] | Shareholders’ equity:
=== band 2 header_reading: None
=== band 3 leaf grid boundaries: [52.6, 315.6, 492.6, 562.2]
=== band 3 header_rows_of: [['Non-current assets:']]
    synthetic row role='continuation' signature=((1, 'June 27,'), (2, 'September 27,'))
    synthetic row role='continuation' signature=((1, '2026'), (2, '2025'))
    synthetic row role=None signature=((0, 'ASSETS:'),)
=== carried_roles_for(synthetic, band 3 header rows, band 3 grid) -> None
=== forced compile: band 3 verdict=escalated cells=0 reason=REGION_TILING_FAILED
=== asserted tokens: baseline=14 forced=14
=== corpus/financial/apple-fy2026q3-statements.pdf page 2: baseline census
  band 0: ignored   cells=  0 table=None header_reading=None | Apple                                            I
  band 1: ignored   cells=  0 table=None header_reading=None | CONDENSED     CONSOLIDATED      STATEMENTS     OF 
  band 2: escalated cells=  0 table=None header_reading=None header_rows=[['Nine Months', 'Ended'], ['June 27,', 'June 28,']] |                                                   
  band 3: escalated cells=  0 table=None header_reading=None header_rows=[['Operating activities:']] | Operating activities:
  band 4: escalated cells=  0 table=None header_reading=None header_rows=[['Investing activities:']] | Investing activities:
  band 5: escalated cells=  0 table=None header_reading=None header_rows=[['Financing activities:']] | Financing activities:
  band 6: asserted  cells=  3 table=table6 header_reading=None lc0=['Increase in cash, cash equivalents, and restricted cash and cash equivalents'] | Increase in cash, cash equivalents, and restricted
  band 7: escalated cells=  0 table=None header_reading=None header_rows=[['Supplemental cash flow disclosure:']] | Supplemental cash flow disclosure:
=== band 2 header_reading: None
=== band 3 leaf grid boundaries: [50.0, 417.2, 488.7, 562.4]
=== band 3 header_rows_of: [['Operating activities:']]
    synthetic row role='continuation' signature=((1, 'Nine'), (1, 'Months'), (2, 'Ended'))
    synthetic row role='continuation' signature=((1, 'June'), (1, '27,'), (2, 'June'), (2, '28,'))
    synthetic row role=None signature=((1, '2026'), (2, '2025'))
=== carried_roles_for(synthetic, band 3 header rows, band 3 grid) -> None
=== forced compile: band 3 verdict=escalated cells=0 reason=REGION_TILING_FAILED
=== asserted tokens: baseline=3 forced=3
```

## 3. Why forced carriage cannot fire — three independent refusals

### 3.1 The reading the prediction named does not exist

`band 2 header_reading: None` on all three pages. Loop M's seam is fed by exactly one producer —
`ruledroles.resolve_ruled_header_rows`, loop L's ruled header law (`compile.py:893-898` is the only
call site that passes `carried=`, and `RegionReport.header_reading` is set only on that branch). Apple's
band 2 never takes it: on p0 and p1 it asserts through the **matrix** branch (`mtable2`;
`classify_hierarchical(band 2)` is `None`, so loop L is never even tried), and on p2 it **escalates**
(header rows `['Nine Months', 'Ended'], ['June 27,', 'June 28,']` — not read at all). There is no
`CarriedHeaderReading` anywhere on the apple document. The handoff's "what `<band 2's reading>` has to be
is the first thing to MEASURE" was the right question: the answer is *nothing*.

### 3.2 The seam matches a redrawn header; it never supplies a missing one

`carried_roles_for` (`ruledroles.py:384`) requires *every* header row of the receiving band to have an
exact per-column text counterpart in the carried block, in order, ending on the carried leaf. The
receiving band's header rows, measured: `[['Operating expenses:']]`, `[['Non-current assets:']]`,
`[['Operating activities:']]` — the section heading, one cell in the stub column, which matches nothing
in any header block. So even the hand-built, most-permissive reading returns `None`, the derivation
fallback runs exactly as it did standalone, and the tiling membrane refuses on the same
`CoverageShape`. This is by design: the seam was built for a continuation page that **redraws** the
header (GrainCorp), and its refusal is the guard against asserting one table's header over another's
rows (review finding F3). Apple's section bands do not redraw anything.

### 3.3 The diagnosis is confirmed at the mechanism

`header_rows_of` on every escalated section band returns exactly one row, the section heading, in
column 0. That row is the band's whole header; leaf columns 1–4 are covered by no header node, which is
`CoverageShape`'s message verbatim. The coverage gap **is** "no column header" — R165's diagnosis is
right; its remedy (reuse loop M's seam) is what this spike refutes.

## 4. What the successor is NOT, and what it may be — PROPOSED, not designed here

The handoff's conditional read: *"if it does not [pass], the coverage gap is not 'missing header' and
the loop this handoff imagines is not the loop to run."* Half of that is wrong: the gap is exactly a
missing column header (§ 3.3). What is not the loop to run is *any* loop that routes through
`carried_header_roles` — that seam has no input on apple and refuses its output.

Two candidate designs, **both PROPOSED, neither measured**, for the fresh session that specifies R165
with R160 (R165's row says why they are one decision):

- **(a) Do not split.** R165's own measurement says all six ruled bands on p0 (five on p2) share one
  `tab:ruleXsSignature` — the author drew one grid. And the matrix reader **already reads section
  headings as row headers inside a band**: `mtable2` on p0 carries `rh0..rh8` = `Net sales:`, `Products`,
  `Services`, `Total net sales`, `Cost of sales:` … — a section heading in the stub column is a row
  header to it, not a header row. If the band boundary did not fall at every section heading, the
  matrix branch would be handed the whole statement under its one column header. The seam is then
  `page_bands`' band split, not carriage.
- **(b) Carry the matrix header.** A second producer for a carried block, from `classify_matrix`'s
  column-header tree, plus a receiving path that treats the section heading as a row header rather than
  a header row. More code than (a), and it keeps the split (a) says is the defect.

The prediction to run first, and it is cheap: **does apple p0 compile as one matrix if bands 2–7 are
handed to `compile_tables` as one band?** That is a `page_bands` question, not a carriage one.

## 5. A second defect, measured on the way — R166

Two apple bands **assert a data row as their column header**:

| page / band | table | asserted header (`-lc0`) | first body row |
| --- | --- | --- | --- |
| p0 band 4 | `table4`, `tab:RecordTable`, 20 cells | `Operating income` (with `35,695 / 28,202 / 122,432 / 100,623` as h1–h4) | `Other income/(expense), net` |
| p2 band 6 | `table6`, `tab:RecordTable`, 3 cells | `Increase in cash, cash equivalents, and restricted cash and cash equivalents` | — |

This is a false assertion **inside the membrane**: the record-table reader takes the band's first
line as its header row and the tiling oracle is satisfied because the "header" covers every column.
Numbers are asserted as column labels. The R161 handoff's part 4 flagged this as unverified; it is now
measured, and raised as `R166`. It is also the reason "asserted tokens 48" on p0 overstates what is
correctly read: 20 of those cells sit under a header that is a data row.

## 6. What this does NOT establish

- Neither candidate design in § 4 was tried. The one-band prediction is unrun.
- The hand-built reading on p1 took `ASSETS:` as its leaf (the script takes band 2's first three
  lines; on p1 the third line is a section heading). It does not affect the result — the receiving row
  `Non-current assets:` matches nothing in any block — but the p1 synthetic block is not band 2's
  header.
- Whether the record-table reader's first-line-as-header is a defect on any *other* corpus document
  was not censused; R166 records apple's two bands only.
