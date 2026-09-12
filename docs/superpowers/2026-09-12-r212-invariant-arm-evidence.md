# Evidence — R212's carrier: the invariant arm, and four seam measurements

**Serves:** prog:criterion:etkl:02 — R212 is a prerequisite of that criterion's measures.
**Date:** 2026-09-12. **Branch:** `r212-invariant-arm`, cut from `a3ff34b`.
**Spec:** `docs/superpowers/specs/2026-09-12-the-ignored-band-carries-its-text-design.md`.

**Doc impact: none.** Evidence + register rows. Nothing queues for a release, nothing blocks one.

This loop ran the spec's § 5 oracle arm 4 — the one the handoff graded **PROPOSED** and ordered run
before any task was written — and measured the four seams a plan would otherwise have assumed. It
writes **no plan**: the session passed the 50K originating floor during measurement, and the
maintainer ruled (2026-09-12) to ship the evidence and leave the plan to a fresh session.

## 1. The invariant arm (spec § 5 arm 4, handoff § 5b)

**The claim under test.** The score is `asserted / (asserted + escalated)` (`document.py:1760`), the
NON_TABLE branch increments neither counter (`compile.py:814-824`), and emission is decoupled from
accounting (`compile.py:802-803`) — so a carrier touching neither counter should leave all 7 corpus
scores byte-identical while the graph hash moves. **Reasoned from reading, not run**, and the spec's
§ 3 rests on it.

