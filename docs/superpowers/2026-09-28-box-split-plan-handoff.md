# Handoff: write the plan for the box split (2026-09-28)

**Serves:** prog:criterion:etkl:03 — cbh is not accepted until `#table9` compiles as the two tables the author drew.

**Topic:** box-split · **Date:** 2026-09-28 · **src measured:** `6eb80ca` · **Doc impact: none.**
**Authored at:** 84,387 working tokens, over the 50K originating floor. That is why the plan is
handed off. Parts 1–4 are pointers. Part 5 is graded.

## 5. Next action (written first)

- **Asserted:** in a fresh session, invoke `superpowers:writing-plans` on the approved spec
  `docs/superpowers/specs/2026-09-28-box-split-design.md` (PR #284). The maintainer approved the
  spec on 2026-09-28. Do not re-open its § 0 rulings.
- **Proposed, to measure before the plan relies on it** (spec § 4, named risks). The plan must
  name these seams rather than answer them:
  1. Does T2 (2 columns, no boxhead) come out with 0 column labels, or does downstream header
     derivation promote `ALB | 1 - 15 October`? The what-if stopped at `_rule_boundaries`, so this
     is unmeasured. O2 will find out in minutes.
  2. **Enumerate** every test, reading, fixture or register row that names a cbh `#tableN` with
     N ≥ 9. The split shifts them by +2.

## 1. Goal

A plan (contract, not code, per CLAUDE.md § Plan authoring discipline) for the spec's § 2–3
implementation, with § 5's oracles (O1 in CI, O2 local, C1–C3), `tab:12`, and the register row
widening R74.

## 2. Where the primaries are

- **The spec**, on PR #284, branch `box-split`: `docs/superpowers/specs/2026-09-28-box-split-design.md`.
  - § 7 carries every measurement, with commands.
  - § 3.4 is the box-scoping table the plan must preserve.
- **Probe scripts** (gitignored, local only): `internal/benchmarks/cbh-boxes-2026-09-28/`.
  - `boxes.py` is the rule reader, the touch test, and the box test.
  - `closed2.py` is the frame check, including the corner-ink fix.
  - `seam.py` is the band-9 what-if.
  - These are throwaway measurement, not implementation. Re-run them; don't copy them.
- **The `tab:11` pattern** for O2 and the strict xfail: `tests/test_carriage.py` (module
  docstring), and `tests/arc-manifest.ttl` (`prog:criterion:tab:11`).
- **Earlier handoffs:** `docs/superpowers/2026-09-28-cbh-box-split-design-handoff.md` (PR #283)
  and `docs/superpowers/2026-09-28-cbh-one-is-not-a-compile.md` (PR #282). Both PRs are open and
  mergeable, and neither has been merged by this session.

## 3. What was decided, and where it is recorded

- **The five rulings** (approach 1, totals deferred, stroke-width touch as AXIOM with zero-width
  rules touching only exactly, trigger of ≥2 closed boxes, declare `tab:12`) are recorded in
  spec § 0.
- **Design §§ 1–4 and the written spec** were approved by the maintainer in chat on 2026-09-28.
  They are recorded in the spec and on PR #284.

## 4. Unverified or assumed

- **T2's header outcome**: part 5, item 1.
- **The band-index shift's blast radius**: part 5, item 2.
- **Spec § 7.4** (`extract_rules` over-read figures) is the earlier handoff's census, not re-run.
- **Where the Note residue and `1,951,264` land after the split** is unmeasured. O2 records it.
- **Whether reportlab can draw a sub-stroke gap for N3**: a 2e-5 gap, in whatever units
  pdfplumber reports back. This is unmeasured. The fixture has to be checked by reading it back
  with pdfplumber, not assumed.
