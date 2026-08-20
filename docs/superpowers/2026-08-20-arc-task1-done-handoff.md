# Handoff — Task 1 of 8 shipped; the controller seat needs a fresh session

**Topic:** process · **Date:** 2026-08-20 · **Branch:** `arc-denominator` @ `c86c39a` (from `main` @
`f436a8c`, pushed) · **Shape: executing** · **Status: TASK 1 COMMITTED, ITS REVIEW IN FLIGHT.
TASKS 2-8 NOT STARTED.**

> Written at ~227k tokens — 1.5× the executing floor. The controller seat (dispatch → review →
> adjudicate, ×7) is what needs the fresh session; the implementer and reviewer seats are already
> fresh subagents and are unaffected. Preflight logged (one override, at 182k).

## Goal

Unchanged: the strategy instrument, slice 1 — give each named rung of the arc a countable denominator
and a dependency edge to the register, so the cockpit stops printing `stage ?/5`.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/plans/2026-08-20-the-arc-has-a-denominator.md` (866 lines, committed `f436a8c`) | **the plan. 8 tasks.** Its § *Decisions this plan makes* (D1-D4) and § *Corrections* are the reversible calls; its § `prog:declaredOn` table is measured, not guessed |
| `docs/superpowers/specs/2026-08-20-the-arc-has-a-denominator-design.md` | the spec — the **binding authority**. The plan argues from it; conflicts resolve against it |
| `.superpowers/sdd/2026-08-20-the-arc-has-a-denominator/progress.md` | **the SDD ledger — read this FIRST.** Pre-flight conflict scan table, and Rulings 1-7 with what each costs if wrong. It is git-ignored: `git clean -fdx` destroys it |
| `.superpowers/sdd/.../task-1-report.md` (20.7 KB) | what Task 1 actually built, its TDD red/green, and its FALSIFICATION block (six refusals, three more than required) |
| `docs/superpowers/2026-08-20-escalation-reason-census.md` | the spent 315 s corpus run. **Tasks 5 and 6 cite it; neither re-runs it** |

## What was decided, and where that decision is recorded

**In the plan (D1-D4), and nowhere else — reversible:** D1 a corpus-dead escalation reason is not met
by being dead · D2 the manifest counts graph-side 24 · D3 liveness is `tab`'s tenth criterion, not a
`dec` one · D4 two lines on the strip, and the `▸` slot shows counts rather than naming a frontier
residue. **D4's second half is the deviation most worth overturning.**

**In the ledger, and nowhere else — reversible:**

- **Ruling 1** — Task 1's seed manifest moved ahead of its tests. Discharged; Task 1 is done.
- **Ruling 2** — Task 8 must update `test_the_strip_never_raises_when_its_sources_are_missing`'s
  monkeypatch list when it renames `cockpit.ARC` → `ARC_MANIFEST`. **Not yet applied — carry it into
  Task 8's dispatch.** If missed, that test passes while patching nothing.
- **Rulings 3 and 7** — run the suite split and in the background. See § *The measured trap* below.
- **Ruling 4** — `prog:Oracle`'s node type is gone; the two properties sit on the criterion.
  **This deviates from spec §3's third bullet.** Cost: a later reader wanting a first-class oracle
  node needs a migration across ~42 criteria.
- **Ruling 5** — `prog:rdflibVersion` is an exact pin against `pyproject.toml:26`'s `rdflib>=7.0`.
  Cost: rdflib 7.7.0 turns CI red on an unrelated PR. **Candidate residue, not yet raised.**
- **Ruling 6** — `prog:CriterionShape` is deliberately not `sh:closed`. Cost: a typo'd
  `prog:blockeBy` silently drops a blocking edge M7 can never see. **Candidate residue, cheap to
  close once Tasks 3-6 fix the real property set.**

## The measured trap the next controller must plan around

**The unfiltered suite is ~35 minutes, and neither leg fits in one 600 s tool call** — `-m "not corpus"`
took 18m10s, `-m corpus` 17m28s (measured on Task 1). The corpus is compiled twice: `tests/test_corpus.py`
(census-measured at 315 s) and again by `test_vacuity_registry.py`'s `corpus_graphs` fixture.
**Dispatch both legs with `run_in_background` from the start.** Task 1 lost most of its wall clock to
this, and its first implementer turn died mid-run against the tool timeout, returning no status
contract at all. Every remaining task has the same "run the full suite" step.

Iterate and falsify with the focused path instead: `./.venv/bin/python -m pytest tests/test_arc_manifest.py -q`
is ~2 s. **Never `python3`** — rdflib 7.1.4 there, and under it `tests/test_arc_manifest.py` is now
*supposed* to go red (M5c refuses the manifest as foreign, by design).

## Unverified or assumed

- **Task 1's review has not returned.** A reviewer was dispatched against `f436a8c..c86c39a` with the
  package at `.superpowers/sdd/.../review-f436a8c..c86c39a.diff`. **Its verdict is unread, so Task 1
  is committed but NOT signed off**, and the ledger carries no `Task 1: complete` line yet. Adjudicate
  its findings before dispatching Task 2.
- **The pre-flight conflict scan is not independent** — the same session authored the plan and scanned
  it. The task review loop is the only compensating check.
- **Rulings 4-6 were made on the implementer's own account of its diff**, before the reviewer had
  looked. If the review contradicts any of them, the review wins.
- **Tasks 2-8 are entirely unstarted.** No file outside Task 1's 16 has been touched.
- Nothing on this branch is pushed. `main` is pushed at `f436a8c`.

## The next concrete action

In a **fresh session**: read the ledger, then read the Task 1 review verdict and adjudicate it — fix
loop if it found Critical/Important, ledger `Task 1: complete` if clean. **Then dispatch Task 2**
(the register repairs), which is short and has no dependencies, and carry Ruling 2 forward until
Task 8 consumes it.
