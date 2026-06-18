# Design — Transplant M4 (Offer → Acceptance): compiling a raw organ offer into a decision-ready context

**Date:** 2026-06-18
**Author:** François Rosselet
**Status:** Approved design, pending implementation plan

## 1. Why this use case

A successful deceased-donor **heart** transplant is a time-critical supply chain: a known
sequence of decision milestones, each with a hard or soft clock, each needing a *specific
context* to decide well. The dominant constraint is the **cold-ischemia window**
(aortic cross-clamp → reperfusion, ≈ 4 h for a heart).

The crash-test claim for iladub: *if it can compile the chaos of a transplant — unstructured
documents, minutes counting, hospital silos, FHIR/LOINC data, critical logistics — into a
clean, decision-aware semantic graph with no spaghetti integration, it can orchestrate any
supply chain.* The maritime/High-Seas-Sales mirror is **out of scope** (already proven
elsewhere); the meta-model is the same.

### The anti-crisis principle (the real insight)

We never act in crisis mode. At every moment the system knows **(a)** which timeline segment
we are in, **(b)** the next milestone and *its required-context schema*, and therefore
**(c)** what knowledge to capture *now*. Knowledge capture is **goal-directed by the next
decision**: documents arriving during segment *N* are compiled against the required-context
contract of milestone *N+1*, so the context is **ready before the clock forces the decision**.

### The end-to-end timeline (orientation; only M4 is built here)

| # | Segment | Milestone event | Clock | Decision (actor) |
|---|---|---|---|---|
| M0 | Identification | Potential donor referred | — | Refer? (OPO coordinator) |
| M1 | Death determination | Brain death declared | — | Death confirmed? (neurology) |
| M2 | Authorization | Consent obtained | — | Authorized? (coordinator/family) |
| M3 | Allocation | Match-run executed | — | Which recipient? (allocation algorithm) |
| **M4** | **Offer → Acceptance** | **Offer transmitted** | pre-clock | **Accept this organ for this recipient? (transplant surgeon)** |
| M5 | Mobilization | Teams committed | pre-clock | Transport feasible in window? (logistics + surgeon) |
| M6 | Procurement | Aortic cross-clamp | 🟢 ischemia START | Organ acceptable on inspection? (surgeon) |
| M7 | Transport | Organ in transit | ⏳ running | Contingency on delay? (event-driven) |
| M8 | Implantation | Reperfusion | 🔴 ischemia STOP | Proceed given actual ischemic time? (surgeon) |
| M9 | Recovery | Graft functioning | post-clock | Adequate function? (ICU) |
| M10 | Handoff | To longitudinal care | post-clock | — |

> Synthetic, illustrative clinical model for the demonstrator — to be confirmed with
> transplant SMEs; not medical guidance. SNOMED/LOINC/HLA identifiers are illustrative;
> keep example documents synthetic and confirm terminology licensing before any real use.

## 2. Scope

**This spec builds exactly one milestone — M4 — end to end:** compile a raw, unstructured
organ-offer document into the SHACL-validated **decision-context** that the accept/decline
decision requires, and frame that decision as a `hol:DecisionHolon` whose required context is
**ready and provenanced** at decision time.

**In scope**
- The **M4 required-context contract** (what the accept/decline decision needs).
- The **two-pass typed-extraction funnel** ("the Claude piece"): Reader → BAML typed
  multi-agent extraction → deterministic RDF mapping → SHACL validation.
- The **deterministic, build-time RDF→BAML generator** (the SKOS/OWL ↔ BAML bridge).
- The **assert/propose** epistemics over the extracted content (reusing existing `iladub`
  vocab): groundable → asserted; ungroundable → quarantined `iladub:CandidateConcept`.
- A **minimal, deterministic decision evaluation** on clean concepts (ABO + size + an
  ischemia-budget feasibility check) producing an accept/decline recommendation **and the
  rejected option with its reason**, recorded as a `hol:DecisionHolon`.
- Heart only; one synthetic offer document (text **and** a PDF rendering); one synthetic
  recipient record.

**Out of scope (named so they are not assumed)**
- Other milestones (M0–M3, M5–M10) and the general timeline engine / cursor / forward-pass
  orchestration — that is the next spec (SP2).
- Live transport routing, weather feeds, full Allen-relation interval engine (the MVP uses
  *extracted/given* time values, not computed routing).
- Promotion machinery (moving a proposition into the grounded graph via
  `iladub:PromotionDecision`) — propositions stay **quarantined** in M4.
- Multi-format ingestion beyond text + PDF/image (Word/Excel → PDF is a future commodity
  step).
- The maritime mirror.

## 3. The M4 required-context contract

The accept/decline decision needs these **clean concepts** on the table. This schema is the
**extraction target** and the **decision input** — one declaration, two consumers.

