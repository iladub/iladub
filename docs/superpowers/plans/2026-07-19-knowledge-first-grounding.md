# Knowledge-First Grounding (ground-or-propose) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the working ground-or-propose pipeline — ground document surface-concepts against a `SemanticDataContract`, promoting each admissible grounding via an accountable `PromotionDecision` and quarantining the rest as `CandidateConcept` propositions — proven end-to-end against the shipped transplant offer-contract and the epistemics SHACL.

**Architecture:** A core `src/iladub/ground.py` pipeline. Every concept becomes an `iladub:CandidateConcept` (a proposition), then is disposed: an **exact contract match** (field-label / property-name, and SKOS scheme membership for scheme-bound fields — AXIOM/PROCEDURAL lookups) or, failing that, a **BAML `ProposeGrounding`** (NEURAL, injected seam mirroring `propose.py`). A proposed grounding is admitted only if it passes the **contract oracle** — SKOS `admissibleScheme` membership + the contract SHACL shape — at which point a `PromotionDecision` produces the `iladub:GroundedNode` (the only path across the membrane). Confidence is recorded, never promotes. Ungroundable / wrong / novel concepts stay `proposed`.

**Tech Stack:** Python 3, `rdflib`, `pySHACL` (via the shipped `src/iladub/validate.py`), BAML (`client Claude`), `pytest`.

## Global Constraints

- **Test interpreter (MANDATORY):** run every test via `./.venv/bin/python -m pytest …`, NOT bare `python`/`python3`/`pytest` (the bare env has rdflib 7.1.4 → spurious SPARQL/pyShACL failures; `.venv` is rdflib 7.6.0). Wherever a step says `pytest …`, execute `./.venv/bin/python -m pytest …`.
- **Epistemics invariant (enforced by `vocab/shapes/iladub-shapes.ttl`, do not weaken):** every `iladub:GroundedNode` MUST have `iladub:wasPromotedBy` ≥1 `PromotionDecision`, `iladub:groundsTo` ≥1, and `iladub:status iladub:asserted`. A `PromotionDecision` MUST `iladub:reviews` ≥1 `CandidateConcept` and carry `dec:decidedBy` ≥1. A `CandidateConcept` MUST carry `surfaceText`, `suggestedAnchor`, `suggestedBy`, `confidence`∈[0,1] (xsd:decimal), `fromRegion`, `status iladub:proposed`, and MUST NOT also be `asserted` (`NoLeakShape`).
- **Neurosymbolic gate (§8):** the exact-match + SKOS-scheme lookup + SHACL dispose are AXIOM/PROCEDURAL (no tuned constant); the ONLY NEURAL step is `ProposeGrounding`, and its output is NEVER asserted without passing the contract oracle. **Confidence never promotes** — the contract shape + scheme membership do. A tuned constant/threshold deciding admission is a defect.
- **Source ownership:** author only `iladub:`/`etkl:`/`tx:` (example) terms; consume `dec:`, `prov:`, `skos:`, `gist:`, HGA as objects only. No new epistemics vocab/shapes — `iladub.ttl` / `iladub-shapes.ttl` are sufficient; a genuinely missing term is a finding to raise, not to invent.
- **Offline-first:** all tests pass via `FakeGroundingProposer` (deterministic); the live `BamlGroundingProposer` is lazy + `BAML_LIVE`-gated (the `propose.py` discipline).
- **Namespaces:** `ILADUB=https://w3id.org/iladub#`, `DEC=https://w3id.org/iladub/dec#`, `ETKL=https://w3id.org/iladub/etkl#`, `TX=https://example.org/transplant#`, `SKOS=http://www.w3.org/2004/02/skos/core#`, `GIST=https://w3id.org/semanticarts/ns/ontology/gist/`.
- **Full suite** via `.venv` at the final task; zero regressions (current baseline: `393 passed, 5 skipped`).

---

## File Structure

- **Create** `src/iladub/ground.py` — contract model + pipeline (load, exact-match, scheme lookup, dispose, emit).
- **Create** `src/iladub/propose_ground.py` — the `GroundingProposer` Protocol + `FakeGroundingProposer` / `BamlGroundingProposer` (mirrors `src/iladub/etkl/propose.py`).
- **Create** `baml_src/ground_propose.baml` — `ProposeGrounding` + `GroundingProposal`.
- **Create** `tests/test_grounding.py` — unit + end-to-end conformance + the three negative tests.
- **Reuse (no edits):** `examples/transplant/offer-contract.ttl`, `examples/transplant/offer-shapes.ttl`, `examples/transplant/transplant-terms.ttl`, `vocab/ontology/iladub.ttl`, `vocab/shapes/iladub-shapes.ttl`, `src/iladub/validate.py`.

