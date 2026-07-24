# The four groundings — iladub ↔ HGA alignment

> Status: **design note** (conceptual alignment). Maps iladub's existing mechanisms onto
> Kurt Cagle & Chloe Shannon's four-grounding framework. No `.ttl` is changed by this page;
> it fixes *where iladub sits* in the HGA grounding vocabulary and *what iladub adds*.
>
> Source: Cagle & Shannon, **"What Does Grounding Really Mean?"** (*The Inference Engineer*,
> 2026-07-11) — subtitle *"Definition, identity, provenance, and containment: the four
> groundings AI systems need."* Alignment target is **HGA** (`holon:`), consumed not authored
> (see [Source ownership](holonic-interaction.md) and `CLAUDE.md`).

## Why this note exists

Cagle's grounding essay *names the four groundings an AI system needs* — but, by his own
framing, it stops at the naming: it does **not** develop an assert-vs-propose discipline, a
decision-promotion framework, or source-level provenance chains. Those three are precisely
iladub's signature. So the four groundings are the cleanest available statement of **what
iladub already builds** and **the exact seam where iladub complements HGA**.

This is the same posture as everywhere else: **embrace the holon-graph big picture; supply
the pragmatic machinery HGA leaves as a bare gate.** The grounding framework gives us Cagle's
own vocabulary to say it in.

## The mapping

Cagle's four groundings, each against the iladub mechanism that *realises* it and the HGA
term it aligns to (HGA terms appear only as alignment objects — never authored here).

| Grounding (Cagle) | What it grounds | iladub mechanism | Aligns to (HGA) |
| --- | --- | --- | --- |
| **Denotative** | *Definition / type* — what a thing **is**; class membership + behavioural rules; guards **semantic drift** | The **semantic data contract as ontology** — typed, vocabulary-grounded objects; SHACL validation at the membrane; SKOS/OWL grounding. *Assert only what you can ground.* | `holon:` boundary (SHACL shape) |
| **Instantive** | *Identity of particulars* — what differentiates one individual and **keeps it consistent** over time ("memory is a queue, not a record") | `iladub:GroundedNode` identity; **converging concept IRIs** (table cells, prose, figures resolve to the *same* IRI); entity harmonisation | `holon:` interior individuals (named, not blank) |
| **Temporal** | *Provenance* — **when** a change happened, **why**, and **what it affected downstream**; "an ongoing discipline, not a one-off log entry" | `dec:DecisionHolon` timeline + events; `iladub:PromotionDecision ⊑ dec:DecisionHolon ⊑ prov:Activity`; **provenance to the page** | `hev:` events · `hprov:` / `prov:` |
| **Spatial** | *Containment / boundaries* — nested "where, relative to what"; **"containment is what makes connection possible"** | The doc-holon membrane: `etkl:RawDocumentHolon` → `etkl:GroundingPortal` → `etkl:CleanDocumentHolon`; `etkl:MembraneHealth` as cleanliness | `holon:` / `hmk:` Markov blanket · `holon:Portal` |

## What iladub adds beyond the naming

The grounding essay describes failure modes (semantic drift, attribute drift, provenance
loss, orphaning) but not the discipline that prevents them. iladub supplies exactly that,
at each grounding:

- **Denotative — assert-vs-propose.** Content groundable in a provided ontology is
  **asserted** (typed, contract-bound, SHACL-validated). Ungroundable content is
  **proposed**, never dropped and never faked, as a quarantined `iladub:CandidateConcept`.
  This is the safety valve Cagle's "semantic drift" needs but does not specify — drift can't
  silently ground, because ungroundable content is *structurally* held at the membrane.

- **Temporal — accountable promotion.** A proposition enters the grounded graph **only** as
  the product of an `iladub:PromotionDecision` — SHACL-enforced: *every grounded node is
  produced by a promotion decision.* This is **stronger than HGA's bare confidence gate**
  (HGA routes low-confidence to a candidate status but does not require an accountable,
  agent-attributed, auditable act). It is the machinery that makes temporal grounding
  ("when / why / what downstream") a first-class record rather than a log.

- **Spatial — off-the-map ≠ false.** A `CandidateConcept` is not a boundary *violation*; it
  is content **off the edge of this holon's map** — the open-world *expansion request*, kept
  distinct from the closed-world *validity failure*. This lands Cagle's own
  ["Off the Edge of the Map"](https://ontologist.substack.com/p/off-the-edge-of-the-map)
  (2026-07-01) follow-up — *a worked HGA example emitting an expansion-request event* — which
  iladub already has in `CandidateConcept`. See [Neurosymbolic-first](neurosymbolic-first.md):
  recovery is open-world, the membrane is closed-world, **the holon is the closure boundary.**

- **Provenance to the page** grounds all four back to the source document region — the
  source-level provenance chain the essay calls for but does not build.

## The one-line reading

Cagle says *what* grounding requires (definition · identity · provenance · containment).
iladub supplies the **accountable machinery** — assert/propose, `PromotionDecision`,
provenance-to-the-page — that makes denotative and temporal grounding *safe* rather than
merely asserted. The four groundings are HGA's; the discipline that earns them is iladub's.

## Upstreaming candidate

`iladub:CandidateConcept` framed as an HGA **expansion-request event**, and
`iladub:PromotionDecision` positioned as the accountable layer *under* HGA's bottom-up
convergence governance, is a clean, dated contribution to the W3C Holon CG — it fills a gap
the CG's own material flags as open, and it stays in iladub's owned namespaces (`dec`/`etkl`/
`iladub`), pointing at HGA terms rather than authoring them.

## Related

- [Holonic interaction model](holonic-interaction.md) — the membrane / portal / projection fabric this note grounds.
- [Neurosymbolic-first](neurosymbolic-first.md) — the open/closed-world split (recovery vs membrane) behind *off-the-map ≠ false*.
- [Assertions & propositions](assertion-proposition.md) — the assert/propose/promote epistemics.
- [dec — decision context](dec.md) — `DecisionHolon` and the promotion decision.
