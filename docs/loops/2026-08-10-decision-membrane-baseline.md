# Decision membrane — the measured before-state (loop `loop-decision-membrane`, Task 1)

**Date:** 2026-08-10 · **Class:** Evidence (immutable after loop close) · **Tree:** `88bd8e4`
**Spec:** `docs/superpowers/specs/2026-08-10-the-decision-membrane-design.md`
**Plan:** `docs/superpowers/plans/2026-08-10-the-decision-membrane.md` (Task 1, Steps 2-3)

**Doc impact:** none. This file records a measurement; it asserts nothing about the released
artifact.

## The command

```
./.venv/bin/python scripts/measure_dec_membrane.py --scope both     # exit code 1
```

Machine: darwin 25.6.0, this repo, `./.venv/bin/python` 3.12.0 · rdflib 7.6.0 ·
pySHACL 0.31.0 · owlrl 7.1.4. Wall clock for the whole run: ~6 min (graincorp-stem 165 s).

`pyrudof` IS installed in this venv, so `membrane.validate` resolves to **rudof** in
production here. This oracle deliberately bypasses that seam and pins **pySHACL**, because
spec §3 was measured under pySHACL and because the oracle must run BOTH closures while
`membrane.validate` always applies the shipped one. Engine equivalence is established
separately by `tests/etkl/test_membrane_equiv.py`, not assumed here.

## The verdict against the spec

Spec §6's four cells, and this run:

| scope | closure | spec §6 foci / results | MEASURED foci / results | |
| --- | --- | --- | --- | --- |
| compile (7 docs) | SHIPPED | 26 / 98 | **26 / 98** | match |
| compile (7 docs) | RDFS | 26 / 194 | **26 / 194** | match |
| grounding (2 docs) | SHIPPED | 719 / 1438 | **719 / 1438** | match |
| grounding (2 docs) | RDFS | 719 / 1438 | **719 / 1438** | match |

Per-document, spec §3.1 / §3.2 / §3.3 and this run also agree on every cell: triples and
`dec:DecisionHolon` counts for all seven documents; 11 / 10 / 3 refusing candidates on apple /
bfs / who; the 2 ons admission holons (`p7`/`p8`, `dec:decidedBy` minCount — R81(a′) live on
the corpus); and grounding’s 133 records / 585 promotions (graincorp-stem) and 58 / 134
(cbh-stem), every promotion refusing both `dec:optionSpace` and `dec:chosen`.

**Nothing in the spec’s §3 needed adjusting.** The tree has not moved.

## Two measured facts the spec did not record

Both were found while building the oracle, and both change how the numbers must be COUNTED
rather than what they are.

**1. Focus nodes must be counted per graph and summed, never unioned across documents.**
`compile_document` gives every corpus document the same default `doc_uri` base, so IRIs
collide across documents. Measured:

```
apple-fy2026q3-statements  11 candidates
bfs-population-bilan-2023  10 candidates
who-wfa-boys-zscore-0-5     3 candidates
union across documents: 23        <- 24 candidates, 23 distinct IRIs
COLLISION apple <-> who-wfa: ['https://example.org/etkl/doc/p0#region2']
```

A cross-document union reports **25** where the true compile-scope count is **26** — it hides
one real defect behind an accident of default naming. The oracle therefore unions focus nodes
*within* a document (across the two shape files, so a candidate refusing under both halves is
one node) and *sums* across documents.

**2. A compiled-graph cache is not verdict-neutral, so the oracle has none.**
The plan offered a cache keyed by pdf sha256 + a digest of `src/**/*.py`. It was built and
measured, and it **silently dropped 24 real refusals** (compile-scope RDFS 194 → 170) — one
`dec:ConfidenceShape` datatype refusal per escalated candidate — while every other number
stayed identical. Cause, measured:

```
Literal(round(0.3, 2), datatype=XSD.decimal)      # holon.py:374, verbatim
  fresh in memory : .value is a float,   ill_typed None   -> pySHACL REFUSES sh:datatype
  after nt/ttl    : .value is a Decimal, ill_typed False  -> pySHACL ACCEPTS
```