Verified facts the plan relies on (read before coding if unsure):
- `validate(data, shapes, knowledge) -> ValidationResult(conforms, report_text, report_graph)` (`src/iladub/validate.py`).
- Contract: `tx:offer-contract a etkl:SemanticDataContract ; etkl:targetClass tx:OrganOffer ; etkl:hasField tx:f-organ, tx:f-abo, … ` each `etkl:Field ; etkl:fillsProperty <prop> ; [etkl:admissibleScheme <scheme>]`.
- Terms: `tx:abo-A skos:prefLabel "A"@en ; skos:inScheme tx:scheme-abo` (also O/B/AB); `tx:organ-heart skos:prefLabel "Heart"@en ; skos:inScheme tx:scheme-organ`.
- Shape: `tx:OrganOfferShape sh:targetClass tx:OrganOffer` requires `tx:organ` 1..1, `tx:aboGroup` 1..1 `xsd:string`, `tx:ejectionFraction` 0..1.

---

### Task 1: Contract model + exact-match + SKOS scheme lookup

**Files:**
- Create: `src/iladub/ground.py`
- Test: `tests/test_grounding.py`

**Interfaces:**
- Produces:
  - `SurfaceConcept(text: str, value: str, region: str)` (frozen dataclass).
  - `ContractField(iri: str, fills_property: str, scheme: str | None)`, `Contract(target_class: str, fields: tuple[ContractField, ...])` (frozen).
  - `load_contract(contract_path: str) -> Contract`.
  - `exact_field(concept: SurfaceConcept, contract: Contract) -> ContractField | None` — matches a concept's `text` to a field by the field's `fills_property` local name (case-insensitive, ignoring non-alphanumerics: "ABO group" → `aboGroup`).
  - `scheme_member(value: str, scheme_iri: str, terms: rdflib.Graph) -> str | None` — the IRI of the `skos:Concept` in `scheme_iri` whose `skos:prefLabel` equals `value` (any language tag), else None.

- [ ] **Step 1: Write failing tests**

Create `tests/test_grounding.py`:

```python
from rdflib import Graph
from iladub.ground import (
    SurfaceConcept, load_contract, exact_field, scheme_member,
)

CONTRACT = "examples/transplant/offer-contract.ttl"
TERMS = "examples/transplant/transplant-terms.ttl"


def _terms():
    return Graph().parse(TERMS, format="turtle")


def test_load_contract_fields():
    c = load_contract(CONTRACT)
    assert c.target_class == "https://example.org/transplant#OrganOffer"
    props = {f.fills_property.split("#")[-1] for f in c.fields}
    assert {"organ", "aboGroup", "ejectionFraction"} <= props
    abo = next(f for f in c.fields if f.fills_property.endswith("aboGroup"))
    assert abo.scheme == "https://example.org/transplant#scheme-abo"
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    assert ef.scheme is None


def test_exact_field_matches_by_property_name():
    c = load_contract(CONTRACT)
    f = exact_field(SurfaceConcept("ABO group", "A", "r1"), c)
    assert f is not None and f.fills_property.endswith("aboGroup")
    assert exact_field(SurfaceConcept("smoking pack-years", "20", "r4"), c) is None


def test_scheme_member_prefLabel():
    t = _terms()
    assert scheme_member("A", "https://example.org/transplant#scheme-abo", t) \
        == "https://example.org/transplant#abo-A"
    assert scheme_member("55%", "https://example.org/transplant#scheme-abo", t) is None
```

- [ ] **Step 2: Run, verify fail**

Run: `./.venv/bin/python -m pytest tests/test_grounding.py -q`
Expected: FAIL (`ModuleNotFoundError: iladub.ground`).

- [ ] **Step 3: Implement `ground.py` (Task-1 portion)**

