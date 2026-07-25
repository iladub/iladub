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
GOV_OFFER = os.path.join(ROOT, "examples", "federation", "governed-offer.ttl")


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


def test_oracle_agrees_with_query_for_unnested_permission():
    """Oracle must not flag as ungranted a concept the CONSTRUCT legitimately emits, even
    when the read-permission is a top-level resource (not linked via odrl:permission)."""
    from rdflib import Literal
    ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
    g = Graph()
    # promoted concept, tagged, with a public label
    g.add((TX.X, RDF.type, SKOS.Concept)); g.add((TX.X, SKOS.prefLabel, Literal("x")))
    g.add((TX.X, ETKL.sensitivity, TX.clinical))
    gn = URIRef("urn:g#n"); pd = URIRef("urn:g#pd")
    g.add((gn, RDF.type, ILADUB.GroundedNode)); g.add((gn, ILADUB.wasPromotedBy, pd))
    g.add((gn, ILADUB.groundsTo, TX.X)); g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((TX["role-r"], ETKL.hasRole, TX["role-r"]))
    # a top-level read-permission (NOT hung off any odrl:Policy via odrl:permission)
    perm = URIRef("urn:g#perm")
    g.add((perm, ODRL.action, ODRL.read)); g.add((perm, ODRL.assignee, TX["role-r"]))
    g.add((perm, ODRL.target, TX.clinical))
    proj = federate.derive_governed_projection(g, g, g, g, TX["role-r"])
    assert (TX.X, SKOS.inScheme, PROJ["projection"]) in proj          # query emits it
    v = federate.certify_governed_federation(g, g, g, TX["role-r"], proj, Graph())
    assert not v.ungranted, v                                          # oracle must agree (not flag it)


# --- AI-agent path: inherits user's role and access ---

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


def test_certify_governed_ok_for_ai_agent_within_entitlement():
    """Governed-bot headline at the ORACLE level: the AI assistant (acting for a recipient
    clinician) grounds to a clinical concept within its inherited entitlement, and
    certify_governed_federation returns ok — the oracle resolves agent→user→role via the
    same (prov:actedOnBehalfOf)?/etkl:hasRole path the query uses."""
    data = Graph().parse(GOV_OFFER, format="turtle")
    proj = federate.derive_governed_projection(data, data, data, data, TX["ai-assistant"])
    consumer = Graph()
    consumer.add((URIRef("urn:ai#gn"), RDF.type, ILADUB.GroundedNode))
    consumer.add((URIRef("urn:ai#gn"), ILADUB.groundsTo, TX.ABO_O))   # clinical: within the AI's inherited entitlement
    v = federate.certify_governed_federation(data, data, data, TX["ai-assistant"], proj, consumer)
    assert v.ok, v
