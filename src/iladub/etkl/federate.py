"""federate — the compile→federate loop (loop F).

A compiled CleanDocumentHolon's projection becomes the provided terminology the next
document grounds against. Projection derivation is AXIOM (federate-projection.rq); this
module is PROCEDURAL engine glue — it drives the grounding portal and the CONSTRUCT and
compares result sets. It carries NO domain decision and NO tuned constant.
See docs/superpowers/specs/2026-07-24-compile-federate-design.md.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from rdflib import Graph, Namespace, RDF

from .. import ground
from . import interpret

ILADUB = Namespace("https://w3id.org/iladub#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
_QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries")


def compile_document(concepts, contract, doc_uri, proposer, terms, contract_shapes) -> Graph:
    """Run the grounding portal over every surface concept; return the interior graph."""
    g = Graph()
    for c in concepts:
        ground.ground_concept(c, contract, doc_uri, proposer, terms, contract_shapes, g)
    return g


def derive_projection(interior: Graph, terms: Graph) -> Graph:
    """AXIOM: run federate-projection.rq over interior ∪ terms → the DocumentProjection."""
    return interpret.run(os.path.join(_QUERIES, "federate-projection.rq"), interior, terms)