**Donor (from the offer document)**
- `organ` (= heart) → FHIR `BiologicallyDerivedProduct`
- `aboGroup` (A/B/AB/O, ± Rh) — coded concept
- `ejectionFraction` (%) — LOINC-coded observation
- `sizeMetric` (donor weight/height) — for size match
- `serology` flags (HIV/HBV/HCV — negative in the success case) — coded
- `hlaTyping` (synthetic markers)
- `causeOfDeathCategory` — coded
- `coldIschemiaLimitMinutes` (≈ 240 for heart) — from the contract/terminology, not the doc
- `projectedTransportMinutes` / `projectedTotalIschemiaMinutes` — extracted/given logistics estimate

**Recipient (from a small given record, not the offer doc in M4)**
- `aboGroup`, `sizeMetric`, `urgencyStatus`, `hlaAntibodies` (sensitization), `ready` flag

**Decision (computed deterministically from the above)**
- `aboCompatible?`, `sizeCompatible?`, `ischemiaFeasible?` (`projectedTotalIschemiaMinutes ≤
  coldIschemiaLimitMinutes`)
- `recommendation` ∈ {accept, decline} + **rejected option** + human-readable reason
- provenance: each donor concept traces to its **source region** in the document

## 4. Architecture — the funnel + the M4 decision frame

Six isolated, independently testable stages. Stages 1–5 are the reusable funnel (SP1); stage
6 is the M4 decision frame.

```
raw offer (text/PDF)
  │
  1. Reader ─────────────► BAML input (text | pdf/image media)
  │
  2. Schema bridge  (BUILD-TIME, deterministic, no LLM)
     ontology (contract + SKOS + SHACL cardinalities) ──► committed .baml types
  │
  3. Multi-agent BAML extraction (RUN-TIME, LLM in a typed cage, parallel)
     ExtractDonorClinical ‖ ExtractImmunology ‖ ExtractLogistics ──► merged typed object
  │
  4. RDF mapping (deterministic):  typed fields ──► RDF candidates
       resolves in SKOS  ──► asserted (contract-bound)
       does not resolve  ──► iladub:CandidateConcept (proposition, quarantined)
  │
  5. SHACL validation (pySHACL): grounded graph + quarantined propositions
  │
  6. M4 decision frame: assemble required-context → deterministic eval →
     hol:DecisionHolon (recommendation + rejected option + provenance)
```

### Stage 1 — Reader
Source → BAML input. MVP supports `text` and native `pdf`/`image` (Claude reads scans/PDFs
directly — no OCR step). Extends `src/iladub/readers.py`.

### Stage 2 — Schema bridge: deterministic, build-time RDF→BAML
A generator (`src/iladub/bridge.py`) reads the `etkl:SemanticDataContract` + SKOS terminology
(+ SHACL cardinalities) and **emits BAML type definitions** — `class`es for the stable
structure, `enum`s for admissible SKOS concepts (e.g. ABO groups, organ types), field-level
`@assert`/`@check` from datatype/cardinality constraints. **This runs before any compilation.**
The `.baml` files are **committed, tested, and validated**; a **sync test** regenerates them
and fails on drift, keeping the ontology the single source of truth. No runtime `TypeBuilder`.

### Stage 3 — Multi-agent BAML extraction (the LLM step, boxed)
Several focused BAML functions, each typed to its slice and run **in parallel** over the
document:
- `ExtractDonorClinical` — organ, EF, cause-of-death, demographics/size
- `ExtractImmunology` — ABO, HLA, serology
- `ExtractLogistics` — origin/destination, projected transport/ischemia minutes

Each agent returns, per field, a **value + confidence + the quoted source span** (the prompt
requires the source text, which becomes `iladub:SourceRegion`/`prov` provenance). BAML coerces
and `@assert`-validates; type/enum violations are retried by BAML; persistent failures are
recorded as **extraction faults** (never silently dropped). Results merge into one typed
object. Orchestration in `src/iladub/extract_baml.py`.

### Stage 4 — RDF mapping (deterministic)
`src/iladub/to_rdf.py` maps the typed object → RDF. A value whose concept resolves in the SKOS
terminology becomes an **asserted**, contract-bound node; an unresolved value (or an `OTHER`
free-text escape in a BAML enum) becomes a **proposition** = `iladub:CandidateConcept` with
`suggestedAnchor`, `suggestedBy` (the agent), `confidence`, `fromRegion`. Never faked
(Principles 3 & 7).

### Stage 5 — SHACL validation (semantic, Pass 2)
pySHACL (`inference="rdfs"`, `advanced=True`) over the graph against the contract target shape
+ `iladub`/`hol` shapes. Extends `src/iladub/validate.py`. Output: the **grounded graph** plus
**quarantined propositions**. The existing `tests/leak-attempt.ttl` guard ensures a proposition
cannot masquerade as an assertion.

