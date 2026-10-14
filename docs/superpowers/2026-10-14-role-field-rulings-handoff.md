# Handoff: R310 and R311 ruled — apply them (2026-10-14)

**Serves:** maintenance — the two rulings the matrix-cell loop left open (contracts and grounding).

**Topic:** contracts and grounding · **Date:** 2026-10-14 · **Branch:**
`matrix-cell-is-an-observation` (PR #340, stacked on #339). Neither PR is merged; the maintainer
has not yet said whether to merge them.

## 5. The next concrete action, typed

1. **ASSERTED: apply R310.** A role-declaring field is admitted only for a concept read in that
   role, at every door (`exact_field`, `marker_field`, the proposer's answer, and whatever
   `_admissible_fields` offers the proposer). One guard after the field is chosen, before
   `_emit_candidate`, was prototyped and reverted (`2026-10-12-matrix-cell-executed-handoff.md`
   § 6): the grounding and feed suites read 165 passed, 1 failed, and the failure is the control
   arm the ruling inverts. Open within it: whether `_admissible_fields` must drop role fields too,
   so the pre-filter does not ask a proposer whose answer cannot be admitted ("no oracle, no
   worker"). Measure that, do not assume it.
2. **PROPOSED: apply R311 where both graphs meet.** The ruling requires a scheme or a value
   constraint on every role field. The scheme is in the contract file (`etkl:admissibleScheme`);
   the value constraint is in a separate shapes file (`examples/finance/statement-shapes.ttl`),
   handed to `ground_document` and never to `load_contract`. So the clause cannot sit in
   `etkl:ContractRoleShape` over the contract graph alone. Candidate placements: (a)
   `load_contract` takes the shapes path and validates contract ∪ shapes; (b) a SHACL shape run
   where `ground_document` first holds both. What could fail: (a) changes a signature with 54
   call sites across `src/`, `scripts/` and `tests/`; (b) needs the constraint set
   (`ground._VALUE_CONSTRAINTS`, nine predicates) stated once, in SHACL, not again in Python.
   Decide the placement in the first third of the session; it is the loop's one design decision.
   After both rulings: invert the R311 pin
   (`test_an_empty_key_under_an_unconstrained_role_field_grounds_by_field_identity`), add the
   negative fixture, regenerate the corpus baseline (the change touches `src/` and `vocab/`), and
   expect apple's counts unchanged (all three of its role fields carry an oracle).

## 1. Goal

Close R310 and R311 as ruled, with apple's grounding unchanged.

## 2. Where the primaries are

- Register rows R310, R311 in `docs/superpowers/residues-open.md` (rulings appended there).
- `src/iladub/ground.py`: `ground_concept`, `load_contract`, `_admissible_fields`,
  `_VALUE_CONSTRAINTS`, `_property_shape`.
- `vocab/shapes/etkl-shapes.ttl`: `etkl:ContractRoleShape`, `etkl:FieldRoleShape`.
- `examples/finance/statement-{contract,shapes}.ttl`.
- Tests: `tests/test_ground_field_role.py`, `tests/test_contract_roles.py`.

## 3. What was decided, and where it is recorded

- R310 and R311: both ruled YES by the maintainer on 2026-10-14, recorded in their register rows.
- The stem's 320 s budget overrun is on `main` too (four timed compiles, executed handoff § 6).
  Whether to raise a row for it was put to the maintainer and is unanswered: recorded nowhere
  else.

## 4. Unverified or assumed

- That `_admissible_fields` needs the R310 guard: not measured.
- That apple's counts survive both changes: predicted from its contract, not run.
- The R310 prototype was run on the non-corpus grounding and feed tests only.
