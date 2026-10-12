# Handoff: a matrix cell is an observation — executed (2026-10-12)

**Serves:** maintenance — direction (b) of the 2026-10-06 ruling (contracts and grounding).

**Topic:** contracts and grounding · **Date:** 2026-10-12 · **Branch:**
`matrix-cell-is-an-observation`, stacked on `matrix-cell-plan` (PR #339) at `4c0191a`.

Part 5 was written first, at about 130K working tokens: over the 50K originating floor and under
the 150K executing floor. The session was a controller: every line of code was written by a
dispatched implementer and reviewed by a second agent, so parts 1–4 are pointers to their reports
and to the diff, and each action in part 5 is graded.

## 5. The next concrete action, typed

1. **ASSERTED: the maintainer reads § 3 below and overturns what he disagrees with.** Fourteen
   decisions were taken on his behalf during execution, on top of the plan's D1–D7. None is a
   ruling. Two change what grounds under a role contract (§ 3, items marked *behaviour*).
2. **PROPOSED: the next subject is the ruling the two new residue rows wait on, not a build.**
   (a) Is a role field filled *only* by a concept read in that role? (b) Must a role field declare
   an oracle (scheme or value constraint)? Both are one-shape or few-line changes once ruled; the
   prediction that could fail is that (a) leaves `tests/test_ground_section_marker.py` and the
   key-split control arms unedited. The final review says the wider form "changes an existing
   control arm", read not run.
3. **PROPOSED: a second role-shaped document is the first real test of D1–D6.** Apple exercises
   none of them (flat row tree, no spanning key, no rider, no path-less column). Until a document
   does, they are pinned by synthetic tests only.

4. **PROPOSED: the stem's budget overrun predates this branch.** Two corpus tests fail on
   graincorp-stem at 320 s (§ 2a). What supports "not this branch": the stem's baseline snapshot
   is byte-identical, `test_expected_verdict` calls no feed or grounding code, and the alarm wraps
   `compile_document` only. What is missing: **no timing was taken on `main`.** One serial stem
   compile on `main`, on a quiet machine, settles it in six minutes. If `main` is under 320 s,
   this branch slowed a compile and that is a defect to find before merge.

## 1. Goal

One contract that names a line item, a period and a value grounds apple's two statements, one
record per cell, and nothing else in the corpus moves.

## 2. Where the primaries are

- **Spec:** `docs/superpowers/specs/2026-10-12-a-matrix-cell-is-an-observation-design.md`; § 9
  overrides §§ 3–5, and § 10 (appended at execution) records where the code departs from § 3.6
  and § 9.3.
- **Plan:** `docs/superpowers/plans/2026-10-12-a-matrix-cell-is-an-observation.md` (D1–D7).
- **Code:** `ground.py` (`load_contract`, `ground_concept`, `_grounds_to`, `marker_field`,
  `ROLE_*`, `SHARED_ROW_KEY`); `feed.py` (`table_records(per_cell=)`, `_header_parts`,
  `ground_document`); `validate.validate(use_shapes=)`; `vocab/ontology/etkl.ttl`
  (`etkl:fieldRole`, `etkl:FieldRole` and its three individuals); `vocab/shapes/etkl-shapes.ttl`
  (`etkl:ContractRoleShape`, `etkl:FieldRoleShape`); `examples/finance/statement-*.ttl`.
- **Tests:** `tests/test_contract_roles.py`, `test_feed_matrix_cell.py`,
  `test_ground_field_role.py`, `test_finance_contract.py` (CI);
  `test_corpus_apple_contract.py` (`corpus`).

## 2a. What was measured

On apple, under `examples/finance/statement-contract.ttl`, first run, no pattern changed after a
run:

| what | predicted | measured |
| --- | --- | --- |
| records / concepts | 180 / 540 | 180 / 540 |
| shared row keys (p0 + p1) | 52 (44 + 8) | 52 (44 + 8) |
| distinct record ids / subjects | 180 / 180 | 180 / 180 |
| row-key regions / column-key regions / key region equal to a cell region | ≤ 59 / 6 / 0 | 59 / 6 / 0 |
| `FeedResult` | — | `(180, 394, 146)` |
| grounded: line items / periods / values | derived 34 / 180 / 180 | 34 / 180 / 180 |
| proposed: unshared lines outside the scheme / shared row keys | 94 / 52 | 94 / 52 |
| shared row keys grounded under a proposer naming the line-item field (P3) | 0 | 0 |
| values carrying `$ ` (D7) | 40 | 40 |
| `validate_shapes=True` (P6) | conforms | conforms |

Falsifications run on the corpus arm: switch off gives 59 records; the refusal branch deleted
grounds `Total net sales` on two subjects per period; `September` removed from the period pattern
loses exactly 28.

After the last `src/` edit (`bab6edc`):

| what | result |
| --- | --- |
| baseline regenerated (P5) | `tests/corpus-baseline/inputs.json` alone; all eleven snapshots byte-identical |
| non-corpus suite, 32 chunks plus `-m serial` | 2146 passed, 1 failed, 7 skipped, 2 xfailed |
| that one failure | `test_arc_manifest.py::test_etkl_criterion_sources_point_at_the_document_they_name`: Task 4's eleven manifest lines moved who-wfa's subject line from 149 to 160. Re-pointed in `e77cc9f`; the file then reads 28 passed |
| corpus suite, 19 files, serial | 86 passed, 2 failed |
| those two failures | `test_expected_verdict[graincorp-stem]` and `test_grounding_where_contracted[graincorp-stem]`, both `BUDGET EXCEEDED … 320s` inside `compile_document` |
| stem compile, standalone, this branch | 329.0 s; `test_corpus_stem.py`'s fixture took 319.92 s and passed |
| `BUDGET_S` | 320, set in `ac3bbf4` (2026-08-04) from a measured 254.1 s |
| machine load during the run | 3.3 to 3.8, from system processes |
| new register rows | R310 to R314; R308 and R309 appended, not struck |

## 3. What was decided, and where it is recorded

The plan's D1–D7 stand as written. In addition, the executing session decided the following; each
is also in spec § 10 or a register row, and none is the maintainer's.

- *behaviour* **"Shared" is counted on the delivered key text**, not the label tuple (final review
  I-1). Two rows with different paths and one joined text are both refused.
- *behaviour* **`marker_field` does not offer a role-declaring field** (final review I-2), narrow
  form. A section caption in the line-item scheme quarantines under a role contract. The wider
  form is a residue row.
- **The shared-label count is PROCEDURAL** (decidable exact arithmetic, one logical table), not
  the AXIOM spec § 3.6 says: it counts over paths `_header_parts` already selected, and a query
  would need a second selection or a throwaway graph.
- **`_grounds_to(declared_role=)`** makes the recorded rejection reason true for a role-picked
  concept on an unconstrained field, rather than making that path unreachable.
- **`load_contract` runs only the two role shapes** (`validate(use_shapes=)`): the whole
  `etkl-shapes.ttl` refuses the three shipped shipping contracts, which declare no
  `etkl:hasTargetShape`. `etkl:ContractRoleShape` also targets subjects of `etkl:hasField`.
- **Under `per_cell`, pass 3 settles subject ties for every record of the call**, non-matrix
  ones included.
- **A row covered only by a `tab:DerivedRowGroup` reads per cell with a shared key and is
  refused.** Unexercised.
- **Key region form is `p<page>#<fragment>`.**
- **The CI matrix is 4×2**, because a 2×2 with one repeated label has no row that can ground.
- **The example's licence header follows `examples/supersession.ttl`**; the plan cited
  `capacity-contract.ttl`, which carries none.
- **The whole-branch review ran before the baseline regeneration**, so one fix wave did not stale
  it.

## 4. Unverified or assumed

- **D1–D6 are exercised by no corpus document** (as § 5.3).
- **A role field with no oracle grounds everything of its role, the empty key included.**
  Measured, pinned "MEASURED, NOT ENDORSED", not guarded.
- **A role-less rider can still fill a role field through `exact_field` or a naming proposer.**
  Measured on a synthetic matrix; 0 on apple.
- **The two role shapes run on pySHACL only.** No engine-parity pin.
- **The apple counts come from single compiles.**
- **Falsification of the switch on the corpus arm ran on an earlier spelling of it**; the final
  spelling was re-falsified on the CI arm only.
