# Handoff — execute the `holon:05` plan (`the membrane reports its health`)

**Date:** 2026-08-25 · **Branch:** `holon-05-plan` @ `ae75da7` (off `main` @ `18226e7`) ·
**Shape: mechanical** — pointers only. It restates nothing from the primaries and settles nothing.

## Goal

One line: **execute `docs/superpowers/plans/2026-08-25-the-membrane-reports-its-health.md`, Task 1
through Task 7.** The spec is twice-amended, every ruling is taken, the plan is written and its seams
are measured. Nothing else is owed before the code.

## Where the primaries are, and what to establish at each

| open | to establish |
|---|---|
| `docs/superpowers/plans/2026-08-25-the-membrane-reports-its-health.md` | **The whole plan.** Read § Global Constraints, § Measurements (M1–M9), § Named seams and § Rule-5 reconciliation **before Task 1**. Then one task at a time. **M9 is the plan's own finding and the one an executor is most likely to skip** — it is a defect the (a′) oracles would otherwise create. |
| the spec, `…/specs/2026-08-25-the-membrane-reports-its-health-design.md` | Read where the plan **cites** it — §4.3 (the query contract), §4.8 (the shape), §4.9 (the tripwire + its fallback), §7 (the oracles), §9 (binding on every test), §11 (the residue rows, verbatim). The plan cites rather than re-derives, so the citation is not optional reading. |
| the four ruling files (`…-b1-`, `…-b2-b3-b7-p1-`, `…-o2-finding6-rulings.md`, `…-seam-6-refusal-vehicle.md`) | Only if a ruling is questioned. All four are cited by the spec and the plan; none is superseded. |
| `CLAUDE.md` § Plan authoring discipline rule 4, § Producer-side guards | **Rule 4 is per task:** no `## FALSIFICATION` block ⇒ the task review fails. |

## What was decided this session, and where each decision is recorded

**All of it is in the plan file and nowhere else — therefore reversible.**

- **The task decomposition (7 tasks) and their ordering** → the plan, § Task ordering.
- **`_seal(graph, legs, validate_shapes)`'s name, signature and seven invariants** → the plan,
  § Interfaces. The *bodies* are deliberately absent (rule 1).
- **O10 (re-entry mints one `sh:conforms`) and O11 (the subclass check) are NEW oracles this plan
  adds** beyond the spec's nine → the plan, M9 and Task 2.
- **The vacuity population is scoped to compile-path queries** (27 of 45 `.rq`, +`membrane-health.rq`;
  `federate.py`'s 3 excluded because `corpus_graphs` holds *compile* graphs) → the plan, Task 6 Step 1.
- **O2's `Compromised` leg is written against `bfs`**, with the `apple` substitution authorised only
  if seam S1 measures it → the plan, Task 4 Steps 1–2.
- **`graincorp-stem` is NOT substitutable** for a cheaper `Intact` specimen → the plan, Task 4 Step 2
  docstring. That is a spec choice (§1, §5.5), not an implementer's.

## Unverified or assumed

- **S1–S6 are open BY DESIGN** and each is a Step 1 of its task. S1 (does apple's lever refuse?),
  S2 (which decision to mutate), S3 (`graph` identity *after* the extraction), S4 (Task 6's row count),
  S5 (doc governance after the `holonic-interaction.md` edit), S6 (is `_legs_for_document` safe to
  hoist above the furnish?).
- **The suite baseline `1312 passed, 7 skipped, 1 xfailed` in 2386.82 s is the SPEC's**, measured
  before any implementation and **not re-run in this session**. ~40 min. A lower passed count at
  Task 7 is a finding, not a rounding error.
- **`graincorp-stem` and `cbh-stem` were never compiled for the escalation census** (plan M8). Three
  of the five that were measured carry the lever, which is enough for Task 4. cbh is *suspected*
  negative from an earlier register note — suspected, not measured.
- **Every wall-clock figure in the plan is a single run on one machine under concurrent load** (three
  measurement agents ran in parallel). Order-of-magnitude cost, not benchmarks.
- **M9's hazard was measured on hand-built graphs through the real `interpret.run`, not through
  `_seal`** — `_seal` does not exist yet. Task 2 Step 7(d) is where it becomes real.
- **Nothing in the plan has been executed.** No vocabulary term, no `.rq`, no test, no record change
  exists yet. `tests/test_doc_governance.py` is green on this branch (`4 passed`, run 2026-08-25);
  that is the only suite run this session.

## The next concrete action

**In a fresh session: read the plan's four front-matter sections, then execute Task 1.** Use
`superpowers:subagent-driven-development` (fresh subagent per task, review between) or
`superpowers:executing-plans`. **Do not start Task 4 before Tasks 2 and 3 are green** — it asserts
against them as shipped.
