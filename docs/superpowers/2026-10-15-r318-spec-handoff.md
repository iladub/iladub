# Handoff: R318 spec written and premise-checked; implementation next (2026-10-15)

**Serves:** maintenance — loop (a) of `2026-10-15-r44-subject-chosen-handoff.md` § 5.2, chosen by
the maintainer on 2026-10-15.

**Topic:** compile · **Date:** 2026-10-15

**Doc impact: none.** A handoff.

Part 5 was written first. The spec's § 1.5 and residue rows were filled in at about 63K working
tokens, over the 50K originating floor, with the override logged. Those edits record a delegated
measurement and narrow one invariant to match it, and they add no design. Grade them accordingly.

## 5. The next concrete action, typed

1. **ASSERTED:** implement `docs/superpowers/specs/2026-10-15-escalation-carries-exact-text-design.md`
   § 3 on a new branch from `main` (this spec merged as #347). The change is small and PROCEDURAL. Whether a plan
   is needed or the spec is enough is the implementer's call; CLAUDE.md § Plan authoring applies if
   one is written.
2. **PROPOSED, and may fail in minutes:** the spec's § 4.1 test seam. Can a constructed `Band`
   reach an escalation in `compile.py`, or do existing tests reach escalations only through a PDF?
   Measure that before writing the test. If neither works, the oracle has to be a fixture PDF.
3. **PROPOSED, falsified by the regenerate:** § 4.3's blast radius. `graph_sha256` should move on
   exactly arxiv, bfs, fed-h41, ons and who-covid. First count the `…-rt` ROUND_TRIP_FAIL
   candidates in each compiled graph (see § 4.3's weakest-part note).

## 1. Goal

Carry `band_text` instead of `render_ascii` as the escalated region's `iladub:surfaceText`, and
close R318.

## 2. Where the primaries are

- The spec (above): § 1 is the measurements, § 3 the design, § 4 the oracles.
- `docs/superpowers/residues-open.md`: rows R318, R319 and R320, raised on this branch.
- `tests/corpus-manifest.ttl`: the bfs and ons adjudications to correct, by appending new nodes
  (spec § 3.5).

## 3. What was decided, and where it is recorded

- (a) before (b): the maintainer, in session. Recorded in the spec § 2.
- The invariant is "exact to the extractor", not "exact to the page": spec § 3.1, from the § 1.5
  measurement.
- `RegionReport.ascii` is renamed `text`, and the probe scripts are renamed with it: spec § 3.2.
  The maintainer confirmed this on 2026-10-15, in session, after being told it costs about 8
  probe-script edits. Recorded here.

## 4. Unverified or assumed

- The spec's § 7, plus: the measurement instrument lived in the scratchpad and is gone (its method
  is in spec § 1.5).
- R320's 42/47 figure is a proxy count. Only arxiv p10r1 was checked by eye.
