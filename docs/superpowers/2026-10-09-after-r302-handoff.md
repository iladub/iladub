# Handoff: after R302, the rulings ratified and `grid_idx` pinned (2026-10-09)

**Serves:** maintenance. Closes R302 and records four maintainer rulings.

**Topic:** compile · **Date:** 2026-10-09

Written at ~73K working tokens, 1.45× the 50K originating floor (pre-flight logged as `handoff`).
Part 5 is graded per action.

## 5. The next concrete action, typed

1. **PROPOSED (graded: low confidence, choice of subject not made).** The standing ruling is "held-out
   corpus, then contracts" (the 2026-10-06 handoff). The held-out rows still open are R300 (fed-h41's
   adopted p3/p5/p10 reports name `pN/adopt#htableK` while the graph holds `pN#htableK`), R299
   (Caltrain heading admitted as data, which blocks `tab:ClockTime`), and R295 (Caltrain's score is
   blind to NON_TABLE pages). The maintainer picks one. R300 *looks* smallest because it is a URI
   mismatch on a document the last three loops measured, but its cause has not been measured. It
   could be R298's class (a dangling link that adoption depends on), and R298 un-adopted bfs p6 when
   it was resolved. **Run first:** open the full R300 row, then check whether the `/adopt` URI is the
   re-compile's `adopt_doc` (`document.py`, adoption pass) leaking into the installed report. That
   costs minutes. If it is not the cause, this action is wrong.

## 1. Goal

Ratify the pending R301 rulings, and run R302 under them.

## 2. Where the primaries are

- `tests/etkl/test_r302_grid_idx.py`: the module docstring states the reachability argument, and each
  test names its falsification.
- `tests/etkl/fixtures.py`, `isolated_rows_grid_pdf(ruled_cell=True)`: the only synthetic shape that
  reaches fallback → guard escalation.
- `~~R302~~` in `docs/superpowers/residues-closed.md`: the measurement and both falsifications.
- `tests/etkl/test_escalation_furnish.py`: `_EVIDENCE` and
  `test_census_counts_a_guard_refusal_as_the_query_does`.

## 3. What was decided, and where it is recorded

The maintainer ruled on 2026-10-09 in this session. The record is **this file** and the PR body, since
PR #325's body only proposed them:

- **R301 ruling 1 RATIFIED.** In § 8 S1, the most specific (longest) owning table URI space wins.
- **R301 ruling 2 RATIFIED.** A withdrawn table's report carries `header_reading=None`.
- **R301 ruling 3 RATIFIED.** `grid_idx = len(pages[p].regions)` stays. Spec § 2.5's band count is
  refuted. R302 runs under it.
- **`_census` ALIGNED with the query.** The maintainer chose "align" over "leave as is". It counts
  `("escalated", "refuse")`. The R303 closed row's line "Unruled: `_census` …" is Evidence, so it is
  not edited. This entry supersedes it.

Decided by the executor, recorded in the R302 closed row: the handoff's proposition that a page
adopting over a fallback region "can be built with the existing synthetic helpers" is **REFUTED**.
R302 closed by its second arm instead of being parked.

## 4. Unverified or assumed

- The unreachability of "fallback, then adopted" is **measured on one shape** and argued in general.
  The argument rests on three readings of the code, none of them a test: (a) the fallback precondition
  means no band asserted or escalated; (b) between the fallback and the adoption gate only
  `ruleguard.guard` moves `escalated_total`; (c) `derive_data_grids` is deterministic. Test 1 pins
  only the consequence on the fixture.
- The full non-corpus suite runs in CI's `test` check. Locally only the files that use the fixture
  and the register run: 68 + 208 + 11 passed. Corpus tests were not re-run. No `src/` line changed.