Same lexical form, same datatype IRI, opposite verdict. The cache was removed; the ~290 s
compile is the honest price. This also means one of R69’s four RDFS refusals per candidate is
an artifact of how the literal is constructed in Python rather than of its published RDF —
Task 2 removes `dec:confidence` from candidates, which closes it either way.

## Raw output, verbatim

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
    triples=3633  dec:DecisionHolon=119  iladub:CandidateConcept=11  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=33s
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     REFUSES   foci=11    results=44
        [  11] dec:optionSpace          :: A real decision deliberates at least two options (the no-change option counts).
               e.g. https://example.org/etkl/doc/p0#region5
        [  11] dec:chosen               :: A decision must record exactly one chosen option.
               e.g. https://example.org/etkl/doc/p0#region5
        [  11] dec:decidedBy            :: A decision must record an accountable agent (human or automated).
               e.g. https://example.org/etkl/doc/p0#region5
        [  11] dec:confidence           :: Confidence, if given, must be a single decimal in [0,1].
               e.g. https://example.org/etkl/doc/p0#region5
    iladub-shapes.ttl    SHIPPED  REFUSES   foci=11    results=44
        [  11] iladub:suggestedBy       :: A candidate must record who/what suggested it.
               e.g. https://example.org/etkl/doc/p2#region2
        [  11] iladub:confidence        :: A candidate must carry a confidence in [0,1].
               e.g. https://example.org/etkl/doc/p2#region2
        [  11] iladub:fromRegion        :: A candidate must record its source region (provenance).
               e.g. https://example.org/etkl/doc/p2#region2
        [  11] iladub:status            :: A candidate's status must be 'proposed'.
               e.g. https://example.org/etkl/doc/p2#region2
    iladub-shapes.ttl    RDFS     REFUSES   foci=11    results=44
        [  11] iladub:suggestedBy       :: A candidate must record who/what suggested it.
               e.g. https://example.org/etkl/doc/p2#region2
        [  11] iladub:confidence        :: A candidate must carry a confidence in [0,1].
               e.g. https://example.org/etkl/doc/p2#region2
        [  11] iladub:fromRegion        :: A candidate must record its source region (provenance).
               e.g. https://example.org/etkl/doc/p2#region2
        [  11] iladub:status            :: A candidate's status must be 'proposed'.
               e.g. https://example.org/etkl/doc/p2#region2
    SHIPPED: 11 distinct refusing foci / 44 results  RDFS: 11 distinct refusing foci / 88 results

--- bfs-population-bilan-2023 ---
    triples=8118  dec:DecisionHolon=232  iladub:CandidateConcept=10  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=22s
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     REFUSES   foci=10    results=40
        [  10] dec:optionSpace          :: A real decision deliberates at least two options (the no-change option counts).
               e.g. https://example.org/etkl/doc/p0#region0
        [  10] dec:chosen               :: A decision must record exactly one chosen option.
               e.g. https://example.org/etkl/doc/p0#region0
        [  10] dec:decidedBy            :: A decision must record an accountable agent (human or automated).
               e.g. https://example.org/etkl/doc/p0#region0
        [  10] dec:confidence           :: Confidence, if given, must be a single decimal in [0,1].
               e.g. https://example.org/etkl/doc/p0#region0
    iladub-shapes.ttl    SHIPPED  REFUSES   foci=10    results=40
        [  10] iladub:suggestedBy       :: A candidate must record who/what suggested it.
               e.g. https://example.org/etkl/doc/p6#region1
        [  10] iladub:confidence        :: A candidate must carry a confidence in [0,1].
               e.g. https://example.org/etkl/doc/p6#region1
        [  10] iladub:fromRegion        :: A candidate must record its source region (provenance).
               e.g. https://example.org/etkl/doc/p6#region1
        [  10] iladub:status            :: A candidate's status must be 'proposed'.
               e.g. https://example.org/etkl/doc/p6#region1
    iladub-shapes.ttl    RDFS     REFUSES   foci=10    results=40
        [  10] iladub:suggestedBy       :: A candidate must record who/what suggested it.
               e.g. https://example.org/etkl/doc/p6#region1
        [  10] iladub:confidence        :: A candidate must carry a confidence in [0,1].
               e.g. https://example.org/etkl/doc/p6#region1
        [  10] iladub:fromRegion        :: A candidate must record its source region (provenance).
               e.g. https://example.org/etkl/doc/p6#region1
        [  10] iladub:status            :: A candidate's status must be 'proposed'.
               e.g. https://example.org/etkl/doc/p6#region1
    SHIPPED: 10 distinct refusing foci / 40 results  RDFS: 10 distinct refusing foci / 80 results

