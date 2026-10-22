"""substrate:03 seams (spec § 4.2, § 4.3, § 8), measured before the plan. Measurement only.

Run from the repo root: PYTHONPATH=src:. .venv/bin/python docs/superpowers/evidence/2026-10-21-substrate-03-seams/seams.py

The bundle mirrors the probe's q8 (role-conditional companion, union view, explicit config), but the
shapes are the shipped vocab/shapes/iladub-shapes.ttl and the guard set is the spec § 4.3 closure set
computed from it. Identity travels by HEADER on every request, as spec § 4.2 mandates.
"""
import json, os, sys

PROBE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "2026-10-21-substrate-03-probe")
sys.path.insert(0, PROBE)
from probe_lib import *  # noqa: E402,F401
from q1q3_fixed import VIEW_QUERY_FIXED  # noqa: E402
from q4b_q6_q7 import config_explicit, CFG_PREDS  # noqa: E402

from rdflib import Graph, BNode, URIRef, RDF  # noqa: E402
from iladub.etkl.writegate import commit_gate_shapes  # noqa: E402
from tests.substrate.doc_a import compiled_interior, ungoverned  # noqa: E402

STEWARD = EX + "roleSteward"
STEWARD_Q = json.dumps({"where": [{"@id": "?$identity", ETKL + "hasRole": {"@id": STEWARD}}]})
ROLE_Q = json.dumps({"where": [{"@id": "?$identity", ETKL + "hasRole": {"@id": "?r"}}]})
ROLE_PREDS = [ETKL + "hasRole", PROV + "actedOnBehalfOf", ETKL + "grantsTag", ETKL + "sensitivity"]
SHAPES = commit_gate_shapes()
SH_PREDS = sorted({str(p) for p in SHAPES.predicates()} - {str(RDF.type)})

FIXTURE = f"""@prefix ex: <{EX}> . @prefix etkl: <{ETKL}> . @prefix prov: <{PROV}> .
ex:d1 a ex:Doc ; etkl:sensitivity ex:tagPublic .
ex:d2 a ex:Doc ; etkl:sensitivity ex:tagClinical .
ex:d3 a ex:Doc ; etkl:sensitivity ex:tagSecret .
ex:roleClinician etkl:grantsTag ex:tagPublic , ex:tagClinical .
ex:roleSteward etkl:grantsTag ex:tagPublic , ex:tagClinical , ex:tagSecret .
ex:U etkl:hasRole ex:roleClinician . ex:A prov:actedOnBehalfOf ex:U .
ex:W etkl:hasRole ex:roleClinician . ex:S etkl:hasRole ex:roleSteward .
ex:A a prov:SoftwareAgent . ex:B a prov:SoftwareAgent .
"""


def bundle(drop_mincount=False):
    sh = [p for p in SH_PREDS if not (drop_mincount and p.endswith("#minCount"))]
    return [policy_node(ETKL + "sensitivityViewPolicy", "view", VIEW_QUERY_FIXED),
            policy_node(EX + "guardShapesClass", "modify", STEWARD_Q, on_class=[SH + "NodeShape"]),
            policy_node(EX + "guardShapesProps", "modify", STEWARD_Q, on_property=sh),
            policy_node(EX + "guardConfig", "modify", STEWARD_Q, on_property=CFG_PREDS),
            policy_node(EX + "guardRoles", "modify", STEWARD_Q, on_property=ROLE_PREDS),
            policy_node(EX + "modifyCompanionRole", "modify", ROLE_Q, required=False)]


def build(c, L, **kw):
    assert c.create(L)[0] == 201
    st, txt = c.insert_ttl(L, SHAPES.serialize(format="turtle"), label=f"{L} shapes"); assert st == 200, txt
    st, txt = c.insert_ttl(L, FIXTURE, label=f"{L} fixture"); assert st == 200, txt
    st, txt = c.sparql(L, "SELECT ?p WHERE { <https://w3id.org/iladub#GroundedNodeShape> sh:property ?p ; "
                          "sh:property ?p . ?p sh:path <https://w3id.org/iladub#wasPromotedBy> }",
                       label=f"{L} root bnode read")
    bn = json.loads(txt)["results"]["bindings"][0]["p"]["value"]
    st, txt = c.insert_jsonld(L, {"@graph": bundle(**kw)}, label=f"{L} policies"); assert st == 200, txt
    st, txt = c.update(L, config_explicit(L), label=f"{L} config"); assert st == 200, txt
    return bn