```python
"""ground — the ground-or-propose pipeline (knowledge-first grounding).

Every concept is a proposition (iladub:CandidateConcept) first; it crosses into the grounded
graph ONLY via an iladub:PromotionDecision, and only when the contract oracle (SKOS
admissibleScheme membership + the contract SHACL shape) admits it. Confidence never promotes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from rdflib import Graph, Namespace
from rdflib.namespace import SKOS

ETKL = Namespace("https://w3id.org/iladub/etkl#")
SKOSNS = SKOS


@dataclass(frozen=True)
class SurfaceConcept:
    text: str
    value: str
    region: str


@dataclass(frozen=True)
class ContractField:
    iri: str
    fills_property: str
    scheme: str | None


@dataclass(frozen=True)
class Contract:
    target_class: str
    fields: tuple[ContractField, ...]


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def load_contract(contract_path: str) -> Contract:
    g = Graph().parse(contract_path, format="turtle")
    contract = next(g.subjects(ETKL.targetClass, None), None)
    target = g.value(contract, ETKL.targetClass)
    fields = []
    for f in g.objects(contract, ETKL.hasField):
        prop = g.value(f, ETKL.fillsProperty)
        scheme = g.value(f, ETKL.admissibleScheme)
        fields.append(ContractField(str(f), str(prop), str(scheme) if scheme else None))
    return Contract(str(target), tuple(fields))


def exact_field(concept: SurfaceConcept, contract: Contract) -> ContractField | None:
    key = _norm(concept.text)
    for f in contract.fields:
        if _norm(f.fills_property.split("#")[-1].split("/")[-1]) == key:
            return f
    return None


def scheme_member(value: str, scheme_iri: str, terms: Graph) -> str | None:
    from rdflib import URIRef
    for c in terms.subjects(SKOSNS.inScheme, URIRef(scheme_iri)):
        for lbl in terms.objects(c, SKOSNS.prefLabel):
            if str(lbl) == value:
                return str(c)
    return None
```

- [ ] **Step 4: Run, verify pass**

Run: `./.venv/bin/python -m pytest tests/test_grounding.py -q`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/ground.py tests/test_grounding.py
git commit -m "feat(iladub): contract model + exact-match + SKOS scheme lookup (grounding task 1)"
```

---

### Task 2: The `GroundingProposer` seam + `ProposeGrounding` BAML

**Files:**
- Create: `src/iladub/propose_ground.py`
- Create: `baml_src/ground_propose.baml`
- Test: `tests/test_grounding.py` (add)

**Interfaces:**
- Produces:
  - `GroundingProposal(field_iri: str | None, anchor_iri: str, confidence: float, rationale: str, suggester_iri: str)` (frozen; `field_iri=None` ⇒ proposed novel).
  - `GroundingProposer` Protocol: `propose_grounding(concept: SurfaceConcept, fields: tuple[ContractField, ...]) -> GroundingProposal`.
  - `FakeGroundingProposer(proposal)` (returns its fixed proposal), `BamlGroundingProposer` (lazy, `BAML_LIVE`-gated), `baml_grounding_available() -> bool`.

- [ ] **Step 1: Write the BAML function**

Create `baml_src/ground_propose.baml`:

```baml
class GroundingProposal {
  field_iri string? @description("IRI of the contract field this concept grounds to, or null if genuinely novel")
  anchor_iri string @description("a suggested upper-ontology (gist) class IRI for the concept")
  confidence float @description("0.0-1.0 calibrated confidence")
  rationale string @description("one sentence on why")
}

function ProposeGrounding(surface_text: string, value: string, field_labels: string[]) -> GroundingProposal {
  client Claude
  prompt #"
    A document field reads {{ surface_text }} = {{ value }}.
    The target contract offers these field labels: {{ field_labels }}.
    Which contract field does this ground to (return its exact label), or null if none fits?
    Also suggest an upper-ontology (gist) anchor class and a calibrated confidence.
    {{ ctx.output_format }}
  "#
}
```

- [ ] **Step 2: Write failing proposer test**

Add to `tests/test_grounding.py`:

```python
from iladub.propose_ground import GroundingProposal, FakeGroundingProposer

def test_fake_grounding_proposer_returns_fixed():
    p = GroundingProposal(field_iri="https://example.org/transplant#f-ef",
                          anchor_iri="https://w3id.org/semanticarts/ns/ontology/gist/Magnitude",
                          confidence=0.9, rationale="EF is a cardiac magnitude",
                          suggester_iri="urn:iladub:suggester/fake")
    from iladub.ground import SurfaceConcept
    got = FakeGroundingProposer(p).propose_grounding(SurfaceConcept("EF", "55%", "r2"), ())
    assert got is p and got.field_iri.endswith("f-ef") and got.confidence == 0.9
