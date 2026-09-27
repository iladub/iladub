# Evidence: cbh's "fused boxhead" is neither extraction nor reading — asserted header ink is booked as escalated (2026-09-27)

**Serves:** maintenance — runs the diagnosis proposed in the last section of
`2026-09-27-extent-reach-refuted-evidence.md` ("fused in extraction, or mis-grouped by the reader?").

**Topic:** jev-reading · **Date:** 2026-09-27 · **src measured:** `56fe088`

**Doc impact: none.**

## 5. Next action (written first)

- **Asserted:** neither arm of the diagnosis holds.
  - The words are not fused in extraction.
  - The reader does not mis-group them.
  - The header is derived, asserted, and disposed by the tiling and conservation oracle.
  - The accounting books it as escalated.
  - No Jev slice is warranted for this ink, and none should be specced.
- **Proposed, for the maintainer to rule (the remedy moves the N/7 benchmark by accounting,
  so this is not mechanical):**
  - At the `max(0, tokens - n)` sites in `compile.py` (the hierarchical and ruled assert
    branches), book the band's non-body words with `_book_recovered_ink` against the emitted
    `HeaderNode` extents. This is the mechanism R176 already ruled for label cells.
  - **Predicted:**
    - cbh 0.9095 → 1.0 and graincorp-stem 0.9659 → 2227/2228.
    - who 0.9156 → 803/806.
    - ons +17 tokens (0.8464 → 0.8685 ceiling).
    - apple, bfs and graincorp-capacity unchanged.
  - **Refutable in minutes:** the census below already computed these values. The same wrapper,
    re-run after the change, must show `e` on these bands equal to the `miss` lists only.
  - **The concern, stated first:** a score rise that comes from moving ink from `e` to `a` is the
    pattern that "score rose, nothing fixed" warns about.
    - It is legitimate here only because every moved word is inside a node the graph carries and
      SHACL disposes.
    - That condition is what the set check below measures. It is not assumed.

## 1. Goal

Decide the tier (PROCEDURAL extraction vs NEURAL reading) of cbh's 80 escalated "fused boxhead"
tokens, which were the proposed first slice of section 4.

## 2. Where the primaries are

- Raw words: `pdfplumber` `extract_words()` on cbh p0. The header is three stacked lines (tops
  105/109/113), and every word is intact (`Time`, `Nominated`, `Accepted`…).
- The "fused" appearance is `RegionReport.ascii`, which truncates each ruled cell to its column
  width (`TimDate Nom`, `VNAVesseTimeDate`). It is a rendering, not the data.
- The booking: `resolve_ruled_header_rows` returns `n` = *body* tokens (`ruledroles.py`
  docstring: `asserted_body_token_count`). The caller then books `escalated += max(0, tokens - n)`
  (`compile.py:1356-1357`; the same form appears at `:1178`, `:1382`, `:1439`).
- The header nodes it just asserted are in the graph (`assert_hier_region` → `HeaderNode` with
  bounds, R177). They are disposed by `region_tiles` and conservation evidence.
- R176's `_book_recovered_ink` (`compile.py:333`) fixed branches that *dropped* ink. These
  branches drop none: they book 100% of the band, with the header on the wrong side.
- Scratch scripts: `census.py` and `pointwise.py`, session scratchpad only (non-durable). Each
  wraps `holon.assert_hier_region` and runs `compile_document` offline, serially, one process per
  document.

## 3. Measured

**Census.** This is the escalated ink inside regions whose verdict is `asserted`, per corpus
document (`compile_document`, HEAD):

| doc | score | a | e | e inside asserted regions | ceiling if all booked |
|---|---|---|---|---|---|
| cbh | 0.9095 | 804 | 80 | 80 (Hierarchical) | 1.0000 |
| graincorp-stem | 0.9659 | 2152 | 76 | 76 (Hierarchical) | 1.0000 |
| who | 0.9156 | 738 | 68 | 68 (Hierarchical) | 1.0000 |
| ons | 0.8464 | 650 | 118 | 17 (Hierarchical) | 0.8685 |
| apple | 0.9419 | 486 | 30 | 0 | — |
| bfs | 0.9021 | 1263 | 137 | 0 | — |
| graincorp-capacity | 1.0000 | 406 | 0 | 0 | — |

**Pointwise and set check.** For every `assert_hier_region` call with `n > 0`, I compared the
band's non-body words (lines above `body_line`) with the words lying exactly inside some emitted
`HeaderNode` box (no tolerance). In every case, `n` equals the body-line token count.

- **cbh**, all 8 calls: `tokens - n == in_header_box`, with nothing missing and nothing extra.
  The final four are 20 each (80 in total).
- **graincorp-stem**: 25 of 26 on the first table. The one miss is `Friday, 31 July 2026`, a
  date line above the header that is correctly escalated. The other two tables match 25/25.
- **ons**: 17, 7, 10, 7, 10, all exact, with no misses and no extras.
- **who**: 5 calls of 13/13 exact = 65. Its other **3** escalated tokens come from regions
  booking 97/1, 85/1 and 85/1. Those regions never reached the wrapper, so this measurement
  does not explain them. who's corrected ceiling is **803/806**, not 1.0.

## 4. Unverified or assumed

- The census ceilings for cbh and graincorp-stem come from the set check. The ceilings for who
  and ons are corrected by the check as stated above. None of them has been produced by running
  a changed `compile.py`.
- Sites `:1178`, `:1382` and `:1439` share the booking form. Only calls that reached
  `assert_hier_region` were observed, so whether every live site carries `HeaderNode` bounds
  (R177 allows boxless span-synthesised nodes) was not checked site by site. Every node observed
  had a box (`boxless=0` throughout).
- Whether moving header ink to `a` changes any `cor:scoreFloor` pin or strict-xfail in the suite
  was not run. It would: cbh and who floors would now sit below their scores. That is expected,
  but it has not been measured.
