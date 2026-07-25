"""Governed / ViewerPass projection: a viewer-relative federation projection derived
under ODRL policy over concept sensitivity tags. AI-inherits-user via a SPARQL property
path. See docs/superpowers/specs/2026-07-25-governed-viewerpass-projection-design.md."""
import os
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")

ETKL = Namespace("https://w3id.org/iladub/etkl#")
HVIEW = Namespace("http://w3id.org/holon/viewer/")
ILADUB = Namespace("https://w3id.org/iladub#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
TX = Namespace("https://example.org/transplant#")
PROJ = Namespace("urn:iladub:")
RECIPE = URIRef("urn:federate:recipe")
QUERIES = os.path.join(ROOT, "vocab", "queries")
GOV_INTERIOR = os.path.join(ROOT, "tests", "federation-governed-interior.ttl")


def test_governance_properties_declared():
    g = Graph().parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    for p in (ETKL.sensitivity, ETKL.hasRole, ETKL.forViewer):
        assert (p, RDF.type, OWL.ObjectProperty) in g, p


def test_hasrole_aligns_to_hview_viewerprofile():
    g = Graph().parse(os.path.join(ONT, "iladub-hga-align.ttl"), format="turtle")
    assert (ETKL.hasRole, RDFS.seeAlso, HVIEW.ViewerProfile) in g


# --- Governed projection tests (AXIOM derivation under ODRL tag policy) ---
from iladub.etkl import interpret


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


# --- GovernedVerdict & certify_governed_federation tests ---
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
