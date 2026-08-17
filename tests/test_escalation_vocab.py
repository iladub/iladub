import os
from rdflib import Graph, Namespace
from rdflib.collection import Collection
from rdflib.namespace import RDF, RDFS, OWL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
DEC = Namespace("https://w3id.org/iladub/dec#")
ETKL = Namespace("https://w3id.org/iladub/etkl#")
RISK = Namespace("https://w3id.org/iladub/risk#")


def _hol():
    return Graph().parse(os.path.join(ONT, "dec.ttl"), format="turtle")


def _etkl():
    return Graph().parse(os.path.join(ONT, "etkl.ttl"), format="turtle")


def _union_members(g, node):
    """The members of an owl:Class/owl:unionOf range or domain node."""
    lst = next(g.objects(node, OWL.unionOf), None)
    assert lst is not None, f"{node} is not an owl:unionOf class expression"
    return set(Collection(g, lst))


def test_escalatedto_ranges_over_decision_or_expansion_request():
    # The derivation asserts `?d dec:escalatedTo ?req` where ?req a dec:ExpansionRequest,
    # which is a dec:Event and NOT a dec:DecisionHolon (dec.ttl:197-198). The range is
    # widened on the precedent of dec:regarding's domain (dec.ttl:204).
    g = _hol()
    assert (DEC.escalatedTo, RDF.type, OWL.ObjectProperty) in g
    assert (DEC.escalatedTo, RDFS.domain, DEC.DecisionHolon) in g
    rng = next(g.objects(DEC.escalatedTo, RDFS.range), None)
    assert rng is not None
    assert _union_members(g, rng) == {DEC.DecisionHolon, DEC.ExpansionRequest}


def test_maxseverity_is_objectproperty_on_scope():
    g = _hol()
    assert (DEC.maxSeverity, RDF.type, OWL.ObjectProperty) in g
    assert (DEC.maxSeverity, RDFS.domain, DEC.Scope) in g
    # range intentionally left open — dec stays standalone (risk:Severity lives in a separate module)
    assert next(g.objects(DEC.maxSeverity, RDFS.range), None) is None


def test_hol_stays_standalone_no_hga():
    with open(os.path.join(ROOT, "vocab", "ontology", "dec.ttl"), encoding="utf-8") as fh:
        text = fh.read()
    assert "w3id.org/holon" not in text


#################################################################
#  etkl:readerScope — the one autonomy scope every region escalation exceeds
#################################################################


def test_readerscope_is_a_scope_with_a_ceiling():
    # T1.1. etkl:readerScope is the object of dec:withinScope (range dec:Scope,
    # dec.ttl:114) and the subject of dec:maxSeverity (domain dec:Scope, dec.ttl:217);
    # untyped it sits outside two declared boundaries at once.
    g = _etkl()
    assert (ETKL.readerScope, RDF.type, DEC.Scope) in g
    assert (ETKL.readerScope, DEC.maxSeverity, RISK.Watch) in g


def test_etkl_does_not_restate_the_severity_ordinals():
    # T1.2. The ordering is risk.ttl's to own — the derivation binds it as a query
    # input rather than writing it (G3 condition 1), and this is that condition's
    # first line of defence at vocabulary level.
    g = _etkl()
    assert list(g.triples((None, RISK.order, None))) == []


def test_reader_ceiling_is_below_the_severity_every_escalation_realizes():
    # T1.3. Pins the *relation* dec:EscalationShape's FILTER (?so > ?co) depends on,
    # not the two numbers, so retuning risk.ttl cannot silently make the shape inert.
    g = _etkl()
    g.parse(os.path.join(ONT, "risk.ttl"), format="turtle")
    ceil = next(g.objects(ETKL.readerScope, DEC.maxSeverity))
    co = next(g.objects(ceil, RISK.order))
    so = next(g.objects(RISK.Breach, RISK.order))
    assert co.toPython() < so.toPython()
