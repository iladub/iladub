# Handoff: box-split execution, Tasks 3 onward (2026-09-28)

**Serves:** prog:criterion:etkl:03 — cbh is not accepted until `#table9` compiles as the two tables the author drew.

**Topic:** box-split · **Date:** 2026-09-28 · **Doc impact: none.**
**Authored at:** ~146K working tokens, as the controller of a subagent-driven execution nearing the
150K executing floor. Parts 1–4 are pointers. Part 5 is graded per action.

## 5. Next action (written first)

- **Asserted:** in a fresh session, invoke `superpowers:subagent-driven-development` on
  `docs/superpowers/plans/2026-09-28-box-split.md`. Its workspace is
  `.superpowers/sdd/2026-09-28-box-split/` (gitignored). **Read `progress.md` there first.** The
  tasks marked `complete` are done, so do not re-dispatch them. Resume at **Task 3**. Then do Task 4
  Steps 4–5 (reuse `task-4-brief.md`, scoped to "Steps 4–5 + the closing FALSIFICATION"), then
  Task 5, then Task 6.
- **Proposed, and it may fail:** Task 4 Step 4 expects O2 to XPASS once Task 3 lands. Spec § 4
  risk 1 names the known way it can fail: T2's first row read as a boxhead. If it fails, the plan
  says **stop and record the graph as a finding, never weaken O2**. Budget for this.
- **Proposed:** Task 3 Step 3 moves two literals, `tests/etkl/test_typing_equiv.py`
  `EXPECTED_VERDICTS["cbh"]` and `test_run_merge_seam.py` `BASELINE_ASSERTED[("cbh-stem-2026-08-03", 0)]`.
  They must be **re-measured**, not re-pinned (evidence file § 2).

## 1. Goal

Finish the plan: split cbh p0 raw band 9 at its two closed boxes (Task 3), then flip `tab:12`,
then run the controls C1/C2 and raise the register row (Task 5), then open the PR (Task 6).

## 2. Where the primaries are

- **Ledger**: `.superpowers/sdd/2026-09-28-box-split/progress.md`. It holds the pre-flight table,
  every `Ruling:`, the deferred minors, and the per-task completion lines, and it ends with a
  RESUME NOTE. The workspace also holds the task briefs and reports, and
  `reviewer-instructions.md`, a shared reviewer brief.
- **Evidence file**: `docs/superpowers/2026-09-28-box-split-evidence.md`.
  - § 1 is the baseline: corpus hashes, the determinism null, and the cbh rosters.
  - § 2 is the positional-dependents census.
  - The "before" corpus snapshot is at `internal/benchmarks/box-split-2026-09-28/before/run1`.
    It is gitignored, so it exists only on this machine.
- **Commits on `box-split`**: see `git log main..box-split`. The code is in `src/iladub/etkl/boxes.py`
  (Task 1) and `src/iladub/etkl/boxsplit.py` plus `vocab/queries/band-boxes.rq` (Task 2).

## 3. What was decided, and where it is recorded

Every controller ruling is a `Ruling:` line in the ledger. It is recorded **nowhere else**, which
makes it reversible. The load-bearing ones for the remaining tasks are:

- **R2**: band indices are page_bands' `raw_bands` indices.
- **Exact `(top, x0)` order is kept.** Float noise sorts cbh's right box first.
- **"Belongs" stays PROCEDURAL in Python**, and the query only counts. The final review may revisit this.
- **Wordless boxes belong to no band.** This guards against a stroked rect being read as a closed box.
- **O2 asserts T2's port column exactly.**

The final message must list every `Ruling:` line (the skill's § Finish).

## 4. Unverified or assumed

- Whether O2 XPASSes after Task 3 (spec § 4 risk 1). This is unmeasured.
- Where the Note residue and `1,951,264` land after the split. This is unmeasured; Task 5 records it.
- The snapshot hash collapses blank-node labels to `_:b`, so a C2 hash match is necessary but not
  sufficient evidence of no change (ledger, Task 0 minor).
- Spec § 0 R-c calls the touch test AXIOM, while spec § 6 calls it PROCEDURAL. The code follows § 6.
  Nobody has ruled on this yet.
