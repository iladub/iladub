# Compile → Federate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove a compiled `CleanDocumentHolon` federates — its projection becomes the provided terminology a second document grounds against — end-to-end from a real CSV.

**Architecture:** Anchor at the format-agnostic grounding seam. Doc A (a real CSV) → `readers` CSV adapter → `SurfaceConcept`s → the existing grounding portal → interior graph. A fixed SPARQL `CONSTRUCT` (`federate-projection.rq`) derives A's `etkl:DocumentProjection` (promoted concepts only, as a SKOS scheme). Doc B grounds against that projection through the **unchanged** portal (`scheme_member` consumes SKOS directly). A round-trip oracle (`federate.certify_federation`) certifies *soundness ∧ opacity ∧ containment*.

**Tech Stack:** Python 3.12, rdflib, pyshacl, pytest. SPARQL CONSTRUCT (`vocab/queries/*.rq`), SHACL (`vocab/shapes/*.ttl`), RDF Turtle vocab (`vocab/ontology/*.ttl`).

## Global Constraints

- **Neurosymbolic gate (hard):** projection derivation is **AXIOM** — a fixed SPARQL `CONSTRUCT` in `vocab/queries/`, open-world, evidence-positive (a concept is projected only when its promotion is *present*). The membrane is **SHACL** (closed-world). The oracle is **PROCEDURAL** engine glue (set comparison over graph results) — justified like `interpret.run`/`oracle.round_trip`: it carries **no** domain decision and **no** tuned constant. No procedural geometry, no tuned tolerance, no span/read/group heuristic.
- **Source ownership:** HGA terms (`hproj:`, `holon:`) appear ONLY as objects, ONLY in `*-hga-align.ttl` modules. `vocab/ontology/etkl.ttl` stays standalone (zero `w3id.org/holon` refs). `hfed:` (reserved in the spec) is **not** used or mirrored.
- **TDD / repo convention:** every shape ships a worked example that CONFORMS and a negative that MUST FAIL. Tests run under `pytest`.
- **Commands:** run tests with `. .venv/bin/activate && python3 -m pytest ...` (the binary is `python3`, not `python`).
- **Branch:** work continues on `iladub-compile-federate-spec`.

**Key existing signatures (do not change):**
- `iladub.ground.SurfaceConcept(text: str, value: str, region: str)` (frozen dataclass).
- `iladub.ground.load_contract(path: str) -> Contract` where `Contract(target_class: str, fields: tuple[ContractField, ...])` and `ContractField(iri, fills_property, scheme)`. Contract TTL uses `etkl:targetClass`, `etkl:hasField`, `etkl:fillsProperty`, `etkl:admissibleScheme`.
- `iladub.ground.ground_concept(concept, contract, offer_uri, proposer, terms, contract_shapes, g) -> str` returns `"grounded"` / `"proposed"`; on grounded it writes into `g`: a `iladub:GroundedNode` (BNode) with `iladub:wasPromotedBy <pd>`, `iladub:groundsTo <concept-iri>`, `iladub:status iladub:asserted`, and `<pd> a iladub:PromotionDecision`.
- `iladub.ground.scheme_member(value, scheme_iri, terms) -> str|None` — matches `?c skos:inScheme <scheme_iri> ; skos:prefLabel "value"` and returns `str(?c)`.
- `iladub.etkl.interpret.run(query_path, *graphs) -> rdflib.Graph`.
- `iladub.validate.validate(data, shapes, knowledge) -> ValidationResult(conforms: bool, report_text: str, report_graph)`.
- Test proposer (deterministic, no model): `from iladub.propose_ground import GroundingProposal, FakeGroundingProposer`; `FakeGroundingProposer(GroundingProposal(None, "urn:x", 0.1, "n/a", "urn:iladub:suggester/fake"))`. Exact/scheme grounding does not call the proposer.

**Fixed IRIs used throughout:**
- Projection scheme: `<urn:iladub:projection>` (typed `etkl:DocumentProjection`, and a `skos:ConceptScheme`).
- `etkl:` = `https://w3id.org/iladub/etkl#`, `iladub:` = `https://w3id.org/iladub#`, `skos:` = `http://www.w3.org/2004/02/skos/core#`, `hproj:` = `http://w3id.org/holon/projection/`.

---

### Task 1: `etkl:DocumentProjection` vocabulary + HGA alignment

**Files:**
- Modify: `vocab/ontology/etkl.ttl` (add the class, standalone)
- Modify: `vocab/ontology/iladub-hga-align.ttl` (add `hproj:` prefix + subclass axiom — this file already holds the `etkl:` holon alignments)
- Test: `tests/test_federation.py` (new)

