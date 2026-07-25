# Governed / ViewerPass Projection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the federation projection viewer-relative — derived per viewer under ODRL policy over concept sensitivity tags, so a consumer (or an AI agent acting for a user) grounds against exactly its entitled projection and can never reach more.

**Architecture:** Extend the shipped compile→federate loop. A new AXIOM CONSTRUCT (`federate-projection-governed.rq`) emits a concept for the recipe's viewer iff the concept is promoted AND an ODRL permission grants the viewer's resolved role read on the concept's `etkl:sensitivity` tag; role resolution — including AI-inherits-user — is the SPARQL property path `(prov:actedOnBehalfOf)?/etkl:hasRole`. `federate.py` gets `derive_governed_projection` + `certify_governed_federation` (adds a governance-soundness check to the existing sound∧opaque∧contained oracle).

**Tech Stack:** Python 3.12, rdflib, pyshacl, pytest. SPARQL CONSTRUCT (`vocab/queries/*.rq`), RDF Turtle vocab, SHACL, ODRL, PROV.

## Global Constraints

- **Neurosymbolic gate (hard):** the governed derivation is **AXIOM** — a fixed SPARQL CONSTRUCT, open-world, evidence-positive (emit a concept only when a *granting* permission is present). AI-inherits-user is a SPARQL property path, NOT procedural code. The membrane is **SHACL** (reuse `etkl:DocumentProjectionShape`, `gsh:AiInheritsUserShape`). The oracle is **PROCEDURAL** glue (set comparison over graph/SPARQL results) — no domain decision, no tuned constant. No Python answers "which concepts may this role see."
- **Source ownership:** new terms authored only in `etkl:`; `etkl.ttl` stays standalone (zero `w3id.org/holon`). HGA terms (`hview:`, `hproj:`, `hpol:`) appear ONLY as objects, ONLY in `*-hga-align.ttl`. `hfed:` (reserved) is **not** used.
- **TDD / repo convention:** a worked example that CONFORMS + a negative that MUST FAIL, per new behavior.
- **Commands:** run tests with `. .venv/bin/activate && python3 -m pytest ...` (binary is `python3`).
- **Branch:** work continues on `iladub-governed-viewerpass`.

**Key existing signatures (do not change):**
- `iladub.etkl.interpret.run(query_path, *graphs) -> rdflib.Graph` (unions its graphs).
- `iladub.etkl.federate.compile_document(concepts, contract, doc_uri, proposer, terms, contract_shapes) -> Graph`
- `iladub.etkl.federate.derive_projection(interior, terms) -> Graph`
- `iladub.etkl.federate.certify_federation(a_interior, a_projection, b_graph) -> FederationVerdict(ok, unsound, leaked, uncontained)`
- `iladub.ground.SurfaceConcept(text, value, region)`; `load_contract(path) -> Contract`; `ground_concept(concept, contract, offer_uri, proposer, terms, contract_shapes, g) -> str`; `scheme_member` matches `?c skos:inScheme <scheme> ; skos:prefLabel "value"`.
- `iladub.readers.read_csv_surface_concepts(path) -> list[SurfaceConcept]`
- `iladub.validate.validate(data, shapes, knowledge) -> ValidationResult(conforms, report_text, report_graph)`
- Test proposer: `from iladub.propose_ground import GroundingProposal, FakeGroundingProposer`.
- `federate.py` already imports: `RDF`, `dataclass`, `Namespace`, `Graph`, `URIRef` (as `URIRef`), `ILADUB`, `SKOS`, `interpret`, `ground`, `os`. (`_projection_concepts`, `_promoted_targets`, `_interior_leaks` helpers already defined.)

