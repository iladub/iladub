# Handoff — the NEURAL worker foundation spec, measured and drafted

**Serves:** maintenance — the foundation under the etkl rung's ready criteria; meets none of them

**Date:** 2026-09-17. **Tree:** branch `neural-worker-foundation-spec`, cut from `main` at `2e2d33b`.

**Doc impact: none.**

**Authored over the floor** (~150K working tokens, estimated from the token counter). Part 5 was
written first and is graded per action.

---

## 5. The next concrete action

### 5a. PROPOSED — attack the spec's §§ 2–5 before planning

`specs/2026-09-17-neural-worker-foundation-design.md` § 1 is measured. §§ 2–5 were drafted over
the floor. **A fresh session reviews them adversarially first**, and plans only what survives.
The two claims to attack first, each checkable in under an hour:

1. **§ 3.2's per-column grain.** Measure which graph fact identifies "the same column" for a
   `SurfaceConcept` (it carries none, `ground.py:37`): across a continuation chain, and for gcap's
   377 empty-text cells. If no fact separates gcap's unlabelled columns, the grain claim needs a
   different key, or it fails.
2. **§ 3.4's null proposer.** Take a recorded grounding population (rerun
   `scripts/neural_seam_population.py`, ~10 min, serial) and compute the null's acceptance under
   `_grounds_to`. If the null is already near 0, the gap tells us little about the model. If the
   null is high, the oracle is weak for that column. Either result reshapes the harness.

*If wrong, found in an hour: both are measurements on existing code.*

### 5b. ASSERTED — before any live run, the key

`ANTHROPIC_API_KEY` is unset in this shell. The repo's only client is Haiku 4.5. The maintainer
sets it; nothing in § 3.4 can run live without it.

### 5c. ASSERTED — do not pick a new proposer, and do not rework `ProposeDimensionName` in the foundation loop

The rework is [[R248]], a separate loop. Row-role and span workers change no corpus figure today
(0 reach, evidence § 4), so the prior handoff's R234 and furniture-peel candidates stay unpicked.

## 1. Where the primaries are

- Evidence: `2026-09-17-neural-worker-seams-evidence.md` (§ 1 classification, § 2 name-blind
  oracle, § 3 rationale/confidence bindings, § 4 population with positive control, § 5 tool belt
  on paper).
- Spec: `specs/2026-09-17-neural-worker-foundation-design.md`.
- Instrument: `scripts/neural_seam_population.py` (`run` / `report`). The raw per-document JSON
  was in the scratchpad and is not kept; rerun it.

## 2. What was decided, and where

| decision | recorded |
| --- | --- |
| The handoff's grain holds for 4 of 5 proposers; two send a closed question as an open string | evidence § 1; spec § 1a |
| `ProposeDimensionName` has no oracle for its answer | evidence § 2; [[R248]] |
| Rationale off the wire, confidence stays (required by `iladub-shapes.ttl:24`) | evidence § 3; spec W4 (PROPOSED) |
| Only grounding has a corpus population: 2,364 calls, 39 distinct questions | evidence § 4 |

## 3. Unverified

- Whether any per-cell value changes the right field for a column (evidence § 4, "Not established").
- Why no corpus band reaches the `not merge_tiling_ok` branch: counted, not traced.
- The tool-belt reuse (evidence § 5): paper only.

## 4. What this session did

Measured the prior handoff's three seams plus a fourth (reach), with a positive control. Wrote the
spec, raised R248, re-pinned `test_residue_graph.py`'s candidate count (90 → 91, R248 only). No
production code touched.