**Interfaces:**
- Produces: the class IRI `etkl:DocumentProjection`; the alignment triple `etkl:DocumentProjection rdfs:subClassOf hproj:Projection`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_federation.py`:

```python
"""Compile→federate loop: a CleanDocumentHolon's projection becomes the next
document's provided terminology. See docs/superpowers/specs/2026-07-24-compile-federate-design.md."""
import os
from rdflib import Graph, Namespace, RDF, RDFS, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")

ETKL = Namespace("https://w3id.org/iladub/etkl#")
HPROJ = Namespace("http://w3id.org/holon/projection/")


def test_document_projection_class_declared():
    g = Graph().parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    assert (ETKL.DocumentProjection, RDF.type, OWL.Class) in g


def test_document_projection_aligns_to_hproj():
    g = Graph().parse(os.path.join(ONT, "iladub-hga-align.ttl"), format="turtle")
    assert (ETKL.DocumentProjection, RDFS.subClassOf, HPROJ.Projection) in g
```

- [ ] **Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_federation.py -q`
Expected: FAIL (both assertions — triples not present yet).

- [ ] **Step 3: Add the class to `vocab/ontology/etkl.ttl`**

Add near the other `etkl:` class declarations (standalone — no `holon:`/`hproj:`):

```turtle
etkl:DocumentProjection a owl:Class ;
    rdfs:label "Document projection"@en ;
    rdfs:comment "A clean document holon's outward-facing concept surface: the promoted grounded concepts it exposes for others to ground against (a SKOS scheme). The Projection aspect made concrete. A compiled holon that becomes a provided terminology for the next compile. Carries ONLY concepts — never the interior (regions, candidate concepts, promotion decisions)."@en .
```

- [ ] **Step 4: Add the alignment to `vocab/ontology/iladub-hga-align.ttl`**

Add the `hproj:` prefix at the top (after the existing `holon:` prefix line):

```turtle
@prefix hproj:  <http://w3id.org/holon/projection/> .
```

Add the axiom in the grounding/projection alignment section (HGA term as object only):

```turtle
#  A clean document holon's outward concept surface IS an HGA projection
#  (mirrors risk:RiskAssessment / tab:NormalizedBase ⊑ hproj:Projection).
etkl:DocumentProjection rdfs:subClassOf hproj:Projection .
```

- [ ] **Step 5: Run tests + source-ownership guard**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_federation.py tests/test_source_ownership.py -q`
Expected: PASS (federation vocab tests pass; source-ownership still green — `hproj:` appears only as an object in the align module).

- [ ] **Step 6: Commit**

```bash
git add vocab/ontology/etkl.ttl vocab/ontology/iladub-hga-align.ttl tests/test_federation.py
git commit -m "feat(etkl): etkl:DocumentProjection ⊑ hproj:Projection — the holon's outward concept surface"
```

---

### Task 2: `federate-projection.rq` — derive the projection (AXIOM)

**Files:**
- Create: `vocab/queries/federate-projection.rq`
- Create: `tests/federation-interior-a.ttl` (a tiny hand-authored A interior + terms fixture)
- Test: `tests/test_federation.py` (append)

**Interfaces:**
- Produces: a query file consumed by `interpret.run(query_path, interior, terms)` that yields a graph of `?c a skos:Concept ; skos:inScheme <urn:iladub:projection> ; skos:prefLabel ?label` for every promoted grounded concept, plus `<urn:iladub:projection> a etkl:DocumentProjection`.

- [ ] **Step 1: Write the fixture `tests/federation-interior-a.ttl`**

```turtle
@prefix iladub: <https://w3id.org/iladub#> .
@prefix skos:   <http://www.w3.org/2004/02/skos/core#> .
@prefix ex:     <https://example.org/demo#> .
@prefix tx:     <https://example.org/transplant#> .

#  A's interior: one PROMOTED grounded node (grounds to tx:ABO_O), plus interior-only
#  terms that MUST NOT appear in the projection. tx:ABO_O's public label lives in terms.
ex:gn1 a iladub:GroundedNode ; iladub:wasPromotedBy ex:pd1 ; iladub:groundsTo tx:ABO_O .
ex:pd1 a iladub:PromotionDecision .
ex:cand1 a iladub:CandidateConcept ; iladub:surfaceText "O" .
ex:region1 a iladub:SourceRegion .

