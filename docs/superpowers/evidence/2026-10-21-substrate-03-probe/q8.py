"""q8: full bundle with a role-conditional (non-required) modify companion; two-step vs
single-transaction provisioning. Measurement only."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import *
from q1q3_fixed import VIEW_QUERY_FIXED
from q4b_q6_q7 import config_explicit, STEWARD_Q, SH_PREDS, CFG_PREDS, step, upd, jdel

ROLE_PREDS = [ETKL + "hasRole", PROV + "actedOnBehalfOf", ETKL + "grantsTag", ETKL + "sensitivity"]
ROLE_COMPANION_Q = json.dumps({"where": [{"@id": "?$identity", ETKL + "hasRole": {"@id": "?r"}}]})

def policies(companion):
    ps = [policy_node(ETKL + "sensitivityViewPolicyFixed", "view", VIEW_QUERY_FIXED),
          policy_node(EX + "guardShapesClass", "modify", STEWARD_Q, on_class=[SH + "NodeShape"]),
          policy_node(EX + "guardShapesProps", "modify", STEWARD_Q, on_property=SH_PREDS),
          policy_node(EX + "guardConfig", "modify", STEWARD_Q, on_property=CFG_PREDS),
          policy_node(EX + "guardRoles", "modify", STEWARD_Q, on_property=ROLE_PREDS)]
    if companion == "role":
        ps.append(policy_node(EX + "modifyCompanionRole", "modify", ROLE_COMPANION_Q, required=False))
    else:
        ps.append(policy_node(EX + "modifyCompanion", "modify", None, required=False, allow=True))
    return ps

def bnode(c, L):
    st, txt = c.sparql(L, "SELECT ?p WHERE { ex:DocShape sh:property ?p }", label=f"{L} root bnode (pre-config)")
    return json.loads(txt)["results"]["bindings"][0]["p"]["value"]

def build_two_step(c, L, companion):
    c.create(L); print(f"  t after create {c.t(L)}")
    c.insert_ttl(L, BASE_TTL, label=f"{L} base"); print(f"  t after base data+shapes+roles {c.t(L)}")
    bn = bnode(c, L)
    for p in policies(companion):
        store_policy(c, L, p)
    print(f"  t after {len(policies(companion))} policies {c.t(L)}")
    st, txt = c.update(L, config_explicit(L), label=f"{L} config"); assert st == 200, txt
    print(f"  t after #config {c.t(L)}")
    return bn

def lit(s):
    return "'''" + s.replace("\\", "\\\\") + "'''"

def policy_sparql(p):
    out = [f"<{p['@id']}> a f:AccessPolicy"]
    out.append("f:action " + ", ".join(f"<{a['@id']}>" for a in p[F + "action"]))
    if p.get(F + "required"): out.append("f:required true")
    if F + "allow" in p: out.append("f:allow true")
    for k in ("onClass", "onProperty"):
        if F + k in p: out.append(f"f:{k} " + ", ".join(f"<{x['@id']}>" for x in p[F + k]))
    if F + "query" in p: out.append("f:query " + lit(p[F + "query"]))
    return " ;\n  ".join(out) + " ."

def build_single(c, L, companion):
    c.create(L); print(f"  t after create {c.t(L)}")
    g = f"urn:fluree:{L}:main"
    data = """ex:DocShape a sh:NodeShape ; sh:targetClass ex:Doc ; sh:property [ sh:path ex:title ; sh:minCount 1 ] .
