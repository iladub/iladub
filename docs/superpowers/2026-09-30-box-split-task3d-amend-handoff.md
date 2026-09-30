# Handoff: box-split — amend the Task 3d plan from its review, then SDD (2026-09-30)

**Topic:** box-split · **Date:** 2026-09-30

**Serves:** prog:criterion:etkl:03 — O2 (`tab:12`) is whole only when T2 compiles with no boxhead.

**Doc impact: none** (this handoff).

Authored at ~70K working tokens (plimslop hook), over the 50K originating floor. Parts 1–4 are
pointers. Part 5 is graded per action.

## 5. Next actions (written first)

- **Asserted.** Amend Task 3d in `docs/superpowers/plans/2026-09-28-box-split.md` with findings
  A1–A6 and the minors from `docs/superpowers/2026-09-30-box-split-task3d-plan-review.md`.
  - **Append** the amendments to Task 3d, for example as a "Task 3d — amendments after review
    (2026-09-30)" block that each sub-task points to. Do not rewrite the existing lines: the plan
    is Evidence, so a later PR may add lines but not delete them.
  - Each finding in the review already names its amendment.
  - This is originating work (rules 1–7 apply, rule 7 included). Take it under the floor.
- **Asserted, after the amendment:** SDD from 3d.0. The maintainer chose subagent-driven
  development for this branch. The ledger is `.superpowers/sdd/2026-09-28-box-split/progress.md`
  (gitignored).
- **Proposed, and it may fail:** A6 (the statement dangles when a table is merged in from `/r2` or
  `/adopt`) was found by reading, not by a run.
  - Its amendment is a MEASURE plus a U14 case in 3d.2, not a fix.
  - If the pass's log does reach the document graph, A6 does not land. Record that in the task
    report and move on.
- **Proposed:** the new shapes are idle on the corpus, so `test_vacuity_registry.py:343` needs
  entries for them (A4).
  - "Idle" has not been read in that test.
  - Measure its definition first.

## 1. Goal

A Task 3d plan that the review's findings no longer refute, so that SDD executes it without a plan
defect surfacing mid-task.

## 2. Where the primaries are

- **The review:** `docs/superpowers/2026-09-30-box-split-task3d-plan-review.md` (`a289fa1`). Read it
  in full. Its `file:line` facts were measured at `6d23e2f`, and `src/` has not changed since.
- **The plan:** `docs/superpowers/plans/2026-09-28-box-split.md`, § "Task 3d" (added in `6d23e2f`).
- **The contract:** spec `docs/superpowers/specs/2026-09-28-box-split-design.md`, § 10.5 and
  § 10.7 (from line ~710 to the end).
- **The previous handoff** (why Task 3d exists and what was approved):
  `docs/superpowers/2026-09-29-box-split-task3d-plan-handoff.md`.

## 3. What was decided, and where it is recorded

- **The maintainer asked for an adversarial plan review before SDD** (2026-09-30, in chat).
  Recorded only in the review file's header and here.
- **The amendments go in a fresh session** (maintainer, 2026-09-30, in chat). Recorded only here.
- **None of the findings re-opens a spec ruling.** That is the review's own judgement (its
  § 5), not a maintainer ruling. If an amendment turns out to need a spec change, that is a
  finding to raise, not to make silently.

## 4. Unverified or assumed

- **The subagent report behind the review was not committed.** Its facts are quoted in the review
  with `file:line`, so re-measure any fact you build on.
- **A6** is unmeasured (see part 5).
- **`feed.py:117`'s `while queue:`** was never opened. Nobody has checked whether it is a
  reachability closure over a table.
- **The meaning of "idle" in `test_vacuity_registry`** has not been read.
- **The review was written up at 52.7K working tokens.** It was over the floor, with the override
  logged. The attacks were decided at ~33K, which was under it.
- **The traps carried over:**
  - `uv run` creates an untracked `uv.lock`: delete it.
  - Corpus runs are serial, one test file per process, from a `.sh` under `bash`.
  - CI skips the corpus.