#  Terms (the terminology A grounded into) supply the public prefLabel.
tx:ABO_O a skos:Concept ; skos:prefLabel "O" .
```

- [ ] **Step 2: Write the failing test (append to `tests/test_federation.py`)**

```python
from iladub.etkl import interpret

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
ILADUB = Namespace("https://w3id.org/iladub#")
TX = Namespace("https://example.org/transplant#")
PROJ = Namespace("urn:iladub:")
QUERIES = os.path.join(ROOT, "vocab", "queries")


def test_projection_construct_emits_only_promoted_concepts():
    interior = Graph().parse(os.path.join(ROOT, "tests", "federation-interior-a.ttl"), format="turtle")
    proj = interpret.run(os.path.join(QUERIES, "federate-projection.rq"), interior)
    # the promoted concept is projected, as SKOS, with its public label
    assert (TX.ABO_O, RDF.type, SKOS.Concept) in proj
    assert (TX.ABO_O, SKOS.prefLabel, None) in proj
    assert (TX.ABO_O, SKOS.inScheme, PROJ["projection"]) in proj
    # interior terms are OPAQUE — none leak into the projection
    for interior_type in (ILADUB.CandidateConcept, ILADUB.PromotionDecision, ILADUB.SourceRegion, ILADUB.GroundedNode):
        assert not any(proj.subjects(RDF.type, interior_type)), interior_type
```

Note: `interpret.run` unions its `*graphs`; here the interior fixture already carries the label, so one graph suffices. In the E2E task terms are passed as a second graph.

- [ ] **Step 3: Run test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_federation.py::test_projection_construct_emits_only_promoted_concepts -q`
Expected: FAIL ("No such file" — the `.rq` does not exist yet).

- [ ] **Step 4: Create `vocab/queries/federate-projection.rq`**

```sparql
PREFIX iladub: <https://w3id.org/iladub#>
PREFIX etkl:   <https://w3id.org/iladub/etkl#>
PREFIX skos:   <http://www.w3.org/2004/02/skos/core#>

#  AXIOM (open-world, evidence-positive): project a concept ONLY when a promotion
#  for it is PRESENT. Emit a SKOS scheme (what the grounding portal consumes) carrying
#  the concept's PUBLIC prefLabel — never the interior (regions, candidates, decisions).
CONSTRUCT {
  <urn:iladub:projection> a etkl:DocumentProjection , skos:ConceptScheme .
  ?concept a skos:Concept ;
           skos:inScheme <urn:iladub:projection> ;
           skos:prefLabel ?label .
}
WHERE {
  ?gn a iladub:GroundedNode ;
      iladub:wasPromotedBy ?pd ;
      iladub:groundsTo ?concept .
  ?pd a iladub:PromotionDecision .
  ?concept skos:prefLabel ?label .
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_federation.py::test_projection_construct_emits_only_promoted_concepts -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add vocab/queries/federate-projection.rq tests/federation-interior-a.ttl tests/test_federation.py
git commit -m "feat(etkl): federate-projection.rq — derive the DocumentProjection (promoted concepts only, AXIOM)"
```

---

### Task 3: `etkl:DocumentProjectionShape` — membrane opacity (SHACL)

**Files:**
- Modify: `vocab/shapes/etkl-shapes.ttl`
- Create: `examples/federation/projection-conformant.ttl`
- Create: `tests/federation-projection-leak.ttl`
- Test: `tests/test_federation.py` (append)

**Interfaces:**
- Produces: `etkl:DocumentProjectionShape` targeting `etkl:DocumentProjection`; a conformant projection and a leaky one for the example+negative convention.

- [ ] **Step 1: Write the conformant example `examples/federation/projection-conformant.ttl`**

```turtle
@prefix etkl: <https://w3id.org/iladub/etkl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix tx:   <https://example.org/transplant#> .

#  A well-formed projection: a scheme + concepts only. No interior terms.
<urn:iladub:projection> a etkl:DocumentProjection , skos:ConceptScheme .
tx:ABO_O a skos:Concept ; skos:inScheme <urn:iladub:projection> ; skos:prefLabel "O" .
```

- [ ] **Step 2: Write the negative `tests/federation-projection-leak.ttl`**

```turtle
@prefix etkl:   <https://w3id.org/iladub/etkl#> .
@prefix iladub: <https://w3id.org/iladub#> .
@prefix skos:   <http://www.w3.org/2004/02/skos/core#> .
@prefix tx:     <https://example.org/transplant#> .

#  MUST FAIL: the projection leaks an interior term (a PromotionDecision) —
#  the membrane did not hold.
<urn:iladub:projection> a etkl:DocumentProjection , skos:ConceptScheme .
tx:ABO_O a skos:Concept ; skos:inScheme <urn:iladub:projection> ; skos:prefLabel "O" .
tx:leaked-decision a iladub:PromotionDecision .
```

