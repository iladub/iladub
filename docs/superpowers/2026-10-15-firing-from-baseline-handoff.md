# Handoff: R259 is next, and its firings come from the corpus baseline (2026-10-15)

**Serves:** prog:criterion:tab:07 — the shared oracle also serves `tab:02`, `tab:05`, `tab:08`,
`tab:09`.

**Topic:** compile · **Date:** 2026-10-15

**Doc impact: none.** A handoff plus an appended amendment to an existing spec (that spec carries
its own `increment`).

Part 5 was written first, at roughly the 50K originating floor. The amendment in spec § 8 was
written at about the same point.

## 5. The next concrete action, typed

1. **ASSERTED:** the next loop executes R259, and its plan is still to be written. Write it from
   `specs/2026-09-18-a-firing-is-not-a-fact-design.md` **§ 8 first**, which supersedes the spec's
   § 2.1 authored record and § 3's I3, and then §§ 2.2–5 for everything § 8 leaves standing. The
   plan is originating work, so start it in a fresh session.
2. **PROPOSED, may fail in minutes. Measure it before the plan's task 1:** the join key between a
   manifest `cor:Document` (`tests/corpus-manifest.ttl`) and its `tests/corpus-baseline/<stem>.json`.
   § 8 assumes that a key exists, and that the baseline's `pdf` field separates the 7 `corpus/`
   documents from the 4 held-out ones. If no key exists, the lift needs one, and that is a design
   question for the plan, not an implementation detail.
3. **PROPOSED:** § 8's strengthened D2 refuses a disposal of a reason with zero live firings. Before
   writing that shape, check that no existing adjudication trips it.

## 1. Goal

The handoff for PR #349 sent this loop to R259. This session confirmed that R259's blocker still
holds and had the maintainer rule the spec's fork. It also found that the corpus baseline has
replaced half of the spec.

## 2. Where the primaries are

- `docs/superpowers/specs/2026-09-18-a-firing-is-not-a-fact-design.md` **§ 8**: the amendment,
  with its measurement inline.
- `docs/superpowers/residues-open.md` **R259**: the full row and its "what would close it".
- `tests/corpus-baseline/*.json`: `pages[].regions[]` carries `reason` and `verdict`. This is the
  firing source.
- `tests/arc-manifest.ttl:1354-1362`: `tab:07`, `blockedBy "R44", "R71"`.
- `scripts/oracle_test_census.py`: O5, the close.
- PR #349 (`role-oracle-spec`): the previous handoff. CI was pending at the start of this session.
  **Verify that it merged.**

## 3. What was decided, and where it is recorded

- R259's blocker still holds at `ff2c0de`. There is no `cor:Firing`, no `cor:disposes`, no
  `escalation_census.py`, and no test with the shared node id. Measured with `grep`/`ls` this
  session, and recorded only here.
- The § 2.3 fork is ruled for **typed `cor:disposes`**: spec § 8.1.
- Firings are **derived from the baseline**, so there is no authored record and no I3: spec § 8.2.
- The maintainer asked whether every residue must close. The answer given is no. tab:07 flips on
  the oracle, the bfs/ons disposals, and R44 and R71 being closed or unblocked with a reason (M8).
  Recorded only here.

## 4. Unverified or assumed

- The join key and the `pdf` discriminator (part 5.2).
- Whether existing adjudications trip the strengthened D2 (part 5.3).
- The exact name of the guard against untagged corpus tests from `9d3c73c`.
- The baseline is only as fresh as its last `regenerate`. CI's `check` proves the fingerprint, not
  the bytes (CLAUDE.md § Corpus baseline).
