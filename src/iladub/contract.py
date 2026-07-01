"""The semantic data contract.

A contract is an ontology, not a JSON/YAML schema: it declares the target
class and SHACL shape(s) the output must conform to, the knowledge module(s)
the transform requires, and the fields that bind target properties to
extractable values. Knowledge enters first (via the contract) and is carried
as an argument to the transform.
"""
from __future__ import annotations

from typing import List, Optional

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

ETKL = Namespace("https://w3id.org/iladub/etkl#")


class SemanticDataContract:
    """Loads and exposes a contract's target semantics."""

    def __init__(self, graph: Graph, shapes: Optional[Graph] = None,
                 knowledge: Optional[Graph] = None):
        self.graph = graph
        self.shapes = shapes if shapes is not None else Graph()
        self.knowledge = knowledge if knowledge is not None else Graph()

    @classmethod
    def from_files(cls, contract: str, shapes: Optional[str] = None,
                   knowledge: Optional[str] = None) -> "SemanticDataContract":
        g = Graph().parse(contract, format="turtle")
        sh = Graph().parse(shapes, format="turtle") if shapes else Graph()
        kn = Graph().parse(knowledge, format="turtle") if knowledge else Graph()
        return cls(g, sh, kn)

    def _contract_node(self) -> Optional[URIRef]:
        return self.graph.value(predicate=RDF.type, object=ETKL.SemanticDataContract)

    def target_classes(self) -> List[URIRef]:
        node = self._contract_node()
        if node is None:
            return []
        return [c for c in self.graph.objects(node, ETKL.targetClass)]
