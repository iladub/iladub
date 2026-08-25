# Handoff — continue the `holon:05` loop at Task 3

**Date:** 2026-08-25 · **Branch:** `holon-05-plan` · **Shape: mechanical** — pointers only.
It restates nothing from the primaries and settles nothing they settle.

**Why this exists:** the controlling session crossed the 150k executing floor
(`managing-context-budget`) with five tasks left. Tasks 1 and 2 are shipped and reviewed.

## Goal

One line: **finish executing `docs/superpowers/plans/2026-08-25-the-membrane-reports-its-health.md`,
Task 3 through Task 7**, under `superpowers:subagent-driven-development`.

## Where the primaries are, and what to establish at each

| open | to establish |
|---|---|
| `.superpowers/sdd/2026-08-25-the-membrane-reports-its-health/progress.md` | **THE LEDGER — read this FIRST and in full.** It is the recovery map: the pre-flight conflict scan (12 cross-task rows + 7 self-consistency rows), four pre-flight rulings R-PF1–R-PF4 (two since resolved by measurement), and every task's completion line. Tasks with a `Task N: complete` line are DONE — do not re-dispatch them. |
| the same directory's `task-N-brief.md` | **Briefs for all 7 tasks are already generated**, each with the plan's Global Constraints and the four controller rulings appended. Dispatch from the brief; never make a subagent read the whole plan. |
| `.../task-2-report.md` | Task 2's measurements (S6, S3), its TDD evidence, and its six-inversion `## FALSIFICATION` block. Read it only if Task 3 or 4 needs a fact about `_seal`. |
| the plan, `docs/superpowers/plans/2026-08-25-the-membrane-reports-its-health.md` | § Global Constraints, § Measurements M1–M9, § Named seams, § Rule-5 reconciliation. **M9 is the plan's own finding and the one an executor is most likely to skip.** |
| the spec, `…/specs/2026-08-25-the-membrane-reports-its-health-design.md` | Read where the plan **cites** it — §4.3 (Task 3's query contract), §4.8 (Task 5's shape), §4.9 (Task 6's tripwire + fallback), §7, §9, §11. The plan cites rather than re-derives, so the citation is not optional reading. |
| `CLAUDE.md` § Plan authoring discipline rule 4 | **Per task:** no `## FALSIFICATION` block ⇒ the task review fails. |

## What was decided in the controlling session, and where each decision is recorded

**All of it is in the ledger and nowhere else — therefore reversible.**

- **R-PF1 (RESOLVED by measurement).** Task 7's `etkl-holons.ttl:75-89` citation is correct after
  Task 1: `:75` is `etkl:MembraneHealth a owl:Class`, `:89` is `etkl:membraneHealth`'s closing comment.
  Task 1 appended below the block, so nothing drifted. Task 7 re-verifies anyway.
- **R-PF2.** `MEMBRANE_HEALTH_RQ` was declared in Task 2 as an inert `Path`; `_seal`'s **invariant 6
  (running the health query) is deliberately NOT yet implemented** — it is Task 3 Step 4. No stub `.rq`
  exists. Task 3 creates the file and wires the call on **both** paths.
- **R-PF3 (RESOLVED by measurement).** Task 4's plan-supplied literal
  `"document-level facts failed dec: SHACL:"` was unmeasured at plan time. Task 2's substituted O10
  test asserts it and **passes**, so Task 4 may use it as written.
- **R-PF4.** O11 is the `MembraneRefusal`-subclass check, not "the page site is unchanged". No test
  about `compile.py` is owed by any task.
- **Ruling — the test file's unused imports stay** (`_validate`, `ILADUB`, `PROV`). Tasks 3 and 4 use
  all three verbatim, and CI runs no linter.
- **Ruling — two Minors were folded into Task 2's fix round** rather than deferred, because both were
  one-line comment edits inside code the Important finding already reopened.

## Unverified or assumed

- **Tasks 3–7 have not been started.** No `.rq`, no shape, no fixture, no record change exists.
- **S1, S2, S4, S5 are open BY DESIGN** and each is a Step 1 of its task. S3 and S6 were **closed by
  Task 2's measurements** — read them in `task-2-report.md`, do not re-derive.
- **Plan M2's census does not reproduce.** It claims 17 `AssertionError` interceptors; Task 2 measured
  **7**. The substantive claim (all isinstance-based, zero `type(e) is`) holds and is stronger. Treat
  other plan counts as re-measurable, not as facts.
- **The plan's O10 test was a defect** — it passed with its own subject deleted, because an rdflib
  `Graph` is a set and an unmutated re-entry mints an identical triple. It was substituted with a form
  driven by the measured R127 lever. **The lesson generalises: every plan-supplied test in Tasks 3–7 is
  a proposition** (Global Constraint 7).
- **The suite baseline `1312 passed, 7 skipped, 1 xfailed` in 2386.82 s is the SPEC's**, measured
  before any implementation and **never re-run**. ~40 min. Task 7 Step 6 is where it gets tested; a
  lower passed count is a finding, not a rounding error.
- **Two Task-2 minors are deferred to the final whole-branch review**, both in the ledger: a report-prose
  line-number slip (corrected in prose, source unaffected), and `MembraneRefusal` not being
  reconstructible from `args` (an uncallable pickle — not live, nothing here pickles exceptions).
- **`graincorp-stem` and `cbh-stem` were never compiled for the escalation census** (plan M8). apple's
  lever is *applicable* but its refusal is unmeasured — that is S1, Task 4's Step 1.

## The next concrete action

**In a fresh session: read the ledger, then execute Task 3** — create `vocab/queries/membrane-health.rq`
against spec §4.3, and wire `_seal`'s invariant 6 on both the returning and the raising path. Dispatch
from `task-3-brief.md`. **Do not start Task 4 before Task 3 is green** — Task 4 asserts against Tasks 2
and 3 exactly as shipped, and implements nothing itself.
