"""The ET(K)L pipeline."""
from __future__ import annotations

from typing import Tuple

from rdflib import Graph

from .contract import SemanticDataContract
from .extract import extract
from .transform import transform
from .validate import ValidationResult, validate


class ContractViolation(RuntimeError):
    """Raised when the output does not conform to its semantic data contract."""


class Pipeline:
    """Extract (contract-guided) -> Transform (knowledge as argument) -> validate -> Load."""

    def __init__(self, contract: SemanticDataContract):
        self.contract = contract

    def run(self, input_path, *, require_conformance: bool = True) -> Tuple[Graph, ValidationResult]:
        # K comes first: the contract's shapes tell extraction what to look for.
        target_paths = self.contract.target_paths()
        fields = extract(input_path, target_paths)

        # K as argument: the knowledge module is an input to the transform.
        target_classes = self.contract.target_classes()
        target_class = target_classes[0] if target_classes else None
        graph = transform(fields, knowledge=self.contract.knowledge, target_class=target_class)

        # Load only what conforms to the contract.
        result = validate(graph, self.contract.shapes, self.contract.knowledge)
        if require_conformance and not result.conforms:
            raise ContractViolation(result.report_text)
        return graph, result
