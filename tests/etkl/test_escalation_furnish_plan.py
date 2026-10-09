"""The furnish query's WHERE is ONE basic graph pattern (R303).

`escalation-furnish.rq` runs on every compiled document. Its evidence set is a closed list of
labels, and the way that list is written decides the cost. MEASURED 2026-10-09: written as a
`VALUES` block mid-group, it split the WHERE into `Join(Join(BGP, VALUES), BGP)`. rdflib evaluates a
Join over a Join non-lazily, so the second BGP ran unbound, and `?o rdfs:label ?label` x
`?d dec:regarding ?r` share no variable. On a synthetic graph that is 220 s at N=300 decisions
against 0.10 s for one BGP, and held-out arxiv's compile ran past 40 min against about 3 before.

The output was identical either way, so no test that reads the derived graph can see this. The
algebra can: one BGP means no Join node on the main spine.
"""
import os

from rdflib.plugins.sparql import prepareQuery

RQ = os.path.join(os.path.dirname(__file__), "..", "..", "vocab", "queries",
                  "escalation-furnish.rq")


def _spine(node):
    """The algebra nodes from the query root down through `p`/`p1`/`p2`."""
    out = [node.name]
    for key in ("p", "p1", "p2"):
        child = node.get(key)
        if hasattr(child, "name"):
            out += _spine(child)
    return out


def test_the_where_is_one_basic_graph_pattern():
    spine = _spine(prepareQuery(open(RQ, encoding="utf-8").read()).algebra)
    assert spine.count("BGP") == 1 and "Join" not in spine, spine
