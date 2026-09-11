# Handoff — the register serves the arc: the spec is written; the plan is next

**Topic:** register-serves-arc
**Serves:** maintenance — the loop changes how the next subject is chosen; it moves no criterion.
**Date:** 2026-09-11. **Loop shape:** originating (a spec, no code), written at ~36K working tokens,
under the 50K floor. **Doc impact: none** (the spec declares its own).

Part 5 written first.

## 5. The next concrete action

### 5a. ASSERTED — write the PLAN from the spec, fresh session

`docs/superpowers/specs/2026-09-11-the-register-serves-the-arc-design.md` § 7 lists six tasks with
interfaces and oracles; § 3 carries each oracle and its falsification. The plan states signatures
and supplies the tests verbatim (CLAUDE.md § Plan authoring rule 1), never the bodies. Task 1 is
mechanical and first: `scripts/residue_graph.py:43` drops the two rows whose status carries a
qualifier (reads 133 open, index has 135); every later task depends on the graph reading every row.
Tasks 5 and 6 are gated on the maintainer being present.

### 5b. PROPOSED — the `Serves:` count leaves zero within three loops

Spec § 3.2's prediction, restated so it is run: after the strip renders `serves a/m/–`, if three
consecutive handoffs declare `maintenance` while `ready` stays at 15, handoff-selection was not the
cause of the flat arc line and spec § 4's fork (a rung for the evidence discipline) is the remedy.
Baseline today: 47 September handoffs, 0 name a criterion, 1 (this loop's predecessor) names the IRI
in prose.

### 5c. PROPOSED — the maintainer's fork in spec § 4 is decided before task 6

Arm A (the 15 no-criterion rows are `maintenance` and that suffices) is recommended in the spec.
It is a ruling, not a measurement; the triage pass cannot park R173 or R188 under either arm because
both have open neighbours, so the fork does not block tasks 1–4.

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the spec | `docs/superpowers/specs/2026-09-11-the-register-serves-the-arc-design.md` | § 1 the measurements, § 2 the triage table (disputable row by row), § 3 the three rules, § 4 the fork |
| the predecessor handoff | `docs/superpowers/2026-09-11-the-register-serves-the-arc-handoff.md` (PR #200) | its part 2 figures at `0bc7aca`; its "61 open rows ≥ 150" is wrong — 36 (spec § 1) |
| the graph | `scripts/residue_graph.py --json`, this session's analysis reproduced in spec § 1 | 13 open rows reach a frontier row through open rows: the 13 frontier rows themselves |
| the readers the spec reuses | `tests/test_residue_register_integrity.py:40`, `scripts/cockpit.py` `topic()`/`work()`/`residues()` | the qualifier precedent (R131, R141); `_WINDOW`; the `_CRITERION` regex |

## 2. What was measured this session (`main` at `3635e08`, 2026-09-11)

All figures are in spec § 1 and § 2 with their commands; the only ones not in the spec:

- `pytest tests/test_doc_governance.py tests/test_cockpit.py tests/test_residue_register_integrity.py`
  with the spec staged: **27 passed**.
- PR #200's `test` check was IN_PROGRESS (`mergeStateStatus BLOCKED`) when this branch was cut from
  its head; this branch is stacked on it.

## 3. What was decided, and where that decision is recorded

- **PARKED is a qualifier on `open`, not a third status or file** — spec § 3.3; reason: the
  integrity test's two-word membrane and the untouched `c/t` tally.
- **The question layer is not built** — spec § 2 and § 6; reason: two of four roots bear on no
  criterion.
- **Nothing in the register, the arc, CLAUDE.md or the code was changed.** The direction remains
  the maintainer's conversational agreement of 2026-09-11 (predecessor handoff part 3); the spec is
  where it is argued, not yet where it is ruled.

## 4. Unverified or assumed

- The § 2 triage assignment of 36 rows to questions is a reading of index text, not a measurement;
  the "bears on no criterion" claim for the 15 rests on there being no rung about evidence discipline,
  which is a fact about the manifest, not about the rows.
- That `work()`'s width tolerates a fourth segment: the strip already truncates the topic at 18
  characters and this loop's predecessor renders as `the residue regist · …`. Not measured.
- That the `Serves:` line's prospective-only binding is enough: 47 documents will never carry it,
  and `serves_window()` will read them as `–` for as long as they sit in the window.
