# Handoff: R305, a committed corpus baseline (2026-10-10)

**Serves:** maintenance. R305 was picked by the maintainer on 2026-10-10 from
`2026-10-10-r300-closed-handoff.md` § 5.1.

**Topic:** test infrastructure · **Date:** 2026-10-10

Part 5 was written first, before execution, under the 50K originating floor.

## 5. The next concrete action, typed

1. **PROPOSED: if this loop has not merged, run O1 first.** The spec
   (`docs/superpowers/specs/2026-10-10-r305-corpus-baseline-design.md` § 5) predicts that a second
   `regenerate` reproduces the committed bytes. If it does not, the baseline is not a cache, and
   the design stops there. That costs one 24-min pass.
2. **PROPOSED: after merge, no subject is chosen.** The candidates from the R300 handoff remain:
   R299, R295, R304 and R83. The maintainer picks.

## 1. Goal

Make a blast-radius check one corpus pass plus a `git diff`, never a re-measurement of `main` (R305).

## 2. Where the primaries are

- The spec: `docs/superpowers/specs/2026-10-10-r305-corpus-baseline-design.md`. § 1 holds this
  session's measurements, and § 5 the oracles.
- The register row: `docs/superpowers/residues-open.md`, R305.

## 3. What was decided, and where it is recorded

- **The CI gate is blocking** (maintainer, 2026-10-10, this session). Recorded in spec § 2 and here.
  It is not in CLAUDE.md (spec § 7).

## 4. Unverified, assumed, or found on the way

See spec § 6.
