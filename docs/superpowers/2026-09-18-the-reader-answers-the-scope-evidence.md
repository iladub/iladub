# Evidence — the reader answers the scope: R213's carriage reaches the graph on live input

**Serves:** maintenance — [[R253]]'s first regime. No criterion is named by a `prog:blockedBy` here.

**Date:** 2026-09-18. **Branch:** `the-reader-answers-the-scope`, cut from `main` at `8d991fd`.

**Doc impact: none.**

---

## 1. The contradiction, in two lines of shipped code

`baml_src/unshown_ink.baml`, the prompt:

> A position covered by a cell that SPANS several rows or columns is not empty — you see that
> cell's content there. Report a position as empty only when the place itself shows nothing.

`src/iladub/etkl/unshownink.py`, refusal 3: every text-layer-empty position must appear in
`empty_cells`, scoped by a `spanned` set **no call site supplies** — `compile.py`'s own comment
recorded the consequence as *"this wiring types NOTHING end-to-end until the spanned set exists"*.

So the reader was refused for obeying its instructions. The set cannot be computed here: a merged
cell's coverage is **drawn, not written**, and the label's word box is small, so no arithmetic over
the text layer recovers it. Per CLAUDE.md § *"One geometric attempt, then NEURAL"*, it is **asked**.

## 2. The change

`UnshownInkReading` gains `covered_cells` — the positions the reader read as covered by a spanning
cell. Refusal 3 accepts a text-layer-empty position accounted for in **either** list. `spanned`
stays a caller argument and still narrows the demand.

**Refusal 4 is new and is what keeps the control honest.** `covered_cells` is the one field a
reader could abuse to make the null control vacuous — call everything covered and nothing is ever
missed — so the claim is itself disposed: a position the reader calls covered must be one the text
layer also found empty. A covered position carrying a glyph refuses the whole region.

## 3. Live, on graincorp-capacity p0 band 3 (27 × 16, 406 populated cells, 110 unshown zeros)

**One region, `BAML_LIVE=1`, `claude-sonnet-5`:**

```
LIVE READING in 49.4s
  refuses_grid : False (rows_seen=27 cols_seen=16)
  empty_cells  : 110
  covered_cells: 25
  note         : "I scanned the grid row by row, noting blank navy cells as empty and treating
                  the season labels in column 0 as spanning multiple rows below their first
                  appearance."
DISPOSED: 109 addresses type tab:UnshownInk
```

**The whole page through the shipped pipeline, second live run:**

```
=== page_bands LIVE, gcap p0, 80s ===
5 bands, 2 gridded (one ask each)
  band 1: 2 lines, unshown = 0
  band 3: 27 lines, unshown = 110
TOTAL unshown carried into the graph: 110
```

The 25 came back **correct on the first live run, with no example in the prompt** — the reader
named the mechanism itself ("season labels … spanning multiple rows"). Under the shipped disposal
that same answer typed **0**.

109 on one run and 110 on the next is [[R253]]'s recorded reader variance, unchanged by this work
and not claimed to be fixed: the miss is `(21, 8)`, and both runs carry zero false positives.

## 4. Falsification

- **Inline, in the pin itself** (`tests/etkl/test_unshown_ink.py::test_the_answer_a_LIVE_reader_actually_gives_now_reaches_the_graph`): the same live-shaped answer **without** `covered_cells` types `frozenset()`. That assertion is the previous state of the world, kept in the test.
- **The control still fires** (`test_refusal_3_still_fires_when_a_position_is_in_NEITHER_list`): a position in neither list refuses, exactly as before. The repair widens the scope; it does not delete the guard.
- **Refusal 4 fires** (`test_refusal_4_a_covered_position_that_HAS_a_glyph_refuses_the_region`).
- Suites green: 27 in `test_unshown_ink.py`; 119 across the unshown/tab/artifact files; 101 across `test_datagrid`, `test_membrane`, `test_holon`.

## 5. What is NOT claimed

- **[[R253]] is not closed.** Its row records *at least three* reader regimes producing a 0. This
  disposes **one** — the reader obeying the prompt about spans. The others are untouched and the
  variance (109 vs 110) is unchanged.
- **Nothing is measured beyond gcap p0.** Six documents have no live reading.
- **The double ask is untouched.** [[R255]]: `page_bands` runs twice per `compile_document`, so a
  full live document still pays two asks per gridded region. This loop changed one page's wiring,
  not the cost.

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