```

- [ ] **Step 3: Run, verify fail**

Run: `./.venv/bin/python -m pytest tests/test_grounding.py -k grounding_proposer -q`
Expected: FAIL (`ModuleNotFoundError: iladub.propose_ground`).

- [ ] **Step 4: Implement `propose_ground.py`**

```python
"""propose_ground — the injected proposer seam for GenAI grounding (knowledge-first).

Mirrors iladub.etkl.propose: INJECTED so the pipeline is offline-testable (FakeGroundingProposer);
the live path (BamlGroundingProposer) is lazy + BAML_LIVE-gated.
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from typing import Protocol

from .ground import ContractField, SurfaceConcept


@dataclass(frozen=True)
class GroundingProposal:
    field_iri: str | None
    anchor_iri: str
    confidence: float
    rationale: str
    suggester_iri: str = "urn:iladub:suggester/baml.ProposeGrounding"


class GroundingProposer(Protocol):
    def propose_grounding(self, concept: SurfaceConcept,
                          fields: tuple[ContractField, ...]) -> "GroundingProposal": ...


@dataclass(frozen=True)
class FakeGroundingProposer:
    proposal: "GroundingProposal"

    def propose_grounding(self, concept, fields):
        return self.proposal


def baml_grounding_available() -> bool:
    return os.environ.get("BAML_LIVE") == "1" and importlib.util.find_spec("baml_client") is not None


class BamlGroundingProposer:
    def propose_grounding(self, concept, fields):
        from baml_client import sync_client
        labels = [f.fills_property.split("#")[-1] for f in fields]
        r = sync_client.b.ProposeGrounding(concept.text, concept.value, labels)
        # map the model's returned label back to a field IRI
        field_iri = None
        if r.field_iri:
            for f in fields:
                if f.fills_property.split("#")[-1] == r.field_iri or f.iri == r.field_iri:
                    field_iri = f.iri
                    break
        return GroundingProposal(field_iri=field_iri, anchor_iri=r.anchor_iri,
                                 confidence=r.confidence, rationale=r.rationale,
                                 suggester_iri="urn:iladub:suggester/baml.ProposeGrounding")
```

- [ ] **Step 5: Run, verify pass**

Run: `./.venv/bin/python -m pytest tests/test_grounding.py -k grounding_proposer -q`
Expected: 1 passed.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/propose_ground.py baml_src/ground_propose.baml tests/test_grounding.py
git commit -m "feat(iladub): GroundingProposer seam + ProposeGrounding BAML (grounding task 2)"
```

---

### Task 3: Dispose + emit — CandidateConcept → PromotionDecision → GroundedNode / quarantine

**Files:**
- Modify: `src/iladub/ground.py` (add emit + dispose + `ground_concept`)
- Test: `tests/test_grounding.py` (add)

**Interfaces:**
- Consumes: Task 1 (`Contract`, `exact_field`, `scheme_member`), Task 2 (`GroundingProposer`, `GroundingProposal`), `validate` (`src/iladub/validate.py`).
- Produces: `ground_concept(concept, contract, offer_uri, proposer, terms, contract_shapes, g) -> str` — appends triples to graph `g`; returns `"grounded"` or `"proposed"`.

**Design.** Every concept first emits an `iladub:CandidateConcept` (status=proposed, surfaceText/suggestedAnchor/suggestedBy/confidence/fromRegion). Then decide the field + suggester:
- **exact_field** hit → `field`, suggester = the exact-match rule agent (`urn:iladub:suggester/exact-match-rule`), confidence 1.0;
- else → `proposal = proposer.propose_grounding(...)`; `field` = the `ContractField` whose `iri == proposal.field_iri` (or None → novel).
Then **dispose** (`_admissible`): a field is admissible iff — for a scheme-bound field — `scheme_member(value, field.scheme, terms)` is not None (the sharp discriminator), AND the tentative offer triple conforms to the field's datatype in `contract_shapes` (validated per-field by targeting only that property). Novel (`field is None`) or inadmissible → leave the CandidateConcept `proposed` (quarantined), return `"proposed"`. Admissible → emit a `PromotionDecision` (reviews the candidate, `dec:decidedBy` the suggester, `dec:rationale`) that produces an `iladub:GroundedNode` (`groundsTo` the field property / scheme concept, `wasPromotedBy` the decision, status=asserted), and add the contract triple `offer_uri field.fills_property value` (a `Literal` for un-schemed, the scheme concept IRI for schemed). Return `"grounded"`.

- [ ] **Step 1: Write failing emit tests**

Add to `tests/test_grounding.py`:

```python
from rdflib import Graph, Namespace, URIRef, RDF
from iladub.ground import load_contract, ground_concept, SurfaceConcept
from iladub.propose_ground import GroundingProposal, FakeGroundingProposer

ILA = Namespace("https://w3id.org/iladub#")
TX = Namespace("https://example.org/transplant#")
OFFER = URIRef("urn:test:offer1")

def _shapes():
    return Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle")

def _noop_proposer():
    return FakeGroundingProposer(GroundingProposal(None, str(TX)+"x", 0.1, "n/a", "urn:iladub:suggester/fake"))

def test_exact_scheme_grounds_with_promotion():
    c = load_contract(CONTRACT); g = Graph()
    out = ground_concept(SurfaceConcept("ABO group", "A", "r1"), c, OFFER,
                         _noop_proposer(), _terms(), _shapes(), g)
    assert out == "grounded"
    gn = list(g.subjects(RDF.type, ILA.GroundedNode))
    assert gn and g.value(gn[0], ILA.wasPromotedBy) is not None
    assert g.value(gn[0], ILA.status) == ILA.asserted
    assert (OFFER, TX.aboGroup, None) not in [(OFFER, TX.aboGroup, None)] or True  # offer carries aboGroup
    assert any(True for _ in g.objects(OFFER, TX.aboGroup))

def test_wrong_scheme_mapping_quarantined():
    # proposer forces "55%" -> aboGroup (a scheme-bound field); scheme membership must reject it.
    c = load_contract(CONTRACT); g = Graph()
    abo = next(f for f in c.fields if f.fills_property.endswith("aboGroup"))
    p = FakeGroundingProposer(GroundingProposal(abo.iri, str(TX)+"x", 0.95, "looks like abo",
                                                "urn:iladub:suggester/fake"))
    out = ground_concept(SurfaceConcept("mystery", "55%", "r3"), c, OFFER, p, _terms(), _shapes(), g)
    assert out == "proposed"
    assert not list(g.subjects(RDF.type, ILA.GroundedNode))
    cc = list(g.subjects(RDF.type, ILA.CandidateConcept))
    assert cc and g.value(cc[0], ILA.status) == ILA.proposed

def test_novel_concept_quarantined():
    c = load_contract(CONTRACT); g = Graph()
    out = ground_concept(SurfaceConcept("smoking pack-years", "20", "r4"), c, OFFER,
                         _noop_proposer(), _terms(), _shapes(), g)
    assert out == "proposed"
    assert not list(g.subjects(RDF.type, ILA.GroundedNode))
```

- [ ] **Step 2: Run, verify fail**

Run: `./.venv/bin/python -m pytest tests/test_grounding.py -k "grounds_with_promotion or quarantined" -q`
Expected: FAIL (`ImportError: cannot import name 'ground_concept'`).

- [ ] **Step 3: Implement emit + dispose + `ground_concept` in `ground.py`**

Add imports at top of `ground.py`: `from decimal import Decimal` and `from rdflib import RDF, RDFS, BNode, Literal, URIRef`.

Key datatype rule (verified against `offer-shapes.ttl`): `tx:aboGroup` is `sh:datatype xsd:string`, so the **offer property value is always the string `Literal(concept.value)`** (never the scheme concept IRI); the scheme concept IRI goes on `iladub:groundsTo` (the grounding *target*), not on the contract property.

```python
ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")

_EXACT_RULE = "urn:iladub:suggester/exact-match-rule"
_GIST_CATEGORY = "https://w3id.org/semanticarts/ns/ontology/gist/Category"


def _emit_candidate(g, concept, anchor_iri, suggester_iri, confidence):
    cand = BNode()
    g.add((cand, RDF.type, ILADUB.CandidateConcept))
    g.add((cand, RDFS.label, Literal(concept.text)))
    g.add((cand, ILADUB.surfaceText, Literal(concept.value)))
    g.add((cand, ILADUB.suggestedAnchor, URIRef(anchor_iri)))
    agent = URIRef(suggester_iri)
    g.add((agent, RDF.type, ILADUB.Suggester))
    g.add((cand, ILADUB.suggestedBy, agent))
    g.add((cand, ILADUB.confidence, Literal(Decimal(str(round(confidence, 6))))))
    region = URIRef("urn:iladub:region:" + concept.region)
    g.add((region, RDF.type, ILADUB.SourceRegion))
    g.add((cand, ILADUB.fromRegion, region))
    g.add((cand, ILADUB.status, ILADUB.proposed))
    return cand, agent


def _grounds_to(concept, field, terms):
    """The contract oracle → the grounding TARGET for iladub:groundsTo, or None if REJECTED.

    Schemed field: the SKOS concept whose prefLabel == value (membership is the sharp
    discriminator — a value not in the scheme is rejected). Un-schemed field: the field's
    fills_property (admitted per-field; the whole-offer OrganOfferShape validates
    datatype/cardinality at close, Task 4)."""
    if field.scheme is not None:
        term = scheme_member(concept.value, field.scheme, terms)
        return URIRef(term) if term else None
    return URIRef(field.fills_property)


def _emit_grounded(g, concept, offer_uri, target_class, field, grounds_to, cand, agent, confidence, rationale):
    pd = BNode()
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, agent))
    g.add((pd, DEC.consideredEvidence, cand))
    g.add((pd, DEC.confidence, Literal(Decimal(str(round(confidence, 6))))))
    g.add((pd, DEC.rationale, Literal(rationale)))
    gn = BNode()
    g.add((gn, RDF.type, ILADUB.GroundedNode))
    g.add((gn, ILADUB.wasPromotedBy, pd))
    g.add((gn, ILADUB.groundsTo, grounds_to))
    g.add((gn, ILADUB.status, ILADUB.asserted))
    g.add((pd, DEC.produced, gn))
    # the contract instance: type once + the property value as a STRING literal (satisfies the shape)
    g.add((offer_uri, RDF.type, URIRef(target_class)))
    g.add((offer_uri, URIRef(field.fills_property), Literal(concept.value)))
    return gn


def ground_concept(concept, contract, offer_uri, proposer, terms, contract_shapes, g) -> str:
    field = exact_field(concept, contract)
    if field is not None:
        suggester, confidence, rationale, anchor = _EXACT_RULE, 1.0, "Exact contract-field match.", _GIST_CATEGORY
    else:
        prop = proposer.propose_grounding(concept, contract.fields)
        anchor, confidence, rationale, suggester = prop.anchor_iri, prop.confidence, prop.rationale, prop.suggester_iri
        field = next((f for f in contract.fields if f.iri == prop.field_iri), None) if prop.field_iri else None
    cand, agent = _emit_candidate(g, concept, anchor, suggester, confidence)
    if field is None:                                  # novel → quarantined proposition
        return "proposed"
    grounds_to = _grounds_to(concept, field, terms)    # the contract oracle
    if grounds_to is None:                             # rejected (e.g. value not in scheme) → stay proposed
        return "proposed"
    _emit_grounded(g, concept, offer_uri, contract.target_class, field, grounds_to, cand, agent, confidence, rationale)
    return "grounded"
```

`contract_shapes` is threaded through `ground_concept`'s signature (kept for interface stability and a future per-field datatype guard) but the sharp discrimination is `_grounds_to`'s scheme membership; whole-offer shape conformance is asserted at close (Task 4). The reviewer should confirm this split is sound (see self-review known-risk).

- [ ] **Step 4: Run, verify pass**

Run: `./.venv/bin/python -m pytest tests/test_grounding.py -k "grounds_with_promotion or quarantined" -q`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/ground.py tests/test_grounding.py
git commit -m "feat(iladub): dispose + emit (CandidateConcept->PromotionDecision->GroundedNode / quarantine) (grounding task 3)"
```

---

### Task 4: Soundness fix (quarantine unverifiable NEURAL) + end-to-end example + negatives (vertical close)

**Files:**
- Modify: `src/iladub/ground.py` (sharpen the dispose: NEURAL→non-scheme field quarantines)
- Modify: `tests/test_grounding.py` (the corrected end-to-end example + boundary + 3 negatives)

**Interfaces:**
- Consumes: `ground_concept` (Task 3), `validate` (`src/iladub/validate.py`), the shipped example TTLs.

**Why the fix (Task-3 review, Important):** `tx:ejectionFraction` carries no distinguishing constraint, so a NEURAL wrong-mapping to it would ground *and* survive the whole-offer SHACL close (a datatype cannot tell a valid EF number from a pack-years number). Sound rule: **ground only what the contract can verify** — an *exact* match (the label match is the oracle) or a *scheme-member* proposal (membership is the oracle); **every other NEURAL proposal quarantines**. This gives the previously-unused verification path its real gatekeeping job.

- [ ] **Step 1: Amend the dispose in `ground.py` (add `is_exact`; NEURAL→non-scheme → quarantine)**

Change `_grounds_to` to take `is_exact` and gate non-scheme fields on it:

```python
def _grounds_to(concept, field, terms, is_exact):
    """The grounding TARGET for iladub:groundsTo, or None if REJECTED (→ quarantine).

    Scheme-bound field: the SKOS concept whose prefLabel == value (membership is the oracle), else
    None. Non-scheme field: admitted ONLY for an EXACT label match (the exact match is the oracle);
    a NEURAL proposal to an unconstrained field has no oracle → None (quarantine). Grounding an
    unverifiable NEURAL guess would be confidence-as-validity (§7)."""
    if field.scheme is not None:
        term = scheme_member(concept.value, field.scheme, terms)
        return URIRef(term) if term else None
    return URIRef(field.fills_property) if is_exact else None
```

And thread `is_exact` through `ground_concept` (set `True` in the exact branch, `False` in the proposer branch), passing it to `_grounds_to`:

```python
def ground_concept(concept, contract, offer_uri, proposer, terms, contract_shapes, g) -> str:
    field = exact_field(concept, contract)
    if field is not None:
        suggester, confidence, rationale, anchor = _EXACT_RULE, 1.0, "Exact contract-field match.", _GIST_CATEGORY
        is_exact = True
    else:
        prop = proposer.propose_grounding(concept, contract.fields)
        anchor, confidence, rationale, suggester = prop.anchor_iri, prop.confidence, prop.rationale, prop.suggester_iri
        field = next((f for f in contract.fields if f.iri == prop.field_iri), None) if prop.field_iri else None
        is_exact = False
    cand, agent = _emit_candidate(g, concept, anchor, suggester, confidence)
    if field is None:                                       # novel → quarantined proposition
        return "proposed"
    grounds_to = _grounds_to(concept, field, terms, is_exact)   # the contract oracle
    if grounds_to is None:                                  # unverifiable / rejected → quarantine
        return "proposed"
    _emit_grounded(g, concept, offer_uri, contract.target_class, field, grounds_to, cand, agent, confidence, rationale)
    return "grounded"
```

- [ ] **Step 2: Write a failing boundary unit test (NEURAL→un-schemed field quarantines)**

Add to `tests/test_grounding.py`:

```python
def test_neural_to_unconstrained_field_quarantined():
    """A NEURAL proposal to ejectionFraction (no scheme, no distinguishing constraint) has no
    oracle → must quarantine, never ground (the soundness boundary)."""
    c = load_contract(CONTRACT); g = Graph()
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    p = FakeGroundingProposer(GroundingProposal(ef.iri, str(TX)+"Magnitude", 0.99, "looks like EF",
                                                "urn:iladub:suggester/fake"))
    out = ground_concept(SurfaceConcept("EF", "55", "r2"), c, OFFER, p, _terms(), _shapes(), g)
    assert out == "proposed"
    assert not list(g.subjects(RDF.type, ILA.GroundedNode))
```

- [ ] **Step 3: Run it — RED then GREEN**

Run: `./.venv/bin/python -m pytest tests/test_grounding.py -k unconstrained -q`
Expected: FAILS before Step 1's amendment is in place (would ground); PASSES after. (If Step 1 is already applied, it passes directly — confirm by temporarily reverting `is_exact` gating that it would otherwise ground.)

- [ ] **Step 4: Write the end-to-end example + conformance + negatives**

Add to `tests/test_grounding.py`. The conformant offer is `{organ, aboGroup}` (both scheme-bound); EF and novel quarantine:

```python
from iladub.validate import validate
from rdflib import BNode, Literal

def _epistemics_knowledge():
    g = Graph()
    for f in ["vocab/ontology/iladub.ttl", "vocab/ontology/dec.ttl"]:
        g.parse(f, format="turtle")
    return g

def _iladub_shapes():
    return Graph().parse("vocab/shapes/iladub-shapes.ttl", format="turtle")

def _build_offer():
    """organ (exact, scheme) + Blood type->aboGroup (NEURAL, scheme-verified) → a conformant offer;
    wrong "55%"->aboGroup (scheme-rejected), EF (NEURAL, unconstrained), novel → all quarantined."""
    c = load_contract(CONTRACT); terms = _terms(); shapes = _shapes(); g = Graph()
    abo = next(f for f in c.fields if f.fills_property.endswith("aboGroup"))
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    out = {}
    out["organ"] = ground_concept(SurfaceConcept("organ", "Heart", "r0"), c, OFFER, _noop_proposer(), terms, shapes, g)
    blood = FakeGroundingProposer(GroundingProposal(abo.iri, str(TX)+"Category", 0.8, "blood type is ABO", "urn:iladub:suggester/fake"))
    out["abo"]   = ground_concept(SurfaceConcept("Blood type", "A", "r1"), c, OFFER, blood, terms, shapes, g)
    wrong = FakeGroundingProposer(GroundingProposal(abo.iri, str(TX)+"x", 0.95, "guess", "urn:iladub:suggester/fake"))
    out["wrong"] = ground_concept(SurfaceConcept("mystery", "55%", "r3"), c, OFFER, wrong, terms, shapes, g)
    efp = FakeGroundingProposer(GroundingProposal(ef.iri, str(TX)+"Magnitude", 0.9, "cardiac EF", "urn:iladub:suggester/fake"))
    out["ef"]    = ground_concept(SurfaceConcept("EF", "55", "r2"), c, OFFER, efp, terms, shapes, g)
    out["novel"] = ground_concept(SurfaceConcept("smoking pack-years", "20", "r4"), c, OFFER, _noop_proposer(), terms, shapes, g)
    return g, out

def test_end_to_end_grounds_and_quarantines():
    g, out = _build_offer()
    assert out == {"organ": "grounded", "abo": "grounded",
                   "wrong": "proposed", "ef": "proposed", "novel": "proposed"}

def test_grounded_offer_conforms_to_contract_and_epistemics():
    g, _ = _build_offer()
    contract_know = Graph().parse(CONTRACT, format="turtle"); contract_know += _terms()
    r1 = validate(g, _shapes(), contract_know)          # organ + aboGroup satisfy OrganOfferShape
    assert r1.conforms, r1.report_text
    r2 = validate(g, _iladub_shapes(), _epistemics_knowledge())   # promotion invariant + no leak
    assert r2.conforms, r2.report_text

# --- negative tests: the epistemics/contract are real; these MUST fail validation ---

def test_neg_grounded_without_promotion_fails():
    g = Graph(); gn = BNode()
    g.add((gn, RDF.type, ILA.GroundedNode))
    g.add((gn, ILA.groundsTo, TX.aboGroup))
    g.add((gn, ILA.status, ILA.asserted))               # missing wasPromotedBy
    r = validate(g, _iladub_shapes(), _epistemics_knowledge())
    assert not r.conforms and "promotion" in r.report_text.lower()

def test_neg_proposition_asserted_fails():
    g = Graph(); cc = BNode()
    g.add((cc, RDF.type, ILA.CandidateConcept))
    g.add((cc, ILA.surfaceText, Literal("x")))
    g.add((cc, ILA.status, ILA.asserted))               # a proposition must not be asserted
    r = validate(g, _iladub_shapes(), _epistemics_knowledge())
    assert not r.conforms

def test_neg_wrong_mapping_asserted_fails_contract():
    # force a 2nd aboGroup INTO the grounded offer -> maxCount 1 violation (what dispose prevents)
    g, _ = _build_offer()
    g.add((OFFER, TX.aboGroup, Literal("55%")))
    contract_know = Graph().parse(CONTRACT, format="turtle"); contract_know += _terms()
    r = validate(g, _shapes(), contract_know)
    assert not r.conforms
```

- [ ] **Step 5: Run the grounding suite**

Run: `./.venv/bin/python -m pytest tests/test_grounding.py -q`
Expected: all pass (Task-1/2/3 tests + boundary + end-to-end + 3 negatives). If `test_grounded_offer_conforms…` fails, check the offer carries exactly one `tx:organ` and one `tx:aboGroup` (both string literals `"Heart"`/`"A"`); the concept IRIs live only on `groundsTo`. Adjust fixture values, not the shapes.

- [ ] **Step 6: Full suite (no regression)**

Run: `./.venv/bin/python -m pytest -q`
Expected: prior baseline (`400 passed, 5 skipped` after task 3) + the new grounding tests, zero failures.

- [ ] **Step 7: Commit**

```bash
git add src/iladub/ground.py tests/test_grounding.py
git commit -m "feat(iladub): quarantine unverifiable NEURAL groundings + end-to-end example + negatives (grounding task 4)"
```

---

## Self-Review (completed)

- **Spec coverage:** ground-or-propose decision → Task 1 (exact/scheme) + Task 2 (NEURAL propose); contract-scheme dispose → Task 3 (`_grounds_to`), whole-offer contract-shape conformance → Task 4; CandidateConcept→PromotionDecision→GroundedNode / quarantine → Task 3 (`_emit_candidate`/`_emit_grounded`); confidence-never-promotes → Task 3 (admission is scheme membership + close-time shape, not confidence); worked example (exact/semantic/wrong/novel) + conformance + 3 negatives → Task 4; offline `FakeGroundingProposer` + `BAML_LIVE` → Task 2. Scope boundary (no ET(K)L feed wiring) honored — the input is `SurfaceConcept`s.
- **Placeholder scan:** none. The offer property value is always a `Literal` (satisfies `aboGroup`'s `xsd:string`); the scheme concept IRI is on `groundsTo`, not the property.
- **Type consistency:** `SurfaceConcept(text,value,region)`, `ContractField(iri,fills_property,scheme)`, `Contract(target_class,fields)`, `GroundingProposal(field_iri,anchor_iri,confidence,rationale,suggester_iri)`, `ground_concept(concept,contract,offer_uri,proposer,terms,contract_shapes,g)->str`, `scheme_member(value,scheme_iri,terms)->str|None`, `_grounds_to(concept,field,terms)->URIRef|None` — used identically across tasks.
- **Known risk (flag for review):** `_grounds_to` for un-schemed fields (e.g. `ejectionFraction`) always admits (returns the property IRI) — no per-field datatype guard; the whole-offer `OrganOfferShape` validation at close (Task 4) enforces datatype/cardinality. This is intentional (per-field partial-offer validation would trip the min-count shape) but the reviewer should confirm it doesn't silently admit a wrong un-schemed grounding. The sharp discriminator (scheme membership) covers the scheme-bound fields, which is where the worked example proves rejection (`"55%"` as `aboGroup`).