**Method.** `scripts/corpus_verdict_snapshot.py` twice over the same checkout: once at `a3ff34b`,
once with a throwaway emitter in the NON_TABLE branch writing three triples per ignored band (a
type, the band's exact text, its page) and touching neither counter. Differ:
`scratchpad/diff_snaps.py`, comparing per-document score, per-page `(asserted, escalated)`,
every per-region verdict, and the canonical graph SHA-256.

**The throwaway was confirmed live before the corpus run**, because a silently no-op emitter
produces an unmoved hash that reads as a refutation when it is an instrument failure. On a
reportlab fixture: 420 → 426 triples (+3 per ignored band × 2 bands), and all four probe strings
went 0 hits → 1 hit.

**VERDICT: CONFIRMED.** All 7 documents, `a3ff34b` vs the same tree + throwaway:

```
apple-fy2026q3-statements     score=SAME ledger=SAME verdicts=SAME hash=MOVED  5103->5121
bfs-population-bilan-2023     score=SAME ledger=SAME verdicts=SAME hash=MOVED  8919->9057
cbh-stem-2026-08-03           score=SAME ledger=SAME verdicts=SAME hash=MOVED 12794->12809
graincorp-capacity-2026-08-04 score=SAME ledger=SAME verdicts=SAME hash=MOVED  5710->5722
graincorp-stem-2026-07-31     score=SAME ledger=SAME verdicts=SAME hash=MOVED 32359->32380
ons-index-of-services-2026-02 score=SAME ledger=SAME verdicts=SAME hash=MOVED 11095->11305
who-wfa-boys-zscore-0-5       score=SAME ledger=SAME verdicts=SAME hash=MOVED 12220->12244

scores moved: 0  ledgers moved: 0  verdicts moved: 0  hashes moved: 7
```

Every score is identical to its full floating-point repr (e.g. bfs `0.40331491712707185` both
sides), every page's `(asserted, escalated)` pair is unchanged, and every per-region verdict string
is unchanged — while all 7 canonical graph hashes moved. **A carrier that touches neither counter
changes the graph and changes no number that grades a document**, which is what the spec's § 3 and
the rung's pinned-score criteria both rest on.

The triple deltas are the carrier's own arithmetic and corroborate the census independently: +3 per
ignored band, so +18/6 bands (apple), +138/46 (bfs), +12/4 (graincorp-capacity), +210/70 (ons) —
matching spec § 2.1's per-document ignored-band counts exactly, in a second instrument that never
read that census.

## 2. The seam the spec named, MEASURED — `document.licence_evidence` is refuted as the producer

Spec § 5 named this seam and refused to answer it: *"it may be the producer, or it may be scoped to
pairs and therefore useless here. Do not assume either."* It is useless here, on four independent
legs, any one of which is sufficient:

1. **Wrong population.** A "non-table block" there is *any OTHER band of the page* — every band
   except the one the recognition AXIOM paired (`document.py:592-599`, the two `if i != …_index`
   loops). That is not the NON_TABLE-classified set: on graincorp-capacity it would include the
   table band's siblings regardless of verdict, and exclude nothing by `classify`.
2. **Pair-scoped.** The only production call is inside `if is_continuation(...)`
   (`document.py:1419-1426`), so it never runs on a page pair the recognition axiom refused.
3. **Never runs at all on the subject document.** `recognized` is `[]` for
   `graincorp-capacity-2026-08-04` (baseline snapshot, this loop) — the document whose title and
   footer the maintainer's ruling licenses. By contrast `graincorp-stem` has `[[0,1],[1,2]]`.
4. **Its graph is discarded.** `licence_evidence` returns a fresh `Graph()` consumed by
   `is_licensed` (`document.py:603-612`), which runs one query and returns a bool. Nothing merges
   it into the compiled graph.

**Consequence for the plan:** the emitter goes in the NON_TABLE branch of `compile_tables`
(`compile.py:814-824`), where `doc`, `idx`, `band` and `page_number` are all already in scope.

## 3. Oracle arm 1 is constructible — but NOT the way the spec describes it

**The spec's wording cannot be executed.** § 5 arm 1 says a synthetic `Band` that classifies
NON_TABLE should be *"compiled through the public API"*, synthetic because `corpus/` is gitignored,
*"as ~10 files under `tests/etkl/` already do."* But `compile_tables` takes a **path**, not bands —
it derives them itself (`compile.py:766`: `bands = page_bands(pdf_path, page_number, …)`) — and no
test in the repo monkeypatches `page_bands`. The ~10 files that build `Band(...)` directly call
`classify` and friends, never the compile path. A hand-built `Band` cannot reach the branch.

**The route that works, run this loop:** build the page with `reportlab`, which is already a test
dependency used by 4 files under `tests/etkl/` (e.g. `test_grid_donation_disposal.py:12-13`,
`pytest.importorskip("reportlab")`), none corpus-gated. A page carrying a one-line title, a ruled
3-column table, and a one-line footer reproduces graincorp's exact shape:

```
b0 lines=1 kind=NON_TABLE     reason='fewer than 2 lines'       'ELEVATION CAPACITY TABLE'
b1 lines=5 kind=RECORD_TABLE  reason='flat single-level header' 'Region Total Share | Vaud …'
b2 lines=1 kind=NON_TABLE     reason='fewer than 2 lines'       'tonnages shown are indicative only'
```

**And that run IS the RED state** the falsification arm needs: 420 triples, and
`'ELEVATION CAPACITY TABLE'`, `'ELEVATION'`, `'tonnages shown are indicative only'` and
`'indicative'` each score **0 hits** among the graph's literals. Instrument:
`scratchpad/probe_nontable.py`.

## 4. `_band_text`'s home — the import cycle, and the file that resolves it

Spec § 2.7 names `document._band_text` (`document.py:540-548`) as the definition of a band's surface
text. It is module-private **and on the wrong side of the import graph**: `document.py` imports from
`.compile` at module level (`document.py:110`), so `compile.py` importing `document._band_text` at
module level is a cycle.

`bands.py` imports **only** `from .geometry import Line, Rule, HRule` (`bands.py:12`) and defines
`Band` itself — so it is reachable from both `compile.py` and `document.py` with no cycle, and is the
natural home. Moving it there is a two-call-site change (`document.py:594,598`). The alternative, a
function-local import inside the branch, matches an idiom `compile.py` already uses
(`from . import donation as _donation`) but leaves the privacy question unanswered.

## 5. The membrane — where a carrier shape would and would not fire

The maintainer ruled the term lives in `etkl:`. **Measured: the compile membrane loads neither the
`etkl` shapes nor the `etkl` ontologies**, so a NodeShape in the natural home would never fire at
compile time:

```
_TAB_SHAPE_FILES = ("tab-shapes.ttl", "tab-physical-shapes.ttl")          compile.py:562
_DEC_SHAPE_FILES = ("dec-shapes.ttl", "iladub-shapes.ttl",
                    "escalation-shapes.ttl")                              compile.py:585
ontology graph   = tab.ttl + dec.ttl + iladub.ttl                         compile.py:605-617
```

`etkl-shapes.ttl` says so of itself (`:68-82`: *"the one shape file the compile membrane does not
load"*), and `etkl-holons.ttl` — the fabric file the ruling points at, holding `RawDocumentHolon` /
`CleanDocumentHolon` / `GroundingPortal` / `MembraneHealth` — is in no membrane list either.

**Wiring one in costs nothing in the vacuity registry, which is the hazard worth checking.** Wired
shapes are enumerated from `_TAB_SHAPE_FILES | _DEC_SHAPE_FILES`
(`tests/etkl/test_vacuity_registry.py:140`), and only an **idle** shape — no focus nodes, or an
`sh:sparql` body naming terms absent from the data — needs a registry row (`:325-329`). A carrier
NodeShape would have focus nodes on all 7 documents (every one has ignored bands, spec § 2.1) and
carry no SPARQL body, so it is not idle and needs no row. The reverse arm (`:352`) only polices rows
for unwired shapes.

**This is a decision the plan must take, not inherit:** enforce at compile time by wiring a shape
file into a membrane set, or accept `tests/test_vocab_shapes.py`-only enforcement (the
`examples/<thing>-conformant.ttl` + `tests/<thing>-bad-*.ttl` convention). The spec's § 3 requires
text and page to be *required*; it does not say by which membrane.

## 6. What this loop did not do

No plan (maintainer ruling, § 0 above). No `src/` change survives it — the throwaway is reverted and
the working tree carried nothing else while it was applied (`git diff --stat`: one file, +10 lines,
all inside the NON_TABLE branch). No vocabulary, no shapes, no new tests. [[R166]], [[R211]],
[[R218]], [[R219]] and etkl:02 are where PR #211 left them.
