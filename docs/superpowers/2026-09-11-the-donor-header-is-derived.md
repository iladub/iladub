# The donor's header is derived — § 5c run on all seven documents, § 5d weighed

**Date:** 2026-09-11, on `main` at `808aa7a`. **Loop shape:** a MEASUREMENT loop against
`2026-09-10-the-donated-reading-tiles-handoff.md` § 5c and § 5d, run before the donation plan they
gate. No compiler behaviour changes. One instrument committed: `scripts/donor_header_criterion.py`.
**Doc impact: none.**

## 1. The proposition, and the population it was run on

§ 5c proposed, from ONE page: *a donor's line 0 is its header iff the page datagrid
(`derive_data_grid`) refuses that page line `HeterogeneousColumn/every-measure`.* It is run here on
the whole R166 census — the 12 asserted `tab:RecordTable` readings of
`docs/superpowers/specs/2026-09-10-the-header-is-assumed-design.md` § 2, whose "is it a header?"
column is a reading made from the printed rows. The band's line 0 is re-identified among the page's
text lines by its whitespace-stripped ink, never by index ([[R202]]; band words are word groups,
`1 736 124` is one word, so raw word-tuple equality found 0 of 12).

```
PYTHONPATH=. .venv/bin/python scripts/donor_header_criterion.py
```

| # | document | page | band | census reading | page line | datagrid verdict on that line |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | cbh-stem | 0 | 9 | NO | 75 | body row |
| 2 | graincorp-capacity | 0 | 3 | NO | 4 | body row |
| 3 | apple | 2 | 6 | NO | 37 | body row |
| 4 | bfs | 5 | 13 | NO (transposed) | 54 | body row |
| 5 | bfs | 6 | 2 | **YES** | 3 | **refused `HeterogeneousColumn/every-measure`** |
| 6-10 | bfs | 6 | 4, 5, 6, 8, 9 | NO | 8, 12, 18, 23, 31 | body row, all five |
| 11 | who | 0 | 4 | NO | 17 | body row |
| 12 | who | 1 | 4 | NO | 16 | body row |

**12 of 12 agree with the census reading in the forward direction**: the one true header is
refused `every-measure`, and every one of the 11 false label rows is placed as a body row of the
page's grid. `derive_data_grid` returned a grid on all 7 pages (none returned `None`).

## 2. The converse is REFUTED — "refused every-measure" does not mean "header"

The same run prints every `every-measure` refusal on each page. Most are headers: graincorp p0
line 3 (`Year | Elevation | Period | Mackay …`), who p0/p1 line 3 (`Year: | Month | Month | L | M
| S …`), cbh lines 8/24/47/67 (the repeated `VNA # Vessel Name …` boxhead) and 76 (`PORT | WHEAT |
MAIN …`), bfs p5 lines 2-4 and 30-31 (a multi-line boxhead). Two classes are not:

- **Page titles.** bfs p5 line 1 (`T1 Bilan de la population …`) and bfs p6 line 1 (`T3
  Population résidante permanente par classe d'âge …`) are refused `every-measure` exactly as the
  header beneath them is.
- **Rows of a SECOND table under a different column universe.** cbh p0 lines 77-80 (`ALB |
  129,183 | APW1/ASW9/AWW1 | 27,023 …`, then ESP, GER, KWI) are data rows of the port-stock table,
  refused because the page's universe is the vessel table's 20 decorated columns.

So the "iff" is one-directional. **What donation needs is the forward direction only**, applied to
the donor: *donate under the donor's line 0 iff the page datagrid refuses that line
`every-measure`; a body-row verdict, any other refusal, or no datagrid on the page refuses the
donation* (§7: the reading escalates rather than carrying a header nobody derived). A title as a
donor's line 0 is the case the forward direction cannot separate; no donor in the corpus has one,
and whether a title line can sit inside a wholly-drawn grid at all is not measured here.

**The corpus has exactly one donor** — bfs p6 band 2, the unique donor of 5 bands
(`scripts/grid_agreement_census.py`, spec `2026-09-10-the-grid-the-author-drew-design.md` § 3). The
derivation is therefore exercised on 1 donor and 11 non-donor data rows, and it is the same
`tab:ColumnHomogeneity` judgement the datagrid already ships (`datagrid.py:507-523`, the universal
quantifier over occupied measure columns, evidence-positive on present non-numeric ink).

**Wider than R203.** The criterion also refuses the assumed header of every other censused band:
graincorp p0 band 3, who p0/p1 band 4, apple p2 band 6, cbh p0 band 9, bfs p5 band 13 — all 11 of
[[R166]]'s false label rows are body rows of their page's grid. R166's widening said the
separating signal *"is not in the band at all"* and the remedy is cross-band; this is that signal,
at page scope, already derived. It is not this plan's to ship (six documents re-baseline), and is
handed on as a proposition in the handoff.

## 3. § 5d weighed: adoption is NOT the cheaper repair for bfs p6

Measured this session, not inferred:

- **Adoption cannot fire on bfs p6 as shipped.** Both gates require `asserted_total == 0`
  (`compile.py:1251` fallback, `:1323` adopt) and the document-level ASK refuses any page carrying
  one `tab:EntryCell` (`vocab/queries/adoption-candidate.rq`). bfs p6 asserts 222 cells.
- **Opening it is [[R160]]'s reader-authority ruling, and the maintainer's.** R160's closure needs
  *"a document where a page both adopts and asserts"* and its 2026-09-05 census said none exists.
  **bfs p6 now is that instance**: the band reader asserts 222 cells with 45 false labels, the
  whole-page reader reads 9 columns × 32 rows = 288 entries with the header refused and [[R205]]'s
  two lost rows included (handoff `2026-09-10-the-donated-reading-tiles` § 2). Appended to R160's
  row; not ruled here.
- **The datagrid emits entries only.** `datagrid.py`'s docstring: *"This module derives the
  entries only. Nothing here reads a header."* Under adoption, band 2's four header lines are
  residue and the page carries 288 entries under NO column labels; under donation it carries 267
  under the author's own labels. Donation keeps the categories; adoption drops them.

**Ruling for the plan session, recorded nowhere but this file and the handoff:** grid donation
stays the arm. R205's two rows stay donation's known loss, and R205's own closure — a re-cut
against the accepted donor grid — is the point at which they become reachable.

## 4. What the plan's decision 1 must now add

Decision 1 (handoff `2026-09-10-the-grid-the-author-drew` § 5a) puts the AXIOM in
`sectiongraph.run_evidence`, which emits per-band nodes and `tab:prevBandIndex` only
(`sectiongraph.py:223-256`). The datagrid's refusal is a PAGE-line fact, and today it reaches a
graph only through `emit_data_grid` under the fallback/adopt gates. The plan must therefore carry
the refusal into the page evidence graph as a fact on the donor's line 0 — `derive_data_grid` is
already classified PROCEDURAL/AXIOM in its own docstring — with the band-line ↔ page-line identity
made by ink, as this instrument does, never by index.

## 5. Unverified or assumed

- The forward direction is exercised on one donor. A second document with a ruled donor is the
  test that would falsify it as a donation licence.
- Whether a page title can be a donor's line 0 (inside a wholly-drawn grid) is not measured.
- `derive_data_grid`'s cost at page scope inside the ordinary compile is not measured; it already
  runs once per candidate page under adoption.
- No suite run; the instrument is corpus-gated ([[R173]]) and has no CI test.
