# Handoff — Loop 1 mid-execution, Task 1 of 4

**Date:** 2026-08-17 · **Branch:** `loop1-gate-and-label` (NOT `main`), base `a1d394b`
**Written at:** 155.1K tokens, past the 150K executing floor — which is why the remaining three
tasks belong to a fresh session. Task 1 was dispatched and is finishing as this is written.

## Goal

Finish executing [`../superpowers/plans/2026-08-17-the-gate-and-the-label.md`](plans/2026-08-17-the-gate-and-the-label.md)
under superpowers:subagent-driven-development: Task 1 (R104, the label) → Task 2 (R102, the gate) →
Task 3 (CLAUDE.md + register pass) → Task 4 (R103's probe measurement) → final whole-branch review.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `.superpowers/sdd/2026-08-17-the-gate-and-the-label/progress.md` | **THE LEDGER — read this first.** It is the recovery map: the pre-flight conflict scan, four pre-execution rulings, and a `Task <N>: complete` line per finished task. **A task with a completion line is DONE — do not re-dispatch it.** Resume at the first task without one. |
| `.superpowers/sdd/…/task-{1,2,3,4}-brief.md` | The four task briefs, already extracted. Dispatch implementers with the brief path — never the whole plan file. |
| `.superpowers/sdd/…/task-1-report.md` | Task 1's report, including its FALSIFICATION block. Written by the implementer; check it exists before reviewing. |
| `docs/superpowers/plans/2026-08-17-the-gate-and-the-label.md` | The contract. Four tasks, four falsifications, the stopping points, the definition of done. |
| `docs/superpowers/specs/2026-08-17-the-gate-and-the-label-design.md` | **The binding authority.** Plan/reviewer conflicts resolve against the spec, not the plan. §7 is the scope fence; §9 the oracles. |
| `docs/superpowers/2026-08-17-loop1-handoff.md` | The pre-execution handoff: what the spec settled, and the five things it left unverified. |

## What was decided, and where each decision is recorded

1. **Work happens in the PRIMARY working copy on branch `loop1-gate-and-label`, not a git worktree.**
   `corpus/` is gitignored, so a worktree would not have it and Tasks 2 and 4 need it. **Consequence:
   subagents must run strictly sequentially** — a shared working copy plus parallel git-writing agents
   interleaves HEAD moves. Recorded in the ledger's header.
2. **Four pre-execution rulings** — line-drift in Task 3's citation, the naming of Task 1d's two
   raising functions, Task 1d's structural test standing as plan-mandated, and CLAUDE.md's edit being
   pre-cleared by the maintainer's explicit request. **All four are in the ledger's § Rulings**, each
   with what it costs if wrong. Carry them forward; Ruling 1 in particular binds Task 3.
3. **Implementers must run suites inline, never backgrounded.** Task 1's implementer stalled waiting
   on a Monitor'd background suite and had to be nudged. Put this in every remaining dispatch:
   *scoped suite for iteration, one inline full `pytest -q` at the end.* Recorded here only.
4. **Model selection:** sonnet for implementers and task reviewers, the most capable model for the
   final whole-branch review. Recorded here only.

## Unverified or assumed

- **Task 1's outcome is unknown at the time of writing.** It had not reported DONE. **Read
  `task-1-report.md` and the git log before assuming anything about it** — including whether its
  FALSIFICATION block exists. If it is absent, the task review fails; that is plan rule 4, not a
  judgment call.
- **No task review has run yet.** Task 1 needs `scripts/review-package` + a task reviewer before it
  gets a completion line.
- **Everything the plan lists as a seam is still unmeasured**, in particular: whether any *production*
  caller invokes `compile_tables` outside `compile_document` (Task 2, and it bounds how wide R102's
  close is), whether `tests/etkl/test_vacuity_registry.py` stays green after ungating, and whether any
  `docs/wiki/` page states the membrane gate (Task 3).
- **The corpus measurements have not been taken:** T2b's 316-with-gate / 0-without pair, the corpus
  wall-clock delta, and Task 4's `tab-datagrid.ttl` count.
- **Nothing has been pushed and no PR exists.** The branch is local.

## The next concrete action

**In a fresh session: read the ledger, then resume superpowers:subagent-driven-development at the
first task without a `complete` line.** For Task 1 that means generating the review package
(`scripts/review-package <plan> a1b2c3d <HEAD>` with BASE `a1d394b`) and dispatching the task
reviewer; for a later task, dispatching its implementer with its already-extracted brief.

Do not re-run the pre-flight scan — it is in the ledger. Do not re-write the spec or the plan.
