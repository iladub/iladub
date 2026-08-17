# R87 — handoff into Task 5

**SUPERSEDED 2026-08-17 by `540e608` (PR #105)** — Tasks 5 and 6 are finished and merged (`3c28458`, `c7c08ec`); criterion 2 shipped as TERM REACHABILITY, not as this file's reading of the plan. Kept as the record of what was known on 2026-08-16.

**Date:** 2026-08-16
**Branch:** `loop-escalation-is-a-decision`, HEAD `0074144`, tree clean

## Goal

Tasks 5 and 6 remain: build the vacuity registry (the guard whose absence let R87 be filed
as *"0 violations, nothing to do"*), then close the record.

**Why this was handed off rather than continued.** Task 5 is the one task in this plan that
DESIGNS something — criterion 2 has to strip negated blocks out of arbitrary `sh:sparql`
bodies and decide what "the body binds" means for every wired shape, not just the one this
loop repaired. That is multi-step reasoning others build on, at 4.5× the originating floor.
Getting it subtly wrong produces a guard that rubber-stamps, which is R87 itself.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/plans/2026-08-15-escalation-is-a-decision.md` | The plan. Task 5's contract, its two criteria, the seeding rule, and T5.1–T5.4. Task 6 unstarted. G1–G7 and §7 (G4) still bind. |
| `0074144` (Task 4 commit message) | O1 shown failing then green; O3's zero-difference result; the blank-node re-measurement; **and a correction to the Task 3 record about which engine leg is unrun**. |
| `262dd2e` (Task 3 commit message) | The wiring, the fixture sweep, the seven-case falsification table, and the method note on a harness that reverted the thing under test. |
| `3eaf65d` → `docs/superpowers/2026-08-15-r87-task3-measurement.md` | The S1 counts table per candidate site. |
| `scratchpad/o3-before.md` + `o3-before-snapshot.json` + `o3-after.json` | O3's two states and the probe that made them, **including a negative control proving the focus-node counter counts**. These are in the session scratchpad and are NOT committed — see "Unverified". |
| `scratchpad/o1_oracle.py` | The O1 harness. Restores from a snapshot, never `git checkout`. |
| `vocab/shapes/escalation-shapes.ttl:12` | `dec:escPrefixes`, declared in-file. The shape file is self-sufficient. |
| `src/iladub/etkl/compile.py:398-417` | `_DEC_SHAPE_FILES`, now three files, with the comment stating why the grounding leg is untouched and why the shape is live on one leg and idle on the other. |

## What was decided, and where each decision is recorded

1. **`escalation-shapes.ttl` is in the COMPILE membrane only.** The grounding membrane
   (`feed.py:586`) is untouched per G4. Recorded in `0074144` and in the `compile.py`
   comment.

2. **The derivation runs at document scope only; the page leg is deliberately unfurnished.**
   Recorded in `262dd2e` and in `document.py`'s call-site comment.
   **This is the fact Task 5 most needs.** `_validate` is called at page scope
   (`compile.py:1083`) and at document scope, with ONE shape set both times, while
   furnishing happens at document scope only. So `dec:EscalationShape` binds rows on the
   document leg and **zero** on the page leg. A registry keyed on shape name alone cannot
   express "live here, idle there", and will either false-positive or need a leg dimension.
   **Decide this explicitly; do not let it be decided by which leg the test happens to
   measure.**

3. **Criterion 2's precondition is measured, not assumed.** The plan says to MEASURE on the
   shipped state before writing the assertion, because `dec:EscalationShape`'s body ends in
   `FILTER NOT EXISTS { $this dec:escalatedTo ?apex }` and, once furnishing ships, that
   filter *correctly* eliminates every row. Measured on the shipped state
   (`scratchpad/o1_oracle.py` step C, on `recognized_pair_plus_escalating_page_pdf`):

   ```
   dec:EscalationShape focus nodes (dec:DecisionHolon)      = 17
   non-negated body bindings (FILTER NOT EXISTS stripped)   = 1
   ```

   So with the negation stripped the body DOES bind. **A criterion 2 that reports
   `dec:EscalationShape` idle after `262dd2e` is a wrong criterion, not a sick shape.**
   Recorded in `0074144`.

4. **The blank-node question is closed by re-measurement.** 0 of 769 `dec:DecisionHolon`
   subjects and 0 of 23 `dec:ExpansionRequest` subjects are blank nodes, corpus-wide.
   R87's row (167/167 grounding, 0/14 compile) is right in direction, wrong in denominator.
   Recorded in `0074144`.

5. **The engine record was WRONG and is corrected in `0074144`.** `membrane.engine_name()`
   returns **`rudof`** here, so every figure in Tasks 1–4 is the rudof leg; it is **pySHACL**
   that is unrun. Tasks 3's commit and its handoff say the reverse — they are superseded on
   this point. Task 6's O4 owes `ILADUB_MEMBRANE=pyshacl`.

## Numbers Task 5 will need, measured this session

Corpus-wide at `262dd2e`, all 7 documents (`scratchpad/o3-before.md`, Table 2):

| | count |
| --- | ---: |
| `dec:DecisionHolon` | 769 |
| chose "escalated" | 32 |
| …with an incoming `dec:supersedes` | 9 |
| `dec:ExpansionRequest` furnished | 23 |

`escalated == superseded + requests` holds on **every document individually** (cbh 4=4+0,
apple 15=5+10, bfs 10=0+10, who 3=0+3, and 0=0+0 on graincorp-capacity, graincorp-stem,
ons). A sharp invariant to check any later change against.

The DEC shape set is now 132 triples (was 120) and contains: `CandidateConceptShape`,
`ConfidenceShape`, `DecisionHolonShape`, `EscalationShape`, `EventShape`,
`ExpansionRequestShape`, `GroundedNodeShape`, `MilestoneShape`, `NoLeakShape`,
`PromotionDecisionShape`. The TAB set is 220 triples. Both are validated against
`_FULL_ONT` (1023 triples).

## Unverified or assumed

* **The batteries against `0074144` have RUN, and one was red. Superseding this document's
  first version.**

  | battery | commit | result |
  | --- | --- | --- |
  | corpus | `0074144` | **39 passed**, 12m10s (`scratchpad/corpus2.log`) |
  | fast | `0074144` | **1 failed**, 1168 passed / 7 skipped / 1 xfailed, 18m16s (`scratchpad/fast2.log`) |

  The failure was `tests/etkl/test_compile_membrane_shapes.py::test_the_membrane_carries_-
  every_shape_file_in_its_leg`, which pins `_DEC_SHAPE_FILES` by EXACT equality so that no
  shape file can enter or leave a membrane silently. Task 4 added one and did not update
  the pin. **The test was right and Task 4 was incomplete.** Fixed at `d278a6f`, where the
  update is itself falsified (remove the file from the membrane again and the test fails at
  the same line, so the pin was not widened into a rubber stamp). The file's own four tests
  pass.

  **Why the miss is worth knowing about:** Task 4 was committed BEFORE its fast suite
  finished. The corpus battery and the O1/O3 oracles were all green, but those answer *"does
  the shape work"* — a different question from *"did anything else depend on the shape
  set"*. Only the fast suite asks the second one, and only it had an answer.

* **NO COMPLETE FAST-SUITE RUN EXISTS AGAINST `d278a6f`.** A re-run was started and killed
  at ~58% with no failures up to that point (`scratchpad/fast3.log`). The one test that was
  red has been run directly and passes (4 passed), but that is not the same claim as a green
  suite. **Re-run `python3 -m pytest -m "not corpus" -q` first.** The corpus battery does
  not need re-running: `d278a6f` touches one test file and no source.
* **The O3 evidence lives only in the session scratchpad** (`o3-before.md`,
  `o3-before-snapshot.json`, `o3-after.json`, `o3_probe.py`, `o1_oracle.py`). It is
  referenced by the Task 4 commit message but not committed. If Task 6 needs to reproduce
  O3, it must re-run the probe or the files must be committed. **Decide which; a commit
  message citing a file nobody can open is the artefact this loop keeps warning about.**
* **The pySHACL leg is unrun on every task of this loop.** Further, the O3 probe's
  focus-node counter parses the report as Turtle and is **not portable** to pySHACL, whose
  report is prose. Task 6's O4 needs a different counter or a different method.
* **Whether each 0-refusal is a strong or a vacuous pass is not established per shape.** A
  conforming rudof report records no "N focus nodes tested". That is exactly what Task 5's
  registry exists to answer, and O1 answers it for `dec:EscalationShape` alone.
* **M7's ten idle shapes have NOT been re-measured.** The plan says seed the registry with
  them and re-measure their focus counts rather than copying spec §3's table. That work is
  entirely unstarted.
* **`dec:EventShape` and `dec:ExpansionRequestShape` went live under this loop** and must
  therefore be ABSENT from the seeded registry, or the "registered but live" arm fails
  immediately. The plan calls this a good first falsification.
* The fast-suite baseline the plan compares against (1152/1155 passed) predates this
  branch. Task 6's O4 still owes the branch's own before-state at `401e0d6`.

## The next concrete action

Run the fast suite to completion against `d278a6f`:

```
./.venv/bin/python -m pytest -m "not corpus" -q
```

Expect 1169 passed / 7 skipped / 1 xfailed (the count at `262dd2e`; `d278a6f` adds no
test). If it is green, begin Task 5 by writing criterion 2 and MEASURING it against the
numbers in decision 3 above — a criterion that reports `dec:EscalationShape` idle is wrong.
Then decide the page-leg / document-leg question in decision 2 **before seeding a single
row**, because it determines whether a registry row is keyed by shape or by (shape, leg).
