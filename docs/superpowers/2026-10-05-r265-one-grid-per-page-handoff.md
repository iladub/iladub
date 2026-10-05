# Evidence + handoff: R265's typing fix is right, but it lowers bfs because the data grid reads one table per page (2026-10-05)

**Serves:** prog:criterion:etkl:03 — R265 is sequenced before R289, the named blocker on lifting cbh's hold.

**Topic:** r265-one-grid-per-page · **Date:** 2026-10-05

**Doc impact: none.**

Branch `r265-grouped-numbers` holds the R265 fix and its test. **It is not merged:** it lowers bfs
from 0.9021 to 0.8706. This note gives the cause, which is measured, and the remedy, which is
proposed. Part 5 was written at about 95K working tokens. That is over the 50K floor for originating
work, so each action below is graded.

## 5. Next concrete action (written first)

1. **PROPOSED: make `datagrid.derive_data_grid` re-seed over the lines its first grid leaves, so it
   produces one grid per recurring signature class rather than one per page. Then land R265 on top.**
   - **Evidence (§ 2.3):** on bfs p5 under the new typing, a second seed over the leftover lines
     gives a clean 19-row × 12-column year table, all `Quantity`. That is about 270 + 228 cells,
     against the old accidental 496.
   - **What may be wrong:**
     - The counterfactual filtered `text_lines` by `top`, which is not how a shipped re-seed would
       work.
     - Adoption, emission and the ledger all assume one grid per page: the `#p<n>-datagrid` URI,
       `DATAGRID_RESIDUE`, `_led.touched`, and `document.py`'s superseded-band withdrawal. Two grids
       touch all of them.
     - A second seed on other pages could adopt fragments. Two matching footnote lines are enough
       to make a signature "recurring".
   - **The falsifier:** a whole-corpus snapshot diff (`scripts/corpus_verdict_snapshot.py` before
     and after, then `corpus_snapshot_diff.py`). The prediction is bfs ≥ 0.9021 and the other 6
     documents IDENTICAL. Anything else is a finding, not a pass.
2. **ASSERTED: do not merge R265 alone, and do not hand `datagrid` the old typer.** Keeping a second,
   wrong typing only to preserve a score is the overfitting that the zero-tolerance rule forbids.
   The old 496 cells were an artefact (§ 2.2).
3. **ASSERTED: R289 stays sequenced after R265**, as in `2026-10-05-r289-typing-not-scope-handoff.md`
   part 5.

## 1. Goal

Land R265: type space-grouped numbers, sign-separated numbers and U+2212 negatives as `tab:Numeric`.

## 2. Findings

### 2.1 The fix and its blast radius (measured)

- `celltype.is_grouped_number` is an SI/ISO 31-0 format grammar, wired into `_cell_datatype`.
  `headers.is_numeric` is deliberately left alone: it is the one parser
  `rows._numeric_token_sum` sums with, and it would read `3 465` as 3 + 465.
- The test `test_grouped_number_types_numeric_r265` was falsified: with the wiring removed, it
  fails on `3 465` → Text.
- Whole-corpus snapshot diff at `4379fbe`, before vs after: **6 of 7 documents are IDENTICAL to the
  triple hash.** bfs is CHANGED: 0.9021 → 0.8706, and on p5, cells 496 → 450, asserted tokens
  936 → 628, chains 9 → 11.

### 2.2 The bfs drop is the data grid's seed, not the split (measured)

- **The grid's typing alone causes the whole drop.** Patching the old typer into
  `datagrid._cell_datatype` only gives bfs exactly 0.9021 (p5 496 cells). Patching it into
  `celltype` instead still gives 0.8706.
- `derive_data_grid` seeds **one grid per page**: the recurring row signature with the largest
  `len × count`. bfs p5 holds two tables:

| typing | year table (12 runs) | canton table (10 runs) | seed | grid |
|---|---|---|---|---|
| old | 15 rows share a signature: 180 | split over 4 signatures, because `- 939` was Text: 90 | years | 46 rows, years + cantons |
| new | 18 rows: 216 | **27 rows: 270** | cantons | 27 rows; all 19 year rows `unplaceable` |

- Under the old typing, the canton rows happened to fit the year table's 12-column universe, so the
  46-row grid that [[R238]] verified came from mistyped cells. The change column (`- 3 933`) was
  family `Text`, which made it a non-measure.

### 2.3 A second seed recovers the year table (measured, counterfactual)

The counterfactual re-ran `derive_data_grid` under the new typing on the lines that grid 1 did not
admit, by filtering `text_lines` on `top`. The result is grid 2: 19 rows × 12 columns, every column
`Quantity`, covering 2005–2023 with the change column now a measure.

## 3. Decided, and where

- R265 is **held**, not merged. This is an agent call recorded here; per the 2026-09-18 ruling, a
  loop that lowers a corpus score does not ship.
- The single-grid limit is raised as [[R290]].

## 4. Unverified or assumed

- Nothing here was run through the local corpus test sweep. The branch's corpus pins (for example
  bfs p5 = 496 cells) will fail as long as the branch is held.
- The second grid's cell count (about 228) is 19 × 12 and was not emitted.

## 2b. Where the primaries are

- Fix: `src/iladub/etkl/celltype.py` (`_GROUPED_NUMBER`, `is_grouped_number`). Test:
  `tests/etkl/test_celltype.py::test_grouped_number_types_numeric_r265`.
- Probes (session scratchpad, not kept): a recompile with the old typer patched per module; a
  signature census of `derive_data_grid`'s seed under both typings; a second seed over the lines
  grid 1 did not admit. Each one is about 20 lines over `iladub.etkl.datagrid` and can be rebuilt
  from § 2.2–2.3.
