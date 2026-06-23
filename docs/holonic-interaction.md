# Holonic interaction model

> Status: **design note** (conceptual). The vocabulary alignment described here is
> a planned follow-up; this page fixes the model before any `.ttl` is written.

Defining holons is the easy half. The architecture lives in **how they interact**.
This page models iladub as a small set of holons connected by a governed interaction —
aligned with the holonic-graph architecture (Kurt Cagle) and its reference ontology,
the Context-Graph Architecture / CGA (Zach Welz's `holonic` library), rather than
reinventing one.

## What a holon is (and why interaction is the point)

A **holon** (Koestler) is something that is *simultaneously a whole and a part*. In the
holonic-graph reading, every holon has four orthogonal aspects expressed as named
graphs:

- **interior** — what is true inside (its assertional state);
- **boundary** — the rules that govern it (SHACL shapes) — a *membrane*, not a wall;
- **projection** — what it exposes to others (its outward face);
- **context** — provenance and history.

A holon never exposes its interior directly. Others see only its **projection**, and
anything crossing the **boundary** is validated against it. Cagle's framing: the
boundary is a **Markov blanket** — it does not prevent interaction, it *governs* it, and
validation is "the computation of the difference between what arrived and what was
expected." Interaction, not definition, is where the work happens.

## iladub as interacting holons

iladub compiles a document by letting a **raw document holon** interact with
**semantic holons** (the provided ontologies and terminologies) through a governed
**portal**, producing a **clean document holon** whose interior is the grounded graph.

```
   RawDocumentHolon ───────────[ GroundingPortal ]───────────▶ CleanDocumentHolon
   (the source doc)         (bidirectional, liminal —            (the compiled output)
        │                    itself a holon: the                        ▲
        │ interior: the       "semantic interaction")                   │ interior: grounded graph
        │ Document Region          │     ▲                              │   + the promotion decisions
        │ Graph (prose,            │     │ candidate groundings         │ boundary: the contract's
        │ tables, figures,         ▼     │ proposed back                 │   SHACL shapes (the membrane)
        │ provenance-to-page)  ┌────────────────────┐                   │ context: provenance-to-region
        ▼                      │   SemanticHolons   │                   │ projection: the FAIR graph
   projection: surface ──────▶ │  ontologies + SKOS │                     machines consume
   concepts / mentions         │  (grounding source)│
                               └────────────────────┘
```

In one sentence:

> A **RawDocumentHolon** and the **SemanticHolons** interact through a grounding
> **Portal**; concept-matching at that portal is governed by **PromotionDecisions** at
> the contract **membrane**; what passes is assembled into a **CleanDocumentHolon**
> whose **membrane-health is its cleanliness**.

## The holon types

| Holon | Interior | Boundary (membrane) | Projection | Context |
|---|---|---|---|---|
| **RawDocumentHolon** | the Document Region Graph (regions, reading order) | well-formedness of the region graph | the surface concepts / mentions it offers | acquisition provenance |
| **SemanticHolon** (knowledge module) | the ontology / SKOS terminology | what a valid grounded instance looks like | the concepts available for grounding | who curates the vocabulary |
| **CleanDocumentHolon** | the grounded graph + its promotion decisions | the contract's SHACL shapes | the FAIR semantic graph | provenance-to-region; the decision log |

A SemanticHolon that exists to bridge vocabularies (e.g. SNOMED ↔ a domain concept) is
specifically an **alignment holon**.

## The interaction primitives

These are what `hol` was missing — and what make the model an *interaction* model:

1. **The membrane.** A holon's boundary is its SHACL shapes. Validating the interior
   against the boundary yields a health — **Intact / Weakened / Compromised**. For the
   clean document holon this *is* the document's quality signal: "clean" is not a vibe,
   it is **membrane health**.

2. **The portal.** Interaction between two holons is a first-class object with its own
   IRI — and *a portal is itself a (liminal) holon*. The **grounding portal** carries
   the concept-matching logic (a transform). "The boundary between knowledge systems is
   where the real complexity lives, and it deserves first-class status." iladub's
   *convergence* principle — table cell, prose, and figure resolving to the **same
   concept IRI** — is multiple region-holons reconciled *through the portal*.

3. **Projection.** Holons interact through projections, never raw interiors. The clean
   document holon's projection is the FAIR graph downstream systems consume.

4. **Topology.** Containment (a holarchy: corpus ⊃ document ⊃ region) is *orthogonal*
   to peer adjacency (a holonet: documents that cross-reference each other).

5. **Propagation.** A change at one holon's boundary is validated, logged to context,
   updates the interior, and changes the **projection** the containing holon sees —
   which then runs its own loop. Re-grounding a region can ripple up to the document and
   the corpus, "recorded, validated, and traceable" at every level.

## Where this meets iladub's existing epistemics

iladub already implements the membrane — it just did not name it. The mapping is direct:

| iladub concept | Holonic-interaction reading |
|---|---|
| the **contract** (`etkl:SemanticDataContract`) + knowledge module | the **boundary / membrane** (SHACL priors) |
| the **grounded graph** | the clean document holon's **interior** |
| a **`iladub:CandidateConcept`** (proposition) | a candidate *at the membrane*, not yet admitted |
| a **grounded assertion** | content *inside* the interior — it crossed the membrane |
| a **`iladub:PromotionDecision`** (`hol:DecisionHolon`) | the **governed membrane-crossing** — an auditable concept-matching decision |
| **convergence** on shared concept IRIs | **portal** reconciliation across region-holons |
| **provenance to the page** | the **context** layer |

So the assertion/proposition boundary is simply *which side of the membrane a node is on,
and which decision moved it there*. The promotion decision is the act of crossing.

## Alignment, not reinvention

There is already a reference-implemented ontology for holon interaction — the **CGA**
ontology shipped with Zach Welz's `holonic` library (portals with three subtypes,
membrane health, projection, holarchy vs holonet, a holon type taxonomy, PROV-O
provenance). Its author recommends **alignment, not import**: keep a standalone,
reasoner-free core and align to other vocabularies rather than forcing everything into
one tree.

