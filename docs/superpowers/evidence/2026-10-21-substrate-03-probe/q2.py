import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import *
from q1q3_fixed import VIEW_QUERY_FIXED

ALLOW_ALL = json.dumps([{"@id": EX + "inlineAllowAll", "@type": [F + "AccessPolicy"],
                         F + "action": [{"@id": F + "view"}, {"@id": F + "modify"}], F + "allow": True}])
POLICIES_USED[EX + "inlineAllowAll (fluree-policy header)"] = json.loads(ALLOW_ALL)

def config_trig(L):
    return f"""INSERT DATA {{ GRAPH <urn:fluree:{L}:main#config> {{
  <urn:fluree:{L}:main:config:ledger> a f:LedgerConfig ;
    f:policyDefaults [ f:defaultAllow false ; f:policyClass f:AccessPolicy ; f:overrideControl f:OverrideNone ] .
}} }}"""

COMBOS = [
    ("no headers", {}),
    ("default-allow:true", {"fluree-default-allow": "true"}),
    ("inline allow-all", {"fluree-policy": ALLOW_ALL}),
    ("default-allow + inline", {"fluree-default-allow": "true", "fluree-policy": ALLOW_ALL}),
    ("policy-class only", {"fluree-policy-class": PC}),
    ("identity S + class", ident(S)),
    ("identity S + class + default-allow", {**ident(S), "fluree-default-allow": "true"}),
    ("identity B + class + inline allow-all", {**ident(B), "fluree-policy": ALLOW_ALL}),
    ("identity B + default-allow", {"fluree-identity": B, "fluree-default-allow": "true"}),
]

def matrix(c, L, phase):
    for name, h in COMBOS:
        st, n, txt = c.count_docs(L, h, label=f"{phase} query {name}")
        t0 = c.t(L)
        tag = abs(hash(name)) % 10**6
        st2, txt2 = c.update(L, f'INSERT DATA {{ ex:w{tag} a ex:Doc ; ex:title "w" }}', h, label=f"{phase} write {name}")
        print(f"[{phase}] {name:40s} query {st} rows={n} {'' if st==200 else short(txt,90)} | write {st2} t {t0}->{c.t(L)} {short(txt2,90)}")
    # PRAGMA forms
    st, n, txt = c.sparql(L, "# PRAGMA default-allow: true\nSELECT ?d WHERE { ?d a ex:Doc }", label=f"{phase} query PRAGMA default-allow")[0], None, None
    st, txt = c.sparql(L, "# PRAGMA default-allow: true\nSELECT ?d WHERE { ?d a ex:Doc }", label=f"{phase} query PRAGMA default-allow")
    from probe_lib import _nrows
    t0 = c.t(L)
    st2, txt2 = c.update(L, '# PRAGMA default-allow: true\nINSERT DATA { ex:wpragma a ex:Doc ; ex:title "w" }', label=f"{phase} write PRAGMA default-allow")
    print(f"[{phase}] {'PRAGMA default-allow: true':40s} query {st} rows={_nrows(txt)} | write {st2} t {t0}->{c.t(L)} {short(txt2,90)}")
    # JSON opts default-allow
    q = {"select": ["?d"], "where": [{"@id": "?d", "@type": EX + "Doc"}], "opts": {"default-allow": True}}
    st, txt = c.jsonq(L, q, label=f"{phase} json opts default-allow")
    print(f"[{phase}] json opts.default-allow query {st} rows={_nrows(txt)} {short(txt,90)}")

if __name__ == '__main__':
    with server() as c:
        L = "q2"; c.create(L); c.insert_ttl(L, BASE_TTL, label="base")
        store_policy(c, L, policy_node(ETKL + "sensitivityViewPolicyFixed", "view", VIEW_QUERY_FIXED))
        # side check (Q1): f:policyClass on the identity node, identity header only
        c.update(L, "INSERT DATA { ex:U f:policyClass f:AccessPolicy }", label="U f:policyClass")
        st, n, _ = c.count_docs(L, {"fluree-identity": U}, label="Q1 U identity-only, node carries f:policyClass")
        print("Q1 identity-only with node f:policyClass: rows", n)
        print("head t before config", c.t(L))
        matrix(c, L, "pre-config")
        t0 = c.t(L)
        st, txt = c.update(L, config_trig(L), label="commit #config policyDefaults")
        print("CONFIG", st, short(txt, 150), t0, "->", c.t(L))
        # read config graph back (root)
        st, txt = c.sparql(L, f"SELECT ?s ?p ?o FROM <urn:fluree:{L}:main#config> WHERE {{ ?s ?p ?o }}", label="read config graph")
        print("config read", st, short(txt, 300))
        matrix(c, L, "post-config")
        # positive controls
        for who in (U, A, B, S):
            st, n, txt = c.count_docs(L, ident(who), label=f"post-config view {who}")
            print("post-config view", who, st, n)
        print(c.dump("q2"), dump_policies("q2"))
