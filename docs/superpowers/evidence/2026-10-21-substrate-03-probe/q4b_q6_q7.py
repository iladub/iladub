"""Q4 redone with SHACL explicitly enabled in the config (q5 showed a LedgerConfig without
f:shaclDefaults disables SHACL, which confounds the 'is the gate up?' check) and with the
blank node addressed as '_:<label>'; plus Q6 (self-promotion) and Q7 (config tamper)."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import *
from q1q3_fixed import VIEW_QUERY_FIXED

STEWARD_Q = json.dumps({"where": [{"@id": "?$identity", ETKL + "hasRole": {"@id": EX + "roleSteward"}}]})
SH_PREDS = [SH + p for p in ("targetClass", "property", "path", "minCount")]
CFG_PREDS = [F + p for p in ("shaclEnabled", "validationMode", "shaclDefaults", "policyDefaults",
                             "defaultAllow", "policyClass", "overrideControl")]

def config_explicit(L):
    g = f"urn:fluree:{L}:main"
    return f"""INSERT DATA {{ GRAPH <{g}#config> {{
  <{g}:config:ledger> a f:LedgerConfig ; f:policyDefaults <{g}:config:policy> ; f:shaclDefaults <{g}:config:shacl> .
  <{g}:config:policy> f:defaultAllow false ; f:policyClass f:AccessPolicy ; f:overrideControl f:OverrideNone .
  <{g}:config:shacl> f:shaclEnabled true ; f:validationMode f:ValidationReject ; f:overrideControl f:OverrideNone .
}} }}"""

def build(c, L, extra_guards=()):
    c.create(L); c.insert_ttl(L, BASE_TTL, label=f"{L} base")
    st, txt = c.sparql(L, "SELECT ?p WHERE { ex:DocShape sh:property ?p }", label=f"{L} root: bnode label (pre-config)")
    bn = json.loads(txt)["results"]["bindings"][0]["p"]["value"]
    store_policy(c, L, policy_node(ETKL + "sensitivityViewPolicyFixed", "view", VIEW_QUERY_FIXED))
    store_policy(c, L, policy_node(EX + "guardShapesClass", "modify", STEWARD_Q, on_class=[SH + "NodeShape"]))
    for pid, preds in extra_guards:
        store_policy(c, L, policy_node(pid, "modify", STEWARD_Q, on_property=preds))
    store_policy(c, L, policy_node(EX + "modifyCompanion", "modify", None, required=False, allow=True))
    q = config_explicit(L)
    st, txt = c.update(L, q, label=f"{L} config (policy+shacl, explicit group IRIs)")
    assert st == 200, txt
    print(f"  [{L}] guards: guardShapesClass{''.join(' + '+g[0].rsplit('/',1)[1] for g in extra_guards)}; bnode={bn}; head t={c.t(L)}")
    return bn

def step(c, L, label, fn):
    t0 = c.t(L); st, txt = fn(); t1 = c.t(L)
    print(f"    {label:66s} {st} t {t0}->{t1} {short(txt,100) if st!=200 else ''}")
    return st

def upd(c, L, q, who, label):
    return lambda: c.update(L, q, ident(who) if who else {}, label=f"{L} {label}")

def jdel(c, L, node, who, label):
    body = {"delete": node, "opts": {"identity": who, "policyClass": PC}}
    return lambda: c.req("POST", f"/v1/fluree/update/{L}", json.dumps(body), {"Content-Type": "application/json"}, label=f"{L} {label}")

INVALID = 'INSERT DATA { ex:bad%d a ex:Doc ; etkl:sensitivity ex:tagPublic }'

if __name__ == '__main__':
    with server() as c:
        print("\n=== Q4 (SHACL on): trap 1")
        for L, guards in (("q4bclass", ()), ("q4bprops", ((EX + "guardShapesProps", SH_PREDS),))):
            bn = build(c, L, guards)
            step(c, L, "W insert invalid ex:Doc (control: gate up?)", upd(c, L, INVALID % 0, W, "W invalid ctl"))
            step(c, L, "W DELETE DATA { DocShape sh:targetClass ex:Doc }", upd(c, L, "DELETE DATA { ex:DocShape sh:targetClass ex:Doc }", W, "W del targetClass"))
            step(c, L, "W SPARQL DELETE {?p sh:minCount ?m} WHERE {...}", upd(c, L, "DELETE { ?p sh:minCount ?m } WHERE { ex:DocShape sh:property ?p . ?p sh:minCount ?m }", W, "W del minCount WHERE"))
            step(c, L, f"W JSON-LD delete {{@id _:{bn}, sh:minCount 1}}", jdel(c, L, {"@id": "_:" + bn, SH + "minCount": 1}, W, "W json del bnode minCount"))
            step(c, L, "W insert invalid ex:Doc (gate after W's attempts)", upd(c, L, INVALID % 1, W, "W invalid after"))
        print("\n=== Q4 steward retraction (SHACL on)")
        L = "q4bsteward"; bn = build(c, L, ((EX + "guardShapesProps", SH_PREDS),))
        step(c, L, "S DELETE DATA { DocShape sh:targetClass ex:Doc }", upd(c, L, "DELETE DATA { ex:DocShape sh:targetClass ex:Doc }", S, "S del targetClass"))
        step(c, L, "W insert invalid ex:Doc after S retraction", upd(c, L, INVALID % 2, W, "W invalid after S"))

        print("\n=== Q6 self-promotion")
        for L, guards in (("q6noguard", ()), ("q6roleguard", ((EX + "guardRole", [ETKL + "hasRole"]),))):
            build(c, L, guards)
            step(c, L, "W INSERT DATA { ex:W etkl:hasRole ex:roleSteward }", upd(c, L, "INSERT DATA { ex:W etkl:hasRole ex:roleSteward }", W, "W self-promote"))
            st, n, _ = c.count_docs(L, ident(W), label=f"{L} W view after")
            print(f"    W now sees {n} docs (3 = steward-level view)")
            step(c, L, "W DELETE DATA { DocShape sh:targetClass ex:Doc } (acting as steward)", upd(c, L, "DELETE DATA { ex:DocShape sh:targetClass ex:Doc }", W, "W del targetClass post-promo"))
            step(c, L, "W insert invalid ex:Doc", upd(c, L, INVALID % 3, W, "W invalid post-promo"))
            step(c, L, "S INSERT DATA { ex:U etkl:hasRole ex:roleSteward } (steward grants)", upd(c, L, "INSERT DATA { ex:U etkl:hasRole ex:roleSteward }", S, "S grants U"))

        print("\n=== Q7 config tamper")
        for L, guards in (("q7noguard", ()), ("q7cfgguard", ((EX + "guardConfig", CFG_PREDS),))):
            build(c, L, guards)
            g = f"urn:fluree:{L}:main"
            step(c, L, "W DELETE DATA { GRAPH #config { <..:shacl> f:shaclEnabled true } }", upd(c, L, f"DELETE DATA {{ GRAPH <{g}#config> {{ <{g}:config:shacl> f:shaclEnabled true }} }}", W, "W del shaclEnabled"))
            step(c, L, "W insert invalid ex:Doc (next tx; lagging config)", upd(c, L, INVALID % 4, W, "W invalid after cfg tamper"))
            step(c, L, "W DELETE DATA { GRAPH #config { <..:policy> f:defaultAllow false } }", upd(c, L, f"DELETE DATA {{ GRAPH <{g}#config> {{ <{g}:config:policy> f:defaultAllow false }} }}", W, "W del defaultAllow"))
            st, n, _ = c.count_docs(L, {}, label=f"{L} no-identity view after defaultAllow tamper")
            print(f"    no-identity query rows after defaultAllow tamper: {n}")
            step(c, L, "no-identity write after defaultAllow tamper", upd(c, L, 'INSERT DATA { ex:anon a ex:Doc ; ex:title "a" }', None, "anon write"))
        print(c.dump("q4b_q6_q7"), dump_policies("q4b_q6_q7"))