ex:d1 a ex:Doc ; ex:title "one" ; etkl:sensitivity ex:tagPublic .
ex:d2 a ex:Doc ; ex:title "two" ; etkl:sensitivity ex:tagClinical .
ex:d3 a ex:Doc ; ex:title "three" ; etkl:sensitivity ex:tagSecret .
ex:roleClinician etkl:grantsTag ex:tagPublic , ex:tagClinical .
ex:roleSteward etkl:grantsTag ex:tagPublic , ex:tagClinical , ex:tagSecret .
ex:U etkl:hasRole ex:roleClinician . ex:A prov:actedOnBehalfOf ex:U . ex:W etkl:hasRole ex:roleClinician .
ex:S etkl:hasRole ex:roleSteward . ex:B a prov:SoftwareAgent . ex:A a prov:SoftwareAgent ."""
    pols = "\n".join(policy_sparql(p) for p in policies(companion))
    for p in policies(companion): POLICIES_USED[p["@id"]] = p
    cfg = config_explicit(L).split("{", 1)[1].rsplit("}", 1)[0]  # the GRAPH block
    q = f"INSERT DATA {{\n{data}\n{pols}\n{cfg}\n}}"
    with open(os.path.join(HERE, f"q8_{L}_single_tx.rq"), "w") as fh: fh.write(PREFIXES + q)
    st, txt = c.update(L, q, label=f"{L} SINGLE tx: data+shapes+policies+#config")
    print(f"  single tx: {st} {short(txt,140)}; t after {c.t(L)}")
    # bnode label: root read may already be closed (config lags one tx?)
    st, txt = c.sparql(L, "SELECT ?p WHERE { ex:DocShape sh:property ?p }", label=f"{L} root bnode after single tx")
    from probe_lib import _nrows
    print(f"  root read after single tx: {st} rows={_nrows(txt)}")
    st2, txt2 = c.sparql(L, "SELECT ?p WHERE { ex:DocShape sh:property ?p }", ident(S), label=f"{L} S bnode read")
    print(f"  S read of property bnode: rows={_nrows(txt2)} (view hides untagged shapes)")
    b = json.loads(txt)["results"]["bindings"]
    return b[0]["p"]["value"] if b else None

def matrix(c, L, bn):
    V = 'INSERT DATA { ex:v%s a ex:Doc ; ex:title "v" ; etkl:sensitivity ex:tagPublic }'
    N = 'INSERT DATA { ex:n%s a ex:Doc ; ex:title "n" ; ex:note "doc-a style, no guarded predicate" }'
    I = 'INSERT DATA { ex:bad%s a ex:Doc ; ex:note "no title" }'
    DA = {"fluree-default-allow": "true"}
    print("  (a) anonymous")
    step(c, L, "anon INSERT valid doc (untagged)", upd(c, L, N % "a1", None, "anon insert"))
    step(c, L, "anon + default-allow INSERT valid doc", lambda: c.update(L, N % "a2", DA, label=f"{L} anon DA insert"))
    step(c, L, "anon INSERT ex:B hasRole roleSteward", upd(c, L, "INSERT DATA { ex:B etkl:hasRole ex:roleSteward }", None, "anon promote B"))
    step(c, L, "anon + default-allow INSERT ex:B hasRole roleSteward", lambda: c.update(L, "INSERT DATA { ex:B etkl:hasRole ex:roleSteward }", DA, label=f"{L} anon DA promote B"))
    print("  (b) B (identity, no role)")
    step(c, L, "B INSERT valid doc (untagged)", upd(c, L, N % "b1", B, "B insert"))
    step(c, L, "B + default-allow INSERT valid doc", lambda: c.update(L, N % "b2", {**ident(B), **DA}, label=f"{L} B DA insert"))
    print("  (c)/(g) W")
    step(c, L, "W INSERT valid doc WITH etkl:sensitivity tag", upd(c, L, V % "w1", W, "W insert tagged"))
    step(c, L, "(g) W INSERT doc-a style (ex:title, ex:note only)", upd(c, L, N % "w2", W, "W insert doc-a style"))
    step(c, L, "W INSERT invalid doc (no title)", upd(c, L, I % "w", W, "W invalid"))
    step(c, L, "W DELETE DATA targetClass", upd(c, L, "DELETE DATA { ex:DocShape sh:targetClass ex:Doc }", W, "W del targetClass"))
    if bn:
        step(c, L, f"W JSON-LD delete _:{bn} sh:minCount 1", jdel(c, L, {"@id": "_:" + bn, SH + "minCount": 1}, W, "W json del minCount"))
    step(c, L, "W self-promotion hasRole roleSteward", upd(c, L, "INSERT DATA { ex:W etkl:hasRole ex:roleSteward }", W, "W self-promote"))
    step(c, L, "W INSERT invalid doc again (gate still up?)", upd(c, L, I % "w2", W, "W invalid 2"))
    print("  (d) S")
    step(c, L, "S INSERT valid doc WITH sensitivity tag", upd(c, L, V % "s1", S, "S insert tagged"))
    step(c, L, "S DELETE DATA targetClass", upd(c, L, "DELETE DATA { ex:DocShape sh:targetClass ex:Doc }", S, "S del targetClass"))

if __name__ == "__main__":
    with server() as c:
        print("== q8two: two-step provisioning, role-conditional companion")
        bn = build_two_step(c, "q8two", "role"); matrix(c, "q8two", bn)
        print("\n== q8e: two-step, ORIGINAL unconditional companion + hasRole guard (e)")
        build_two_step(c, "q8e", "unconditional")
        step(c, "q8e", "anon INSERT ex:B hasRole roleSteward", upd(c, "q8e", "INSERT DATA { ex:B etkl:hasRole ex:roleSteward }", None, "anon promote B"))
        step(c, "q8e", "anon + default-allow INSERT ex:B hasRole roleSteward", lambda: c.update("q8e", "INSERT DATA { ex:B etkl:hasRole ex:roleSteward }", {"fluree-default-allow": "true"}, label="q8e anon DA promote B"))
        step(c, "q8e", "anon INSERT valid doc (untagged)", upd(c, "q8e", 'INSERT DATA { ex:e1 a ex:Doc ; ex:title "e" }', None, "anon insert"))
        print("\n== q8one: SINGLE-transaction provisioning, role-conditional companion (f)")
        bn = build_single(c, "q8one", "role"); matrix(c, "q8one", bn)
        print(c.dump("q8"), dump_policies("q8"))
