# Handoff — Tasks 1-3 complete and reviewed clean; Task 4 in flight, 5-6 remain

**Topic:** the arc / M19 · **Date:** 2026-08-23 · **Branch:** `the-worktree-that-resolves`
**Runner:** `./.venv/bin/python`, never `python3`.
**Shape: executing, written at ~110k** — under the 150k executing floor, deliberately early.
The ledger, not this file, is the resumption state.

## §1 Goal

Finish executing `docs/superpowers/plans/2026-08-23-the-worktree-that-resolves.md` under
`superpowers:subagent-driven-development`. Tasks 1, 2 and 3 are complete with clean reviews.
**Task 4 was dispatched (opus) at BASE `95bfb9a` and may still be running** — check
`git log --oneline 95bfb9a..HEAD` and `task-4-report.md` before assuming anything about it.

## §2 Where the primaries are

| primary | what to establish there |
| --- | --- |
| `.superpowers/sdd/2026-08-23-the-worktree-that-resolves/progress.md` | **the ledger — read this first.** Pre-flight table, rulings PF-1…PF-4 plus the brief-re-extraction ruling, every task's completion line and deferred minors. Trust it and `git log` over any recollection |
| `docs/superpowers/plans/…-the-worktree-that-resolves.md` | the plan (amended: PF-4 correction is in Task 3 Step 5, PF-1 is Task 3 Step 3 invariant 5) |
| `docs/superpowers/specs/…-the-worktree-that-resolves-design.md` | the spec — the binding authority. §7 oracle 2 carries a struck-through correction |
| `…/task-{1..6}-brief.md`, `task-{1..4}-report.md` | briefs 3 and 6 were RE-EXTRACTED after the plan amendment; 4 and 5 were already current |
| `tests/test_arc_ablation.py` | M19. **Every line number in every brief is stale** — Tasks 1-3 shifted them. Locate by content |

## §3 Commits so far

| task | commits | verdict |
| --- | --- | --- |
| 1 — probe module + explicit `PYTHONPATH` on `_run_module` | `256955b..7e4f84c` | review clean |
| 2 — `_MATERIALISED`/`_declared_inputs`/`_materialise` + disjointness collision guard | `6f977b6..2d08f06` | review clean |
| 3 — `_run_control`, the un-ablated control run | `2d08f06..95bfb9a` | review clean |
| 4 — collection ERROR names the removed artifact (R118) | dispatched at `95bfb9a` | unknown at write time |

## §4 Rulings made in this session (the maintainer's to undo)

1. **Re-extract each brief before dispatching it.** The six briefs were extracted at 08:03,
   *before* the PF-4 plan amendment. The on-disk Task 3 brief still carried the unsatisfiable
   falsification #1 and only five Step 3 invariants; dispatching it would have re-introduced the
   defect PF-4 had just removed. Re-extracted 3 and 6; 4 and 5 were byte-identical.
   **Cost if wrong: none** — the plan is the source of truth and the extraction is mechanical.
2. **Task 4 goes to opus, not sonnet.** The plan's own Unverified §2 names it the likeliest place
   a plan-supplied test turns out unwritable, and it needs three measured probe constants, a regex
   widening and a path-form judgment. **Cost if wrong: one expensive dispatch.**
3. **Removed a pre-existing leaked git worktree** (`…/T/arcci/wt`, detached `2a19171`, created
   07:04, `arcci` prefix — not from this branch's code, which uses `arc-m19-*`). `git worktree
   list` now shows the main tree only. **Cost if wrong: a throwaway detached worktree that any
   M19 run would have recreated.**

## §5 Unverified or assumed — not empty

1. **Whether §4.1 flips any live pair is still unknown.** `ablation_refusals` has not been run to
   completion against the live manifest since Tasks 2-3 landed. Spec §9 predicts zero new edges;
   that is a prediction, and Global Constraint 9 forbids tuning it away if it is wrong. Task 6
   settles it.
2. **Seam S2 was still unmeasured when Task 4 was dispatched** — which pytest flag puts a
   collection ERROR's exception in `proc.stdout`. Task 4 Step 1 owns the measurement. The module
   docstring's claim is a candidate, not a measurement.
3. **`_ERROR_PROBE` / `_UNRELATED_REMOVAL` were not known to exist.** Task 4 owns finding or
   constructing them.
4. **The plan is 1168 lines against a 338-line spec** — a worse ratio than the 919-line plan
   CLAUDE.md holds up as its counter-example. It contains no function bodies (verified: zero
   non-test `def`s) and the bulk is measurement transcripts plus verbatim tests, so it is not the
   rule-1 violation the ratio suggests. **Flagged to the maintainer, not ruled on.**
5. **No adversarial review has run on the spec.** PF-4 shows that class of reading catching a real
   spec defect, so it is live.

## §6 Deferred minors, for the final whole-branch review

- Task 1: `tests/test_arc_ablation.py` module docstring limitation 4 is stale — describes the
  pre-fix hazard as current. **Already owned by Task 5 Step 1.**
- Task 2: the `ablation_refusals` collision guard sits after the pre-existing `dangling`/`testless`
  assertions rather than literally first. Both are filesystem-free, so "before any worktree" holds;
  wording gap only.

## §7 The next concrete action

If Task 4 has landed: build its review package
(`scripts/review-package <plan> 95bfb9a HEAD`) and dispatch the task reviewer, telling it to judge
the S2 measurement and the three probe constants as *measurements owed*, and that Step 6 requires
**both** inversion directions. Then Tasks 5 and 6 in order — re-extract each brief first.
Task 6 runs `ablation_refusals` live; **a newly grounding pair is a FINDING to record, never a
result to suppress or tune away** (Global Constraint 9). Finish with the whole-branch review on
the most capable model, pointed at §6's minors.