- [ ] **Step 3: Write the failing tests (append to `tests/test_federation.py`)**

```python
from iladub.validate import validate

SH_DIR = os.path.join(ROOT, "vocab", "shapes")


def _proj_shapes_knowledge():
    shapes = Graph().parse(os.path.join(SH_DIR, "etkl-shapes.ttl"), format="turtle")
    knowledge = Graph().parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    return shapes, knowledge


def test_conformant_projection_passes_shape():
    shapes, knowledge = _proj_shapes_knowledge()
    data = Graph().parse(os.path.join(ROOT, "examples", "federation", "projection-conformant.ttl"), format="turtle")
    assert validate(data, shapes, knowledge).conforms


def test_leaky_projection_fails_shape():
    shapes, knowledge = _proj_shapes_knowledge()
    data = Graph().parse(os.path.join(ROOT, "tests", "federation-projection-leak.ttl"), format="turtle")
    assert not validate(data, shapes, knowledge).conforms
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_federation.py::test_conformant_projection_passes_shape tests/test_federation.py::test_leaky_projection_fails_shape -q`
Expected: `test_leaky_...` currently PASSES-as-conforms (no shape yet) so the assertion `not conforms` FAILS. Both are red until the shape exists.

- [ ] **Step 5: Add the shape to `vocab/shapes/etkl-shapes.ttl`**

```turtle
#################################################################
#  Membrane opacity: a document projection may carry ONLY concepts —
#  never an interior term (candidate concept / promotion decision /
#  source region). The interior stays inside the holon.
#################################################################

etkl:prefixes-fed
    sh:declare [ sh:prefix "iladub" ; sh:namespace "https://w3id.org/iladub#"^^xsd:anyURI ] .

etkl:DocumentProjectionShape a sh:NodeShape ;
    sh:targetClass etkl:DocumentProjection ;
    sh:sparql [
        sh:message "A document projection must carry only concepts — an interior term (CandidateConcept / PromotionDecision / SourceRegion) leaked across the membrane." ;
        sh:prefixes etkl:prefixes-fed ;
        sh:select """
            SELECT $this WHERE {
                { ?x a iladub:CandidateConcept } UNION
                { ?x a iladub:PromotionDecision } UNION
                { ?x a iladub:SourceRegion }
            }
        """ ;
    ] .
```

Check the top of `vocab/shapes/etkl-shapes.ttl` for the prefixes `etkl:`, `sh:`, `xsd:` — add any missing (`@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .`).

- [ ] **Step 6: Run tests to verify they pass**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_federation.py::test_conformant_projection_passes_shape tests/test_federation.py::test_leaky_projection_fails_shape -q`
Expected: PASS (conformant conforms; leaky fails).

- [ ] **Step 7: Commit**

```bash
git add vocab/shapes/etkl-shapes.ttl examples/federation/projection-conformant.ttl tests/federation-projection-leak.ttl tests/test_federation.py
git commit -m "feat(etkl): etkl:DocumentProjectionShape — projection carries only concepts (membrane opacity)"
```

---

### Task 4: CSV → `SurfaceConcept` adapter (format layer)

**Files:**
- Modify: `src/iladub/readers.py`
- Create: `examples/federation/doc-a.csv`
- Test: `tests/test_federation.py` (append)

**Interfaces:**
- Produces: `iladub.readers.read_csv_surface_concepts(path: str) -> list[SurfaceConcept]` — one `SurfaceConcept(text=header, value=cell, region="row{r}:col{header}")` per data cell (header row names the concept; each data row supplies a value).

- [ ] **Step 1: Write the fixture `examples/federation/doc-a.csv`**

```csv
aboGroup,organ
O,heart
```

- [ ] **Step 2: Write the failing test (append)**

```python
from iladub.readers import read_csv_surface_concepts
from iladub.ground import SurfaceConcept


def test_csv_adapter_yields_surface_concepts():
    concepts = read_csv_surface_concepts(os.path.join(ROOT, "examples", "federation", "doc-a.csv"))
    assert SurfaceConcept(text="aboGroup", value="O", region="row1:col-aboGroup") in concepts
    assert SurfaceConcept(text="organ", value="heart", region="row1:col-organ") in concepts
    assert len(concepts) == 2
```

- [ ] **Step 3: Run test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_federation.py::test_csv_adapter_yields_surface_concepts -q`
Expected: FAIL (`ImportError: cannot import name 'read_csv_surface_concepts'`).

- [ ] **Step 4: Add the adapter to `src/iladub/readers.py`**

