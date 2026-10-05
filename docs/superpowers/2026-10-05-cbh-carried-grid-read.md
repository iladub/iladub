# Evidence + handoff: cbh's carried grid read against the page — one new defect, R74's premise stale (2026-10-05)

**Serves:** prog:criterion:etkl:03 — the "carried grid read against the source page" that the 2026-10-05 cbh adjudication names as one of two things standing between cbh and acceptance.

**Doc impact: none.**

Written under the 50K originating floor (40,158 working tokens at the gate, read off `plimslop preflight`). Part 5 was written first. The measurements ran in a read-only subagent at `main` `4d07b7c`; the read of the header rules (§ 2.3) is this session's own.

## 5. Next action (written first)

- **Proposed — a spec for [[R289]], in a fresh session.** The hold cannot be lifted on this read: 16 header words are carried as data (§ 2.1), and the grounding test counts the four rows they form as records. The prediction to RUN before any design is written: *the `Accepted`/`Completed` line becomes body because its ink crosses the header box's bottom rule.* On p0 the header box is bounded by full-width rules at y = 105.0 and 118.7. The line's ink spans y 113.5–119.5, so its centre (116.5) is inside the box but its bottom is 0.8 pt below the rule. The synthetic fixture `tests/etkl/fixtures.py::_draw_section` draws a two-line header wholly inside its box, and `tests/etkl/test_grid_region.py` passes the welded `Time Nom Accepted` on it. **If this is wrong, the next session finds out in minutes**: find which reader produces `p0/r2#htable1`'s labels (the compile reports `adopted=()`, so it is not the data grid) and where that reader decides header-vs-body. If that decision is not a rule-containment test, the prediction is refuted and the seam is elsewhere. Two things the spec must NOT do: tune a tolerance on the 0.8 pt (CLAUDE.md § 8; ink-centre membership in the author's drawn box is an AXIOM, not a constant, but that is the spec's argument to make), or weaken [[R258]]'s split (`(7,5) 'Accepted'` and `(7,14) 'Completed'` are its "first body row" addresses, which is this defect seen from the other side).

## 1. What was run

- Compile: `compile_document("corpus/ag-trade/cbh-stem-2026-08-03.pdf")` at `4d07b7c`. Score 1.0, 878 asserted / 0 escalated tokens, 13,698 triples, `adopted=()`.
- Independent instrument: poppler `pdftotext -bbox` (1,244 words) and `pdftotext -layout`; drawn rules from pdfplumber `page.rects` / `page.lines`. The only pipeline input is the compiled graph under test. Both extractors put `ALB` at (52.8, 699.66).
- `pytest -q tests/etkl/test_datagrid.py -k cbh_p0` → `4 passed, 55 deselected`.
- `pytest -q tests/test_corpus.py -k cbh -rA -s` → `2 passed, 9 deselected in 54.39s`. It prints `score=1.0000 pages=1 chains=[4, 1, 1]` and `records=57 grounded=183 still-quarantined=749`.
- The measurement scripts were scratch and are **not** kept (see § 4).

## 2. Findings

### 2.1 NEW: each roster's `r0` is header ink carried as data → [[R289]]

- Each of the four port rosters (`p0/r2#htable1`, `htable3`, `htable5`, `htable7`) carries a row `r0` of four `tab:EntryCell`s: `Accepted` (c4), `Accepted` (c5), `Completed` (c18), `Completed` (c19). That makes 16 header words carried as data, and 4 rows with no vessel.
- On the page these words are the bottom line of a three-line header. `Time Nom` / `Date Nom` / `Date Loading` / `Time Loading` sit above the main label line, and `Accepted` / `Completed` sit below it. The labels the reader carries for c4, c5, c18 and c19 are only `Time Nom`, `Date Nom`, `Date Loading` and `Time Loading`.
- Row counts per roster are 11/17/15/6 carried against 10/16/14/5 vessel rows on the page. The only difference is `r0`.
- *Inferred, not measured:* `records=57` = 11 + 17 + 15 + 6 + 4 + 4, so the grounding test counts the four header rows as records.
- **Why the coverage checks did not catch it:** every `Accepted` word lies inside a carried entry bbox, so page-word accounting (§ 2.2) is clean. Coverage is not role. The defect showed up only in the row counts.

### 2.2 The rest of the carried grid holds against the page

