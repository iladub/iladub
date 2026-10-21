import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import *
from q1q3_fixed import VIEW_QUERY_FIXED
with server() as c:
    L = "q1json"; c.create(L); c.insert_ttl(L, BASE_TTL, label="base")
    store_policy(c, L, policy_node(ETKL + "sensitivityViewPolicyFixed", "view", VIEW_QUERY_FIXED))
    base = {"select": ["?d"], "where": [{"@id": "?d", "@type": EX + "Doc"}]}
    for frm in (None, L + ":main"):
        for opts in (None, {"identity": U, "policyClass": PC}, {"identity": U}, {"identity": S, "policyClass": PC}, {"identity": B, "policyClass": PC}):
            q = dict(base)
            if frm: q["from"] = frm
            if opts: q["opts"] = opts
            st, txt = c.jsonq(L, q, label=f"Q1 json from={frm} opts={opts}")
            print(frm, opts, st, short(txt, 100))
    # also /v1/fluree/query (no ledger in path)
    q = dict(base, **{"from": L + ":main", "opts": {"identity": U, "policyClass": PC}})
    st, txt = c.req("POST", "/v1/fluree/query", json.dumps(q), {"Content-Type": "application/json"}, label="Q1 json /v1/fluree/query U")
    print("/v1/fluree/query", st, short(txt, 100))
    print(c.dump("q1json"))
