"""Follow-up to q7: is an anonymous (no-identity) write admitted once the non-required
{f:modify, f:allow true} companion exists? Separates companion vs config IRI form."""
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import *
from q1q3_fixed import VIEW_QUERY_FIXED
from q2 import config_trig
from q4b_q6_q7 import config_explicit, STEWARD_Q, step, upd

with server() as c:
    for L, cfg, comp in (("anonA", config_trig, False), ("anonB", config_trig, True),
                         ("anonC", config_explicit, False), ("anonD", config_explicit, True)):
        c.create(L); c.insert_ttl(L, BASE_TTL, label=f"{L} base")
        store_policy(c, L, policy_node(ETKL + "sensitivityViewPolicyFixed", "view", VIEW_QUERY_FIXED))
        store_policy(c, L, policy_node(EX + "guardShapesClass", "modify", STEWARD_Q, on_class=[SH + "NodeShape"]))
        if comp:
            store_policy(c, L, policy_node(EX + "modifyCompanion", "modify", None, required=False, allow=True))
        st, txt = c.update(L, cfg(L), label=f"{L} config"); assert st == 200, txt
        print(f"[{L}] config={'bnode policyDefaults (Q2 form)' if cfg is config_trig else 'explicit IRIs + shacl'} companion={comp}")
        step(c, L, "anon INSERT DATA valid ex:Doc", upd(c, L, 'INSERT DATA { ex:anon a ex:Doc ; ex:title "a" }', None, "anon insert"))
        step(c, L, "anon + fluree-default-allow:true INSERT", lambda: c.update(L, 'INSERT DATA { ex:anon2 a ex:Doc ; ex:title "a" }', {"fluree-default-allow": "true"}, label=f"{L} anon default-allow insert"))
        step(c, L, "anon DELETE DATA { DocShape sh:targetClass ex:Doc }", upd(c, L, "DELETE DATA { ex:DocShape sh:targetClass ex:Doc }", None, "anon del targetClass"))
        step(c, L, "anon INSERT DATA { ex:B etkl:hasRole ex:roleSteward }", upd(c, L, "INSERT DATA { ex:B etkl:hasRole ex:roleSteward }", None, "anon promote B"))
        st, n, _ = c.count_docs(L, {}, label=f"{L} anon view"); print(f"    anon view rows: {n}")
    print(c.dump("anon_companion"), dump_policies("anon_companion"))
