# Handoff: after R303, a refusal is furnished (2026-10-09)

**Serves:** maintenance. R303 is closed on branch `r303-refusal-furnished`.

**Topic:** compile · **Date:** 2026-10-09

Written at ~70K working tokens, under the 150K executing floor this loop ran at, and 1.4× the 50K
originating floor that part 5 is, so part 5 is graded per action.

## 5. The next concrete actions, each one typed

1. **ASSERTED.** The maintainer ratifies, or overturns, the three R301 execution rulings still
   pending since PR #325: S1 most-specific space, `header_reading=None` on an escalated report, and
   the `grid_idx` revert. The PR #325 body carries each one. No code moves until they are ruled, and
   R302 depends on the third.
2. **PROPOSED (graded: medium confidence).** R302 (`grid_idx` unpinned) is a synthetic-fixture loop:
   build a page that adopts over a fallback region, so that pass 1's region count and the
   re-compile's differ. The proposition is that such a page can be built with the existing
   synthetic helpers. Nobody has tried. If it cannot be built, the row says why no corpus page
   reaches it, and R302 may be a parking candidate instead (`scripts/residue_graph.py --candidates`
   lists it).
3. **PROPOSED, a choice for the maintainer.** `_census` in `tests/etkl/test_escalation_furnish.py`
   counts only `"escalated"`, while the query now reads `"escalated"` and `"refuse"`. On bfs the two
   agree (no refusal, measured: O4 byte-identical, `requests == live == 5`). On a document carrying a
   refusal, `requests == live` would fail. Align `_census` with the query, or leave it as is. Not
   ruled.

## 1. Goal

R303 is closed: a region the producer guard withdraws reaches a human through a
`dec:ExpansionRequest`.

## 2. Where the primaries are

- The closed row, `~~R303~~` in `docs/superpowers/residues-closed.md`: every oracle's figure.
- The query, `vocab/queries/escalation-furnish.rq` (its EVIDENCE SET note).
- The pins: `tests/test_r301_fed_h41.py::test_r303_…` (corpus), the furnish test in
  `tests/etkl/test_ruleguard.py`, and `tests/etkl/test_escalation_furnish_plan.py`.

## 3. What was decided, and where it is recorded

- **The spec's `VALUES` became a `FILTER IN`.** It was refuted in execution, and the measurement is
  in the query header, the closed row and commit `e10d5b5`. That was the executor's call, not a
  maintainer ruling: the evidence set is the same closed list of labels, and only its construct
  changed.

## 4. Unverified or assumed

- `tests/etkl/test_vacuity_registry.py` was not run. The prediction that its counts do not move
  rests on O4: the seven corpus documents are byte-identical, and fed-h41 is held-out.
- The full non-corpus suite is left to CI's `test` check. Only the touched and register test files
  were run locally.