```python
import csv as _csv

from .ground import SurfaceConcept


def read_csv_surface_concepts(path: str) -> list[SurfaceConcept]:
    """Format adapter: a CSV's header row names the concepts; each data cell is a value.
    Returns region-anchored SurfaceConcepts. Deterministic — no model calls. This is the
    format-coupled boundary; the grounding portal downstream is format-agnostic."""
    out: list[SurfaceConcept] = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = _csv.DictReader(fh)
        for r, row in enumerate(reader, start=1):
            for header, cell in row.items():
                out.append(SurfaceConcept(text=header, value=cell,
                                          region="row%d:col-%s" % (r, header)))
    return out
```

If `readers.py` imports would create a cycle with `ground`, keep the `from .ground import SurfaceConcept` inside the function body.

- [ ] **Step 5: Run test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_federation.py::test_csv_adapter_yields_surface_concepts -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/readers.py examples/federation/doc-a.csv tests/test_federation.py
git commit -m "feat(readers): CSV → SurfaceConcept adapter (the format-coupled boundary)"
```

---

### Task 5: `federate.py` — `compile_document` + `derive_projection`

**Files:**
- Create: `src/iladub/etkl/federate.py`
- Test: `tests/test_federation.py` (append)

**Interfaces:**
- Consumes: `ground.ground_concept`, `interpret.run`, `federate-projection.rq`.
- Produces:
  - `federate.compile_document(concepts, contract, doc_uri, proposer, terms, contract_shapes) -> rdflib.Graph` — runs the grounding portal over every concept, returns the interior graph.
  - `federate.derive_projection(interior, terms) -> rdflib.Graph` — runs `federate-projection.rq` over `interior ∪ terms`.

- [ ] **Step 1: Write the failing test (append)**

```python
from iladub.etkl import federate
from iladub.ground import load_contract
from iladub.propose_ground import GroundingProposal, FakeGroundingProposer
from rdflib import URIRef

def _noop_proposer():
    return FakeGroundingProposer(GroundingProposal(None, "urn:x", 0.1, "n/a", "urn:iladub:suggester/fake"))


def test_compile_then_derive_projection():
    # minimal A: contract + terms + one concept "aboGroup"="O" grounding to tx:ABO_O
    contract = load_contract(os.path.join(ROOT, "examples", "federation", "doc-a-contract.ttl"))
    shapes = Graph().parse(os.path.join(ROOT, "examples", "federation", "doc-a-shapes.ttl"), format="turtle")
    terms = Graph().parse(os.path.join(ROOT, "examples", "federation", "terms.ttl"), format="turtle")
    concepts = [SurfaceConcept(text="aboGroup", value="O", region="row1:col-aboGroup")]
    interior = federate.compile_document(concepts, contract, URIRef("urn:doc:a"),
                                         _noop_proposer(), terms, shapes)
    assert any(interior.subjects(RDF.type, ILADUB.GroundedNode))
    proj = federate.derive_projection(interior, terms)
    assert (TX.ABO_O, SKOS.inScheme, PROJ["projection"]) in proj
```

This test consumes fixtures created in Task 7 (`doc-a-contract.ttl`, `doc-a-shapes.ttl`, `terms.ttl`). If executing tasks strictly in order, create those three fixtures now from the Task 7 listings (they are shared); Task 7 only adds the B-side and CSVs. (Noted so an out-of-order reader isn't blocked.)

- [ ] **Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_federation.py::test_compile_then_derive_projection -q`
Expected: FAIL (`ModuleNotFoundError: iladub.etkl.federate`).

- [ ] **Step 3: Create `src/iladub/etkl/federate.py`**

```python
"""federate — the compile→federate loop (loop F).

A compiled CleanDocumentHolon's projection becomes the provided terminology the next
document grounds against. Projection derivation is AXIOM (federate-projection.rq); this
module is PROCEDURAL engine glue — it drives the grounding portal and the CONSTRUCT and
compares result sets. It carries NO domain decision and NO tuned constant.
See docs/superpowers/specs/2026-07-24-compile-federate-design.md.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from rdflib import Graph, Namespace, RDF

from .. import ground
from . import interpret

ILADUB = Namespace("https://w3id.org/iladub#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
_QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries")


def compile_document(concepts, contract, doc_uri, proposer, terms, contract_shapes) -> Graph:
    """Run the grounding portal over every surface concept; return the interior graph."""
    g = Graph()
    for c in concepts:
        ground.ground_concept(c, contract, doc_uri, proposer, terms, contract_shapes, g)
    return g


def derive_projection(interior: Graph, terms: Graph) -> Graph:
    """AXIOM: run federate-projection.rq over interior ∪ terms → the DocumentProjection."""
    return interpret.run(os.path.join(_QUERIES, "federate-projection.rq"), interior, terms)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_federation.py::test_compile_then_derive_projection -q`
