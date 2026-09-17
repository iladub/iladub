# Measurement — the section total is in its own band ([[R47]], [[R50]], [[R77]])

**Serves:** prog:criterion:tab:04 — R77 is one of its three blockers

**Date:** 2026-09-17 · **Tree:** branch `section-total-is-in-its-own-band`, cut from `main` at
`275659a`, working tree clean · **Runner:** `./.venv/bin/python` · **Class:** evidence.

**Doc impact: none.**

This loop was handed [[R77]] as its subject by the maintainer, after the previous handoff's § 5a
prediction was run and refuted. It measured, and built nothing. What it found is that R77's
*claim* is true, its *mechanism* is the second of two gates, and the first gate has been recorded
in [[R47]] since 2026-08-04.

---

## 1. The handoff's § 5a probe — REFUTED, in one command

`2026-09-17-refuse-the-decoration-universe-handoff.md` § 5a predicted, typed PROPOSED, that cbh
page 0's four lost grid rows *"fail for ONE shared reason"*. They do not:

```
$ ./.venv/bin/python -c "… derive_data_grid('corpus/ag-trade/cbh-stem-2026-08-03.pdf', 0) …"
{26: 'unplaceable', 42: 'AggregateWitness/no-reconciliation',
 63: 'AggregateWitness/no-reconciliation', 74: 'AggregateWitness/no-reconciliation'}
```

Two classes, not one: a placement refusal on the vessel row, and three panel totals that reach G8
and fail its arithmetic. [[R243]] is therefore **two defects**, and the loop that handoff imagined
— one cause, one remedy — is not the loop to run. The grading worked exactly as CLAUDE.md
§ "The handoff's next action is TYPED" intends: three minutes, not a day.

## 2. R77's figures are stale; its structural claim survives

R77 (2026-08-09) records `compile_tables` on cbh p0 as `asserted=66, escalated=879, score=0.0698`.
Live at `275659a`:

```
LIVE cbh p0: asserted=54 escalated=842 score=0.0603   regions=10
```

All three figures moved. The half that is load-bearing **holds**: `asserted != 0`, so
`datagrid_fallback` (`compile.py:1408`, `asserted_total == 0 and escalated_total == 0`) still never
fires on this page, and the data grid is still not on its score path.

## 3. The four totals are each their OWN region, and are IGNORED

The page-scope region dump is what reframes the subject:

| region | kind | verdict | reason | tokens a/e |
| ---: | --- | --- | --- | --- |
| 1, 3, 5, 7 | UNSUPPORTED_TABLE | escalated | `REGION_TILING_FAILED` | 0 / 195, 290, 251, 106 |
| **2, 4, 6, 8** | **NON_TABLE** | **ignored** | **`fewer than 2 lines`** | **0 / 0** |
| 9 | RECORD_TABLE | asserted | — | 54 / 0 |

Regions 2, 4, 6, 8 carry exactly `374,904`, `737,289`, `660,363`, `178,708` — the four panel
totals, one per region, each a single line. They are ignored at `regions.py:91`
(`"fewer than 2 lines" if len(band.lines) < 2`) before any table reading happens.

**This refutes R77's stated mechanism.** R77 says the totals are missed because
`rows.detect_aggregation_rows` requires exactly two occupied columns and a label-less total is
not a candidate. The detector never receives them: they are not rows of any region it runs over.
Their ink is in **neither** score operand (`0 / 0`), so R77's predicted movement — *"4 cells of
945, 0.0698 -> ~0.074"* — is wrong in both directions.

Region 9, the only asserted region on the page, is R74's table B.

## 4. Document scope reads the page very differently from page scope

| | asserted regions | score |
| --- | --- | --- |
| `compile_tables(CBH, 0)` | 1 (`table9`) | 0.0603 |
| `compile_document(CBH)` | 5 — the four rosters **repaired** + `table9` | 0.9095 |

`repaired_bands ((0,1),(0,3),(0,5),(0,7))`; the four rosters chain into one logical table
(`htable1/3/5/7`). The four totals stay `ignored` under both. And loop N's chain arithmetic runs
over that chain **without abstaining** and confirms nothing:

```
ChainArithmetic(page_confirmed=0, document_confirmed=0, retracted=0,
                newly_confirmed=0, abstained=None, groups_derived=0)
typed SectionTotal 0 · AggregationRow 0 · DetectedAggregationRow 0 · confirmsSection 0
literal '374,904' present · '737,289' present · '660,363' present · '178,708' present
```

The ink is carried; the values are read by nothing.

## 5. Where `_confirm_section_total` bails, instrumented rather than read

`document._confirm_section_total` is the one mechanism built for this shape. Wrapped and run over
all four repaired bands, it returns `(False, None)` on every one — and it does **not** bail at its
first guard:

```
BAND htable1 | lines 18 | hrules 12 [183.05, 191.09] | lines_below_last_rule 1
    band y:   65.4 -> 199.1   last 2 lines: ['10223 "TBA" …', '10226 "TBA" …']
    RETURNS (False, None)
```

