# Assertions & propositions

iladub's epistemic core. A carrier is trusted only if it does not invent its cargo.

Namespace: `https://w3id.org/etkl/iladub#`.

## The two layers

- **Assertions** — content groundable in a provided ontology. Typed, contract-bound,
  SHACL-validated. The grounded graph.
- **Propositions** — content iladub *cannot* yet ground. Not dropped, not faked: a
  quarantined `iladub:CandidateConcept` carrying `surfaceText`, a `suggestedAnchor`
  (e.g. a gist class), `suggestedBy` (model/rule/person), `confidence` ∈ [0,1], and
  `fromRegion` (provenance). Status = `proposed`.

## Promotion is a decision

A proposition enters the grounded graph **only** as the product of an
`iladub:PromotionDecision` (⊑ `hol:DecisionHolon`): it `reviews` the candidate, has an
option space (accept-as-anchor / refine-to-domain-concept / reject), a chosen outcome,
an accountable agent, and (if accepted) `produces` the grounded node.

The gist anchor survives as **lineage** (`rdfs:subClassOf gist:…`), not as the
assertion — the grounded node binds to a domain concept. So a proposition becomes a
seed for *extending the bridging ontology*: iladub tells you where your coverage has
gaps and offers a starting point. Coverage and tool co-evolve.

## The invariant (SHACL-enforced)

- Every `iladub:GroundedNode` must have `iladub:wasPromotedBy` a promotion decision,
  must `groundsTo` a provided-ontology concept, and have status `asserted`.
- A `CandidateConcept` must carry all of: surfaceText, suggestedAnchor, suggestedBy,
  confidence, fromRegion, status=proposed.
- A candidate must **not** also be `asserted` (no-leak SPARQL check).

**Never let a proposition pass as an assertion.** This is a checkable property, not a
discipline you hope holds. Decision-lineage (`hol:revisitIf`) can reopen past
promotions when the bridge later gains coverage; automated promotion is bounded by the
holon's `autonomyScope`.
