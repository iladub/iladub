"""Events that may reopen a decision. An Event carries a named condition key
(matched against a decision's hol:revisitIf) and a payload of new values folded
into re-evaluation."""
from __future__ import annotations

from dataclasses import dataclass, field

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

DEC = Namespace("https://w3id.org/iladub/dec#")


@dataclass(frozen=True)
class Event:
    condition: str
    payload: dict = field(default_factory=dict)

    def to_rdf(self, subject: URIRef) -> Graph:
        g = Graph()
        g.add((subject, RDF.type, DEC.Event))
        g.add((subject, DEC.condition, Literal(self.condition)))
        return g
