# Handoff: R295, a rule separates only where it is drawn (2026-10-06)

**Serves:** maintenance — loop 1 of the four the maintainer accepted on 2026-10-06 (§ 3).

**Topic:** compile · **Date:** 2026-10-06

**Doc impact: none.**

Written at about 35K working tokens, under the 50K originating floor. Part 5 comes first.

## 5. Next concrete action

1. **PROPOSED (refutable in minutes).** Candidate remedy: in `grid._rule_boundaries`, a word has
   to respect a rule's x only where that rule's **y-extent overlaps the word**. Today the tiling
   test pools every rule x in the band and checks every word against all of them, so one crossing
   word discards all of the author's rules. **Prediction:** Caltrain pages 0 to 3 come out at 17 to 19
   leaf columns with no other change. Lines 0 and 1 (title), line 37 (footer) and the last-column
   times all lie outside the y-extent of the rules they cross (§ 2, *Measured*). **Run it first**:
   monkeypatch `_rule_boundaries` and re-run the § 2 reproduction on the four pages. If it fails,
   the fallback is to scope the test to `gridregion.grid_lines`. That set already excludes lines 0,
   1 and 37, but it keeps line 2 (the "Northbound – …" heading), because the title-area marks
   enclose it. The y-extent is the author's mark, so there is no tolerance to tune. Whether
   *touching* counts as overlap (line 2's bottom at y 105 against the grid rules' top at y 105) is
   a seam to measure, not a constant to choose.
2. **PROPOSED (outcome unknown, so measure before and after).** Blast radius. `_rule_boundaries`
   has three callers: `grid.py:113` (the leaf grid), `spangraph.py:81` (span donation) and
   `sectiongraph.py:299` (section merge). A change to it moves all three. Before touching `src/`,
   count across the seven, then the four held-out documents, the bands that carry interior
   vertical rules but come out with fewer leaf columns than the rules draw. That count is the
   census, and after the change it is the regression control. Then run the seven serially at the
   new head: every document at or above `cor:scoreFloor`, with hashes compared. Read any
   document whose hash moves before calling it either a regression or a repair.
3. **ASSERTED (the definition of done).** Caltrain's pages 0, 1 and 3 enter the score's
   denominator (asserted or escalated). Page 2 no longer asserts a 2-column reading. Caltrain's
   score falls from 1.0. All seven stay at or above their floors. A test on a **synthetic**
   fixture pins the remedy, and the task report carries its `## FALSIFICATION` block. `corpus/`
   and `held-out/` are gitignored, and CI skips corpus-gated tests, so a green CI does not
   show the corpus is safe. Sweep the corpus locally, one test file per process.

## 1. Goal

Make the score able to see Caltrain's three ignored timetable pages, and stop page 2 asserting a
misread, by fixing **where the compiler looks for the grid**, not whether it calls something a
table. This loop does not try to accept Caltrain. Its header comes from the legend row
"6XX Local" (§ 2), and fixing that is loop 2.

## 2. Where the primaries are

- **[[R295]]** in `residues-open.md`, and `2026-10-06-held-out-corpus.md` § 3 and § 4.
- `src/iladub/etkl/grid.py:40` `_rule_boundaries` (the all-or-nothing tiling test) and `:92`
  `infer_leaf_grid` (falls back to whitespace when that test returns None).
- `src/iladub/etkl/regions.py:88-110` (`_reason`, `classify`) emits *"fewer than 2 columns"*. It
  only reports the leaf grid it is handed.
- `src/iladub/etkl/compile.py:469` `page_bands` and `:92` `_build_ruled_band`.
  `src/iladub/etkl/gridregion.py:82` `grid_lines` (`vocab/queries/grid-region.rq`) and `:137`
  `peel_leading_captions`.
- Fetch: `.venv/bin/python scripts/fetch_corpus.py tests/held-out-manifest.ttl held-out`.

**Measured 2026-10-06 at `6992458` (same `src/` as `main`), offline:**

- `page_bands(caltrain, p)` returns **one band per page**: 38 lines, about 440 words. That is 3
  title lines, the grid, and 1 footer line ("EFFECTIVE September 21, 2024 … See Page 2 For …").
- The author drew the grid's columns as 19 rule xs spaced about 41.6 pt apart (page 0: 14.0,
  24.9, 112.6, 154.3, … 737.4, 779.0), each running y 105 to 574 in about 25 segments. Six
  further one-off marks sit at y 81 to 99 (x = 21.4, 25.8, 27.4, 31.8, 729.6, 778.8). Line 3,
  "6XX Local" (y 90 to 97), sits among them, so they are **probably a legend swatch**. That is
  not verified.
- **43 of 440 words** on page 0 straddle the pooled rule set: the title lines, the footer, the
  zone letters crossed by x = 21.4, and every time in the last train column crossed by x = 729.6.
  So `_rule_boundaries` returns None, and the whitespace profile gives **1 column** on pages 0, 1
  and 3 and **2 columns** (`[18, 574, 778]`) on page 2, which then classifies `RECORD_TABLE`.
- `grid_lines` already excludes lines 0, 1 and 37 on pages 0 and 2, but `peel_leading_captions`
  peels **0** lines, because lines 0 and 1 are not enclosed by any rule's y-extent (its
  "Voyage" guard).
- **Counterfactual** (a hand-built band, not a remedy): dropping lines 0 to 2, line 37 and every
  rule shorter than 15 pt gives 18 or 19 columns, `UNSUPPORTED_TABLE`, *"header has 1 words but
  18 columns"*. Dropping either the lines or the marks alone does not get there: the lines alone
  give 6 columns, and the marks alone give 1.

Reproduction (the scratchpad scripts were not committed):

```python
from iladub.etkl.compile import page_bands
from iladub.etkl.regions import classify
b = page_bands("held-out/caltrain-weekend-timetable.pdf", 0)[0]
r = classify(b); print(len(b.lines), r.kind.name, r.reason, r.grid.ncols)
# -> 38 NON_TABLE fewer than 2 columns 1
```

## 3. What was decided, and where it is recorded

- **Maintainer, 2026-10-06, in conversation (recorded only here):** next loops in order: (1)
  R295, the grid's scope; (2) Caltrain's header, reusing the ons boxhead-reader method; (3) a
  membrane guard so an asserted table cannot merge columns the author separated with rules, then
  checking fed-h41's asserted cells against it; (4) contracts, as ruled earlier. Prose read as
  table (arxiv, who-covid) is deferred, because it fails safe: it escalates.
- **The remedy class is AXIOM, not NEURAL.** The evidence (the author's rules) is on the page and
  is unambiguous. The NEURAL table-or-not worker proposed earlier in the same conversation was
  withdrawn once this was measured.
- **Fixing Caltrain spends it as a held-out document.** The next check of whether the 7/7
  generalises needs a fresh batch.

## 4. Unverified or assumed

- Whether the y-extent rule alone (item 1) is enough. Item 1 is the test.
- Whether any of the seven carries the same defect. Item 2's census answers that.
- The two-ended peel was refuted before ([[R232]], [[R233]]): the leading cut removed real
  header rows. Item 1 removes no lines, so it should not repeat that failure. That reasoning
  has not been measured.
- What the six title-area marks are (§ 2).
