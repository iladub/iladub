"""Compile→federate loop: a CleanDocumentHolon's projection becomes the next
document's provided terminology. See docs/superpowers/specs/2026-07-24-compile-federate-design.md."""
import os
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef
from iladub.etkl import interpret, federate
from iladub.ground import load_contract, SurfaceConcept
from iladub.propose_ground import GroundingProposal, FakeGroundingProposer
from iladub.validate import validate
from iladub.readers import read_csv_surface_concepts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
SH_DIR = os.path.join(ROOT, "vocab", "shapes")

ETKL = Namespace("https://w3id.org/iladub/etkl#")
HPROJ = Namespace("http://w3id.org/holon/projection/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
ILADUB = Namespace("https://w3id.org/iladub#")
TX = Namespace("https://example.org/transplant#")
PROJ = Namespace("urn:iladub:")
QUERIES = os.path.join(ROOT, "vocab", "queries")


def test_document_projection_class_declared():
    g = Graph().parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    assert (ETKL.DocumentProjection, RDF.type, OWL.Class) in g


def test_document_projection_aligns_to_hproj():
    g = Graph().parse(os.path.join(ONT, "iladub-hga-align.ttl"), format="turtle")
    assert (ETKL.DocumentProjection, RDFS.subClassOf, HPROJ.Projection) in g


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


def test_csv_adapter_yields_surface_concepts():
    from iladub.readers import read_csv_surface_concepts
    from iladub.ground import SurfaceConcept

    concepts = read_csv_surface_concepts(os.path.join(ROOT, "examples", "federation", "doc-a.csv"))
    assert SurfaceConcept(text="aboGroup", value="O", region="row1:col-aboGroup") in concepts
    assert SurfaceConcept(text="organ", value="heart", region="row1:col-organ") in concepts
    assert len(concepts) == 2


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

    # success criterion #2: the DERIVED projection passes the membrane shape (not just hand-authored fixtures)
    _shapes, _knowledge = _proj_shapes_knowledge()
    assert validate(projection, _shapes, _knowledge).conforms

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
