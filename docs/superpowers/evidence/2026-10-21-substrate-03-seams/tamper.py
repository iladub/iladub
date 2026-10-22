"""(rev 2: follow-ups also target the blank node, which onClass does not cover)\nsubstrate:03: can W tamper with the POLICY nodes themselves? (not in spec § 4.3's closure set).
Each case on a fresh governed ledger; after the tamper attempt, W retries the shape retraction it
was refused. Measurement only. Run as seams.py is."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seams import *  # noqa

GP = f"<{EX}guardShapesProps>"
GC = f"<{EX}guardShapesClass>"
TC = f"DELETE DATA {{ {GN} sh:targetClass <https://w3id.org/iladub#GroundedNode> }}"
CASES = [
    ("W DELETE guardShapesProps f:onProperty sh:targetClass", f"DELETE DATA {{ {GP} f:onProperty sh:targetClass }}"),
    ("W DELETE guardShapesProps f:required true", f"DELETE DATA {{ {GP} f:required true }}"),
    ("W DELETE guardShapesProps a f:AccessPolicy", f"DELETE DATA {{ {GP} a f:AccessPolicy }}"),
    ("W DELETE guardShapesProps f:action f:modify", f"DELETE DATA {{ {GP} f:action f:modify }}"),
    ("W INSERT a non-required modify allow-true policy",
     f"INSERT DATA {{ <{EX}wAllow> a f:AccessPolicy ; f:action f:modify ; f:allow true }}"),
    ("W INSERT a required modify allow-true policy onProperty targetClass",
     f"INSERT DATA {{ <{EX}wAllow2> a f:AccessPolicy ; f:action f:modify ; f:required true ; f:allow true ; f:onProperty sh:targetClass }}"),
]
if __name__ == "__main__":
    with server() as c:
        for i, (label, q) in enumerate(CASES):
            L = f"tamper{i}"
            bn = build(c, L)
            print(f"== {L}")
            step(c, L, label, upd(c, L, q, W, label))
            step(c, L, "  then: W DELETE DATA GroundedNodeShape sh:targetClass", upd(c, L, TC, W, "W del tc"))
            step(c, L, "  then: W delete blank-node sh:minCount (guardShapesProps only)",
                 jdel_hdr(c, L, rdflib_delete_body(bn), W, "W del minCount"))
            st, txt = step(c, L, "  then: W commit ungoverned(doc-a)",
                           ins(c, L, ungoverned(compiled_interior()), W, "W ungov"))
