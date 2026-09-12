# Handoff — R212's carrier: the ignored band carries its text (spec written, no code)

**Topic:** the-ignored-band
**Serves:** prog:criterion:etkl:02 — R212 is a prerequisite of that criterion's measures, not a
criterion of its own.
**Date:** 2026-09-12. **Branch:** `r212-carry-the-ignored-bands-text`, cut from `ec1dc4e`.
**Spec:** `docs/superpowers/specs/2026-09-12-the-ignored-band-carries-its-text-design.md`.

**Doc impact: none.** Spec + two register rows. Nothing queues for a release, nothing blocks one.

Part 5 was written first, while under the originating floor.

## 5. The next concrete action

### 5a. ASSERTED: write the plan for the carrier, from the spec's § 5

Mechanical in the sense that the design is settled and the oracle is named. The spec fixes what is
carried, what is refused and why (§ 3), and states five oracle arms plus the one seam that must be
measured before the emitter's call site is written (§ 5, `document.licence_evidence`). A plan turns
that into tasks; it does not re-derive the design.

**Do not re-open the vocabulary choice.** Three candidates were considered and refused with reasons
in § 3 — `iladub:CandidateConcept`, `tab:RegionCaption`, and the transient `tab:PriorPageTextBlock`
family. Each refusal cites a measurement in § 2.

### 5b. PROPOSED: carriage moves no corpus score — RUN THE INVARIANT ARM BEFORE BUILDING ON IT

The spec's § 3 rests on this, and it is a prediction, not a measurement: the score is
`asserted / (asserted + escalated)` (`document.py:1760`), the NON_TABLE branch increments neither
counter (`compile.py:814-824`), and emission is decoupled from accounting (`compile.py:802-803`). So
a carrier that touches neither counter should leave all 7 corpus scores byte-identical while the
graph hash moves.

**That reasoning is from reading, not from running.** `scripts/corpus_verdict_snapshot.py:47-89`
dumps per-region verdicts plus a canonical graph SHA-256; run it both sides of a throwaway emitter
before any task is written. **If any score moves, the spec's § 3 is wrong at its load-bearing point**
and the carrier needs a different seam — a rung whose criteria are pinned scores cannot absorb a
carrier that shifts them. Cheap to refute: one script, two runs.

### 5c. What this loop deliberately leaves exposed

[[R218]] and [[R219]]. Neither blocks the plan; both were found by this loop's own measurements and
are recorded rather than fixed.

## 1. Where the primaries are

- **The spec** — `docs/superpowers/specs/2026-09-12-the-ignored-band-carries-its-text-design.md`.
  § 2 is every measurement this loop made; § 3 the design and the three refusals; § 5 the oracle and
  the seam; § 6 what is assumed.
- **The ruling that made this a prerequisite** — `specs/2026-09-11-the-span-the-author-drew-design.md`
  § 0, § 3.3, § 5 step 2 (PR #209, `f1df625`), and [[R212]]'s row.
- **The census instrument** — `scratchpad/ignored_band_census.py`, this session's scratchpad. **Not
  committed**; § 6 of the spec says why it should be forked from
  `scripts/unbooked_ink_census.py:61-80` rather than reused as-is.
- **The criterion** — `tests/arc-manifest.ttl:210-219`, and its hold note at
  `tests/corpus-manifest.ttl:56-57`, whose route step 3 is the maintainer reading the carried
  records against the page.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The carrier is a committed fact in an owned namespace, neither asserted nor escalated | spec § 3 — **here and nowhere else yet; reversible** |
| `iladub:CandidateConcept`, `tab:RegionCaption` and `tab:PriorPageTextBlock` are each refused, with a measured reason | spec § 3 — same status |
| Every ignored band is carried, with no rule selecting "furniture" | spec § 3; this is what keeps the step PROCEDURAL under §8 |
| The proposer input is the NEXT loop, not this one | spec § 4 |
| `tab:RegionCaption`'s missing provenance is not repaired here | [[R218]] |
| The census's band-vs-distinct-text confound is not resolved here | [[R219]] |

The namespace for the new term (`tab:` vs `etkl:`) is **deliberately not decided** — spec § 6.

## 3. Unverified or assumed

- **The invariant arm is unrun** (5b). It is the claim most likely to be wrong and cheapest to check.
- **The census re-derives bands** via `page_bands` + `classify` instead of capturing the list
  `compile_tables` actually used; ordering was replicated by reading, not proven equal (spec § 6).
- **"No test pins zero-emission on the ignored path"** is one grep over `tests/`, not an enumeration.
- **Whether carrying all 146 bands is wanted** is a maintainer question the spec answers by carrying
  all of them. Reversible.
- **`document.licence_evidence` as the producer** is a named seam, not an answer (spec § 5).
- The 146/2935 figures are this session's, at `ec1dc4e`; the graincorp per-band figures are exact,
  the corpus aggregate is an upper bound ([[R219]]).

## 4. What this loop did not touch

No `src/` change, no vocabulary, no shapes, no tests beyond the register's own pins. [[R166]],
[[R211]] and etkl:02 are all where PR #210 left them.