Expected: PASS (requires the Task 7 shared fixtures to exist — create them per the note in Step 1).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/federate.py tests/test_federation.py examples/federation/doc-a-contract.ttl examples/federation/doc-a-shapes.ttl examples/federation/terms.ttl
git commit -m "feat(etkl): federate.compile_document + derive_projection"
```

---

### Task 6: `federate.certify_federation` — the round-trip oracle

**Files:**
- Modify: `src/iladub/etkl/federate.py`
- Test: `tests/test_federation.py` (append)

**Interfaces:**
- Consumes: an A interior graph, an A projection graph, a B graph.
- Produces:
  - `federate.FederationVerdict(ok: bool, unsound: tuple, leaked: tuple, uncontained: tuple)` (frozen).
  - `federate.certify_federation(a_interior, a_projection, b_graph) -> FederationVerdict`.

- [ ] **Step 1: Write the failing tests (append)**

```python
def _promoted_concepts(interior):
    return {str(o) for s, o in interior.subject_objects(ILADUB.groundsTo)
            if (s, ILADUB.wasPromotedBy, None) in interior}


def test_oracle_passes_on_faithful_federation():
    interior = Graph().parse(os.path.join(ROOT, "tests", "federation-interior-a.ttl"), format="turtle")
    proj = interpret.run(os.path.join(QUERIES, "federate-projection.rq"), interior)
    # B grounded to tx:ABO_O, which IS in the projection
    b = Graph()
    b.add((URIRef("urn:doc:b#gn"), RDF.type, ILADUB.GroundedNode))
    b.add((URIRef("urn:doc:b#gn"), ILADUB.groundsTo, TX.ABO_O))
    v = federate.certify_federation(interior, proj, b)
    assert v.ok, v


def test_oracle_fails_when_projection_unsound():
    # a projection concept with no promoted grounded node behind it
    interior = Graph().parse(os.path.join(ROOT, "tests", "federation-interior-a.ttl"), format="turtle")
    proj = interpret.run(os.path.join(QUERIES, "federate-projection.rq"), interior)
    proj.add((TX.FABRICATED, RDF.type, SKOS.Concept))
    proj.add((TX.FABRICATED, SKOS.inScheme, PROJ["projection"]))
    v = federate.certify_federation(interior, proj, Graph())
    assert not v.ok and v.unsound


def test_oracle_fails_when_b_uncontained():
    # B's only terminology in this loop is A's projection, so B must ground ONLY to
    # projected concepts. A target outside the projection is a containment breach.
    interior = Graph().parse(os.path.join(ROOT, "tests", "federation-interior-a.ttl"), format="turtle")
    proj = interpret.run(os.path.join(QUERIES, "federate-projection.rq"), interior)
    b = Graph()
    b.add((URIRef("urn:doc:b#gn"), RDF.type, ILADUB.GroundedNode))
    b.add((URIRef("urn:doc:b#gn"), ILADUB.groundsTo, TX.OUTSIDE))  # not in the projection
    v = federate.certify_federation(interior, proj, b)
    assert not v.ok and v.uncontained
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_federation.py -k oracle -q`
Expected: FAIL (`AttributeError: module ... has no attribute 'certify_federation'`).

- [ ] **Step 3: Add the oracle to `src/iladub/etkl/federate.py`**

```python
@dataclass(frozen=True)
class FederationVerdict:
    ok: bool
    unsound: tuple      # projection concepts with no promoted grounded node behind them
    leaked: tuple       # interior-class instances found in the projection (opacity breach)
    uncontained: tuple  # concepts B grounded to that A never projected


def _projection_concepts(projection: Graph) -> set:
    return {str(s) for s in projection.subjects(RDF.type, SKOS.Concept)}


def _promoted_targets(interior: Graph) -> set:
    return {str(o) for s, o in interior.subject_objects(ILADUB.groundsTo)
            if (s, ILADUB.wasPromotedBy, None) in interior}


def _interior_leaks(projection: Graph) -> set:
    leaks = set()
    for cls in (ILADUB.CandidateConcept, ILADUB.PromotionDecision, ILADUB.SourceRegion):
        leaks |= {str(s) for s in projection.subjects(RDF.type, cls)}
    return leaks


