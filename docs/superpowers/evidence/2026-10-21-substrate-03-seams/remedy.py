"""substrate:03: candidate remedy for tamper.py's hole. Adds a steward-only guard onClass
f:AccessPolicy and one onProperty over the policy predicates; re-runs every tamper case, plus the
config node's type retraction, with and without the remedy. Measurement only. Run as seams.py is."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seams
from seams import *  # noqa
from tamper import CASES, TC

POL_PREDS = [F + p for p in ("action", "required", "query", "onClass", "onProperty", "allow")]
_base = seams.bundle


def remedied(**kw):
    return _base(**kw) + [
        policy_node(EX + "guardPolicyClass", "modify", STEWARD_Q, on_class=[F + "AccessPolicy"]),
        policy_node(EX + "guardPolicyProps", "modify", STEWARD_Q, on_property=POL_PREDS)]


def cfg_type(L):
    g = f"urn:fluree:{L}:main"
    return f"DELETE DATA {{ GRAPH <{g}#config> {{ <{g}:config:ledger> a f:LedgerConfig }} }}"


if __name__ == "__main__":
    with server() as c:
        for name, fn in (("base", _base), ("remedy", remedied)):
            seams.bundle = fn
            cases = CASES + [("W DELETE config node a f:LedgerConfig", None)]
            for i, (label, q) in enumerate(cases):
                L = f"{name}{i}"
                bn = build(c, L)
                print(f"== {L} ({name})")
                step(c, L, label, upd(c, L, q or cfg_type(L), W, label))
                step(c, L, "  then: W delete blank-node sh:minCount",
                     jdel_hdr(c, L, rdflib_delete_body(bn), W, "W del minCount"))
                step(c, L, "  then: W commit ungoverned(doc-a)",
                     ins(c, L, ungoverned(compiled_interior()), W, "W ungov"))
                if name == "remedy" and i == 0:
                    step(c, L, "  control: W commit compiled_interior()", ins(c, L, compiled_interior(), W, "W doc-a"))
                    step(c, L, "  control: S DELETE guardShapesProps a f:AccessPolicy",
                         upd(c, L, f"DELETE DATA {{ <{EX}guardShapesProps> a f:AccessPolicy }}", S, "S del pol"))
