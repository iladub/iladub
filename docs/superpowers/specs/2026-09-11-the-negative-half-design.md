# Spec — the negative half: the six unmet `dec` criteria are one shape of work, and it is asserted

**Topic:** negative-half
**Serves:** prog:criterion:dec:02 — and its five siblings dec:09, dec:12, dec:13, dec:15, dec:17,
which the strip's `ready` derivation lists beside it and which are the same work.
**Date:** 2026-09-11. **Loop shape:** originating, written under the 50K floor (fresh session,
no working figure reported). **Doc impact: none** — test fixtures, tests and the arc manifest;
no released page changes.

## 1. Why this subject, and how it was chosen

Per CLAUDE.md § Deferred residues (the rule PR #204 landed): the subject comes from the strip's
`ready`/`frontier`, never from the register. `arc-unblocked.rq` run against `tests/arc-manifest.ttl`
on `86340a5` returns 15 ready criteria: dec ×6, etkl ×5, holon ×1, substrate ×3. The six `dec`
rows are all of that rung's unmet criteria (`dec 11/17` on the strip), all declared 2026-05-31
from CLAUDE.md § Serialization's rule *"every vocabulary/shape ships with a worked example that
conforms AND a negative test that must fail"*, and each states the one missing thing:

| criterion | shape (`prog:statement`) | the missing negative half | oracle test the manifest already names |
| --- | --- | --- | --- |
| dec:02 | `dec:ConfidenceShape` (`dec-shapes.ttl:38`) | an out-of-range or duplicated `dec:confidence` | `tests/test_vocab_shapes.py::test_confidence_out_of_range_rejected` |
| dec:09 | `iladub:PromotionDecisionShape` (`iladub-shapes.ttl:53`) | a promotion lacking `iladub:reviews` or `dec:decidedBy` | `tests/test_boundary.py::test_unaccountable_promotion_rejected` |
| dec:12 | `risk:RiskAssessmentShape` (`risk-shapes.ttl:35`) | an assessment without subject, context or severity | `tests/test_risk.py::test_contextless_assessment_rejected` |
| dec:13 | `risk:SensitivityShape` (`risk-shapes.ttl:49`) | a sensitivity without severity or `risk:reads` | `tests/test_risk.py::test_sensitivity_without_reads_rejected` |
| dec:15 | `gsh:PermissionShape` (`governance-shapes.ttl:45`) | a permission without `odrl:action` or `odrl:assignee` | `tests/test_governance.py::test_permission_without_action_rejected` |
| dec:17 | the four PROV axioms (`dec.ttl:38,55,72,85`) | a test asserting them | `tests/test_hga_alignment.py::test_dec_provenance_axioms_present` |

**Measured 2026-09-11, before choosing:** none of the five shape names appears in any `tests/*.py`
(`grep -rln` finds them only in the shapes, the manifest and three M-fixtures); no test mentions
`prov:Activity`/`wasAssociatedWith`/`prov:generated`; all four axioms are present at the cited
lines of `vocab/ontology/dec.ttl`. The claims the criteria make are still true.

Why six and not one: `**Serves:**` takes one IRI (the strip reads the first token), so dec:02 is
named and the siblings ride in prose. They are one shape of work — a fixture and a test each —
and closing them moves the arc line `dec 11/17 → 17/17`, the first rung to fill.

## 2. The rule, its expression, its oracle, and what it must not touch

**Rule.** Each shape gains one negative fixture under `tests/` that trips **that shape and is
pinned to it by `sh:sourceShape`** — not merely `conforms == False`. A fixture that fails for a
different reason (a bare `dec:DecisionHolon` with `dec:confidence 1.5` also trips
`dec:DecisionHolonShape`'s min-counts) is CLAUDE.md § Plan authoring defect 5 in fixture form: a
test that goes red with its subject deleted only if it pins the subject. The four existing
negative tests in these files assert `not c` alone; the six new ones pin the source shape.

**Expression.** Five fixtures, named for what they leak, beside the existing ones
(`tests/dec-bad.ttl`, `tests/risk-leak.ttl`, `tests/transplant-governance-leak.ttl`):

- `tests/dec-confidence-leak.ttl` — a `dec:DecisionHolon` carrying `dec:confidence 1.5` and a
  second value, so the `sh:maxInclusive` and `sh:maxCount` arms both fire.
- `tests/promotion-unaccountable-leak.ttl` — an `iladub:PromotionDecision` with neither
  `iladub:reviews` nor `dec:decidedBy`.
- `tests/risk-assessment-contextless-leak.ttl` — a `risk:RiskAssessment` with `risk:severity`
  only (no subject, no context).
- `tests/sensitivity-without-reads-leak.ttl` — a `risk:Sensitivity` with a severity and no
  `risk:reads`.
- `tests/permission-without-action-leak.ttl` — an `odrl:permission` object with an assignee and
  no `odrl:action`.

Six tests at the node ids the manifest names (§ 1 table), each reading `sh:sourceShape` from
pySHACL's results graph via a three-line helper local to its module — local, because
`tests/test_arc_ablation.py` runs oracles one subprocess per module and a shared helper would
couple modules the ablation keeps apart. dec:17's test parses `vocab/ontology/dec.ttl` alone
(the module is standalone; PROV is not HGA) and asserts the four triples.

**Manifest.** Each criterion flips `prog:met false → true`, gains `prog:metOn "2026-09-11"`,
and declares its `prog:oracleArtifact`s in dec:11's form (shape:line, the conformant example,
the leak fixture). `prog:retrospective` stays false (declared 05-31, met 09-11; M4 cannot fire).
The `# UNMET.` prose above dec:09 and the `prog:oracleTest is a TARGET` remarks are rewritten.

**The four `prog:proposedDependsOn` edges stay proposed, and their rationales are corrected.**
dec:02→dec:01, dec:12→dec:11, dec:13→dec:11, dec:15→dec:14 each say *"Ungroundable: fails A1
… and A2"*. After this loop A1 and A2 hold, and M17 would force assertion unless another arm
fails. **A6 fails on every one** — predicted, then measured by the membrane at task time: each
new oracle declares its shape file (`dec-shapes.ttl:38` vs dec:01's `:15`; `risk-shapes.ttl:35`/
`:49` vs dec:11's `:17`; `governance-shapes.ttl:45` vs dec:14's `:27`), and A6 compares with the
`:line` suffix stripped. So each rationale's last clause becomes *"fails A6 — both declare
`<file>`"*, the form dec:08→dec:01 already uses. M18 needs exactly one rationale per edge; the
text is replaced, not appended.

**Oracle.** (i) Each new test RED before its fixture exists (missing file), GREEN after.
(ii) **Falsification per fixture:** make the leaking node conform (add the missing property /
put the confidence in range) → the test must go RED on the `sourceShape` assertion, with
`conforms` possibly still false — that is the proof the pin does the work `not c` would not.
(iii) `tests/test_arc_manifest.py` green on the flipped manifest — M2 (metOn present), M8, M15,
M17 (no edge newly groundable), M18 (one rationale each). (iv) `tests/test_arc_landscape.py`
green after `scripts/arc_depends.py` regenerates the cache. (v) `tests/test_artifact_terms.py`
and `tests/test_artifact_declarations.py`: the tracked-`.ttl` pin re-measured 149 → 154 in both
(the [[R179]] trap, hit again by PR #204 § 7 — five new tracked `.ttl` files). (vi) The strip
reads `dec ▰▰▰▰ 17/17` and `serves 1/3/…` with this spec's handoff on disk.

**Must not touch.** The shapes themselves (a negative test that needs the shape edited is a
different loop); the four existing `not c` tests (Evidence they are not, but they are other
criteria's oracles and the ablation keys on their node ids); the `dec:08→dec:01` edge; the etkl
criteria (the corpus loops of September are not re-opened here).

## 3. What is NOT done

- No `prog:dependsOn` is asserted. If the membrane refutes § 2's A6 prediction on any edge (M17
  fires), that edge is asserted in the same change and `test_arc_ablation` becomes its oracle —
  recorded in the handoff as a refuted prediction, not silently done.
- The residue register gains no row: nothing is deferred. It is opened for nothing, per § 3.2
  of the register-serves-the-arc spec — these criteria have no `prog:blockedBy`.
- The remaining 9 ready criteria (etkl ×5, holon:06, substrate ×3) are not touched; the next
  loop chooses from the same derivation.
