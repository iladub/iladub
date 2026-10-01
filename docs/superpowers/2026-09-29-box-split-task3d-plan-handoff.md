# Handoff: box-split — plan Task 3d from the approved spec § 10 (2026-09-29)

**Topic:** box-split · **Date:** 2026-09-29

**Serves:** prog:criterion:etkl:03 — O2 (`tab:12`) is whole only when T2 compiles with no boxhead.

**Doc impact: none** (this handoff). The spec already declares `increment` for § 10.

Authored at 53,180 working tokens (plimslop hook), just over the originating floor. Parts 1–4 are
pointers. Part 5 is graded per action.

## 5. Next actions (written first)

- **Asserted.** A fresh session writes the Task 3d plan from spec § 10 **as amended by § 10.7**.
  Append it to `docs/superpowers/plans/2026-09-28-box-split.md` as a Task 3d, between Task 3 and
  Task 4, or write it as an SDD brief if the maintainer prefers.
  - Use `superpowers:writing-plans` under CLAUDE.md § Plan authoring discipline, rules 1–7.
  - The contract to plan against is § 10.5 plus § 10.7's additions:
    - the `_band_subgraph` seam;
    - MEASURE (vi);
    - U14;
    - the extra FALSIFICATION line.
  - § 10.7 R-2 widens § 10.6's first register row, and R-3 adds one; both go to Task 5.
- **Asserted, after the plan:** execute Task 3d (the maintainer chose subagent-driven development for
  this branch), then Task 4 Steps 4–5, then Tasks 5–6.
- **Proposed, and it may fail:** the worker answers T2 with `0`. No worker has been asked yet.
  - If it answers `1`, that is a finding about the worker (§ 10.5 O2). It is not a reason to lower
    the oracle.
- **Proposed:** remedy (a) is the whole fix for R-1.
  - Only `_band_subgraph` is known to close over reachability from a table.
  - MEASURE (vi) exists to find the others. If it finds one, it needs the same bound, and that is a
    plan finding.

## 1. Goal

O2 XPASSes as a whole: T2 is a RecordTable with 0 header nodes and 4 rows, T1 keeps its 7-column
boxhead, and no adoption regresses.

## 2. Where the primaries are

- **Spec § 10 and § 10.7:** `docs/superpowers/specs/2026-09-28-box-split-design.md`, from
  "## 10. Addendum" to the end. § 10.2's census and § 10.7's probes are the measured parts.
- **The plan to extend:** `docs/superpowers/plans/2026-09-28-box-split.md`, Tasks 0–6. Read its
  Global Constraints and Review Focus before adding a task.
- **The SDD ledger** (gitignored, local only): `.superpowers/sdd/2026-09-28-box-split/progress.md`.
- **The probes** are not durable; they live in a session scratchpad. Their outputs are quoted in
  § 10.7. Rebuild them from § 10.7's text if U14 needs a corpus-side check:
  - `probe_subgraph.py`: a synthetic `ReadingRecorder` with two bands, with and without the edge;
  - `probe_adopt.py`: a spy on `document._band_subgraph` during `compile_document`.

## 3. What was decided, and where it is recorded

- **§ 10 as amended is approved** (maintainer, 2026-09-29, in chat). It is recorded only by this
  handoff and the PR #284 thread; the spec text carries no approval line.
- **R-1's remedy (a):** `_band_subgraph` does not traverse into a `dec:DecisionHolon`. Recorded in
  § 10.7, under "R-1 ruled" (`7627ef2`).
- **The earlier rulings** (form, and the NEURAL decider with a one-way oracle) are recorded in the
  addendum of `docs/superpowers/2026-09-28-box-split-t2-measurements.md`.

## 4. Unverified or assumed

- These are carried over from `docs/superpowers/2026-09-29-box-split-s10-review-handoff.md` § 4:
  - the census witness was computed in Python, not by the `.rq`;
  - the colour value type is unknown;
  - "asked" questions are assumed to dedupe across passes by key;
  - no `tab:hasHeaderNode` consumer has been checked against a table with zero header nodes;
  - the bfs p6 `#table2` reading is inferred from two rows.
- **The pass-2 merge** (`document.py:1549`) was not measured with the edge present. Remedy (a)
  should cover it too, but that is a prediction.
- **Adoption regression is inferred, not run.** The review showed the pointed-into count going
  0 → 4 synthetically, and that adoption withdraws the asked tables today. No compile with an
  answered `0` has been run.
- **`uv run` in this checkout creates an untracked `uv.lock`.** Delete it; never commit it.
