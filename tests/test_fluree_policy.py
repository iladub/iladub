"""Fluree f: enforcement compile: the governed ODRL tag-policy compiled to a data-driven
Fluree f:AccessPolicy, and certified faithful (f: grants == ODRL grants), no server.
See docs/superpowers/specs/2026-07-25-fluree-f-enforcement-design.md."""
import os
from rdflib import Graph, Namespace, RDF, OWL, Literal, URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONT = os.path.join(ROOT, "vocab", "ontology")
QUERIES = os.path.join(ROOT, "vocab", "queries")
ODRL_FIXTURE = os.path.join(ROOT, "tests", "fluree-odrl-policy.ttl")

ETKL = Namespace("https://w3id.org/iladub/etkl#")
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
TX = Namespace("https://example.org/transplant#")
FLUREE_DIR = os.path.join(ROOT, "src", "iladub", "fluree")
F = Namespace("https://ns.flur.ee/db#")


def test_grantstag_declared():
    g = Graph().parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    assert (ETKL.grantsTag, RDF.type, OWL.ObjectProperty) in g


def test_compile_f_grants_reshapes_odrl():
    from iladub.etkl import interpret

    policy = Graph().parse(ODRL_FIXTURE, format="turtle")
    grants = interpret.run(os.path.join(QUERIES, "compile-f-grants.rq"), policy)
    pairs = {(str(r), str(t)) for r, t in grants.subject_objects(ETKL.grantsTag)}
    assert pairs == {
        (str(TX["role-opo"]), str(TX.clinical)),
        (str(TX["role-opo"]), str(TX.phi)),
        (str(TX["role-recipient-ctr"]), str(TX.clinical)),
    }


def _template_graph():
    return Graph().parse(os.path.join(FLUREE_DIR, "f-policy-template.jsonld"), format="json-ld")


def test_template_is_a_view_access_policy():
    g = _template_graph()
    pol = next(g.subjects(RDF.type, F.AccessPolicy))
    assert (pol, F.action, F.view) in g
    assert (pol, F.required, None) in g


def test_template_query_binds_identity_and_joins():
    g = _template_graph()
    q = " ".join(str(o) for o in g.objects(None, F.query))
    for ref in ("?$identity",
                "http://www.w3.org/ns/prov#actedOnBehalfOf",
                "https://w3id.org/iladub/etkl#hasRole",
                "https://w3id.org/iladub/etkl#grantsTag",
                "https://w3id.org/iladub/etkl#sensitivity"):
        assert ref in q, ref


def test_compile_f_policy_is_faithful():
    from iladub.etkl import federate
    policy = Graph().parse(ODRL_FIXTURE, format="turtle")
    f_policy = federate.compile_f_policy(policy)
    # grants restated as etkl:grantsTag
    pairs = {(str(r), str(t)) for r, t in f_policy.subject_objects(ETKL.grantsTag)}
    assert (str(TX["role-opo"]), str(TX.phi)) in pairs
    # and the template's policy triple is present
    assert (None, RDF.type, F.AccessPolicy) in f_policy
    v = federate.certify_f_faithful(policy, f_policy)
    assert v.ok, v


def test_certify_flags_dropped_grant():
    from iladub.etkl import federate
    policy = Graph().parse(ODRL_FIXTURE, format="turtle")
    f_policy = federate.compile_f_policy(policy)
    f_policy.remove((TX["role-opo"], ETKL.grantsTag, TX.phi))   # drop a grant
    v = federate.certify_f_faithful(policy, f_policy)
    assert not v.ok and (str(TX["role-opo"]), str(TX.phi)) in v.missing


def test_certify_flags_extra_grant():
    from iladub.etkl import federate
    policy = Graph().parse(ODRL_FIXTURE, format="turtle")
    f_policy = federate.compile_f_policy(policy)
    f_policy.add((TX["role-recipient-ctr"], ETKL.grantsTag, TX.phi))   # phi not granted to recipient by ODRL
    v = federate.certify_f_faithful(policy, f_policy)
    assert not v.ok and (str(TX["role-recipient-ctr"]), str(TX.phi)) in v.extra


def test_certify_flags_broken_ai_inherits_user():
    from iladub.etkl import federate, interpret
    policy = Graph().parse(ODRL_FIXTURE, format="turtle")
    grants = interpret.run(os.path.join(QUERIES, "compile-f-grants.rq"), policy)
    # a template variant whose f:query resolves role WITHOUT the actedOnBehalfOf leg
    bad = Graph()
    pol = URIRef("urn:bad:policy")
    bad.add((pol, RDF.type, F.AccessPolicy))
    bad.add((pol, F.query, Literal(
        '{"where":[{"@id":"?$identity","https://w3id.org/iladub/etkl#hasRole":{"@id":"?role"}},'
        '{"@id":"?role","https://w3id.org/iladub/etkl#grantsTag":{"@id":"?tag"}},'
        '{"@id":"?$this","https://w3id.org/iladub/etkl#sensitivity":{"@id":"?tag"}}]}')))
    v = federate.certify_f_faithful(policy, grants + bad)
    assert not v.identity_ok and not v.ok