**Fixed IRIs / predicates:**
- Projection scheme: `<urn:iladub:projection>` (per derivation call = one viewer's projection graph).
- Recipe node: `<urn:federate:recipe>`; `etkl:forViewer` links it to the viewer.
- `etkl:` = `https://w3id.org/iladub/etkl#`, `iladub:` = `https://w3id.org/iladub#`, `skos:` = `http://www.w3.org/2004/02/skos/core#`, `odrl:` = `http://www.w3.org/ns/odrl/2/`, `prov:` = `http://www.w3.org/ns/prov#`, `hview:` = `http://w3id.org/holon/viewer/`.

---

### Task 1: Governance vocabulary — `etkl:sensitivity`, `etkl:hasRole`, `etkl:forViewer`

**Files:**
- Modify: `vocab/ontology/etkl.ttl` (add three properties, standalone)
- Modify: `vocab/ontology/iladub-hga-align.ttl` (add `hview:` prefix + one informative `seeAlso`)
- Test: `tests/test_governed_projection.py` (new)

**Interfaces:**
- Produces: `etkl:sensitivity`, `etkl:hasRole`, `etkl:forViewer` (all `owl:ObjectProperty`); alignment `etkl:hasRole rdfs:seeAlso hview:ViewerProfile`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_governed_projection.py`:

```python
"""Governed / ViewerPass projection: a viewer-relative federation projection derived
under ODRL policy over concept sensitivity tags. AI-inherits-user via a SPARQL property
path. See docs/superpowers/specs/2026-07-25-governed-viewerpass-projection-design.md."""
import os
from rdflib import Graph, Namespace, RDF, RDFS, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")

ETKL = Namespace("https://w3id.org/iladub/etkl#")
HVIEW = Namespace("http://w3id.org/holon/viewer/")


def test_governance_properties_declared():
    g = Graph().parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    for p in (ETKL.sensitivity, ETKL.hasRole, ETKL.forViewer):
        assert (p, RDF.type, OWL.ObjectProperty) in g, p


def test_hasrole_aligns_to_hview_viewerprofile():
    g = Graph().parse(os.path.join(ONT, "iladub-hga-align.ttl"), format="turtle")
    assert (ETKL.hasRole, RDFS.seeAlso, HVIEW.ViewerProfile) in g
```

- [ ] **Step 2: Run test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_governed_projection.py -q`
Expected: FAIL (triples not present).

- [ ] **Step 3: Add the three properties to `vocab/ontology/etkl.ttl`**

Add near the other `etkl:` property declarations (standalone — no `holon:`/`hview:`):

```turtle
etkl:sensitivity a owl:ObjectProperty ;
    rdfs:label "sensitivity"@en ;
    rdfs:comment "A declared sensitivity / compartment tag on a concept, used to govern which viewers a projection exposes it to. Supplied in a governance graph separate from the domain subject (sensitivity is not stamped on the subject). One categorical dimension; ABAC adds more."@en .

etkl:hasRole a owl:ObjectProperty ;
    rdfs:label "has role"@en ;
    rdfs:comment "The role a person or agent holds — the ViewerPass role handle a governed projection is scoped to. An AI agent inherits its user's role via prov:actedOnBehalfOf then etkl:hasRole."@en .

etkl:forViewer a owl:ObjectProperty ;
    rdfs:label "for viewer"@en ;
    rdfs:comment "A projection-derivation recipe's viewer (a role, person, or agent). The governed CONSTRUCT reads it to scope the projection to that viewer's entitlements."@en .
```

- [ ] **Step 4: Add the alignment to `vocab/ontology/iladub-hga-align.ttl`**

Add the `hview:` prefix near the other prefixes:

```turtle
@prefix hview:  <http://w3id.org/holon/viewer/> .
```

Add the informative alignment (HGA term as object only) in the grounding/projection alignment section:

```turtle
#  etkl:hasRole is the ViewerPass role handle — informatively related to HGA's
#  viewer profile (align, don't subclass; access rides odrl:/prov:).
etkl:hasRole rdfs:seeAlso hview:ViewerProfile .
```

- [ ] **Step 5: Run tests + source-ownership guard**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_governed_projection.py tests/test_source_ownership.py -q`
Expected: PASS (governance vocab tests pass; source-ownership green — `hview:` only as an object in the align module).

- [ ] **Step 6: Commit**

```bash
git add vocab/ontology/etkl.ttl vocab/ontology/iladub-hga-align.ttl tests/test_governed_projection.py
git commit -m "feat(etkl): governance vocab — etkl:sensitivity, etkl:hasRole, etkl:forViewer"
```

---

### Task 2: `federate-projection-governed.rq` — the governed derivation (AXIOM)

**Files:**
- Create: `vocab/queries/federate-projection-governed.rq`
- Create: `tests/federation-governed-interior.ttl` (interior + terms + governance + policy + roles fixture)
- Test: `tests/test_governed_projection.py` (append)

**Interfaces:**
- Consumes: `interpret.run(query_path, *graphs)`.
- Produces: a query that, given interior ∪ terms ∪ governance ∪ policy ∪ a recipe graph (`<urn:federate:recipe> etkl:forViewer <viewer>`), emits `?concept a skos:Concept ; skos:inScheme <urn:iladub:projection> ; skos:prefLabel ?label` for every promoted concept whose tag the viewer's resolved role is granted read on, plus `<urn:iladub:projection> a etkl:DocumentProjection , skos:ConceptScheme`.

- [ ] **Step 1: Write the fixture `tests/federation-governed-interior.ttl`**

```turtle
@prefix iladub: <https://w3id.org/iladub#> .
@prefix etkl:   <https://w3id.org/iladub/etkl#> .
@prefix skos:   <http://www.w3.org/2004/02/skos/core#> .
@prefix odrl:   <http://www.w3.org/ns/odrl/2/> .
@prefix prov:   <http://www.w3.org/ns/prov#> .
@prefix ex:     <https://example.org/demo#> .
@prefix tx:     <https://example.org/transplant#> .

#  --- interior: two PROMOTED concepts ---
ex:gn1 a iladub:GroundedNode ; iladub:wasPromotedBy ex:pd1 ; iladub:groundsTo tx:ABO_O .
ex:pd1 a iladub:PromotionDecision .
ex:gn2 a iladub:GroundedNode ; iladub:wasPromotedBy ex:pd2 ; iladub:groundsTo tx:DONOR_ID .
ex:pd2 a iladub:PromotionDecision .

#  --- terms: public labels ---
tx:ABO_O   a skos:Concept ; skos:prefLabel "O" .
tx:DONOR_ID a skos:Concept ; skos:prefLabel "ET-DONOR-2026-0091" .

#  --- governance: concept sensitivity tags (separate from the domain subject) ---
tx:ABO_O   etkl:sensitivity tx:clinical .
tx:DONOR_ID etkl:sensitivity tx:phi .

#  --- roles ---
tx:role-opo           etkl:hasRole tx:role-opo .            # a role is its own role handle
tx:role-recipient-ctr etkl:hasRole tx:role-recipient-ctr .

#  --- ODRL policy over TAGS ---
tx:policy a odrl:Policy ;
    odrl:permission
      [ odrl:action odrl:read ; odrl:assignee tx:role-opo ;           odrl:target tx:clinical ] ,
      [ odrl:action odrl:read ; odrl:assignee tx:role-opo ;           odrl:target tx:phi ] ,
      [ odrl:action odrl:read ; odrl:assignee tx:role-recipient-ctr ; odrl:target tx:clinical ] .
```

Note: a role's own `etkl:hasRole` pointing to itself lets the `(prov:actedOnBehalfOf)?/etkl:hasRole` path resolve a bare-role viewer to itself. Person/agent viewers are added in Task 4.

- [ ] **Step 2: Write the failing test (append to `tests/test_governed_projection.py`)**

```python
from iladub.etkl import interpret
from rdflib import URIRef

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
ILADUB = Namespace("https://w3id.org/iladub#")
TX = Namespace("https://example.org/transplant#")
PROJ = Namespace("urn:iladub:")
RECIPE = URIRef("urn:federate:recipe")
QUERIES = os.path.join(ROOT, "vocab", "queries")
GOV_INTERIOR = os.path.join(ROOT, "tests", "federation-governed-interior.ttl")


def _run_governed(viewer):
    data = Graph().parse(GOV_INTERIOR, format="turtle")
    recipe = Graph()
    recipe.add((RECIPE, ETKL.forViewer, viewer))
    return interpret.run(os.path.join(QUERIES, "federate-projection-governed.rq"), data, recipe)


def test_governed_opo_sees_phi_and_clinical():
    proj = _run_governed(TX["role-opo"])
    assert (TX.ABO_O, SKOS.inScheme, PROJ["projection"]) in proj      # clinical
    assert (TX.DONOR_ID, SKOS.inScheme, PROJ["projection"]) in proj   # phi


def test_governed_recipient_sees_clinical_only():
    proj = _run_governed(TX["role-recipient-ctr"])
    assert (TX.ABO_O, SKOS.inScheme, PROJ["projection"]) in proj              # clinical granted
    assert (TX.DONOR_ID, SKOS.inScheme, PROJ["projection"]) not in proj       # phi WITHHELD (not granted)
    assert not any(proj.subjects(RDF.type, ILADUB.PromotionDecision))         # interior opaque
```

- [ ] **Step 3: Run test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_governed_projection.py -k governed_ -q`
Expected: FAIL ("No such file" — the `.rq` does not exist).

- [ ] **Step 4: Create `vocab/queries/federate-projection-governed.rq`**

```sparql
PREFIX iladub: <https://w3id.org/iladub#>
PREFIX etkl:   <https://w3id.org/iladub/etkl#>
PREFIX skos:   <http://www.w3.org/2004/02/skos/core#>
PREFIX odrl:   <http://www.w3.org/ns/odrl/2/>
PREFIX prov:   <http://www.w3.org/ns/prov#>

#  AXIOM (open-world, evidence-positive): project a concept for the recipe's viewer ONLY
#  when (a) it is promoted, and (b) an ODRL permission grants the viewer's resolved role
#  read on the concept's sensitivity tag. The viewer→role resolution — including
#  AI-inherits-user — is the property path (prov:actedOnBehalfOf)?/etkl:hasRole.
#  A concept with no matching grant is withheld by omission, never filtered out.
CONSTRUCT {
  <urn:iladub:projection> a etkl:DocumentProjection , skos:ConceptScheme .
  ?concept a skos:Concept ;
           skos:inScheme <urn:iladub:projection> ;
           skos:prefLabel ?label .
}
WHERE {
  <urn:federate:recipe> etkl:forViewer ?viewer .
  ?viewer (prov:actedOnBehalfOf)?/etkl:hasRole ?role .

  ?gn a iladub:GroundedNode ;
      iladub:wasPromotedBy ?pd ;
      iladub:groundsTo ?concept .
  ?pd a iladub:PromotionDecision .
  ?concept skos:prefLabel ?label .
  ?concept etkl:sensitivity ?tag .

  ?perm odrl:action odrl:read ;
        odrl:assignee ?role ;
        odrl:target ?tag .
}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_governed_projection.py -k governed_ -q`
Expected: PASS (OPO sees both; recipient sees clinical only, PHI withheld, no interior leak).

- [ ] **Step 6: Commit**

```bash
git add vocab/queries/federate-projection-governed.rq tests/federation-governed-interior.ttl tests/test_governed_projection.py
git commit -m "feat(etkl): federate-projection-governed.rq — viewer-relative projection under ODRL tag policy (AXIOM)"
```

---

### Task 3: `federate.derive_governed_projection` + `certify_governed_federation`

**Files:**
- Modify: `src/iladub/etkl/federate.py`
- Test: `tests/test_governed_projection.py` (append)

**Interfaces:**
- Consumes: `interpret.run`, `certify_federation`, `federate-projection-governed.rq`.
- Produces:
  - `federate.derive_governed_projection(interior, terms, governance, policy, viewer) -> Graph`
  - `federate.GovernedVerdict(ok, unsound, leaked, uncontained, ungranted)` (frozen)
  - `federate.certify_governed_federation(interior, governance, policy, viewer, projection, consumer_graph) -> GovernedVerdict`

- [ ] **Step 1: Write the failing test (append)**

```python
from iladub.etkl import federate


def test_derive_governed_projection_scopes_to_viewer():
    data = Graph().parse(GOV_INTERIOR, format="turtle")
    # split the single fixture into the argument graphs the function expects
    proj = federate.derive_governed_projection(data, data, data, data, TX["role-recipient-ctr"])
    assert (TX.ABO_O, SKOS.inScheme, PROJ["projection"]) in proj
    assert (TX.DONOR_ID, SKOS.inScheme, PROJ["projection"]) not in proj


def test_certify_governed_ok_when_faithful():
    data = Graph().parse(GOV_INTERIOR, format="turtle")
    proj = federate.derive_governed_projection(data, data, data, data, TX["role-recipient-ctr"])
    consumer = Graph()
    consumer.add((URIRef("urn:c#gn"), RDF.type, ILADUB.GroundedNode))
    consumer.add((URIRef("urn:c#gn"), ILADUB.groundsTo, TX.ABO_O))  # grounded within entitlement
    v = federate.certify_governed_federation(data, data, data, TX["role-recipient-ctr"], proj, consumer)
    assert v.ok, v


def test_certify_governed_flags_ungranted_leak_in_projection():
    data = Graph().parse(GOV_INTERIOR, format="turtle")
    proj = federate.derive_governed_projection(data, data, data, data, TX["role-recipient-ctr"])
    proj.add((TX.DONOR_ID, RDF.type, SKOS.Concept))                 # a phi concept the recipient wasn't granted
    proj.add((TX.DONOR_ID, SKOS.inScheme, PROJ["projection"]))
    v = federate.certify_governed_federation(data, data, data, TX["role-recipient-ctr"], proj, Graph())
    assert not v.ok and v.ungranted
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_governed_projection.py -k "governed_projection_scopes or certify_governed" -q`
Expected: FAIL (`AttributeError: module ... has no attribute 'derive_governed_projection'`).

- [ ] **Step 3: Add to `src/iladub/etkl/federate.py`**

Append (the module already imports `RDF`, `dataclass`, `Namespace`, `Graph`, `URIRef`, `ILADUB`, `SKOS`, `interpret`, `os`; add `ODRL` and `ETKL` namespaces near the top with the others):

```python
ETKL = Namespace("https://w3id.org/iladub/etkl#")
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
PROV = Namespace("http://www.w3.org/ns/prov#")
RECIPE = URIRef("urn:federate:recipe")


def derive_governed_projection(interior: Graph, terms: Graph, governance: Graph,
                               policy: Graph, viewer) -> Graph:
    """AXIOM: run federate-projection-governed.rq for `viewer`. Materialize a one-triple
    recipe graph (<urn:federate:recipe> etkl:forViewer viewer) and union all graphs."""
    recipe = Graph()
    recipe.add((RECIPE, ETKL.forViewer, URIRef(str(viewer))))
    return interpret.run(os.path.join(_QUERIES, "federate-projection-governed.rq"),
                         interior, terms, governance, policy, recipe)


@dataclass(frozen=True)
class GovernedVerdict:
    ok: bool
    unsound: tuple
    leaked: tuple
    uncontained: tuple
    ungranted: tuple    # concepts in the projection whose tag the viewer's role was not granted


def _roles_of(viewer, *graphs) -> set:
    """Resolve the viewer's role(s) via (prov:actedOnBehalfOf)?/etkl:hasRole over the union."""
    g = Graph()
    for x in graphs:
        g += x
    q = """
        PREFIX etkl: <https://w3id.org/iladub/etkl#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?role WHERE { ?viewer (prov:actedOnBehalfOf)?/etkl:hasRole ?role }
    """
    return {str(r) for (r,) in g.query(q, initBindings={"viewer": URIRef(str(viewer))})}


def _permitted_for_role(governance: Graph, policy: Graph, roles: set) -> set:
    """Concepts whose sensitivity tag some role in `roles` is granted read on."""
    granted_tags = set()
    for perm in policy.objects(None, ODRL.permission):
        if (perm, ODRL.action, ODRL.read) in policy:
            assignees = {str(a) for a in policy.objects(perm, ODRL.assignee)}
            if assignees & roles:
                granted_tags |= {str(t) for t in policy.objects(perm, ODRL.target)}
    permitted = set()
    for concept, tag in governance.subject_objects(ETKL.sensitivity):
        if str(tag) in granted_tags:
            permitted.add(str(concept))
    return permitted


def certify_governed_federation(interior: Graph, governance: Graph, policy: Graph, viewer,
                                projection: Graph, consumer_graph: Graph) -> GovernedVerdict:
    """certify_federation (sound ∧ opaque ∧ contained) PLUS governance-soundness:
    every concept in the projection must be one the viewer's role was granted read on."""
    base = certify_federation(interior, projection, consumer_graph)
    roles = _roles_of(viewer, interior, governance, policy)
    permitted = _permitted_for_role(governance, policy, roles)
    proj_concepts = _projection_concepts(projection)
    ungranted = tuple(sorted(proj_concepts - permitted))
    ok = base.ok and not ungranted
    return GovernedVerdict(ok=ok, unsound=base.unsound, leaked=base.leaked,
                           uncontained=base.uncontained, ungranted=ungranted)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_governed_projection.py -q`
Expected: PASS (derive scopes to viewer; faithful → ok; ungranted phi in projection → not ok).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/federate.py tests/test_governed_projection.py
git commit -m "feat(etkl): derive_governed_projection + certify_governed_federation (governance-soundness)"
```

---

### Task 4: The AI-agent path + a full governed federation demonstrator

**Files:**
- Create: `examples/federation/governed-offer.ttl` (interior + terms + governance + policy + viewers)
- Test: `tests/test_governed_projection.py` (append)

**Interfaces:**
- Consumes: `derive_governed_projection`, `certify_governed_federation`, `ground.ground_concept`/`compile_document`, `read_csv_surface_concepts`.
- Produces: the demonstrator proving an AI agent inherits its user's role.

- [ ] **Step 1: Write the demonstrator fixture `examples/federation/governed-offer.ttl`**

```turtle
@prefix iladub: <https://w3id.org/iladub#> .
@prefix etkl:   <https://w3id.org/iladub/etkl#> .
@prefix skos:   <http://www.w3.org/2004/02/skos/core#> .
@prefix odrl:   <http://www.w3.org/ns/odrl/2/> .
@prefix prov:   <http://www.w3.org/ns/prov#> .
@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex:     <https://example.org/demo#> .
@prefix tx:     <https://example.org/transplant#> .

#  A compiled donor-offer interior (two promoted concepts), reusing the transplant world.
ex:gn1 a iladub:GroundedNode ; iladub:wasPromotedBy ex:pd1 ; iladub:groundsTo tx:ABO_O .
ex:pd1 a iladub:PromotionDecision .
ex:gn2 a iladub:GroundedNode ; iladub:wasPromotedBy ex:pd2 ; iladub:groundsTo tx:DONOR_ID .
ex:pd2 a iladub:PromotionDecision .

tx:ABO_O    a skos:Concept ; skos:prefLabel "O" .
tx:DONOR_ID a skos:Concept ; skos:prefLabel "ET-DONOR-2026-0091" .

tx:ABO_O    etkl:sensitivity tx:clinical .
tx:DONOR_ID etkl:sensitivity tx:phi .

#  Roles (self-referential role handle) + a recipient clinician + an AI assistant for her.
tx:role-opo           etkl:hasRole tx:role-opo ; rdfs:label "OPO / procurement"@en .
tx:role-recipient-ctr etkl:hasRole tx:role-recipient-ctr ; rdfs:label "Recipient centre"@en .
tx:clinician-aliki a prov:Person ; etkl:hasRole tx:role-recipient-ctr .
tx:ai-assistant a prov:SoftwareAgent ; prov:actedOnBehalfOf tx:clinician-aliki .   # inherits her role

tx:policy a odrl:Policy ;
    odrl:permission
      [ odrl:action odrl:read ; odrl:assignee tx:role-opo ;           odrl:target tx:clinical ] ,
      [ odrl:action odrl:read ; odrl:assignee tx:role-opo ;           odrl:target tx:phi ] ,
      [ odrl:action odrl:read ; odrl:assignee tx:role-recipient-ctr ; odrl:target tx:clinical ] .
```

- [ ] **Step 2: Write the failing tests (append)**

```python
GOV_OFFER = os.path.join(ROOT, "examples", "federation", "governed-offer.ttl")


def test_ai_agent_inherits_user_role_and_cannot_reach_phi():
    data = Graph().parse(GOV_OFFER, format="turtle")
    # the AI assistant acts for a recipient-centre clinician -> resolves to the recipient projection
    proj = federate.derive_governed_projection(data, data, data, data, TX["ai-assistant"])
    assert (TX.ABO_O, SKOS.inScheme, PROJ["projection"]) in proj           # clinical: allowed
    assert (TX.DONOR_ID, SKOS.inScheme, PROJ["projection"]) not in proj    # phi: withheld from the AI too


def test_ai_agent_grounding_to_phi_is_uncontained():
    data = Graph().parse(GOV_OFFER, format="turtle")
    proj = federate.derive_governed_projection(data, data, data, data, TX["ai-assistant"])
    consumer = Graph()  # the agent tries to ground to donor PHI
    consumer.add((URIRef("urn:ai#gn"), RDF.type, ILADUB.GroundedNode))
    consumer.add((URIRef("urn:ai#gn"), ILADUB.groundsTo, TX.DONOR_ID))
    v = federate.certify_governed_federation(data, data, data, TX["ai-assistant"], proj, consumer)
    assert not v.ok and v.uncontained    # PHI is not in the agent's projection -> containment breach


def test_ai_agent_without_user_fails_inherits_shape():
    from iladub.validate import validate
    SH = os.path.join(ROOT, "vocab", "shapes")
    shapes = Graph().parse(os.path.join(SH, "governance-shapes.ttl"), format="turtle")
    data = Graph()
    PROV = Namespace("http://www.w3.org/ns/prov#")
    ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
    # a software agent granted directly, with no prov:actedOnBehalfOf
    perm = URIRef("urn:perm")
    data.add((URIRef("urn:policy"), ODRL.permission, perm))
    data.add((perm, ODRL.action, ODRL.read))
    data.add((perm, ODRL.assignee, TX["rogue-agent"]))
    data.add((TX["rogue-agent"], RDF.type, PROV.SoftwareAgent))
    assert not validate(data, shapes, Graph()).conforms
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_governed_projection.py -k "ai_agent" -q`
Expected: FAIL (missing fixture on the first two; the third should already pass since `gsh:AiInheritsUserShape` exists — if the whole file errors on the missing fixture path, create the fixture from Step 1 first).

- [ ] **Step 4: (Fixture is the implementation for this task — created in Step 1.)**

No code change needed beyond the fixture; the behavior is already provided by Tasks 1–3 and the existing `gsh:AiInheritsUserShape`. Re-run:

Run: `. .venv/bin/activate && python3 -m pytest tests/test_governed_projection.py -q`
Expected: PASS (AI inherits recipient role → clinical only; agent grounding to PHI → uncontained; rogue agent → shape fails).

- [ ] **Step 5: Commit**

```bash
git add examples/federation/governed-offer.ttl tests/test_governed_projection.py
git commit -m "test(etkl): AI-agent-for-user governed federation — the AI can't reach what its user can't"
```

---

### Task 5: Upgrade the transplant governance example — derived role projections

**Files:**
- Modify: `examples/transplant/transplant-governance.ttl`
- Modify: `tests/test_governance.py`

**Interfaces:**
- Consumes: `federate.derive_governed_projection`.
- Produces: the transplant `view-opo`/`view-recipient` as DERIVED projections; the existing PHI-withholding intent proven on derived output.

- [ ] **Step 1: Rewrite the projection section of `examples/transplant/transplant-governance.ttl`**

Replace the block under `#  Role-polymorphic projections (ViewerPass). ...` (the hand-materialized `tx:view-opo` / `tx:view-recipient`) with a governed model: tag the offer's concepts, retarget the policy to tags, and declare roles' `etkl:hasRole`. Add the `etkl:` prefix at the top (`@prefix etkl: <https://w3id.org/iladub/etkl#> .`). Concretely, replace the two `tx:view-*` blocks with:

```turtle
#  Concepts the offer grounds to, tagged by sensitivity (governance graph). The
#  role-polymorphic projections are now DERIVED per role by federate-projection-governed.rq
#  under this ODRL tag policy — not materialised here. (See tests/test_governance.py.)
tx:ABO_O    etkl:sensitivity tx:clinical .
tx:LVEF     etkl:sensitivity tx:clinical .
tx:DONOR_ID etkl:sensitivity tx:phi .

tx:role-opo           etkl:hasRole tx:role-opo .
tx:role-recipient-ctr etkl:hasRole tx:role-recipient-ctr .
```

And retarget `tx:policy` so its permissions grant `odrl:target` the **tags** (`tx:clinical` / `tx:phi`) rather than the data fields — OPO reads `{clinical, phi}`, recipient reads `{clinical}`:

```turtle
tx:policy a odrl:Policy ;
    odrl:permission
      [ odrl:action odrl:read ; odrl:assignee tx:role-opo ;           odrl:target tx:clinical ] ,
      [ odrl:action odrl:read ; odrl:assignee tx:role-opo ;           odrl:target tx:phi ] ,
      [ odrl:action odrl:read ; odrl:assignee tx:role-recipient-ctr ; odrl:target tx:clinical ] .
```

Add the promoted-concept interior + terms the derivation needs (so the file is self-contained for the test):

```turtle
tx:gn-abo a iladub:GroundedNode ; iladub:wasPromotedBy tx:pd-abo ; iladub:groundsTo tx:ABO_O .
tx:pd-abo a iladub:PromotionDecision .
tx:gn-lvef a iladub:GroundedNode ; iladub:wasPromotedBy tx:pd-lvef ; iladub:groundsTo tx:LVEF .
tx:pd-lvef a iladub:PromotionDecision .
tx:gn-donorid a iladub:GroundedNode ; iladub:wasPromotedBy tx:pd-donorid ; iladub:groundsTo tx:DONOR_ID .
tx:pd-donorid a iladub:PromotionDecision .
tx:ABO_O    a skos:Concept ; skos:prefLabel "O" .
tx:LVEF     a skos:Concept ; skos:prefLabel "38" .
tx:DONOR_ID a skos:Concept ; skos:prefLabel "ET-DONOR-2026-0091" .
```

Add the `iladub:` and `skos:` prefixes at the top if not present (`@prefix iladub: <https://w3id.org/iladub#> .`, `@prefix skos: <http://www.w3.org/2004/02/skos/core#> .`). Keep the rest of the file (donor, roles' labels, ODRL AI-inherits-user assistant, constitutional risk apex) unchanged. Leave `tx:ai-assistant` / `tx:clinician-aliki` as they are (they already carry `prov:actedOnBehalfOf`); ensure `tx:clinician-aliki etkl:hasRole tx:role-recipient-ctr` is present (add it if the file used only `tx:hasRole` — replace `tx:hasRole` with `etkl:hasRole`).

- [ ] **Step 2: Rewrite the derived-view assertions in `tests/test_governance.py`**

Replace `test_recipient_projection_withholds_donor_phi` with a version that DERIVES the views:

```python
def test_recipient_projection_withholds_donor_phi():
    """Concentric openness: the recipient view is DERIVED and excludes donor PHI; the OPO view includes it."""
    from iladub.etkl import federate
    from rdflib import RDF
    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
    PROJ = Namespace("urn:iladub:")
    data = _g(GOV_EX)
    opo = federate.derive_governed_projection(data, data, data, data, TX["role-opo"])
    recip = federate.derive_governed_projection(data, data, data, data, TX["role-recipient-ctr"])
    # OPO sees donor PHI; recipient does not
    assert (TX["DONOR_ID"], SKOS.inScheme, PROJ["projection"]) in opo
    assert (TX["DONOR_ID"], SKOS.inScheme, PROJ["projection"]) not in recip
    # both keep the de-identified clinical concepts
    assert (TX["ABO_O"], SKOS.inScheme, PROJ["projection"]) in opo
    assert (TX["ABO_O"], SKOS.inScheme, PROJ["projection"]) in recip
```

Leave `test_governance_example_conformant`, `test_direct_ai_grant_rejected`, and `test_ai_assistant_inherits_a_user` unchanged (the AI-inherits-user assertion still holds).

- [ ] **Step 3: Run the governance tests**

Run: `. .venv/bin/activate && python3 -m pytest tests/test_governance.py -q`
Expected: PASS (derived recipient view withholds PHI; OPO includes it; existing conformance + AI-inherits-user intact). If `test_governance_example_conformant` fails because the retargeted ODRL still validates under `gsh:PermissionShape` (it requires `odrl:action` + `odrl:assignee`, both still present), no change is needed; if a leftover `tx:hasRole` triple remains, convert it to `etkl:hasRole`.

- [ ] **Step 4: Commit**

```bash
git add examples/transplant/transplant-governance.ttl tests/test_governance.py
git commit -m "refactor(examples): transplant role projections are now DERIVED under the tag policy (ViewerPass)"
```

---

### Task 6: Full-suite regression check

**Files:**
- None (verification only).

- [ ] **Step 1: Run the full suite**

Run: `. .venv/bin/activate && python3 -m pytest -q`
Expected: all pass (prior 509 + the new governed-projection tests), 5 skipped. If any prior test regressed, fix in the task that introduced the regression (do not paper over it here).

- [ ] **Step 2: Commit (only if a fix was needed; otherwise skip)**

```bash
git add -A && git commit -m "fix(etkl): <describe regression fix>"
```

---

## Self-Review

**Spec coverage:**
- §3.1 governed CONSTRUCT → Task 2.
- §3.2 vocab (`etkl:sensitivity`/`hasRole`/`forViewer`) + `hview:` alignment → Task 1.
- §3.3 `derive_governed_projection` + `certify_governed_federation` (governance-soundness) → Task 3.
- §3.4 SHACL reuse (`DocumentProjectionShape`, `AiInheritsUserShape`) → exercised in Tasks 4 (rogue agent) and existing suite; no new shape (matches spec "no new shape required").
- §4 demonstrator + transplant upgrade → Tasks 4 (AI path) + 5 (transplant derived).
- §4 tests (OPO vs recipient, consumer can't reach PHI, AI agent, negatives: uncontained, ungranted, agent-without-user) → Tasks 2/3/4.
- §5 gate: derivation AXIOM (Task 2), membrane SHACL (reused), oracle PROCEDURAL set-comparison (Task 3, no tuned constant) → covered.
- §6 source-ownership: `hview:` object-only in align module (Task 1); `etkl.ttl` standalone; `hfed:` unused → covered.

**Placeholder scan:** none — every step has full TTL/SPARQL/Python/command content.

**Type consistency:** `derive_governed_projection(interior, terms, governance, policy, viewer)`, `certify_governed_federation(interior, governance, policy, viewer, projection, consumer_graph)`, `GovernedVerdict(ok, unsound, leaked, uncontained, ungranted)`, `_roles_of`, `_permitted_for_role`, fixed IRIs `<urn:iladub:projection>` / `<urn:federate:recipe>`, predicates `etkl:sensitivity`/`etkl:hasRole`/`etkl:forViewer` — used consistently across Tasks 1–5. Namespaces `ETKL`/`ODRL`/`PROV`/`SKOS`/`ILADUB`/`TX`/`PROJ`/`HVIEW` used consistently in tests.

**Note on Task 4 Step 4:** the AI-agent behavior needs no new code — it falls out of the property path built in Task 2 and the oracle in Task 3; the "implementation" is the demonstrator fixture. This is legitimate (the task's deliverable is the proven end-to-end path), not a placeholder.
