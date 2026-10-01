# Handoff: R261 — write the plan for the approved totals-family spec (2026-10-01)

**Topic:** r261-totals-family · **Date:** 2026-10-01

**Serves:** prog:criterion:etkl:03 — the plan for the spec that carries cbh's totals family.

**Doc impact: none** (this handoff; the spec declares its own increment).

Authored at 52,645 working tokens (plimslop hook), 1.05x the originating floor. The spec was
finished and approved under it; the plan was not started for that reason. Part 5 is written first
and graded per action.

## 5. Next actions (written first)

- **Asserted.** Fresh session: `superpowers:writing-plans` against
  `docs/superpowers/specs/2026-10-01-r261-totals-family-design.md` (commit `5d45fac`, approved by the
  maintainer in chat 2026-10-01). Output: `docs/superpowers/plans/2026-10-0X-r261-totals-family.md`.
  Do not re-open the spec's rulings (§ 0 R-a…R-d).
- **Asserted:** the plan's task 1 is P3 (spec § 5.1), and every § 3 seam becomes a MEASURE step
  with its command, never a claim (CLAUDE.md plan rules 2–3).
- **Proposed, and it may fail — P3:** the total-of-totals question answers *yes* on `1,951,264`.
  Unprobed. If it does not, the grand total is not bound and cbh is not accepted by this loop
  (spec § 5.1). The session finds out in minutes, at plan task 1.
- **Proposed, and it may fail:** `tab:PrintedTotal ⊑ tab:AggregationCell` survives the shape
  enumeration (spec § 4). If an `EntryCell`/`AggregationCell` shape demands a grid position, the
  superclass changes; the plan must settle this before the vocabulary task.

## 1. Goal

A plan, contract-style (interfaces, invariants, falsifying oracles; no function bodies), for the
approved R261 spec.

## 2. Where the primaries are

- The spec: `docs/superpowers/specs/2026-10-01-r261-totals-family-design.md` — §§ 2–5 are the
  contract; § 3 lists the seams to measure; § 6 is what is not done (plan rule 5 reconciles tests
  against it).
- Start point and measurements: `docs/superpowers/2026-10-01-r261-totals-family-spec-handoff.md`
  (Addendum 1 = P2 and census; Addendum 2 = P1).
- The probe to extend for P3: `scripts/r261_total_question_probe.py`.

## 3. Decided, and where recorded

- Rulings R-a…R-d: spec § 0, approved in chat 2026-10-01. Recorded in the spec and user memory
  `r261-totals-family-loop` only; R47/R261 ✎ amendments land with the loop (spec § 6).

## 4. Unverified or assumed

- Every `file:line` in spec § 3 was read by a subagent at `ced805a`, not run. Re-measure.
- That `offer_single_line` returns `None` on cbh's port-total bands is inferred from its query.
- That band 9's carved remainder classifies `NON_TABLE` is the box-split counterfactual, not a
  measurement on a carved band.
