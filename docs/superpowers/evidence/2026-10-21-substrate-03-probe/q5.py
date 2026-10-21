import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import *
from q1q3_fixed import VIEW_QUERY_FIXED

POLICY_DEFAULTS = "f:policyDefaults [ f:defaultAllow false ; f:policyClass f:AccessPolicy ; f:overrideControl f:OverrideNone ]"
SHACL_DEFAULTS = "f:shaclDefaults [ f:shaclEnabled true ; f:validationMode f:ValidationReject ; f:overrideControl f:OverrideNone ]"

def config(L, *groups):
    body = " ;\n    ".join(groups)
    sep = " ;\n    " if groups else ""
    return f"""INSERT DATA {{ GRAPH <urn:fluree:{L}:main#config> {{
  <urn:fluree:{L}:main:config:ledger> a f:LedgerConfig{sep}{body} .
}} }}"""

def setup(c, L, groups, policies=True):
    c.create(L); c.insert_ttl(L, BASE_TTL, label="base")
    if policies:
        store_policy(c, L, policy_node(ETKL + "sensitivityViewPolicyFixed", "view", VIEW_QUERY_FIXED))
        store_policy(c, L, policy_node(EX + "modifyCompanion", "modify", None, required=False, allow=True))
    if groups is not None:
        q = config(L, *groups)
        st, txt = c.update(L, q, label=f"{L} config")
        print(f"  config commit: {st} {short(txt,80)}\n  config body: {' '.join(q.split())}")

def attempt(c, L, label, h, pragma=""):
    t0 = c.t(L)
    st, txt = c.update(L, pragma + 'INSERT DATA { ex:bad a ex:Doc ; etkl:sensitivity ex:tagPublic }', h, label=f"{L} {label}")
    print(f"  {label:55s} {st} t {t0}->{c.t(L)} {short(txt,140)}")

with server() as c:
    cases = [
        ("q5none", None, True, "no config (control)"),
        ("q5bare", [], False, "bare f:LedgerConfig, no policies, no groups"),
        ("q5pol", [POLICY_DEFAULTS], True, "LedgerConfig with policyDefaults only"),
        ("q5both", [POLICY_DEFAULTS, SHACL_DEFAULTS], True, "policyDefaults + explicit shaclDefaults"),
        ("q5shonly", [SHACL_DEFAULTS], False, "shaclDefaults only, no policies"),
    ]
    for L, groups, pols, desc in cases:
        print(f"\n== {L}: {desc}")
        setup(c, L, groups, pols)
        if pols:
            attempt(c, L, "W (identity+class) insert invalid ex:Doc", ident(W))
            attempt(c, L, "W + PRAGMA validation-mode: warn", ident(W), "# PRAGMA validation-mode: warn\n")
        if L in ("q5none", "q5bare", "q5shonly"):
            attempt(c, L, "no identity insert invalid ex:Doc", {})
            attempt(c, L, "no identity + PRAGMA validation-mode: warn", {}, "# PRAGMA validation-mode: warn\n")
    print(c.dump("q5"), dump_policies("q5"))
