"""interpret — the declarative CONSTRUCT executor (neurosymbolic loop one).

Loads a version-controlled SPARQL CONSTRUCT (.rq) from vocab/queries/ and runs it
via rdflib over the union of the given graphs. This is the ONLY procedural piece of
the transform, and it is PROCEDURAL engine glue (Python — iladub's reference language):
it invokes a standard SPARQL engine
on a standard query. It contains NO transform logic and NO tuned constant — the
transform lives entirely in the .rq files (AXIOM). Irreducible because SPARQL must be
invoked from somewhere; the invocation carries no domain decision.
"""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph


def run(query_path, *graphs):
    """Execute the CONSTRUCT at `query_path` over the union of `graphs`; return the
    constructed rdflib.Graph."""
    union = Graph()
    for g in graphs:
        union += g
    query = Path(query_path).read_text(encoding="utf-8")
    result = union.query(query)
    out = Graph()
    for triple in result:
        out.add(triple)
    return out
