# Handoff — continue the `holon:05` loop at Task 5

**Topic:** the `holon:05` membrane-health loop — Tasks 1 through 4 are shipped and reviewed; the work
is executing the plan from Task 5 through Task 7.

**Date:** 2026-08-25 · **Branch:** `holon-05-plan` · **Shape: mechanical** — pointers only.
It restates nothing from the primaries and settles nothing they settle.

**Why this exists:** the second controlling session crossed the 150k executing floor
(`managing-context-budget`) and was directed to finish Task 4 and stop. **Tasks 1, 2, 3 and 4 are
shipped and reviewed.** This supersedes `2026-08-25-holon-05-task-3-handoff.md`, which is spent.

## Goal

One line: **finish executing `docs/superpowers/plans/2026-08-25-the-membrane-reports-its-health.md`,
Task 4 through Task 7**, under `superpowers:subagent-driven-development`.

## Where the primaries are, and what to establish at each

| open | to establish |
|---|---|
| `.superpowers/sdd/2026-08-25-the-membrane-reports-its-health/progress.md` | **THE LEDGER — read this FIRST and in full.** The recovery map: the pre-flight conflict scan, rulings R-PF1–R-PF4, every task's completion line, and every `Ruling:` taken since. Tasks with a `Task N: complete` line are DONE — do not re-dispatch. |
| the same directory's `task-N-brief.md` | **Briefs for all 7 tasks are pre-generated**, each with the plan's Global Constraints and the four pre-flight rulings appended. Dispatch from the brief; never make a subagent read the whole plan. |
| `.../task-3-report.md` | Task 3's measurements, its TDD evidence, its seven-inversion `## FALSIFICATION` block, and the appended `# FIX REPORT — review round 1`. Read it if Task 4 needs a fact about `_seal` or the health derivation. |
| `.../task-2-report.md` | Task 2's S6 and S3 measurements. **S3 and S6 are CLOSED — do not re-derive them.** |
| the plan | § Global Constraints, § Measurements M1–M9, § Named seams, § Rule-5 reconciliation. **M9 is the plan's own finding and the one an executor is most likely to skip.** |
| the spec, `…/specs/2026-08-25-the-membrane-reports-its-health-design.md` | Read where the plan **cites** it — §4.3 (Task 3's query, now shipped), §4.8 (Task 5's shape), §4.9 (Task 6's tripwire + fallback), §7, §9, §11. The plan cites rather than re-derives, so the citation is not optional reading. |
| `CLAUDE.md` § Plan authoring discipline rule 4 | **Per task:** no `## FALSIFICATION` block ⇒ the task review fails. |

## What was decided in the second session, and where each decision is recorded

**All of it is in the ledger and nowhere else — therefore reversible.**

- **Task 3's separate commit `b91e152` (touching `tests/etkl/test_document.py`, a file its brief does
  not list) was ruled IN SCOPE.** It repairs a parity test that Task 2 broke. The repair enumerates the
  five seal triples and subtracts them rather than relaxing the equality to `>=`.
- **Task 3's plan-gap repair was ACCEPTED**: `_seal` re-entry could leave two health values on one
  subject — spec §4.3 invariant 3's collision reached by re-entry rather than by union. The fix adds
  `graph.remove((_DOC, ETKL.membraneHealth, None))`, a pinning test and a fourth inversion. The task
  reviewer independently confirmed the ordering is identical on both paths and that the **type** triple
  correctly needs no equivalent removal.
- **Task 3 review Minors 2, 3 and 6 were FOLDED into the fix round**; **Minors 4, 5 and 7 were
  DEFERRED** to the final whole-branch review. All six are in the ledger with their reasons.
- **Two Task-2 minors remain deferred** to the final whole-branch review (a report-prose line-number
  slip; `MembraneRefusal` not reconstructible from `args`).

## Unverified or assumed

