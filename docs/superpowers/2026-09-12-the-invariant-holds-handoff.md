# Handoff — R212's carrier: the invariant holds, and the spec's arm 1 does not

**Topic:** the-invariant
**Serves:** prog:criterion:etkl:02 — R212 is a prerequisite of that criterion's measures, not a
criterion of its own.
**Date:** 2026-09-12. **Branch:** `r212-invariant-arm`, cut from `a3ff34b`.
**Evidence:** `docs/superpowers/2026-09-12-r212-invariant-arm-evidence.md`.
**Spec:** `docs/superpowers/specs/2026-09-12-the-ignored-band-carries-its-text-design.md`.

**Doc impact: none.** Evidence + a register annotation. Nothing queues for a release, nothing
blocks one.

This loop ran the arm the previous handoff graded PROPOSED, measured the four seams a plan would
otherwise have assumed, and wrote **no plan** — the session passed the 50K originating floor during
measurement, and the maintainer ruled to ship the evidence and leave the plan to a fresh session.
Part 5 was written first.

## 5. The next concrete action

### 5a. ASSERTED: write the plan from spec § 5, with this loop's four corrections applied

The design is settled, the oracle is named, and the claim it rested on is now measured rather than
predicted. A plan turns spec § 5 into tasks; it does not re-derive the design, and it must **not**
re-open the vocabulary choice (three candidates refused with measured reasons in spec § 3) or the
two 2026-09-12 rulings (**all** ignored bands are carried; the term lives in **`etkl:`**).

Four things the plan must take from the evidence doc rather than from the spec:

1. **The emitter's site is settled** — the NON_TABLE branch of `compile_tables`
   (`compile.py:814-824`), where `doc`, `idx`, `band` and `page_number` are all in scope.
   `document.licence_evidence` is **refuted** as the producer on four independent legs (evidence
   § 2). Spec § 5's seam question is answered; do not re-measure it.
2. **Spec § 5 arm 1 cannot be executed as written** (evidence § 3). Use the `reportlab` route.
3. **`_band_text` must move to `bands.py`** or be imported function-locally — `compile.py` cannot
   import it from `document.py` at module level without a cycle (evidence § 4).
4. **The membrane home is a decision the plan takes** (evidence § 5): the compile membrane loads
   neither the `etkl` shapes nor the `etkl` ontologies, so a shape in the natural home never fires
   at compile time.

### 5b. PROPOSED: a carrier NodeShape wired into a membrane set needs no vacuity-registry row

If the plan chooses compile-time enforcement (5a item 4), it will add a shape file to
`_TAB_SHAPE_FILES`/`_DEC_SHAPE_FILES`. **Prediction: that costs zero registry rows**, because
`tests/etkl/test_vacuity_registry.py` requires a row only for an *idle* shape — no focus nodes, or
an `sh:sparql` body naming absent terms (`:325-329`) — and a carrier shape has focus nodes on all 7
documents and no SPARQL body.

**Reasoned from reading the registry's two criteria, not from running it with such a shape
present.** If it is wrong, the plan gains a registry row and a test to keep green, which changes a
task's shape but not the design. Cheap to refute: add the shape, run that one test file.

### 5c. What this loop deliberately leaves exposed

[[R218]] and [[R219]], untouched from the spec loop. No new residue was raised: the arm-1 defect is
**corrected in evidence § 3**, not deferred, and a row for a fixed thing would inflate the
denominator without recording debt.

## 1. Where the primaries are

- **The evidence** — `docs/superpowers/2026-09-12-r212-invariant-arm-evidence.md`. § 1 is the
  invariant arm's full output; § 2 the four-leg seam refutation; § 3 the arm-1 defect and the route
  that works; § 4 the import cycle; § 5 the membrane measurement.
- **The spec** — unchanged, and **still correct on its design**; only its § 5 arm 1 *wording* is
  refuted (evidence § 3). Read spec § 3 for what is carried and the three refusals.
- **The instruments** — `scripts/corpus_verdict_snapshot.py` (shipped); `scratchpad/diff_snaps.py`
  and `scratchpad/probe_nontable.py` (this session's scratchpad, **not committed**).
- **The criterion** — `tests/arc-manifest.ttl:210-219`, hold note at `tests/corpus-manifest.ttl:56-57`.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| **The invariant HOLDS** — 7/7 documents: score, ledger and every region verdict byte-identical; 7/7 graph hashes moved | evidence § 1, and [[R212]]'s ✎ note |
| `document.licence_evidence` is **refuted** as the carrier's producer | evidence § 2 |
| Spec § 5 arm 1 is **not constructible as worded**; the `reportlab` route is, and is the RED state | evidence § 3 |
| `_band_text`'s cycle-free home is `bands.py` | evidence § 4 |
| The compile membrane loads neither `etkl` shapes nor `etkl` ontologies — the shape's home is the plan's decision | evidence § 5 |
| No plan this loop — floor ruling, maintainer, 2026-09-12 | here and evidence § 0 |

## 3. Unverified or assumed

- **5b is unrun** (above) — the one prediction this handoff makes.
- **The membrane choice is not made.** Evidence § 5 measures what is and is not loaded; it does not
  rule which way the plan should go.
- **The term's local name is still unfixed** — the plan's to choose; the namespace is not.
- The triple-delta corroboration in evidence § 1 matches spec § 2.1's per-document counts, but
  [[R219]]'s band-vs-distinct-text confound is untouched: it counts bands, as that census did.
- The 7 scores are this session's, at `a3ff34b`, on this machine.

## 4. What this loop did not touch

No `src/` change survives it — the throwaway emitter was applied for two snapshots and reverted
(`git checkout src/iladub/etkl/compile.py`), and the tree carried nothing else while it was
applied. No vocabulary, no shapes, no new tests. [[R166]], [[R211]], [[R218]], [[R219]] and
etkl:02 are where PR #211 left them.