### Stage 6 — M4 decision frame
Assemble the M4 required-context from the grounded graph + the recipient record, run the
**deterministic** evaluation (ABO/size compatibility, ischemia-budget feasibility), and record
a `hol:DecisionHolon`:
- `prov:used` → the evidence (donor concepts, recipient record)
- `prov:wasAssociatedWith` → the deciding agent (surgeon, synthetic)
- the **rejected option** and its reason (e.g. *"decline: projected ischemia 270 min > 240 min
  limit"*)
- `prov:generated` → the recommendation
This is "logic application on clean concepts" — small, deterministic, and the payoff: the
context is **ready and provenanced** at decision time.

## 5. Domain content (synthetic)

In a **demo namespace** (`ex:`), layered on `etkl`/`hol`/`iladub`/`prov`/`fhir` — **not** core
vocab (CLAUDE.md domain-neutrality). New files under `examples/transplant/`:
- `transplant-ontology.ttl` — minimal classes/properties for the M4 slice (Organ, donor/recipient
  immunology + size + ischemia concepts), aligned to FHIR/`hol`.
- `offer-contract.ttl` — the `etkl:SemanticDataContract` declaring the M4 required-context schema.
- `transplant-terms.ttl` — synthetic multilingual (de/fr/en) SKOS terminology (ABO, organ,
  serology, LOINC-coded EF), illustrative notations marked synthetic.
- `offer.txt` and `offer.pdf` — one synthetic Eurotransplant-style heart-offer message, including
  groundable facts **and one deliberately unmapped term** to force a proposition.
- `recipient.ttl` — one synthetic recipient record.
- `offer-conformant.ttl` (passes) and `offer-leak.ttl` (must fail) — per CLAUDE.md every shape
  ships a passing **and** a failing test.

## 6. Two passes ↔ assert/propose (the trust gradient)

The LLM is boxed on both sides:
1. **Deterministic type generation** (stage 2) — ontology compiles to fixed BAML types.
2. **Controlled LLM extraction inside a typed cage** (stage 3) — schema-constrained, `@assert`,
   retried, provenanced.
3. **Deterministic grounding** (stage 4) — SKOS resolution decides asserted vs proposition.
4. **Deterministic semantic validation** (stage 5) and **deterministic decision** (stage 6).

BAML's `@assert`/`@check` = Pass 1 (typed/structural). pySHACL = Pass 2 (semantic). A concept
ungroundable in the provided ontology is **quarantined**, never dropped, never promoted in M4.

## 7. CI / testing strategy (the non-deterministic LLM constraint)

CLAUDE.md requires pytest in CI on every push; the LLM step is non-deterministic, so:
- **Deterministic layers → normal pytest:** the RDF→BAML generator (golden ontology→`.baml`),
  the RDF mapping (typed object → expected `.ttl`), SHACL (conformant + negative `.ttl`).
- **BAML extraction → recorded-response fixtures** (offline, deterministic). The live-API path
  is gated behind `BAML_LIVE=1` / a pytest marker so CI never calls the API. A small set of
  recorded extraction fixtures verifies the typed output **and** the candidate/proposition
  mapping.
- **Sync test:** regenerate `.baml`, diff against committed → fail on drift.
- **Gated end-to-end smoke (live):** real doc → real BAML → SHACL-validated graph → decision.

## 8. Files & dependencies

**New dependencies** (add to `pyproject.toml`): `baml-py` + the BAML CLI (codegen); an
Anthropic provider client for BAML; API key via env (`ANTHROPIC_API_KEY`).

**Layout**
- `baml_src/` — generated type `.baml` (from stage 2) + the extraction-agent `.baml` functions
  + client config + BAML `test` blocks.
- `src/iladub/bridge.py` — deterministic RDF→BAML generator (stage 2).
- `src/iladub/extract_baml.py` — parallel multi-agent extraction + merge (stage 3).
- `src/iladub/to_rdf.py` — typed → RDF candidates (stage 4).
- reuse/extend `readers.py` (stage 1), `validate.py` (stage 5), `contract.py`, `pipeline.py`
  (wire the M4 path), add a thin `decision.py` (stage 6).
- `examples/transplant/` — domain content (§5).
- `tests/` — generator golden test, mapping test, SHACL conformant/negative, BAML
  recorded-fixture test, sync test, M4 decision test (accept **and** decline/rejected-option).

## 9. Grounding (design inspiration, not authority)

The temporal/decision framing draws on vault concepts (consulted via the `eduba` skill):
**EventBasedModeling** (state-changes as start/end events), **Allen's Interval Algebra**
(interval relations emerge from start/end pairs — the basis for the ischemia-feasibility check,
implemented minimally here as a numeric budget; full interval engine deferred to SP2), and
**gates-to-boundaries** (SHACL = sensory validation, ODRL = motor governance). *Both vault
event pages are `confidence: low` stubs — design inspiration, not authoritative sources.*

## 10. Open items to resolve during planning (not blockers)

- **Grounding-vs-promotion wiring:** confirm, against the actual `iladub`/`hol` shapes, how
  directly-extracted contract-bound assertions relate to `iladub:GroundedNode` /
  `wasPromotedBy` (M4 keeps propositions quarantined; no promotion).
- **Exact agent split & merge semantics:** confirm the three-agent split and how overlapping
  fields are reconciled on merge.
- **BAML recorded-fixture mechanism:** confirm the offline/record-replay approach for CI
  against the installed `baml-py` version.