def certify_federation(a_interior: Graph, a_projection: Graph, b_graph: Graph) -> FederationVerdict:
    """Certify: projection ⊆ promoted interior (sound) ∧ projection carries no interior term
    (opaque) ∧ every concept B grounded to is in the projection (contained)."""
    proj_concepts = _projection_concepts(a_projection)
    promoted = _promoted_targets(a_interior)

    unsound = tuple(sorted(proj_concepts - promoted))
    leaked = tuple(sorted(_interior_leaks(a_projection)))

    # Containment: B's ONLY terminology in this loop is A's projection, so every concept
    # B grounded to must be in the projection's concept set.
    b_targets = {str(o) for s, o in b_graph.subject_objects(ILADUB.groundsTo)}
    uncontained = tuple(sorted(b_targets - proj_concepts))

    ok = not (unsound or leaked or uncontained)
    return FederationVerdict(ok=ok, unsound=unsound, leaked=leaked, uncontained=uncontained)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_federation.py -k oracle -q`
Expected: PASS (faithful → ok; fabricated concept → `unsound`; B target outside projection → `uncontained`).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/federate.py tests/test_federation.py
git commit -m "feat(etkl): federate.certify_federation — round-trip oracle (sound ∧ opaque ∧ contained)"
```

---

### Task 7: End-to-end demonstrator — a real CSV federates to a second CSV

**Files:**
- Create: `examples/federation/terms.ttl`, `doc-a-contract.ttl`, `doc-a-shapes.ttl`, `doc-b-contract.ttl`, `doc-b-shapes.ttl`, `doc-b.csv` (`doc-a.csv` exists from Task 4)
- Test: `tests/test_federation.py` (append the E2E test)

**Interfaces:**
- Consumes everything above. Produces the closing proof: real doc → compile → project → second doc grounds against projection → oracle ok.

- [ ] **Step 1: Write the shared terminology `examples/federation/terms.ttl`**

```turtle
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix tx:   <https://example.org/transplant#> .

#  A's provided terminology (synthetic, domain-neutral health example).
tx:scheme-abo a skos:ConceptScheme .
tx:ABO_O a skos:Concept ; skos:inScheme tx:scheme-abo ; skos:prefLabel "O" .
tx:ABO_A a skos:Concept ; skos:inScheme tx:scheme-abo ; skos:prefLabel "A" .
```

- [ ] **Step 2: Write A's contract + shapes**

`examples/federation/doc-a-contract.ttl`:

```turtle
@prefix etkl: <https://w3id.org/iladub/etkl#> .
@prefix tx:   <https://example.org/transplant#> .

tx:contract-a a etkl:Contract ;
    etkl:targetClass tx:Offer ;
    etkl:hasField tx:field-abo .
tx:field-abo etkl:fillsProperty tx:aboGroup ; etkl:admissibleScheme tx:scheme-abo .
```

`examples/federation/doc-a-shapes.ttl`:

```turtle
@prefix sh:  <http://www.w3.org/ns/shacl#> .
@prefix tx:  <https://example.org/transplant#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

tx:OfferShape a sh:NodeShape ; sh:targetClass tx:Offer ;
    sh:property [ sh:path tx:aboGroup ; sh:maxCount 1 ] .
```

- [ ] **Step 3: Write B's contract, shapes, and `doc-b.csv`**

`examples/federation/doc-b-contract.ttl` — note `admissibleScheme` is **A's projection scheme**:

```turtle
@prefix etkl: <https://w3id.org/iladub/etkl#> .
@prefix tx:   <https://example.org/transplant#> .

tx:contract-b a etkl:Contract ;
    etkl:targetClass tx:Referral ;
    etkl:hasField tx:field-donorAbo .
tx:field-donorAbo etkl:fillsProperty tx:donorAbo ; etkl:admissibleScheme <urn:iladub:projection> .
```

`examples/federation/doc-b-shapes.ttl`:

```turtle
@prefix sh:  <http://www.w3.org/ns/shacl#> .
@prefix tx:  <https://example.org/transplant#> .

tx:ReferralShape a sh:NodeShape ; sh:targetClass tx:Referral ;
    sh:property [ sh:path tx:donorAbo ; sh:maxCount 1 ] .
```

`examples/federation/doc-b.csv` — the header normalises to `donorAbo` (matches `tx:donorAbo`), value `O` is a projected concept's prefLabel:

```csv
donorAbo
O
```

- [ ] **Step 4: Write the failing E2E test (append)**

