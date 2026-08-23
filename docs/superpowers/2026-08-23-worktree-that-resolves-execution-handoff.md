# Handoff — the plan is written and Task 1 is committed but UNREVIEWED

**Topic:** the arc / M19 · **Date:** 2026-08-23 · **Branch:** `the-worktree-that-resolves`
**Runner:** `./.venv/bin/python`, never `python3`.
**Shape: executing, stopped at 189k** — past the 150k executing floor. Six SDD tasks remain to be
coordinated; the ledger, not this file, is the resumption state.

## §1 Goal

Finish executing `docs/superpowers/plans/2026-08-23-the-worktree-that-resolves.md` under
`superpowers:subagent-driven-development`. **Next action: dispatch the Task 1 task reviewer**
(§5). Task 1's code is committed but nothing independent has checked it.

## §2 Where the primaries are

| primary | what to establish there |
| --- | --- |
| `.superpowers/sdd/2026-08-23-the-worktree-that-resolves/progress.md` | **the ledger — read this first.** Pre-flight scan table, four rulings (PF-1…PF-4), the Task 3 measurement, and the stop point. It is the recovery map; trust it and `git log` over any recollection |
| `docs/superpowers/plans/2026-08-23-the-worktree-that-resolves.md` | the plan. §Measurements M1–M10 are its own re-derivations; §Named seams S1/S2; §Rule-5 reconciliation; six tasks; §Unverified at plan time |
| `docs/superpowers/specs/2026-08-23-the-worktree-that-resolves-design.md` | the spec — the binding authority the plan argues from. §7 oracle 2 now carries a struck-through correction |
| `.superpowers/sdd/2026-08-23-the-worktree-that-resolves/task-{1..6}-brief.md` | all six briefs already extracted. `task-1-report.md` holds Task 1's S1 transcripts, TDD and falsification evidence |
| `.superpowers/sdd/2026-08-23-the-worktree-that-resolves/review-256955b..7e4f84c.diff` | Task 1's review package, already written. Hand this path to the task reviewer |
| `tests/test_arc_ablation.py` | M19. Line numbers in the plan predate Task 1 — locate by content |

## §3 What was decided, and where each decision is recorded

| decision | recorded where | status |
| --- | --- | --- |
| PF-1 — Task 3's control wraps a `RuntimeError` escaping `_ablate` and re-raises it with the `_declared_inputs` partition | ledger **and** plan Task 3 Step 3 invariant 5 | **downgraded to defensive** by the PF-4 measurement; "implement it, do not build a test around it" |
| PF-2 — every path comparison `.resolve()`d (macOS `/tmp` → `/private/tmp`, `/var/folders` → `/private/var/folders`) | ledger; the plan's probe code already complies | applied in Task 1 |
| PF-3 — no nested git worktree; the branch is the isolation, because M19 creates and prunes worktrees of `REPO` itself | ledger only — **reversible** | held for Task 1 |
| PF-4 — spec §7 oracle 2 / plan Task 3 falsification #1 are unsatisfiable; replaced | ledger, plan Task 3 Step 5, **and** spec §7 oracle 2 | **settled by measurement**, command inline in all three |
| S1 (inherited `PYTHONPATH`) is unset in both shapes measured | `task-1-report.md` | settled; the implementation still handles a set value |
| `etkl:01`'s oracle is the PARAMETRIZED corpus id at `arc-manifest.ttl:149ff`, not `:158` | ledger + plan Unverified §3 (struck) | settled by measurement |

## §4 Unverified or assumed — not empty

1. **Task 1 is UNREVIEWED.** `7e4f84c` is self-reported DONE. No task reviewer has run, so its
   spec-compliance and quality verdicts do not exist. Do not treat it as complete.
2. **S2 is still open** — which pytest flag puts a collection ERROR's exception in `proc.stdout`.
   Plan § Named seams. It belongs to Task 4 and must be measured before that rule is written.
   The module docstring's claim at `:169-170` is a candidate, not a measurement.
3. **Task 4's `_ERROR_PROBE` / `_UNRELATED_REMOVAL` pair is still not known to exist.** Plan
   Unverified §2 calls this the likeliest place a plan-supplied test turns out unwritable. Nobody
   has looked.
4. **Task 2's collision fixture has never been built or validated.** The membrane checks that the
   `prog:oracleArtifact` triple exists, not that the file does (`tests/arc-shapes.ttl:273-354`) —
   checked — but no fixture has been run through `validate_manifest`.
5. **Whether §4.1 flips any live pair is still unknown.** `ablation_refusals` has not been run
   since Task 1 landed. Spec §9 predicts zero; that is a prediction.
6. **The plan is 1168 lines against a 338-line spec** — a worse ratio than the 919-line plan
   CLAUDE.md holds up as its counter-example. It contains no function bodies (verified: zero
   non-test `def`s), and the bulk is measurement transcripts plus verbatim tests. Flagged to the
   maintainer, not ruled on.
7. **No adversarial review has run on the spec.** The plan is a second reading of its numbers, not
   of its design — and PF-4 shows that reading catching a spec defect, so the class is live.

## §5 The next concrete action

Dispatch the Task 1 task reviewer (`superpowers:subagent-driven-development`,
`task-reviewer-prompt.md`) with three paths: `task-1-brief.md`, `task-1-report.md`, and
`review-256955b..7e4f84c.diff`, plus the plan's Global Constraints block verbatim. Then continue
the task loop at Task 2. Do not re-dispatch Task 1's implementer — its work is committed.
