# Handoff — write the `holon:05` plan (`the membrane reports its health`)

**Date:** 2026-08-25 · **Branch:** `holon-05-o2-ruling` @ `c39b7ca` · **Shape: mechanical** — pointers
only. It restates nothing from the primaries and settles nothing.

## Goal

One line: **write the implementation plan for `holon:05`.** The spec is revised, adversarially
reviewed, and now twice-amended; every ruling it was waiting on has been taken. Nothing else is owed
before the plan.

## Where the primaries are, and what to establish at each

| open | to establish |
|---|---|
| `docs/superpowers/specs/2026-08-25-the-membrane-reports-its-health-design.md` | **The whole spec.** Read the header's two amendment notes first, then §2 (measured facts, each stated once), then §4 (design), §7 (oracles), §8 (done), §9 (not done), §10 (seams to measure), §11 (residues). Every later section cites §2.x — follow the citation, do not re-derive. |
| `docs/superpowers/2026-08-25-holon-05-o2-finding6-rulings.md` | **Read before §7 and §4.5.** What (a′) is, why the seam starts at the *furnish*, and the four things the ruling explicitly does **not** settle — those are yours to measure. |
| `docs/superpowers/2026-08-25-holon-05-seam-6-refusal-vehicle.md` | Only if a ruling is questioned, or when you need the exact mutation. The ANSWER block is the one part the plan actually consumes. |
| the review + the two earlier ruling files (`…-adversarial-review.md`, `…-b1-ruling.md`, `…-b2-b3-b7-p1-rulings.md`) | Only if an earlier ruling is questioned. Cited by the spec, not superseded. |
| `docs/superpowers/2026-08-25-holon-05-measurements.md`, `…-design-decisions.md` | The evidence §2 was written from. Open a section, not the file. |
| `CLAUDE.md` § Plan authoring discipline | **Rules 1–6, before writing a line.** Rule 6 is the one this loop is most exposed to: the invariants are settled in the spec, so the plan **cites** them (`see spec §4.5`) and never re-argues them. |

## What was decided, and where each decision is recorded

**All of it is recorded in one file each, and nowhere else — therefore reversible.**

- **B1** (subject is `etkl:CompiledDocumentHolon`) → `…-b1-ruling.md`.
- **B2, B3, B7, P1** (owned activity node; four-artifact amendment; site constraint + shape; registry)
  → `…-b2-b3-b7-p1-rulings.md`.
- **O2's `Compromised` leg = option (a′)** → `…-o2-finding6-rulings.md`, ruling 1. Maintainer's choice
  from the four costed options, 2026-08-25.
- **Finding 6 ships as `R127`, unfixed, findings 7–8 as `R128`/`R129`; candidate successor loop named
  alongside `holon:06`, not pre-committed** → same file, ruling 2. Taken on the assistant's
  recommendation at the maintainer's request.
- **The spec edits those two rulings require** → made, and listed at the end of that same file so the
  plan can check they landed.

## Unverified or assumed

- **Whether re-entering the extracted seam on an already-furnished graph is a no-op absent the
  mutation.** O2's third leg has no control arm until this is measured. `escalation-furnish.rq` would
  run a second time over a graph already carrying its own output; the unmutated re-entry **must**
  still conform. Not measured.
- **Whether any CORPUS document escalates at document scope.** The seam-6 lever was proven on
  `recognized_pair_plus_escalating_page_pdf` (`tests/etkl/test_escalation_wiring.py:33-34,54-61`), a
  **synthetic PDF generator**. O2's other two legs use corpus specimens. Not measured, and the oracle's
  docstring must say which it ended up using rather than letting the reader assume all three match.
- **What the extraction does to `DocumentReport` construction** (`document.py:1636-1639`, keyword since
  R73) and **which object `graph` names across it** (`:1609` uses in-place `+=`). §10 seams 3 and 4 —
  precautionary before the ruling, live after it.
- **§10 seams 1, 2, 5, 7 are untouched by these rulings and remain unmeasured**, including the catcher
  census, which `MembraneRefusal` makes load-bearing and which has already been missed once.
- **`R127`'s coupling to O2 is asserted from the seam-6 measurement, not re-run here.** The census
  (`{1: 17}`, `{1: 18}` over two documents) is that file's, dated 2026-08-25.
- **The suite baseline `1312 passed, 7 skipped, 1 xfailed` in 2386.82 s** is §8's, measured before any
  implementation. Not re-run this session. ~40 minutes.
- **`tests/test_doc_governance.py` is green** on this branch (`4 passed`, run 2026-08-25). Nothing else
  was run.

## The next concrete action

**In a fresh session, in its first third: write the plan** from the spec, citing the rulings rather
than re-deriving them. Start by measuring §10's open seams — 1, 2, 5, 7, plus the two named under
*Unverified* above — because every one of them is a load-bearing claim the plan would otherwise assert
from reading, which is CLAUDE.md rule 2's exact failure. **Delegate the measurement, author the plan.**
