# Handoff: substrate:03, spec approved and plan not yet written (2026-10-21)

**Serves:** prog:criterion:substrate:03 — verify it is still `prog:met false` before starting.

**Topic:** substrate · **Date:** 2026-10-21

**Doc impact: none.** This is only a handoff.

Part 5 was written first. The session handed off at 67,499 working tokens, 1.35× the 50K originating
floor, immediately after the maintainer approved the written spec.

## 5. The next concrete action, typed

1. **ASSERTED: write the plan** at `docs/superpowers/plans/2026-10-21-substrate-03-in-engine-policy.md`
   with superpowers:writing-plans, from the approved spec
   `docs/superpowers/specs/2026-10-21-substrate-03-in-engine-policy-design.md`. Do it in the first
   third of a fresh session. The plan obeys CLAUDE.md § Plan authoring discipline: interfaces,
   invariants and oracles, with no function bodies. Every task carries a FALSIFICATION block; the arms
   are listed in spec § 5. Cite the spec's sections instead of restating them (rule 6).
2. **PROPOSED: the two seams in spec § 4.2 and § 4.3 hold the way the design assumes.** The first is
   whether rdflib keeps Fluree's `_:fdb-…` blank-node label when serialising JSON-LD. The second is
   whether the `onClass sh:NodeShape` guard refuses W's retraction of `ex:DocShape a sh:NodeShape`.
   Neither has been measured. The plan's **first task** measures both. If the type retraction is
   admitted, the remedy goes into spec § 4.3, as an amendment PR, and not into the plan. The probe
   harness in `docs/superpowers/evidence/2026-10-21-substrate-03-probe/probe_lib.py` gives you a
   governed ledger in under a minute.
3. **PROPOSED: the composite holds.** That composite is iladub-shapes' `INVARIANT` 400 for W under
   the full bundle (spec § 8). It is unmeasured, so a plan task must run it before building on it.

## 1. Goal

Implement substrate:03, in-engine policy plus a closed write gate, and close R328. The detail is in
spec § 1.

## 2. Where the primaries are

- The spec: the path above (PR #363).
- The probe evidence: `docs/superpowers/evidence/2026-10-21-substrate-03-probe/`. `q8.out` is the
  assembled bundle. `q8.policies.jsonld` holds the exact `f:query` values. `q8_q8one_single_tx.rq`
  is the one-transaction provisioning.
- The code it touches, as listed in spec § 4. Also read the design handoff
  `docs/superpowers/2026-10-21-substrate-03-design-approved-handoff.md` § 2.

## 3. What was decided, and where it is recorded

- The spec, approved by the maintainer on 2026-10-21 ("approved, write the plan"). It is recorded in
  the spec's **Approved:** line. The approval covers § 4.1's steward role as a parameter, and § 7's
  list of what is not done.

## 4. Unverified or assumed

- The two seams and the composite in part 5, items 2 and 3.
- Spec § 8 in full. All of § 2 was measured by a subagent on macOS. The controller read its outputs
  but did not re-run them.
- Linux policy behaviour. It is first exercised by the `substrate` CI job on the implementation PR.
