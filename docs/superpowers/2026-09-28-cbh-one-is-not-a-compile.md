# Note: cbh's 1.0 is not a compile — `#table9` covers two side-by-side tables (2026-09-28)

**Serves:** prog:criterion:etkl:03 — cbh must NOT be accepted on its 1.0 score; this note says why.

**Topic:** jev-reading · **Date:** 2026-09-28 · **src measured:** `6eb80ca` · **Doc impact: none.**

## 5. Next action (written first)

- **Asserted:** do not accept cbh at 1.0. Its old hold's condition ("where did the 86 tokens go")
  was met by PR #280/#281, but meeting it uncovered a misread region. The ons acceptance used the
  test "none of it is a misread entry", and cbh fails that test.
- **Proposed, for a fresh session (spec, then src/):** split `#table9` at the author's drawn
  marks. Each of the two tables has its own filled title bar, its own boxhead and its own ruled
  box, with an empty gutter between them (x≈690–830). The result should be two `tab:RecordTable`s:
  - stock-at-port, 7 columns × 4 ports;
  - shutdown dates, 2 columns × 4 ports.

  Alongside the two tables, the "Note:" block should become notes rather than entry rows, and
  1,951,264 should go to the ship-roster table above it (R74: that table's exact grand total).
  - **Refutable in minutes:** PR #277 recorded that drawn marks can dispose an extent on cbh. The
    fresh session re-checks that on this region first. If the ruled boxes don't tile these two
    tables exactly, this arm is wrong.
  - **Concern first:** the ink score will probably not move, or will fall (compare PR #280, where
    forcing boxes gave 0.9095→0.8251). That is because the score is blind to this defect: every
    word here is "asserted" today. The oracle has to be structural, meaning table count, column
    count and cells per row, pinned as a carriage test like `tab:11`. It cannot be the score.

## 3. Measured (`compile_document`, offline, HEAD `6eb80ca`)

`#table9` today is one `RecordTable` with 3 `HeaderNode`s, 3 `LeafColumn`s and 9 `LeafRow`s:

- **Label cells:** `lc0` "Stock at Port (Main Storage Area) as at 29/07/2026" (x 39),
  `lc1` "PORT MAINTENANCE SHUTDOWN DATES - 2026" (x 545), and `lc2` "1,951,264" (x 812, a
  **number read as a label**).
- **Entry cells:** each one holds a **whole line** of one table. For example, `e1_0` = "PORT WHEAT
  MAIN WHEAT GRADES BARLEY CANOLA OTHER TOTAL" (the left table's boxhead as one entry), `e2_0` =
  "ALB 129,183 APW1/ASW9/AWW1 27,023 3,345 1,293 160,845", and `e1_1` = "ALB 1 - 15 October".
  `e6_0`…`e9_0` are the Note paragraph.
- **The page:** a render of y≥670 shows two separately boxed tables, each with a blue title bar,
  plus the notes below the left one and the total at the far right.

This extends R74. That row said the data grid leaks one line. The compile path does worse: it
merges two whole tables and a notes block into a single 2-column table.
