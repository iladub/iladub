# Governed / ViewerPass projection — a viewer-relative federation projection

- **Date:** 2026-07-25
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). A single vertical slice ("loop F-gov") extending the compile→federate loop.
- **Context:** The compile→federate loop (`docs/superpowers/specs/2026-07-24-compile-federate-design.md`, shipped PR #63) exposes a *flat* `etkl:DocumentProjection`. This increment makes the projection **viewer-relative**: derived per viewer under ODRL policy over concept **sensitivity tags**, so a consumer — or an AI agent acting on behalf of a user — grounds against exactly its entitled projection and **can never reach more**. It fulfils the note already written in `examples/transplant/transplant-governance.ttl` ("in production these are derived by named CONSTRUCT queries under each role's policy") and lands the **governed-bot** value (AI-inherits-user, ABAC-shaped access) end-to-end.

---

## 1. Purpose and scope

Turn the federation projection into a **governed, viewer-relative** projection. A viewer's projection contains only the concepts whose **sensitivity tag** the viewer's role is granted read on by an ODRL policy. The viewer may be a plain role, a person, or an **AI agent acting for a user** — resolved by one SPARQL property path (`(prov:actedOnBehalfOf)?/etkl:hasRole`), so the AI inherits exactly its user's access.

**In scope:**
- `vocab/queries/federate-projection-governed.rq` — a role-parameterized CONSTRUCT (AXIOM) gating concepts by ODRL read-grants over their sensitivity tag.
- Thin owned vocab: `etkl:sensitivity` (concept → tag), `etkl:hasRole` (person/agent → role), `etkl:forViewer` (recipe → viewer).
- `federate.derive_governed_projection(...)` and `federate.certify_governed_federation(...)` (extends the existing oracle with a **governance-soundness** check).
- **Upgrade** `examples/transplant/transplant-governance.ttl` + `tests/test_governance.py`: the hand-materialized `view-opo`/`view-recipient` become **derived** via the governed CONSTRUCT.
- A federated demonstrator under `examples/federation/`: a recipient-centre **consumer** and an **AI agent** for a recipient clinician each ground against their derived role projection and cannot reach PHI concepts.

**Non-goals (deferred, each a later increment):**
- Multi-dimensional ABAC `f(region, role, desk, deal)` — this slice does **one** categorical tag dimension (extensible by adding tags).
- `risk:` contextual-sensitivity derivation of the tag (this slice uses a **declared** classification graph; `risk:` can subsume it later).
- Multi-producer / multi-hop projection union (the fixed `<urn:iladub:projection>` IRI limitation, already deferred by the compile→federate spec §8).
- Enforcement at a Fluree `f:` policy layer (topic 1 — the substrate increment).

**Success criteria:**
1. A viewer's derived projection contains **exactly** its promoted-and-granted concepts — a non-granted (e.g. `phi`) concept never appears for a role without the grant. Proven by deriving OPO (gets PHI+clinical) vs recipient (clinical only).
2. A consumer — including an AI agent via `prov:actedOnBehalfOf` — grounding against its role projection **cannot ground to** a concept outside it (containment holds; the leak is caught when injected).
3. The whole governance decision, **including AI-inherits-user**, is declarative (AXIOM CONSTRUCT + SHACL); no procedural code answers "which concepts may this role see."
4. `hfed:` unused; `hproj:`/`hview:`/`hpol:` appear only as alignment objects.

---

## 2. Architecture and data flow

```
CleanDocumentHolon A (interior: promoted concepts)
  + governance graph:  ?concept ──etkl:sensitivity──► ?tag      (ABO_O:clinical, donorId:phi)
  + ODRL policy:       permission[ odrl:action odrl:read ; odrl:assignee ?role ; odrl:target ?tag ]
  + viewer recipe:     <urn:federate:recipe> etkl:forViewer ?viewer
        │ federate-projection-governed.rq  (AXIOM CONSTRUCT)
        │   emit ?concept  iff
        │     ?concept promoted  AND  ?concept etkl:sensitivity ?tag
        │     AND ?viewer (prov:actedOnBehalfOf)?/etkl:hasRole ?role
        │     AND policy has permission(read, ?role, ?tag)
        ▼
  A's role-scoped etkl:DocumentProjection  (only tags ?role may read)
        │ consumed as terminology (grounding portal UNCHANGED)
        ▼
  consumer ?viewer grounds ─► reaches only entitled concepts
        │ federate.certify_governed_federation
        ▼  sound ∧ opaque ∧ contained ∧ governance-sound
```

**AI-inherits-user** is the `(prov:actedOnBehalfOf)?/etkl:hasRole` path: a human viewer resolves via `hasRole`; an AI agent resolves through its user first. `gsh:AiInheritsUserShape` (existing) is the membrane precondition — an agent with no `actedOnBehalfOf` fails validation before any derivation.

---

## 3. Components

### 3.1 The governed CONSTRUCT — `vocab/queries/federate-projection-governed.rq` (AXIOM)
Extends `federate-projection.rq`. WHERE clause (all positive graph patterns — evidence-positive, open-world):
- `?gn a iladub:GroundedNode ; iladub:wasPromotedBy ?pd ; iladub:groundsTo ?concept .` `?pd a iladub:PromotionDecision .` `?concept skos:prefLabel ?label .` (promoted, as before)
- `?concept etkl:sensitivity ?tag .` (the concept's declared tag)
- `<urn:federate:recipe> etkl:forViewer ?viewer . ?viewer (prov:actedOnBehalfOf)?/etkl:hasRole ?role .` (viewer → role, incl. AI-inherits-user)
- `?perm odrl:action odrl:read ; odrl:assignee ?role ; odrl:target ?tag .` (a *present* read-grant for this role on this tag)

CONSTRUCT emits the same SKOS shape as `federate-projection.rq` (`?concept a skos:Concept ; skos:inScheme <urn:iladub:projection> ; skos:prefLabel ?label` + the scheme typed `etkl:DocumentProjection , skos:ConceptScheme`). A concept with no matching grant is simply never emitted — the membrane withholds by omission, not by filtering.

### 3.2 Vocab (standalone, in `etkl.ttl`)
- `etkl:sensitivity` — `owl:ObjectProperty`, a concept's declared sensitivity/compartment tag (domain left open; range a tag resource). Supplied in a governance graph separate from the domain subject.
- `etkl:hasRole` — `owl:ObjectProperty`, a person's or agent's role (the ViewerPass role handle).
- `etkl:forViewer` — `owl:ObjectProperty`, a derivation recipe's viewer.

None reference HGA. Alignment (objects only, in `iladub-hga-align.ttl`): `etkl:hasRole rdfs:seeAlso hview:ViewerProfile` (informative — HGA's ViewerPass profile); no subclassing required.

### 3.3 `federate.py` additions (PROCEDURAL glue, justified)
- `derive_governed_projection(interior, terms, governance, policy, viewer) -> Graph` — materializes `<urn:federate:recipe> etkl:forViewer <viewer>` into a recipe graph (the reshape recipe pattern) and runs `interpret.run(federate-projection-governed.rq, interior, terms, governance, policy, recipe)`. No domain decision; the gating lives entirely in the `.rq`.
- `certify_governed_federation(interior, governance, policy, viewer, projection, consumer_graph) -> GovernedVerdict` — calls the existing `certify_federation(interior, projection, consumer_graph)` for sound/opaque/contained, then adds:
  - `permitted = { c : (c etkl:sensitivity T) in governance, policy grants role(viewer) read on T }` (computed by set logic over the graphs).
  - `ungranted = projection_concepts − permitted` (governance-soundness; non-empty ⇒ a concept slipped in without a grant).
  - `GovernedVerdict(ok, unsound, leaked, uncontained, ungranted)`; `ok = base.ok and not ungranted`.
  - `role(viewer)` is resolved by the same property path in a small SPARQL/graph query — reused, not reimplemented.

### 3.4 SHACL (reuse)
- `etkl:DocumentProjectionShape` (existing) — the derived governed projection still carries only concepts.
- `gsh:AiInheritsUserShape` (existing) — asserted as a precondition on the viewer graph for the AI-agent path.
No new shape required.

---

## 4. Demonstrator — upgrade the transplant governance scenario

Reuses transplant's world (OPO vs recipient-centre roles; donor-PHI vs de-identified-clinical).

- **Governed fixtures under `examples/federation/`:** a donor-offer interior whose promoted concepts are tagged (`concept-abo → clinical`, `concept-donor-identity → phi`, …); roles `tx:role-opo`, `tx:role-recipient-ctr` with `etkl:hasRole`; an ODRL policy granting `role-opo read {clinical, phi}` and `role-recipient-ctr read {clinical}`; a recipient clinician and an AI assistant (`prov:actedOnBehalfOf` the clinician).
- **Upgrade `examples/transplant/transplant-governance.ttl` + `tests/test_governance.py`:** the hand-materialized `tx:view-opo` / `tx:view-recipient` are replaced by **derived** projections. `test_governance` now derives them via `derive_governed_projection` and asserts the recipient view withholds the PHI concept while both keep the clinical concepts — the same intent as today, now proven on derived output.

**Tests (`tests/test_governed_projection.py`):**
- Derive for `role-opo` → projection includes the `phi`-tagged concept; derive for `role-recipient-ctr` → it does **not** (withheld by omission), both include `clinical` concepts.
- A recipient-centre consumer grounds against its derived projection and its grounded set excludes the PHI concept.
- The **AI agent** (`actedOnBehalfOf` the recipient clinician) derives to the recipient projection and likewise cannot ground to the PHI concept — the governed-bot claim.
- `certify_governed_federation` returns `ok` for the faithful case.
- **Negative — leak/containment:** a consumer graph grounding to the PHI concept → `uncontained` non-empty, `ok` False.
- **Negative — governance-soundness:** a projection containing a `phi` concept for `role-recipient-ctr` → `ungranted` non-empty, `ok` False.
- **Negative — AI without user:** an agent viewer with no `prov:actedOnBehalfOf` → `gsh:AiInheritsUserShape` fails.

---

## 5. Neurosymbolic gate compliance (Global Constraint)

- **Governed derivation → AXIOM.** `federate-projection-governed.rq` is a fixed SPARQL CONSTRUCT, open-world, evidence-positive (emit only when a granting permission is present). The **AI-inherits-user** resolution is a SPARQL property path, not procedural code. No tuned constant.
- **Membrane → SHACL.** `DocumentProjectionShape` + `AiInheritsUserShape` (both existing).
- **Oracle → PROCEDURAL, justified.** `certify_governed_federation` is set comparison over graph/SPARQL results — same class as `interpret.run`/`oracle.round_trip`; no domain decision, no tuned tolerance. `derive_governed_projection` only materializes a recipe and delegates to `interpret.run`.
- No Python answers a "which concepts may this role see" question — that decision is entirely in the CONSTRUCT and the ODRL policy.

---

## 6. Source-ownership & alignment discipline

- `etkl:sensitivity`, `etkl:hasRole`, `etkl:forViewer` are authored only in `etkl:`; `etkl.ttl` stays standalone.
- HGA terms appear only as objects in `iladub-hga-align.ttl`: `etkl:hasRole rdfs:seeAlso hview:ViewerProfile` (informative). Access rides `odrl:` (aligned to `hpol:`) and `prov:` (aligned to `hview:`) — not re-authored.
- `hfed:` (reserved) unused. Governed federation is `hproj:` projection-exchange under `hpol:`/`hview:`-aligned policy.

---

## 7. Relation to prior work and steering

- Extends the **compile→federate loop** (PR #63): same `etkl:DocumentProjection`, same portal-unchanged consumption, same round-trip oracle — now viewer-relative.
- Realizes the **High Seas / governed-bot** thesis (`internal/decisions/2026-07-02-fluree-as-hga-substrate.md`, `[[governed-bot-poc]]`, `[[high-seas-bridge]]`): AI-inherits-user + policy-as-data on the membrane; the single-tag dimension is the seed of ABAC `f(region,role,desk,deal)`.
- Fulfils the "in production these are derived" note in `transplant-governance.ttl`.
- The projection derived here is the natural thing to later register as a **named query on Fluree** (topic 1) with the tag policy enforced as `f:` — deferred.

---

## 8. Open questions / later increments

1. Multi-dimensional ABAC (`region`/`desk`/`deal` tags) — more `etkl:sensitivity` dimensions + policy over their conjunction.
2. `risk:` contextual sensitivity as the tag source (inherited top-down) instead of a declared classification graph.
3. Fluree `f:` enforcement of the tag policy at the substrate (topic 1).
4. Per-producer projection scheme IRIs (lift the fixed `<urn:iladub:projection>` — shared with the compile→federate deferred list).