def rdflib_delete_body(bn):
    """Seam A: the exact bytes rdflib produces for the engine's own label."""
    g = Graph(); g.add((BNode(bn), URIRef(SH + "minCount"), __import__("rdflib").Literal(1)))
    return json.dumps({"delete": json.loads(g.serialize(format="json-ld"))})


def jdel_hdr(c, L, body, who, label):
    h = {"Content-Type": "application/json", **(ident(who) if who else {})}
    return lambda: c.req("POST", f"/v1/fluree/update/{L}", body, h, label=f"{L} {label}")


def step(c, L, label, fn):
    t0 = c.t(L); st, txt = fn(); t1 = c.t(L)
    print(f"    {label:64s} {st} t {t0}->{t1} {short(txt, 110) if st != 200 else ''}")
    return st, txt


def upd(c, L, q, who, label):
    return lambda: c.update(L, q, ident(who) if who else {}, label=f"{L} {label}")


def ins(c, L, g, who, label):
    return lambda: c.insert_ttl(L, g.serialize(format="turtle"), ident(who) if who else {}, label=f"{L} {label}")


GN = "<https://w3id.org/iladub#GroundedNodeShape>"
INVARIANT = "INVARIANT: every grounded node must be produced by a promotion decision."

if __name__ == "__main__":
    print("closure-set shape predicates:", len(SH_PREDS))
    with server() as c:
        L = "seams"
        bn = build(c, L)
        print(f"== {L}: full bundle on iladub-shapes.ttl, blank node {bn}")
        print("  delete body (rdflib):", rdflib_delete_body(bn))
        for who in (U, A, B, W, S):
            st, n, _ = c.count_docs(L, ident(who), label=f"count {who}")
            print(f"    count({who.rsplit('/', 1)[1]}) = {n}  ({st})")
        step(c, L, "SEAM B: W DELETE DATA GroundedNodeShape a sh:NodeShape",
             upd(c, L, f"DELETE DATA {{ {GN} a sh:NodeShape }}", W, "W del type"))
        step(c, L, "W DELETE DATA GroundedNodeShape sh:targetClass",
             upd(c, L, f"DELETE DATA {{ {GN} sh:targetClass <https://w3id.org/iladub#GroundedNode> }}", W, "W del tc"))
        step(c, L, "SEAM A: W JSON-LD (rdflib bytes, header id) delete minCount",
             jdel_hdr(c, L, rdflib_delete_body(bn), W, "W del minCount"))
        st, txt = step(c, L, "COMPOSITE: W commit ungoverned(doc-a)", ins(c, L, ungoverned(compiled_interior()), W, "W ungov"))
        print("      INVARIANT in report:", INVARIANT in txt)
        step(c, L, "control: W commit compiled_interior()", ins(c, L, compiled_interior(), W, "W doc-a"))
        step(c, L, "W self-promotion", upd(c, L, f"INSERT DATA {{ ex:W etkl:hasRole <{STEWARD}> }}", W, "W promote"))
        step(c, L, "anon commit compiled_interior()", ins(c, L, compiled_interior(), None, "anon doc-a"))
        step(c, L, "B commit compiled_interior()", ins(c, L, compiled_interior(), B, "B doc-a"))
        step(c, L, "control: S JSON-LD (rdflib bytes, header id) delete minCount",
             jdel_hdr(c, L, rdflib_delete_body(bn), S, "S del minCount"))
        step(c, L, "control: S DELETE DATA GroundedNodeShape a sh:NodeShape",
             upd(c, L, f"DELETE DATA {{ {GN} a sh:NodeShape }}", S, "S del type"))

        L = "seams-nomin"
        bn = build(c, L, drop_mincount=True)
        print(f"== {L}: falsification arm, minCount guard dropped, blank node {bn}")
        step(c, L, "ARM: W JSON-LD (rdflib bytes, header id) delete minCount",
             jdel_hdr(c, L, rdflib_delete_body(bn), W, "W del minCount"))
        st, txt = step(c, L, "after: W commit ungoverned(doc-a)", ins(c, L, ungoverned(compiled_interior()), W, "W ungov"))
