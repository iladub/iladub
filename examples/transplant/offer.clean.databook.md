---
id: https://example.org/transplant/databooks/offer-2026-0091.clean
title: "Donor organ offer ET-2026-0091 (compiled)"
type: databook
version: 1.0.0
created: 2026-06-23
process:
  transformer: "BAML + Claude"
  transformer_type: llm
  transformer_iri: https://api.anthropic.com/v1/models/claude-opus-4-8
  inputs:
    - iri: https://example.org/transplant/databooks/offer-2026-0091
      role: primary
    - iri: https://example.org/transplant/knowledge/offer-contract
      role: contract
    - iri: https://example.org/transplant/knowledge/transplant-terms
      role: knowledge
    - iri: https://example.org/transplant/knowledge/offer-shapes
      role: constraint
  agent:
    name: iladub
    role: orchestrator
  timestamp: 2026-06-23T00:00:00Z
---

## M4 — Offer acceptance decision

Recommendation: **accept**. ABO compatible and within cold-ischemia window.

<!-- databook:id: asserted -->
<!-- databook:graph: https://example.org/transplant/databooks/offer-2026-0091.clean#asserted -->
```turtle
@prefix tx: <https://example.org/transplant#> .
tx:offer a tx:OrganOffer ;
    tx:organ tx:organ-heart ;
    tx:aboGroup "O" ;
    tx:ejectionFraction "60" .
```

<!-- databook:id: propositions -->
<!-- databook:graph: https://example.org/transplant/databooks/offer-2026-0091.clean#propositions -->
```turtle
@prefix iladub: <https://w3id.org/iladub#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
iladub:candidate-1 a iladub:CandidateConcept ;
    iladub:confidence "0.9"^^xsd:decimal ;
    iladub:fromRegion [ a iladub:SourceRegion ;
        iladub:surfaceText "transient takotsubo-pattern wall-motion abnormality" ] .
```

<!-- databook:id: decision -->
<!-- databook:graph: https://example.org/transplant/databooks/offer-2026-0091.clean#decision -->
```turtle
@prefix tx: <https://example.org/transplant#> .
@prefix dec: <https://w3id.org/iladub/dec#> .
tx:m4-decision a dec:DecisionHolon ;
    dec:optionSpace tx:opt-accept , tx:opt-decline ;
    dec:chosen tx:opt-accept ;
    dec:decidedBy tx:surgeon-1 ;
    dec:rationale "ABO compatible and within cold-ischemia window." .
tx:opt-accept a dec:Option .
tx:opt-decline a dec:Option ;
    dec:rejectedBecause "ABO compatible and within cold-ischemia window." .
```