--- cbh-stem-2026-08-03 ---
    triples=12140  dec:DecisionHolon=65  iladub:CandidateConcept=0  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=26s
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     conforms  foci=0     results=0
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 0 distinct refusing foci / 0 results  RDFS: 0 distinct refusing foci / 0 results

--- graincorp-capacity-2026-08-04 ---
    triples=5705  dec:DecisionHolon=18  iladub:CandidateConcept=0  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=10s
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     conforms  foci=0     results=0
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 0 distinct refusing foci / 0 results  RDFS: 0 distinct refusing foci / 0 results

--- graincorp-stem-2026-07-31 ---
    triples=29999  dec:DecisionHolon=36  iladub:CandidateConcept=0  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=165s
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     conforms  foci=0     results=0
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 0 distinct refusing foci / 0 results  RDFS: 0 distinct refusing foci / 0 results

--- ons-index-of-services-2026-02 ---
    triples=11062  dec:DecisionHolon=218  iladub:CandidateConcept=0  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=8s
    dec-shapes.ttl       SHIPPED  REFUSES   foci=2     results=2
        [   2] dec:decidedBy            :: A decision must record an accountable agent (human or automated).
               e.g. https://example.org/etkl/doc/p8#p8-datagrid-admission
    dec-shapes.ttl       RDFS     REFUSES   foci=2     results=2
        [   2] dec:decidedBy            :: A decision must record an accountable agent (human or automated).
               e.g. https://example.org/etkl/doc/p8#p8-datagrid-admission
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 2 distinct refusing foci / 2 results  RDFS: 2 distinct refusing foci / 2 results

--- who-wfa-boys-zscore-0-5 ---
    triples=8058  dec:DecisionHolon=81  iladub:CandidateConcept=3  iladub:GroundedNode=0  iladub:PromotionDecision=0  wall=39s
    dec-shapes.ttl       SHIPPED  conforms  foci=0     results=0
    dec-shapes.ttl       RDFS     REFUSES   foci=3     results=12
        [   3] dec:optionSpace          :: A real decision deliberates at least two options (the no-change option counts).
               e.g. https://example.org/etkl/doc/p0#region2
        [   3] dec:chosen               :: A decision must record exactly one chosen option.
               e.g. https://example.org/etkl/doc/p0#region2
        [   3] dec:decidedBy            :: A decision must record an accountable agent (human or automated).
               e.g. https://example.org/etkl/doc/p0#region2
        [   3] dec:confidence           :: Confidence, if given, must be a single decimal in [0,1].
               e.g. https://example.org/etkl/doc/p0#region2
    iladub-shapes.ttl    SHIPPED  REFUSES   foci=3     results=12
        [   3] iladub:suggestedBy       :: A candidate must record who/what suggested it.
               e.g. https://example.org/etkl/doc/p2#region1
        [   3] iladub:confidence        :: A candidate must carry a confidence in [0,1].
               e.g. https://example.org/etkl/doc/p2#region1
        [   3] iladub:fromRegion        :: A candidate must record its source region (provenance).
               e.g. https://example.org/etkl/doc/p2#region1
        [   3] iladub:status            :: A candidate's status must be 'proposed'.
               e.g. https://example.org/etkl/doc/p2#region1
    iladub-shapes.ttl    RDFS     REFUSES   foci=3     results=12
        [   3] iladub:suggestedBy       :: A candidate must record who/what suggested it.
               e.g. https://example.org/etkl/doc/p2#region1
        [   3] iladub:confidence        :: A candidate must carry a confidence in [0,1].
               e.g. https://example.org/etkl/doc/p2#region1
        [   3] iladub:fromRegion        :: A candidate must record its source region (provenance).
               e.g. https://example.org/etkl/doc/p2#region1
        [   3] iladub:status            :: A candidate's status must be 'proposed'.
               e.g. https://example.org/etkl/doc/p2#region1
    SHIPPED: 3 distinct refusing foci / 12 results  RDFS: 3 distinct refusing foci / 24 results

