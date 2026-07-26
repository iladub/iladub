"""The Fluree WRITE/commit gate: iladub's promotion invariant enforced at commit
(a grounded node without an accountable promotion is REJECTED), plus a static f:modify
policy authorizing writes only to the promotion's dec:decidedBy agent.
See docs/superpowers/specs/2026-07-25-fmodify-write-gate-design.md."""
import os
from rdflib import Graph

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
TST = os.path.join(ROOT, "tests")


def _knowledge():
    g = Graph()
    for f in ("iladub.ttl", "dec.ttl"):
        g.parse(os.path.join(ONT, f), format="turtle")
    return g


def test_gate_admits_a_properly_promoted_write():
    from iladub.etkl import writegate
    data = Graph().parse(os.path.join(TST, "writegate-promoted.ttl"), format="turtle")
    result = writegate.gate_admits(data, _knowledge())
    assert result.conforms, result.report_text


def test_gate_rejects_a_grounded_node_without_promotion():
    from iladub.etkl import writegate
    data = Graph().parse(os.path.join(TST, "writegate-unpromoted.ttl"), format="turtle")
    result = writegate.gate_admits(data, _knowledge())
    assert not result.conforms
    assert "promotion" in result.report_text.lower()


def test_gate_rejects_a_leaked_candidate():
    from iladub.etkl import writegate
    data = Graph().parse(os.path.join(TST, "leak-attempt.ttl"), format="turtle")
    result = writegate.gate_admits(data, _knowledge())
    assert not result.conforms


from rdflib import Namespace, RDF, Literal, URIRef

F = Namespace("https://ns.flur.ee/db#")
FLUREE_DIR = os.path.join(ROOT, "src", "iladub", "fluree")


def _modify_template():
    return Graph().parse(os.path.join(FLUREE_DIR, "f-modify-policy-template.jsonld"), format="json-ld")


def test_modify_template_is_f_modify_and_binds_accountable():
    g = _modify_template()
    pol = next(g.subjects(RDF.type, F.AccessPolicy))
    assert (pol, F.action, F.modify) in g
    q = " ".join(str(o) for o in g.objects(None, F.query))
    for ref in ("?$identity",
                "https://w3id.org/iladub#wasPromotedBy",
                "https://w3id.org/iladub/dec#decidedBy"):
        assert ref in q, ref


def test_certify_modify_authorization_ok():
    from iladub.etkl import writegate
    v = writegate.certify_modify_authorization(_modify_template())
    assert v.ok and v.is_modify and v.wires_accountable, v


def test_certify_rejects_non_modify_policy():
    from iladub.etkl import writegate
    g = Graph()
    pol = URIRef("urn:bad:viewpol")
    g.add((pol, RDF.type, F.AccessPolicy))
    g.add((pol, F.action, F.view))   # f:view, not f:modify
    g.add((pol, F.query, Literal(
        '{"where":[{"@id":"?$this","https://w3id.org/iladub#wasPromotedBy":{"@id":"?pd"}},'
        '{"@id":"?pd","https://w3id.org/iladub/dec#decidedBy":{"@id":"?$identity"}}]}')))
    v = writegate.certify_modify_authorization(g)
    assert not v.is_modify and not v.ok


def test_certify_rejects_unaccountable_query():
    from iladub.etkl import writegate
    g = Graph()
    pol = URIRef("urn:bad:modpol")
    g.add((pol, RDF.type, F.AccessPolicy))
    g.add((pol, F.action, F.modify))
    # f:query omits decidedBy — anyone could write, not just the accountable decider
    g.add((pol, F.query, Literal(
        '{"where":[{"@id":"?$this","https://w3id.org/iladub#wasPromotedBy":{"@id":"?pd"}}]}')))
    v = writegate.certify_modify_authorization(g)
    assert not v.wires_accountable and not v.ok
