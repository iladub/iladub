# Handoff: R261 loop (b) — spec written; review it, then plan (2026-10-02)

**Topic:** r261-totals-family · **Date:** 2026-10-02

**Serves:** prog:criterion:etkl:03 — loop (b) of the R261 totals family: the grand total `1,951,264`.

**Doc impact: none.**

Written at about 52K working tokens, just over the originating floor (override logged). The spec
was drafted under it, and the self-review pass and this handoff were done just over it. Part 5 was
written first.

## 5. Next actions (written first)

- **Asserted:** the maintainer reviews the spec
  `docs/superpowers/specs/2026-10-02-r261-grand-total-design.md`. That is brainstorming step 8, and
  the HARD-GATE: no plan is written before the written spec is approved.
- **Asserted, after approval:** a fresh session runs `superpowers:writing-plans` from the spec,
  after `managing-context-budget`. Plan Task 1 is spec § 6.1.
- **Proposed, and it may fail:** spec § 6.1 predicts that `AskTotalRole`, asked through BAML,
  reproduces P4b on its 6 cases. If it fails, the wording is not re-tuned, and the grand total
  returns to the maintainer as a ruling.

## 1. Goal

Turn the approved loop (b) design into a written spec, and get it reviewed before any plan.

## 2. Where the primaries are

- **The spec:** `docs/superpowers/specs/2026-10-02-r261-grand-total-design.md`. § 0 holds the
  concerns and rulings R-e…R-h. § 7 holds the seams, measured by RUN at `dfc8be9`.
- **The previous handoffs:**
  - `docs/superpowers/2026-10-02-r261-grand-total-write-spec-handoff.md` part 3: the design as
    approved in chat.
  - `docs/superpowers/2026-10-02-r261-grand-total-spec-handoff.md` part 2: every other primary.
- **PR #291,** the base of this branch: the P4/P4b evidence and the probe. It must merge first.

## 3. Decided, and where recorded

- **The design (R-e…R-h):** approved in chat 2026-10-02, now recorded in the spec's § 0.
- **Spec wording changes the seams forced, not yet reviewed by the maintainer:**
  - The crop is derived through graph links and PrintedTotal boxes, because the carve empties the
    operand total bands. Recorded in spec § 3.
  - The `tab:totalOf` comment is amended alongside `tab:aggregates`, since it reserves the same
    level. Recorded in spec § 4.
  - The recorded-readings listing includes each operand's `tab:cellText`. Recorded in spec § 3.

## 4. Unverified or assumed

- **How a `tab:totalOf` table URI maps back to a band index** in `compile_tables`. Spec § 3 names
  this as a seam for the plan to measure.
- **The § 6.1 BAML reproduction of P4b.** Unrun.
- **The § 7 seam scripts** live in a session scratchpad, not in the tree. Their outputs are quoted in
  the spec. Re-measure them; do not trust them as recorded facts.
- **The context figure** comes from the hook: 50,406 working tokens at the last prompt, plus this
  writing.

## Addendum — the spec is APPROVED (2026-10-02)

The maintainer approved the written spec in session on 2026-10-02 (*"approved"*), including the
three seam-forced wording changes listed in part 3. That clears brainstorming's HARD-GATE for the
plan. Part 5's first asserted action is done. **START:** a fresh session runs
`managing-context-budget`, then `superpowers:writing-plans` from the spec. The planning session
did not start here because the session stood at 61K working tokens, 1.2× the originating floor.