iladub follows the same principle it applies to provenance ("don't reinvent"): iladub's
holon types and its grounding portal are defined in the `iladub`/`hol` namespaces and
**aligned** to the W3C Holon CG ontology, not copied from it.

> **Anchor (settled 2026-06-23):** the alignment target is **Cagle's W3C Holon CG /
> HGA** (`holon:` = `http://w3id.org/holon/`), *not* Welz's CGA (`urn:holonic:ontology:`),
> which remains useful conceptual prior art. HGA's `holon:DataHolon` ("information-bearing
> artefact … produced and consumed by the pipeline") is the natural anchor for iladub's
> document/semantic holons; `holon:Portal` (a *navigational* link) anchors the grounding
> portal, which **adds** the concept-matching transform. Note HGA has **no `holon:Boundary`
> class** (boundary semantics ride on `holon:boundaryMode` + SHACL shapes). See
> `CLAUDE.md` ("Holonic interaction model").

## What is built

- `vocab/ontology/iladub-holons.ttl` — the holon types + grounding portal + membrane
  health, in the `iladub` namespace, **standalone** (no HGA dependency).
- `vocab/ontology/iladub-hga-align.ttl` — the **optional** HGA alignment
  (alignment-not-import): `rdfs:subClassOf holon:DataHolon` / `holon:Portal` axioms only.
- `vocab/shapes/iladub-hga-shapes.ttl` — `iladub:HgaGroundingGovernanceShape`: a
  `holon:GroundingRecord` may reach `holon:RegisteredStatus` **only** as the product of an
  `iladub:PromotionDecision` (iladub's invariant layered onto HGA's bare confidence gate).
- `examples/holon-grounding-conformant.ttl` + `tests/holon-grounding-leak.ttl` — a
  conforming governed-grounding traversal and a negative case; exercised by
  `tests/test_hga_alignment.py`.

## Planned work (not done yet)

- A membrane-health check that computes and reports a compiled document's cleanliness
  (`iladub:membraneHealth` → Intact / Weakened / Compromised) from validation results.
- A full raw→clean traversal example spanning RawDocumentHolon → portal → CleanDocumentHolon
  (the current example covers the grounding-governance crossing only).

## Sources

- Kurt Cagle, *The Holonic Graph* and *The World Is Not a Database* (The Inference
  Engineer / The Ontologist, 2026) — the four-layer holon, SHACL-as-priors, the boundary
  as a Markov blanket, portals as liminal holons.
- Zach Welz, `holonic` library and the Context-Graph Architecture (CGA) ontology — the
  reference implementation: portal subtypes, membrane health, holarchy vs holonet,
  alignment-not-import.
- Arthur Koestler, *The Ghost in the Machine* (1967) — the holon and the holarchy.
