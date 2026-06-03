"""Transform extracted fields into a typed graph, with knowledge as an argument.

The knowledge module is an *input* to this function, not something reconstructed
afterwards. The output is a typed resource whose properties are the contract's
target paths — ready to be validated against the contract's shapes.
"""
from __future__ import annotations

from typing import Dict, Optional

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

EX = Namespace("https://example.org/demo#")


def transform(fields: Dict[URIRef, str], *, knowledge: Optional[Graph] = None,
              target_class: Optional[URIRef] = None,
              subject: Optional[URIRef] = None) -> Graph:
    """Build a typed resource graph from extracted fields."""
    graph = Graph()
    subject = subject or EX["extracted-resource"]
    if target_class is not None:
        graph.add((subject, RDF.type, target_class))
    for prop, value in fields.items():
        graph.add((subject, prop, Literal(value)))
    return graph