`lines_below_last_rule = 1` clears the "nothing printed below the grid's closing rule" test
(`document.py:1154`). What follows is the fall-through: the band's last line is a **vessel row**,
so `last in agg` is false and `is_aggregation_shaped(rows[last])` is false, and the function
returns "no total candidate printed". The total `374,904` sits at y≈210, in the gap below the band
that ends at 199.1. **The oracle's window is the band, and the total is one band away.** The
refusal is silent — no note — because the code believes nothing was printed.

## 6. The `gap_factor` arm is REFUTED, not untried

`bands.detect_bands(lines, gap_factor: float = 1.8)` cuts wherever `gap > 1.8 × median_gap`. On
cbh p0, captured from the live pipeline:

```
lines 85  median_gap 2.040  threshold(1.8x) 3.672

band  1  y   65.4->199.1  n=18  cut_gap=12.47 (6.11x)  'GERALDTON' …
band  2  y  209.8->215.8  n= 1  cut_gap=10.68 (5.24x)  '374,904'
band  3  y  226.7->383.4  n=21  cut_gap=10.92 (5.35x)  'KWINANA' …
band  4  y  394.1->400.1  n= 1  cut_gap=10.68 (5.24x)  '737,289'
```

Every cut on the page is **5.2x–6.1x** the median against a **1.8x** threshold. A `gap_factor`
large enough to pull a total into its roster (> 5.24) also exceeds every other cut on the page
(max 6.11) by too little to be a discriminator — and at 6.11 the whole page collapses into one
band. **No value of that constant admits the total and keeps the four panels apart.** The tuned
constant is not the remedy here, and this is the measurement that says so rather than a preference.

`detect_bands` is reading the author correctly: the total really is a separate printed block.

## 7. The arithmetic is AVAILABLE and EXACT — 4 of 4 panels

The repaired roster tables carry cells (`cells=170 / 268 / 228 / 84`), reached via **incoming**
`tab:atRow` edges — an outgoing-only query on a leaf row shows `rdf:type tab:LeafRow` and nothing
else, which is how this was nearly misread as "the rows carry no cells".
`_logical_row_sequence(htable1)` returns 11 rows with `why: None` — no abstention.

Summing each column over each table's own rows:

```
htable1  rows=11  target=374904   MATCHING COLUMNS: [(13, 10, 374904)]  agg_shaped(last)=False detect={}
htable3  rows=17  target=737289   MATCHING COLUMNS: [(13, 16, 737289)]  agg_shaped(last)=False detect={}
htable5  rows=15  target=660363   MATCHING COLUMNS: [(13, 14, 660363)]  agg_shaped(last)=False detect={}
htable7  rows= 6  target=178708   MATCHING COLUMNS: [(13,  5, 178708)]  agg_shaped(last)=False detect={}
```

Column 13, exactly, on all four, with **no other column matching**. The member counts
`[10, 16, 14, 5]` are the same member sets the grid path independently found
(`aggregates {20: 10, 42: 16, 63: 14, 74: 5}`, `test_datagrid.py:611`). Two independent paths
agree on the operands.

So the remedy is **constructible**: the disposer exists, is exact, reads no label, and has a
witness on every panel. Nothing is missing but the window.

## 8. The two gates compose, in a fixed order

1. **The window gate ([[R47]])** — the total is not in the band, so no candidate is found at all.
2. **The candidate-shape gate ([[R77]])** — the total line carries **one** occupied column
   (`'374,904'`, no label), and `is_aggregation_shaped` requires exactly two. Even with the window
   widened, `detect_aggregation_rows` would refuse it.

**R77's mechanism is real and currently unreachable**, masked by a gate upstream of it. This is
neither a confirmation of R77 as written nor a refutation: it is a re-statement that puts it
second. Closing R77 alone moves nothing while gate 1 stands.

## 9. Attribution — [[R47]] has owned this since 2026-08-04

R47's own evidence column already says it, verbatim: the specimen is *"currently in a **separate**
`detect_bands` band from the grid"*, with *"total `374,904` at y≈210 vs. the section's rule bottom
199.6"*, and *"loop Q shipped an adjacent oracle without closing this row's gap; the real
specimen's below-grid content is still read as an ordinary, unattributed trailing band line"*.

This loop **re-confirms R47 at HEAD and adds three things it did not have**: the `gap_factor` arm
is refuted with numbers (§ 6); the arithmetic is exact on 4/4 panels, so the remedy is
constructible (§ 7); and R77 composes behind it in a fixed order (§ 8).

[[R50]] is adjacent but insufficient on its own: it names `_confirm_section_total`'s last-row-only
scope, and its remedy — *"walk back from the FIRST non-grid line after the closing rule"* — walks
**within the band**, which cannot reach a total that is in the next band. R50 itself flagged that
its scope was *"consistent with (though not solely explained by)"* cbh's zero; § 5 supplies the
rest of the explanation.

