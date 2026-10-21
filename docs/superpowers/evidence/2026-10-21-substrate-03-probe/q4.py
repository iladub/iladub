import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import *
from probe_lib import _nrows
from q1q3_fixed import VIEW_QUERY_FIXED
from q2 import config_trig

STEWARD_Q = json.dumps({"where": [{"@id": "?$identity", ETKL + "hasRole": {"@id": EX + "roleSteward"}}]})
SH_PREDS = [SH + p for p in ("targetClass", "property", "path", "minCount")]

def bnode_of(c, L):
    st, txt = c.sparql(L, "SELECT ?p WHERE { ex:DocShape sh:property ?p }", label="root: find property-shape bnode")
    return json.loads(txt)["results"]["bindings"][0]["p"]["value"]

def mincount_present(c, L):
    st, txt = c.sparql(L, "SELECT ?m WHERE { ex:DocShape sh:property ?p . ?p sh:minCount ?m }", label="root: minCount present?")
    return _nrows(txt)

def targetclass_present(c, L):
    st, txt = c.sparql(L, "SELECT ?c WHERE { ex:DocShape sh:targetClass ?c }", label="root: targetClass present?")
    return _nrows(txt)

def step(c, L, label, fn):
    t0 = c.t(L); st, txt = fn(); t1 = c.t(L)
    print(f"  {label:70s} {st} t {t0}->{t1} {short(txt,110) if st!=200 else ''}")
    return st

def build(c, L, guard_props, companion):
    c.create(L); c.insert_ttl(L, BASE_TTL, label="base")
    store_policy(c, L, policy_node(ETKL + "sensitivityViewPolicyFixed", "view", VIEW_QUERY_FIXED))
    store_policy(c, L, policy_node(EX + "guardShapesClass", "modify", STEWARD_Q, on_class=[SH + "NodeShape"]))
    if guard_props:
        store_policy(c, L, policy_node(EX + "guardShapesProps", "modify", STEWARD_Q, on_property=SH_PREDS))
    if companion:
        store_policy(c, L, policy_node(EX + "modifyCompanion", "modify", None, required=False, allow=True))
    bn = bnode_of(c, L)  # read as root BEFORE config: after it, no-identity reads return 0 rows
    st, txt = c.update(L, config_trig(L), label="config")
    assert st == 200, txt
    print("  post-config root read of targetClass rows:", targetclass_present(c, L))
    return bn

def run_variant(c, L, guard_props, companion):
    print(f"\n== {L}: guard onClass NodeShape{' + onProperty sh:*' if guard_props else ''}; companion={companion}")
    bn = build(c, L, guard_props, companion); print("  property-shape bnode id:", bn)
    step(c, L, "W INSERT DATA valid ex:Doc", lambda: c.update(L, 'INSERT DATA { ex:dw a ex:Doc ; ex:title "w" ; etkl:sensitivity ex:tagPublic }', ident(W), label=f"{L} W insert valid"))
    step(c, L, "S INSERT DATA valid ex:Doc", lambda: c.update(L, 'INSERT DATA { ex:ds a ex:Doc ; ex:title "s" ; etkl:sensitivity ex:tagPublic }', ident(S), label=f"{L} S insert valid"))
    step(c, L, "W DELETE DATA { DocShape sh:targetClass ex:Doc }", lambda: c.update(L, "DELETE DATA { ex:DocShape sh:targetClass ex:Doc }", ident(W), label=f"{L} W delete targetClass"))
    step(c, L, "W SPARQL DELETE{?p sh:minCount ?m} WHERE{DocShape sh:property ?p...}", lambda: c.update(L, "DELETE { ?p sh:minCount ?m } WHERE { ex:DocShape sh:property ?p . ?p sh:minCount ?m }", ident(W), label=f"{L} W delete minCount via WHERE"))
    body = {"delete": {"@id": bn, SH + "minCount": 1}, "opts": {"identity": W, "policyClass": PC}}
    step(c, L, f"W JSON-LD delete {{@id {bn}, sh:minCount 1}}", lambda: c.req("POST", f"/v1/fluree/update/{L}", json.dumps(body), {"Content-Type": "application/json"}, label=f"{L} W json delete bnode minCount"))
    step(c, L, "W INSERT invalid ex:Doc (no title) — is the gate up?", lambda: c.update(L, 'INSERT DATA { ex:bad1 a ex:Doc ; etkl:sensitivity ex:tagPublic }', ident(W), label=f"{L} W insert invalid #1"))
    step(c, L, "W DELETE guard policy's f:required (policy tamper)", lambda: c.update(L, f"DELETE DATA {{ ex:guardShapesClass f:required true }}", ident(W), label=f"{L} W tamper guard"))
    step(c, L, "S DELETE DATA { DocShape sh:targetClass ex:Doc }", lambda: c.update(L, "DELETE DATA { ex:DocShape sh:targetClass ex:Doc }", ident(S), label=f"{L} S delete targetClass"))
    step(c, L, "W INSERT invalid ex:Doc (no title) after S retraction", lambda: c.update(L, 'INSERT DATA { ex:bad2 a ex:Doc ; etkl:sensitivity ex:tagPublic }', ident(W), label=f"{L} W insert invalid #2"))

def trap2(c, L):
    print(f"\n== {L}: trap 2 — DELETE…WHERE by an identity whose view hides the rows")
    build(c, L, True, True)
    for who in (B, U):
        st, n, _ = c.count_docs(L, ident(who), label=f"{L} view {who}")
        print(f"  {who} sees {n} docs")
    step(c, L, "B DELETE {?d ex:title ?t} WHERE {?d a ex:Doc; ex:title ?t}", lambda: c.update(L, "DELETE { ?d ex:title ?t } WHERE { ?d a ex:Doc ; ex:title ?t }", ident(B), label=f"{L} B delete where"))
    step(c, L, "U DELETE {ex:d3 ex:title ?t} WHERE {ex:d3 ex:title ?t} (d3 secret)", lambda: c.update(L, "DELETE { ex:d3 ex:title ?t } WHERE { ex:d3 ex:title ?t }", ident(U), label=f"{L} U delete hidden d3"))
    step(c, L, "U DELETE DATA { ex:d3 ex:title \"three\" } (hidden row, ground)", lambda: c.update(L, 'DELETE DATA { ex:d3 ex:title "three" }', ident(U), label=f"{L} U delete data hidden d3"))
    st, n, _ = c.count_docs(L, ident(S), label="S view after"); 
    st, txt = c.sparql(L, "SELECT ?d ?t WHERE { ?d ex:title ?t }", ident(S), label="S titles after"); print("  S (sees all tagged) title rows after:", _nrows(txt), short(txt, 300))

with server() as c:
    run_variant(c, "q4nocomp", guard_props=False, companion=False)
    run_variant(c, "q4class", guard_props=False, companion=True)
    run_variant(c, "q4props", guard_props=True, companion=True)
    trap2(c, "q4trap2")
    print(c.dump("q4"), dump_policies("q4"))