- **Tasks 5–7 have not been started.** No shape, no tripwire, no record change exists.
- **`R127` HAS NO RESIDUE-REGISTER ROW, AND THIS IS THE MOST IMPORTANT LINE IN THIS FILE.** Verified:
  `grep -c R127 docs/superpowers/residues.md docs/superpowers/residues-open.md` → `0` and `0`; the
  register tops out at **R126**. "R127" is a label this loop's own spec and plan invented for a residue
  that was never registered — while Global Constraint 10 says it "must survive this loop intact" and
  **four shipped tests now ride it** (`test_membrane_health.py:216, :388, :460, :578`). **Task 7 must
  CREATE the row**, not update one, and record 4 coupled tests by name. CLAUDE.md directs a maintainer
  to read `residues.md` in full; R127 is not in it, so closing R127 later turns four tests red for an
  invisible reason. This blocks the loop's definition of done.
- **Task 4 found a plan defect and substituted around it**, and the reviewer verified the substitution
  is a strict superset, not a weakening. The brief's `== [ETKL.Intact]` control arm was false on all
  three candidate vehicles and contradicted a **shipped Task-3 assertion 81 lines above it in the same
  file** (`test_membrane_health.py:386`). That is CLAUDE.md rule 5's failure mode, found for the second
  time on this branch.
- **TASK 2 SHIPPED A REGRESSION ITS REVIEW MISSED, and this is the most important line here.**
  `tests/etkl/test_document.py::test_single_page_document_matches_compile_tables` was already red at
  `f33db9f` — verified directly by the controller, not merely reported: checking out `f33db9f`'s two
  files and running it gives `AssertionError: assert 329 == 326`. Task 2's scoped review ran nothing
  wider than its own test file. **CONSEQUENCE: the plan's suite baseline `1312 passed, 7 skipped,
  1 xfailed` is NOT a clean comparator.** Task 7 Step 6 must treat any delta as a failure to
  ATTRIBUTE, not as noise, and must not assume a green branch.
- **The corpus files are indicatively green, not measured green.** `tests/test_corpus*.py` +
  `tests/test_cbh_*.py` gave **49 passed in 641.44 s**, but the run started at `b91e152` and the fix
  round mutated the tree mid-flight — including `vocab/queries/membrane-health.rq`, which
  `interpret.run` reads at RUNTIME. Re-run it at a pinned commit if the answer has to be load-bearing.
  Also: `tests/etkl/test_cbh_e2e.py` does not exist; the file is `tests/test_cbh_e2e.py`.
- **O5 pins the QUERY, not `_seal`'s USE of it.** Nothing in the suite distinguishes "derived by
  `membrane-health.rq`" from "a Python reimplementation that agrees" — the Task 3 implementer measured
  this by storing a hand-coded equivalent and watching all 12 tests pass. Not patched: the brief
  declares O5 explicitly not the falsifying oracle, and O1 is. Deferred Minor 7; CLAUDE.md §8's gate is
  the only thing standing there.
- **Plan M2's census does not reproduce** — it claims 17 `AssertionError` interceptors; the measured
  figure is **7**. The substantive claim (all isinstance-based, zero `type(e) is`) holds and is
  stronger. **Treat every other plan count as re-measurable, not as fact.**
- **S1, S2, S4 and S5 are open BY DESIGN**, each a Step 1 of its task. `graincorp-stem` and `cbh-stem`
  were never compiled for the escalation census (plan M8); apple's lever is *applicable* but its
  refusal is unmeasured — that is S1, Task 4's Step 1.
- **Every plan-supplied test in Tasks 4–7 is a PROPOSITION** (Global Constraint 7). Task 2's
  implementer found one that passed with its own subject deleted; Task 3's review found a shipped
  query clause that no test pinned at all. Both were caught by measuring, not by reading.

## The next concrete action

**In a fresh session: read the ledger FIRST and let it tell you where Task 4 stands.**

Execute **Task 5** — dispatch from `task-5-brief.md` (the health signal's own shape, spec §4.8). Its
brief's note flags a missing `pytest` import in the fixture block; the implementer must MEASURE that
rather than transcribe it. Then Task 6, then Task 7 — and Task 7 carries the R127 register row above,
the four deferred Task-3 minors, the four deferred Task-4 minors, and the two deferred Task-2 minors,
all listed in the ledger.

Banked, do not re-derive: all three corpus PDFs are PRESENT and Task 4's two `@pytest.mark.corpus`
legs RAN (2 passed, 202.63 s); R-PF3 is resolved by measurement; S1 and S2 are answered in
`task-4-report.md`.
