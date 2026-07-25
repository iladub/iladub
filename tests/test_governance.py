"""Information governance on the transplant showcase — concentric openness made concrete.

Demonstrates: ODRL policy-as-data per role; role-polymorphic projections that withhold donor
PHI from the recipient centre; and the AI-inherits-user invariant (an AI agent may never hold a
direct grant — it must act on behalf of a user). Access uses plain odrl:/prov:, aligned to HGA
hpol:/hview:.
"""
import os
from rdflib import Graph, Namespace, URIRef
from pyshacl import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SH  = os.path.join(ROOT, "vocab", "shapes")
EX  = os.path.join(ROOT, "examples", "transplant")
TST = os.path.join(ROOT, "tests")

TX = Namespace("https://example.org/transplant#")

def _g(*paths):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    return g

def _v(data, shapes):
    c, _, t = validate(_g(*data), shacl_graph=_g(*shapes), inference="rdfs", advanced=True)
    return c, t

GOV_SHAPES = os.path.join(SH, "governance-shapes.ttl")
GOV_EX = os.path.join(EX, "transplant-governance.ttl")

def test_governance_example_conformant():
    """Policies well-formed; the AI assistant acts on behalf of a clinician (no direct grant)."""
    c, t = _v([GOV_EX], [GOV_SHAPES])
    assert c, t

def test_direct_ai_grant_rejected():
    """An AI/software agent granted access directly (no user) MUST fail the invariant."""
    c, _ = _v([os.path.join(TST, "transplant-governance-leak.ttl")], [GOV_SHAPES])
    assert not c

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

def test_ai_assistant_inherits_a_user():
    """The conformant AI assistant carries a user to inherit access from."""
    g = _g(GOV_EX)
    PROV = Namespace("http://www.w3.org/ns/prov#")
    assert (TX["ai-assistant"], PROV.actedOnBehalfOf, TX["clinician-aliki"]) in g
