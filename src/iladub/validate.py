"""SHACL validation: load only what conforms to the contract."""
from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph
from pyshacl import validate as _pyshacl_validate


@dataclass
class ValidationResult:
    conforms: bool
    report_text: str
    report_graph: Graph


def validate(data: Graph, shapes: Graph, knowledge: Graph) -> ValidationResult:
    """Validate ``data`` against ``shapes`` with ``knowledge`` as the ontology graph."""
    conforms, report_graph, report_text = _pyshacl_validate(
        data,
        shacl_graph=shapes,
        ont_graph=knowledge,
        inference="rdfs",
        advanced=True,
    )
    return ValidationResult(conforms=conforms, report_text=report_text,
                            report_graph=report_graph)