```python
def test_e2e_compile_federate_loop():
    # --- A compiles from a real CSV (deterministic exact+scheme grounding, no model) ---
    a_contract = load_contract(os.path.join(ROOT, "examples", "federation", "doc-a-contract.ttl"))
    a_shapes = Graph().parse(os.path.join(ROOT, "examples", "federation", "doc-a-shapes.ttl"), format="turtle")
    terms = Graph().parse(os.path.join(ROOT, "examples", "federation", "terms.ttl"), format="turtle")
    a_concepts = read_csv_surface_concepts(os.path.join(ROOT, "examples", "federation", "doc-a.csv"))
    a_interior = federate.compile_document(a_concepts, a_contract, URIRef("urn:doc:a"),
                                           _noop_proposer(), terms, a_shapes)
    assert any(a_interior.subjects(RDF.type, ILADUB.GroundedNode))

    # --- derive A's projection ---
    projection = federate.derive_projection(a_interior, terms)
    assert (TX.ABO_O, SKOS.inScheme, PROJ["projection"]) in projection

    # --- B grounds against A's PROJECTION as its provided terminology (portal unchanged) ---
    b_contract = load_contract(os.path.join(ROOT, "examples", "federation", "doc-b-contract.ttl"))
    b_shapes = Graph().parse(os.path.join(ROOT, "examples", "federation", "doc-b-shapes.ttl"), format="turtle")
    b_concepts = read_csv_surface_concepts(os.path.join(ROOT, "examples", "federation", "doc-b.csv"))
    b_interior = federate.compile_document(b_concepts, b_contract, URIRef("urn:doc:b"),
                                           _noop_proposer(), projection, b_shapes)
    # B resolved its value against A's projected concept
    assert (None, ILADUB.groundsTo, TX.ABO_O) in b_interior

    # --- the oracle certifies the federation ---
    verdict = federate.certify_federation(a_interior, projection, b_interior)
    assert verdict.ok, verdict
```

- [ ] **Step 5: Run the E2E test to verify it fails, then passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_federation.py::test_e2e_compile_federate_loop -q`
Expected: FAIL first if any fixture is missing; once all Step 1–3 fixtures exist, PASS. If B does not ground (`groundsTo tx:ABO_O` absent), check: `doc-b.csv` header normalises to the `tx:donorAbo` local name, the value `O` equals `tx:ABO_O`'s `skos:prefLabel`, and B's `admissibleScheme` is `<urn:iladub:projection>`.

- [ ] **Step 6: Run the FULL suite (nothing regressed)**

Run: `. .venv/bin/activate && python3 -m pytest -q`
Expected: all pass (prior 498 + the new federation tests), 5 skipped.

- [ ] **Step 7: Commit**

```bash
git add examples/federation/ tests/test_federation.py
git commit -m "test(etkl): end-to-end compile→federate — a real CSV's projection grounds a second CSV"
```

---

## Self-Review

**Spec coverage:**
- §1 purpose / SemanticHolon⇄CleanDocumentHolon symmetry → Tasks 5–7 (compile, project, B grounds against projection).
- §2 data flow / format-agnostic seam → Task 4 (CSV adapter is the only format-coupled part) + Task 5.
- §3.2 projection CONSTRUCT (promoted-only, public label) → Task 2.
- §3.4 oracle (sound ∧ opaque ∧ contained) → Task 6.
- §3.5 vocab (`etkl:DocumentProjection` ⊑ `hproj:Projection`) → Task 1; shape → Task 3.
- §4 demonstrator + conformance + two negatives → Tasks 3 (leaky projection) + 6 (unsound, uncontained) + 7 (E2E).
- §5 gate compliance → CONSTRUCT is AXIOM (Task 2), SHACL membrane (Task 3), oracle is documented PROCEDURAL glue with no tuned constant (Task 6).
- §6 source-ownership → Task 1 puts `hproj:` only as an object in the align module; `test_source_ownership` run in Task 1 Step 5. `hfed:` never used.

**Placeholder scan:** no TBD/TODO; every code/query/fixture step shows full content.

**Type consistency:** `SurfaceConcept(text, value, region)`, `ground_concept(...)->str`, `interpret.run(path,*graphs)`, `validate(...).conforms`, `FederationVerdict(ok, unsound, leaked, uncontained)`, `certify_federation(a_interior, a_projection, b_graph)`, `compile_document(concepts, contract, doc_uri, proposer, terms, contract_shapes)`, `derive_projection(interior, terms)`, `read_csv_surface_concepts(path)` — used consistently across tasks. Fixed IRI `<urn:iladub:projection>` and scheme labels consistent between the `.rq`, the shape, and the fixtures.

**Cross-task fixture note:** Task 5 consumes the shared fixtures (`terms.ttl`, `doc-a-contract.ttl`, `doc-a-shapes.ttl`) that are fully listed in Task 7; the plan flags this in Task 5 Step 1 so an in-order implementer creates them when first needed.