Neither R47 nor R50 is named by any `prog:blockedBy`. **R77 is the arc-serving row** of the three
(`tab:04`, with R74 and R80).

## 10. The shape is cbh-only — stated because it constrains any remedy

Across all 7 documents / 27 pages, one-line all-numeric bands:

```
cbh-stem p0 band2 '374,904' prev_band_lines=18   band4 '737,289'   band6 '660,363'   band8 '178,708'
TOTAL one-line all-numeric bands: 4
```

Four, all on one page of one document. **A rule keyed on "a one-line numeric band" is fitted to
this page by construction** and must not be written. The honest form of the rule is keyed on the
*arithmetic*, not the shape — a following band whose measure reconciles exactly with the preceding
table's own column — which is general, has a corpus population of 4, and whose false-positive
surface is § 11's open question.

The vocabulary needs nothing new: `tab:SectionTotal` and `tab:confirmsSection` already exist
(`vocab/ontology/tab.ttl:551-556`) and their comments state exactly this law.

## 11. What this does NOT establish

- **The false-positive surface of arithmetic binding is measured only at its LOOSEST, as an upper
  bound.** Testing *any* numeric token anywhere on a page against *any* asserted table's column
  sums, with no adjacency requirement at all:

  ```
  CORPUS col_sums=175 page_numbers=1690 matches=15
  cbh-stem            MATCHES=4  ['178708','374904','660363','737289']   ← the four true totals
  graincorp-capacity  MATCHES=2  ['0','14000']
  who-wfa             MATCHES=9  ['17','20','21','47.0','49.0']
  apple / bfs / ons / graincorp-stem   MATCHES=0
  ```

  **4 true positives and 11 coincidences.** The form is deliberately conservative — who-wfa's
  z-score integers (`17`, `20`, `21`) collide trivially, and nothing here requires the number to
  be adjacent to the table whose columns it matches. The rule § 10 describes requires the value to
  sit in the band **immediately following** that table and to match **that table's own** columns.

  **Tightened to that adjacency, the surface is `true=4 false=4`:**

  ```
  TRUE  cbh-stem  p0  table_band=1 next_band=2 value=374904 (next band has 1 lines)
  TRUE  cbh-stem  p0  table_band=3 next_band=4 value=737289 (next band has 1 lines)
  TRUE  cbh-stem  p0  table_band=5 next_band=6 value=660363 (next band has 1 lines)
  TRUE  cbh-stem  p0  table_band=7 next_band=8 value=178708 (next band has 1 lines)
  FALSE who-wfa   p0  table_band=3 next_band=4 value=17      (next band has 6 lines)
  FALSE who-wfa   p0  table_band=4 next_band=5 value=20      (next band has 6 lines)
  FALSE who-wfa   p1  table_band=3 next_band=4 value=17.0    (next band has 6 lines)
  FALSE who-wfa   p1  table_band=4 next_band=5 value=20.0    (next band has 6 lines)
  ```

  All 4 true positives survive; 11 coincidences fall to 4 (graincorp-capacity's `0` and `14000`
  are both killed by adjacency). **The arithmetic is therefore NOT self-disposing** — a remedy may
  not be justified on "exact Decimal equality cannot be a coincidence", because on this corpus it
  is one four times.

  **A discriminator is visible in the data and is deliberately NOT adopted here:** every true
  positive's following band has **1** line and every false positive's has **6**. That is the
  one-line-band shape § 10 already refuses to key a rule on — n=8, four of them one page of one
  document, and the six skipped pages below are unmeasured. Recording it as a *correlation to be
  falsified*, not as the rule.
- **SIX PAGES ARE UNMEASURED IN BOTH CENSUSES, and they are not clean pages — they are missing
  ones.** The tightened census maps a region to a band **by index**, and refuses the page when the
  counts disagree rather than guessing:

  ```
  apple p0 (8 bands, 3 regions) · apple p1 (8, 3) · apple p2 (8, 10)
  bfs p5 (15, 17) · ons p7 (16, 18) · ons p8 (9, 11)
  ```

  Two of the three documents with the largest escalation surface in the corpus are in that list.
  **`false=4` is therefore a floor, not a count**, and any remedy justified on it is justified on
  an audited-incomplete denominator. Closing this needs a y-overlap region↔band match in place of
  the index match; it is the next loop's first action.

- **Nothing pins cbh's real zero.** `tests/etkl/test_section_repair.py:540` asserts
  `SectionTotal == 2` on a *fixture* and `:577` asserts none on a refusing fixture. A fix would
  land with no real-document test going red, so an oracle on cbh is part of any remedy.
- **Why vessel row 26 is `unplaceable` is untouched** — the other half of [[R243]], on the grid
  path, not this one.
- **Whether the remedy belongs in `_confirm_section_total`'s window or in a trailing-strip
  peel/carry (R47's framing) is undecided** — two candidate designs, named in § 8, not chosen here.
- The §8 class of the widened window is **not** settled by this document.
