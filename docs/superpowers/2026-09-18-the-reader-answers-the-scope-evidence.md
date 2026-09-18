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
- ~~**The double ask is untouched.**~~ **SUPERSEDED by § 6, appended later in the same loop** —
  the double ask was measured and fixed, and the live cost halved. The sentence stands as written
  because it was true when the section was written.

---

## 6. Appended — one ask per question, and a reader that can no longer kill the compile

### 6.1 The waste, counted before it was fixed

`compile.page_bands` invocations inside one `compile_document`, counted by shim at `8d991fd`:

```
graincorp-capacity   {0: 2}                             2 calls,  1 page
bfs-population       {0:3, 1:2, 2:2, 3:2, 4:3, 5:3, 6:3}  18 calls, 7 pages
```

`page_bands` runs once in `document.compile_document`, again in `compile.compile_tables`, and a
third time on a section-repaired page ([[R255]], [[R256]]). Every pass re-asked the reader about
every gridded region it saw. On bfs that is **2.57× the necessary model calls, 61% of the answers
discarded** — at ~50 s and one image call each.

### 6.2 The fix, and the live A/B

`CachingRegionReader` memoises on the crop's **content hash** plus the grid dimensions, so the
same question asked by three call sites costs one ask, while a genuinely different region (the
section-repaired partition draws different extents) hashes differently and is asked. Live, full
`compile_document` on graincorp-capacity, same process, same commit:

```
ARM BEFORE (no cache): 4 live model asks |  113s | score 1.0000
ARM AFTER  (cached)  : 2 live model asks |   79s | score 1.0000
```

Half the asks, 30% less wall-clock, identical score.

**It also removes a correctness defect, which is why the cache sits at the reader and not around
`page_bands`:** the passes were INDEPENDENT readings of one page, so [[R253]]'s variance could
hand `compile_tables` a different `unshown` set than `compile_document` saw — and the split
[[R258]] measures as one-address fragile was then decided on one of the two arbitrarily. One
answer per question makes the passes agree by construction.

### 6.3 A reader exception aborted the whole document, and now makes no claim

Observed live during the A/B: a BAML cast of a model answer raised inside
`sync_client.b.ReadEmptyCells`, the exception propagated out of `region_unshown` → `page_bands` →
`compile_document`, and the run died. **One flaky call about one region would take a 27-page
document with it.** `unshownink`'s own docstring already promised the opposite — *"Every failure
path returns the empty set: a reader that cannot be reached, a crop that cannot be rendered and a
refused region are all 'no claim'"* — but the read sat outside the guard that delivers it. It is
inside now. This is the shape of [[R253]]'s recorded ABORTED run whose traceback was never
captured.

### 6.4 Falsification

- **The cache pin inverts.** With the memoisation removed, `test_the_same_crop_is_asked_ONCE…`
  fails on `3 != 1`; restored, green. The two null controls (a different crop, a different grid)
  stay green either way — correctly, since they assert the cache must still *ask*.
- **A failure is not cached** (`test_a_FAILURE_is_not_cached`): a reader that raises once and then
  answers is asked twice, so a transient failure does not become a permanent silence.
- **The abort guard** (`test_a_reader_that_RAISES_makes_no_claim_and_does_not_abort_the_compile`)
  runs the real region with a raising reader and requires `frozenset()`.
- 31 tests green in `test_unshown_ink.py`.

### 6.5 Still not claimed

The per-page ask count is **not** the same as the page-pass count: bfs's 18 passes become 7, but
how many asks that is depends on gridded regions per page, and **no live run of bfs has been
made**. The gcap A/B is the only live cost measurement here.

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