- **Text:** 878 of 878 carried nodes (786 EntryCells, 87 LabelCells, 5 PrintedTotals) equal the poppler words whose centres lie in their bbox.
- **Coverage:** 0 of 1,244 page words are unaccounted for, and 0 lie inside more than one carried bbox. The split is 879 in entry bboxes, 145 in label bboxes, 5 in PrintedTotals, 124 caption words and 91 ignored words.
- **Drawn intervals:** 786 of 786 entry cells and 87 of 87 labels lie inside a drawn column interval. Each carried column maps one-to-one onto a drawn interval.
- **Column by nearest printed label ink (no rules used):** 850 agree and 8 disagree. Neither group of disagreements is a carriage error:
  - 4 are T1's `TOTAL` values. They are left-aligned under a centred `TOTAL` label, sit inside TOTAL's drawn interval, and land nearest `OTHER`.
  - 4 are the outer words of the two `Louis Dreyfus Company Grains Australia` cells, which are wider than their label.
  - T2 (`table11`) has no column labels, so this check cannot be run on it.
  - **Null control:** swapping the columns of `htable1-e10_13` (`35,000`) and `htable1-e10_16` (`Lupins`) raises the count to exactly 10 disagreements, the 8 plus those two cells.
- **Rows:** none of the 57 carried rows has a y-centre spread above 0.000 pt (line height 6.000 pt, row pitch 8.040 pt).
- **Totals:** every printed port total equals the exact Decimal sum of its carried Volume cells (374,904 / 737,289 / 660,363 / 178,708), and so does `1,951,264`.
- **Source quirk:** T1's ALB row prints `160,845` against a component sum of `160,844`. That is on the page, not a carriage error.

### 2.3 R74's "the data grid leaks one row" is FALSE at HEAD

- `derive_data_grid(cbh, 0)` (universe `alignment`) admits 45 rows. Rows 75–80 are not among them, and no admitted line contains `1,951,264`.
- No carried EntryCell or LabelCell bbox contains any of the 16 words on the `1,951,264` line or the 85 Note words.
- `1,951,264` is `p0/r2#printedtotal9-l0`, a `tab:PrintedTotal` with no `tab:totalOf` whose `tab:aggregates` are the four port totals.
- This agrees with [[R74]]'s 2026-09-30 narrowing: the leak stopped on 2026-09-17 ([[R243]]). What still keeps R74 open is that `tab:StackedGrids` is not derived, and nothing in cbh's carriage depends on that. The 2026-10-05 adjudication's wording, "the data grid leaks one row from the page's second table", is **stale**. It is corrected by the adjudication this change appends, not edited in place.
- **Header rules** (this session, pdfplumber): full-width horizontal rules at y = 105.0, 118.7, 126.7 and 134.8 in the band 80–140. Word extents in that band: `Time Nom` / `Date Nom` 105.4–111.4, the main label line 109.4–115.4, `Accepted` 113.5–119.5, and the first data row 120.7–126.7.

### 2.4 Uncarried bands

There are two `etkl:IgnoredBand`s, both "fewer than 2 columns": `p0#ignored0` (`Daily Ship Roster / As of03/08/2026`) and `p0/r2#ignored9` (the Note, by the R288 ruling). There is no escalated or residue band.

## 3. Decided, and where

- **Hold kept, now with the new blocker named:** cbh's 2026-10-05 (second) `cor:adjudication`, appended at the end of its entry in `tests/corpus-manifest.ttl`. This is agent-composed. It is reversible until the maintainer merges it.
- **[[R289]] raised:** `docs/superpowers/residues-open.md` and the index line in `residues.md`.
- **Whether R74 still stands between cbh and acceptance** is NOT decided. That is the maintainer's call, and § 2.3 is the evidence for it.

## 4. Unverified or assumed

- The cause of [[R289]] is the § 5 prediction and nothing more. No code was read.
- `records=57` including the four header rows is inferred from the sum, not traced.
- The measurement scripts lived in a session scratchpad and are gone. Re-measuring R289 takes no script: `grep -c 'atRow <…#htable1-r0>'` on a compile, or the row counts in § 2.1. A spec for R289 should make the row-count check (vessel rows on the page = carried rows) a test, not a probe.
- Whether the other three rosters' header boxes have the same 0.8 pt overhang is not measured. Only the first roster's rules were read.
