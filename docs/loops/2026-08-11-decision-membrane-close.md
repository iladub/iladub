# Decision membrane — the measured after-state (loop `loop-decision-membrane`, Task 8)

**Date:** 2026-08-11 · **Class:** Evidence (immutable after loop close) · **Tree:** `044e998`
**Spec:** `docs/superpowers/specs/2026-08-10-the-decision-membrane-design.md`
**Plan:** `docs/superpowers/plans/2026-08-10-the-decision-membrane.md` (Task 8, Step 1)
**Before-state:** `docs/loops/2026-08-10-decision-membrane-baseline.md` (Task 1)

**Doc impact:** none. This file records a measurement; it asserts nothing about the released
artifact. (The spec's own `contradiction` is resolved in the same change — see its header.)

## The four cells

Spec §6's table, baseline beside this run. Focus nodes are DISTINCT within a document and
SUMMED across documents — `compile_document` gives every corpus document the same default
`doc_uri`, so a cross-document union under-reports (apple and who-wfa both mint
`<doc>/p0#region2`).

| scope | closure | baseline foci / results | NOW |
| --- | --- | --- | --- |
| compile (7 docs) | SHIPPED | 26 / 98 | **0 / 0** |
| compile (7 docs) | RDFS | 26 / 194 | **0 / 0** |
| grounding (2 docs) | SHIPPED | 719 / 1438 | **0 / 0** |
| grounding (2 docs) | RDFS | 719 / 1438 | **0 / 0** |

`VERDICT: CONFORMS`, exit code **0** (the baseline run exited 1).

## What the loop actually enforced, and where

Zero refusals is the weaker half of the claim. The stronger half is that the shapes are now
APPLIED by the pipeline rather than only by this oracle:

- `compile._validate` (`src/iladub/etkl/compile.py`) — the compile membrane, in two legs.
- `ground_document(..., validate_shapes=True)` (`src/iladub/feed.py`) — the grounding
  membrane, and the only one where `iladub:GroundedNodeShape` is non-vacuous: a compiled graph
  has `iladub:GroundedNode=0` on all seven documents (see the raw output below), so the
  differentiator shape has nothing to target until grounding runs.

Falsified against the real corpus, not fixtures:

```
BEFORE  : cbh-stem-2026-08-03 grounded=134  membrane=True
DOCTORED: one wasPromotedBy removed        membrane=False
          report: 'INVARIANT: every grounded node must be produced by a promotion decision.'
RESTORED:                                  membrane=True
```

## The finding this loop did not expect

**rudof cannot evaluate an `sh:sparql` constraint whose focus node is a blank node** — it binds
`$this` through `VALUES $this { _:b… }`, illegal SPARQL, and RAISES rather than returning a
verdict. Registered as R88; the dec/iladub shapes are pinned to pySHACL at both membranes
(`compile._DEC_ENGINE`, read by `feed._validate_grounding` at call time).

It matters that the baseline document (Task 1) contains this sentence:

> Engine equivalence is established separately by `tests/etkl/test_membrane_equiv.py`, not
> assumed here.

**That sentence was false when written.** `test_membrane_equiv.py` loaded only
`tab-shapes.ttl`, `tab-physical-shapes.ttl` and `tab.ttl`; no dec/iladub equivalence had ever
been measured. The loop's own before-state document asserted a check that did not exist, in the
same breath as refusing to assume it — which is the R76/plan-discipline failure mode wearing a
new costume. The battery now carries leg 4 (dec/iladub differential, both `sh:sparql`
constraints) and leg 5 (blank-node focus). A dec/iladub leg written with IRI subjects only
would still have missed it; **the blank-node case is the one that matters.**

## `escalation-shapes.ttl` — measured on all seven, wired into nothing

The spec deferred this as "clean on apple p0, unmeasured on the other six." Measured here on
all seven documents under both closures, against `escalation-shapes.ttl` (12 triples):

```
document                                          SHIPPED                   RDFS
apple-fy2026q3-statements                    (True, 0, 0)           (True, 0, 0)
bfs-population-bilan-2023                    (True, 0, 0)           (True, 0, 0)
cbh-stem-2026-08-03                          (True, 0, 0)           (True, 0, 0)
graincorp-capacity-2026-08-04                (True, 0, 0)           (True, 0, 0)
graincorp-stem-2026-07-31                    (True, 0, 0)           (True, 0, 0)
ons-index-of-services-2026-02                (True, 0, 0)           (True, 0, 0)
who-wfa-boys-zscore-0-5                      (True, 0, 0)           (True, 0, 0)

TOTAL refusing focus nodes — SHIPPED: 0  RDFS: 0
```

Nothing violates it; it is simply in no membrane. Registered as R87.

## The rest of the battery

```
corpus battery   : 10 passed  (all 7 documents compile; both contracted documents ground
                   AND conform — cbh-stem records=58 grounded=134 quarantined=775,
                   graincorp-stem records=133 grounded=585 quarantined=1265)
full suite       : 1170 passed, 7 skipped, 1 xfailed = 1178 collected
vocab/shapes/    : byte-identical to main (`git diff --stat main -- vocab/shapes/` empty)
```

The suite is run in ten chunks, not one invocation: this harness kills a background task at
~5 min and a foreground one at 10 min, and the second membrane leg costs ~7% wall clock.

## Residues

**Closed and deleted from the register:** R69, R81, R82.

**Registered by this loop:** R86 (a quarantined concept mints no decision holon — 2040
refusals across the two contracted documents carry no decision at all), R87
(`escalation-shapes.ttl` in no membrane), R88 (the rudof blank-node incapacity and the pin
that works around it), R89 (`BandRecorder`'s Python guard now duplicates two membrane-enforced
constraints), R90 (the bbox dropped from `ROUND_TRIP_FAIL` propositions), R91 (`document.py`
duplicates `emit_data_grid`'s `dec:decidedBy`).

## Raw output

```
measure_dec_membrane — engine=pySHACL inference=none advanced=True
  ontology : dec.ttl + iladub.ttl + etkl.ttl + tab.ttl
  shapes   : dec-shapes.ttl + iladub-shapes.ttl  (parsed and reported SEPARATELY)
  closures : SHIPPED=membrane.subclass_closure  RDFS=membrane.rdfs_closure
  documents: 7 present

==============================================================================
COMPILE SCOPE
==============================================================================

--- apple-fy2026q3-statements ---
    triples=3725  dec:DecisionHolon=119  iladub:CandidateConcept=11  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=35s
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     conforms  foci=0     results=0
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 0 distinct refusing foci / 0 results  RDFS: 0 distinct refusing foci / 0 results

--- bfs-population-bilan-2023 ---
    triples=8181  dec:DecisionHolon=232  iladub:CandidateConcept=10  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=23s
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     conforms  foci=0     results=0
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 0 distinct refusing foci / 0 results  RDFS: 0 distinct refusing foci / 0 results

--- cbh-stem-2026-08-03 ---
    triples=12153  dec:DecisionHolon=65  iladub:CandidateConcept=0  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=27s
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     conforms  foci=0     results=0
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 0 distinct refusing foci / 0 results  RDFS: 0 distinct refusing foci / 0 results

--- graincorp-capacity-2026-08-04 ---
    triples=5705  dec:DecisionHolon=18  iladub:CandidateConcept=0  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=9s
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     conforms  foci=0     results=0
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 0 distinct refusing foci / 0 results  RDFS: 0 distinct refusing foci / 0 results

--- graincorp-stem-2026-07-31 ---
    triples=29999  dec:DecisionHolon=36  iladub:CandidateConcept=0  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=166s
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     conforms  foci=0     results=0
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 0 distinct refusing foci / 0 results  RDFS: 0 distinct refusing foci / 0 results

--- ons-index-of-services-2026-02 ---
    triples=11076  dec:DecisionHolon=218  iladub:CandidateConcept=0  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=8s
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     conforms  foci=0     results=0
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 0 distinct refusing foci / 0 results  RDFS: 0 distinct refusing foci / 0 results

--- who-wfa-boys-zscore-0-5 ---
    triples=8077  dec:DecisionHolon=81  iladub:CandidateConcept=3  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=40s
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     conforms  foci=0     results=0
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 0 distinct refusing foci / 0 results  RDFS: 0 distinct refusing foci / 0 results

COMPILE SCOPE TOTALS (7 documents; focus nodes DISTINCT within a document, SUMMED across documents)
  | closure  | refusing focus nodes | validation results |
  |----------|----------------------|--------------------|
  | SHIPPED  |                    0 |                  0 |
  | RDFS     |                    0 |                  0 |

==============================================================================
GROUNDING SCOPE
==============================================================================

--- cbh-stem-2026-08-03 ---
    triples=10774  dec:DecisionHolon=0  iladub:CandidateConcept=909  iladub:GroundedNode=134  iladub:PromotionDecision=134  records=58 grounded=134 quarantined=775
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     conforms  foci=0     results=0
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 0 distinct refusing foci / 0 results  RDFS: 0 distinct refusing foci / 0 results

--- graincorp-stem-2026-07-31 ---
    triples=28240  dec:DecisionHolon=0  iladub:CandidateConcept=1850  iladub:GroundedNode=585  iladub:PromotionDecision=585  records=133 grounded=585 quarantined=1265
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     conforms  foci=0     results=0
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 0 distinct refusing foci / 0 results  RDFS: 0 distinct refusing foci / 0 results

GROUNDING SCOPE TOTALS (2 documents; focus nodes DISTINCT within a document, SUMMED across documents)
  | closure  | refusing focus nodes | validation results |
  |----------|----------------------|--------------------|
  | SHIPPED  |                    0 |                  0 |
  | RDFS     |                    0 |                  0 |

VERDICT: CONFORMS (0 refusing focus nodes summed over every scope and closure)
```