COMPILE SCOPE TOTALS (7 documents; focus nodes DISTINCT within a document, SUMMED across documents)
  | closure  | refusing focus nodes | validation results |
  |----------|----------------------|--------------------|
  | SHIPPED  |                   26 |                 98 |
  | RDFS     |                   26 |                194 |

==============================================================================
GROUNDING SCOPE
==============================================================================

--- cbh-stem-2026-08-03 ---
    triples=9702  dec:DecisionHolon=0  iladub:CandidateConcept=909  iladub:GroundedNode=134  iladub:PromotionDecision=134  records=58 grounded=134 quarantined=775
    dec-shapes.ttl       SHIPPED  REFUSES   foci=134   results=268
        [ 134] dec:optionSpace          :: A real decision deliberates at least two options (the no-change option counts).
               e.g. N6c2973cf13f14efb88fefc107ea5b0fb
        [ 134] dec:chosen               :: A decision must record exactly one chosen option.
               e.g. N6c2973cf13f14efb88fefc107ea5b0fb
    dec-shapes.ttl       RDFS     REFUSES   foci=134   results=268
        [ 134] dec:optionSpace          :: A real decision deliberates at least two options (the no-change option counts).
               e.g. N6c2973cf13f14efb88fefc107ea5b0fb
        [ 134] dec:chosen               :: A decision must record exactly one chosen option.
               e.g. N6c2973cf13f14efb88fefc107ea5b0fb
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 134 distinct refusing foci / 268 results  RDFS: 134 distinct refusing foci / 268 results

--- graincorp-stem-2026-07-31 ---
    triples=23560  dec:DecisionHolon=0  iladub:CandidateConcept=1850  iladub:GroundedNode=585  iladub:PromotionDecision=585  records=133 grounded=585 quarantined=1265
    dec-shapes.ttl       SHIPPED  REFUSES   foci=585   results=1170
        [ 585] dec:optionSpace          :: A real decision deliberates at least two options (the no-change option counts).
               e.g. Nb57faf693b8c48629c376ba87b67c58a
        [ 585] dec:chosen               :: A decision must record exactly one chosen option.
               e.g. Nb57faf693b8c48629c376ba87b67c58a
    dec-shapes.ttl       RDFS     REFUSES   foci=585   results=1170
        [ 585] dec:optionSpace          :: A real decision deliberates at least two options (the no-change option counts).
               e.g. Nb57faf693b8c48629c376ba87b67c58a
        [ 585] dec:chosen               :: A decision must record exactly one chosen option.
               e.g. Nb57faf693b8c48629c376ba87b67c58a
    iladub-shapes.ttl    SHIPPED  conforms  foci=0     results=0
    iladub-shapes.ttl    RDFS     conforms  foci=0     results=0
    SHIPPED: 585 distinct refusing foci / 1170 results  RDFS: 585 distinct refusing foci / 1170 results

GROUNDING SCOPE TOTALS (2 documents; focus nodes DISTINCT within a document, SUMMED across documents)
  | closure  | refusing focus nodes | validation results |
  |----------|----------------------|--------------------|
  | SHIPPED  |                  719 |               1438 |
  | RDFS     |                  719 |               1438 |

VERDICT: REFUSES (1490 refusing focus nodes summed over every scope and closure)
```

Exit code: **1** (the oracle refuses, as it must at the before-state).
