import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import *

VIEW_QUERY_FIXED = json.dumps({"where": [
    ["union",
     [{"@id": "?$identity", PROV + "actedOnBehalfOf": {"@id": "?principal"}},
      {"@id": "?principal", ETKL + "hasRole": {"@id": "?role"}}],
     [{"@id": "?$identity", ETKL + "hasRole": {"@id": "?role"}}]],
    {"@id": "?role", ETKL + "grantsTag": {"@id": "?tag"}},
    {"@id": "?$this", ETKL + "sensitivity": {"@id": "?tag"}}]})

def counts(c, L, tag):
    out = {}
    st, n, _ = c.count_docs(L, label=f"{tag} no-identity"); out["none"] = (st, n)
    for who in (U, A, B, W, S):
        st, n, txt = c.count_docs(L, ident(who), label=f"{tag} {who} hdr+class")
        out[who.rsplit('/',1)[1]] = (st, n)
    st, n, txt = c.count_docs(L, ident(U, policy_class=False), label=f"{tag} U hdr no class")
    out["U-noclass"] = (st, n, short(txt, 120))
    # JSON opts.identity
    q = {"from": L, "select": ["?d"], "where": [{"@id": "?d", "@type": EX + "Doc"}],
         "opts": {"identity": U, "policyClass": PC}}
    st, txt = c.jsonq(L, q, label=f"{tag} U json opts.identity+policyClass"); out["U-json"] = (st, _n(txt), short(txt,120))
    q["opts"] = {"identity": U}
    st, txt = c.jsonq(L, q, label=f"{tag} U json opts.identity only"); out["U-json-noclass"] = (st, _n(txt), short(txt,120))
    q.pop("opts")
    st, txt = c.jsonq(L, q, label=f"{tag} json no opts"); out["json-none"] = (st, _n(txt))
    return out

def _n(txt):
    try: v = json.loads(txt); return len(v) if isinstance(v, list) else None
    except ValueError: return None

with server() as c:
    # ---------- Q3 as-is template
    L = "q3asis"; c.create(L); c.insert_ttl(L, BASE_TTL, label="base")
    store_policy(c, L, policy_node(ETKL + "sensitivityViewPolicy", "view", VIEW_QUERY_ASIS))
    print("t", c.t(L))
    print("AS-IS", counts(c, L, "asis"))
    # data fix: U is own principal
    t0 = c.t(L); st, txt = c.update(L, "INSERT DATA { ex:U prov:actedOnBehalfOf ex:U }", label="U self-principal (no identity)")
    print("insert U aoBo U", st, t0, "->", c.t(L))
    print("AS-IS + U aoBo U", counts(c, L, "asis+self"))

    # ---------- Q3 fixed chain (union)
    L = "q3fixed"; c.create(L); c.insert_ttl(L, BASE_TTL, label="base")
    POLICIES_USED.pop(ETKL + "sensitivityViewPolicy", None)
    store_policy(c, L, policy_node(ETKL + "sensitivityViewPolicyFixed", "view", VIEW_QUERY_FIXED))
    print("FIXED", counts(c, L, "fixed"))

    # ---------- Q1 writes: steward-only modify policy (required) + view fixed
    store_policy(c, L, policy_node(EX + "stewardModify", "modify", json.dumps({"where": [
        {"@id": "?$identity", ETKL + "hasRole": {"@id": EX + "roleSteward"}}]})))
    for who in (W, S):
        nm = who.rsplit('/',1)[1]
        t0 = c.t(L); st, txt = c.insert_ttl(L, f'<{EX}x{nm}1> a <{EX}Doc> ; <{EX}title> "x" .', ident(who), label=f"Q1 /insert ttl as {nm}")
        print(f"/insert {nm}", st, short(txt,150), t0, "->", c.t(L))
        t0 = c.t(L); st, txt = c.update(L, f'INSERT DATA {{ ex:x{nm}2 a ex:Doc ; ex:title "x" }}', ident(who), label=f"Q1 /update sparql as {nm}")
        print(f"/update {nm}", st, short(txt,150), t0, "->", c.t(L))
        t0 = c.t(L)
        body = {"ledger": L, "insert": {"@id": f"{EX}x{nm}3", "@type": EX + "Doc", EX + "title": "x"},
                "opts": {"identity": who, "policyClass": PC}}
        st, txt = c.req("POST", f"/v1/fluree/update/{L}", json.dumps(body), {"Content-Type": "application/json"}, label=f"Q1 /update json opts.identity as {nm}")
        print(f"/update json opts {nm}", st, short(txt,150), t0, "->", c.t(L))
    t0 = c.t(L); st, txt = c.update(L, 'INSERT DATA { ex:xnone a ex:Doc ; ex:title "x" }', label="Q1 /update no identity")
    print("/update no identity", st, short(txt,150), t0, "->", c.t(L))
    t0 = c.t(L); st, txt = c.update(L, 'INSERT DATA { ex:xnoclass a ex:Doc ; ex:title "x" }', ident(W, False), label="Q1 /update W no class")
    print("/update W identity no class", st, short(txt,150), t0, "->", c.t(L))
    print(c.dump("q1q3"), dump_policies("q1q3"))
