---
id: https://example.org/transplant/databooks/offer-2026-0091.clean-leak
title: "Donor organ offer ET-2026-0091 (compiled, LEAK)"
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
  agent:
    name: iladub
    role: orchestrator
  timestamp: 2026-06-23T00:00:00Z
---

## M4 — LEAK case (asserted offer missing required organ)

<!-- databook:id: asserted -->
```turtle
@prefix tx: <https://example.org/transplant#> .
tx:offer a tx:OrganOffer ;
    tx:aboGroup "O" ;
    tx:ejectionFraction "60" .
```
