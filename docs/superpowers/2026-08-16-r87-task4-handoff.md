# R87 — handoff into Task 4

**SUPERSEDED 2026-08-17 by `540e608` (PR #105)** — Tasks 4–6 are finished and merged; the work this file hands off is done. Kept as the record of what was known on 2026-08-16.

**Date:** 2026-08-16
**Branch:** `loop-escalation-is-a-decision`, HEAD `262dd2e`, tree clean

## Goal

Finish the R87 plan: Tasks 4–6 remain (wire the shape, build the vacuity registry, close
the record). **Task 3 is shipped but its batteries were never run** — see "The next
concrete action".

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/plans/2026-08-15-escalation-is-a-decision.md` | The plan. Tasks 4–6 are unstarted and unamended. G1–G7 and the §7 test prohibitions (G4) still bind. |
| `a5166fe` (Task 1 commit message) | The vocabulary, the S2 measurement, the T1 falsification table. |
| `d2c9b74` (Task 2 commit message) | The derivation's measurements, the supersession finding, the T2 falsification table. |
| `3eaf65d` → `docs/superpowers/2026-08-15-r87-task3-measurement.md` | The S1 counts table, per candidate site, per document, with the probe script in full. **Task 3's report points at this rather than restating it.** |
| `262dd2e` (Task 3 commit message) | What shipped in the wiring, the fixture sweep that forced a new fixture, the seven-case falsification table, and the method note on a falsification harness that silently reverted the thing under test. |
| `src/iladub/etkl/document.py:126-153` | `ESCALATION_FURNISH_RQ`, `_ESCALATION_VOCAB_FILES`, `_escalation_vocab()`. |
| `src/iladub/etkl/document.py:1541-1575` | The call site and the comment stating why it is there and nowhere else. |
| `tests/etkl/test_escalation_wiring.py` | T3.1–T3.5 plus the carry pin. One `-m corpus` test (apple, ~38 s); the rest are fast (~15 s total, one shared module-scoped compile). |
| `tests/etkl/fixtures.py` (last function) | `recognized_pair_plus_escalating_page_pdf` — the only synthetic shape that both escalates and opens `document.py`'s validation gate. Its docstring carries the measurement that forced it. |

## What was decided, and where each decision is recorded

1. **S1 — the derivation runs at site (iii), `document.py` before the whole-graph
   validation.** Selected by the measurement at `3eaf65d`, not by reading. Recorded in
   `262dd2e` and in the call-site comment.

2. **The PAGE leg is deliberately left unfurnished.** Furnishing at page scope is
   unguardable (no `dec:supersedes` edge ever enters a page graph) and measurably wrong:
   4 spurious expansion requests on cbh-stem, 5 on apple. Recorded in `262dd2e` and in the
   call-site comment.
   **Consequence Task 4 and Task 5 both need:** once `escalation-shapes.ttl` joins
   `_DEC_SHAPE_FILES` (`compile.py:399`), that ONE shape set is used by BOTH `_validate`
   call sites — page scope (`compile.py:1083`) and document scope. `dec:EscalationShape`
   will be live on the document leg and **idle on the page leg**. A vacuity registry keyed
   only by shape name cannot express that, and Task 5's criterion 2 has to be measured
   against it. It is also a Task 6 residue.

3. **The vocabulary constant lives in `document.py`, not `compile.py`.** A stated deviation
   from the plan's File Structure table, whose assignment predates S1's answer. Recorded in
   `262dd2e`.

4. **Task 3's tests live in a new file, `tests/etkl/test_escalation_wiring.py`.** The plan
   assigns Task 3 no test file. Recorded in `262dd2e` and nowhere else.

5. **A new synthetic fixture was necessary.** Measured by sweeping all 50 single-argument
   fixtures through `compile_document`: no existing one both escalates and opens the
   validation gate. Recorded in `262dd2e`; the sweep itself was not committed.

## Unverified or assumed

* **NEITHER BATTERY HAS BEEN RUN AGAINST `262dd2e`, ON EITHER ENGINE.** A `-m corpus` run
  followed by `-m "not corpus"` was started and killed before the corpus leg emitted one
  line. The only evidence behind the commit is `test_escalation_wiring.py` (6 fast + 1
  corpus, green) and its seven falsifications. **This commit enlarges the data graph of
  every escalating document**, and the plan says so itself: "This is the commit that can
  break every escalating document."
* **Two existing corpus tests now run the derivation over an already-furnished graph.**
  `test_escalation_furnish.py`'s two `-m corpus` tests call `_derive(rep.graph)` on a graph
  that `compile_document` has already furnished. T2.6 (idempotence) says the result is
  unchanged; that is an inference from a test, not a measurement of these two tests, and
  the corpus battery is what would settle it.
* **`tests/etkl/test_section_repair.py` uses `rdflib.compare.isomorphic`** on driver output.
  Whether any such comparison now sees the furnished triples is unmeasured.
* **The rudof leg has not been run at all** in this session or the previous one. Every
  figure in Tasks 1–3 is the default engine.
* **Only apple, who-wfa, cbh-stem and graincorp-stem have been measured for supersession.**
  bfs, graincorp-capacity and ons remain unmeasured at any site.
* **Task 3's counts table is not reproduced in its own report**, contrary to the plan's
  literal instruction; it points at `3eaf65d` instead. If a reviewer wants the table in the
  report, that is a fair objection and the fix is a copy.
* The fast-suite baseline figure (1155 passed / 7 skipped / 1 xfailed, 18m25s) is still the
  one taken with Task 1's edits in the tree. Task 6's O4 still owes the branch's own
  before-state at `401e0d6`.

## The next concrete action

Run the corpus battery against `262dd2e` before touching Task 4:

```
./.venv/bin/python -m pytest -m corpus -q
```

Task 3 is the commit that can break every escalating document, and nothing has yet looked.
If it is green, run `-m "not corpus"`, then start Task 4 (`escalation-shapes.ttl` joins
`_DEC_SHAPE_FILES` at `compile.py:399`) — whose O1 requires showing the membrane REFUSE a
document with `dec:escalatedTo` removed from the CONSTRUCT template, before showing it
green. If either battery is red, that is Task 3's defect and it comes before Task 4.
