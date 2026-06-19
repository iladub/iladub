"""M4 orchestration: compile a raw organ offer into a validated, decision-ready
context. Reader -> multi-agent BAML extraction -> RDF (assert/propose) -> SHACL
-> deterministic decision. The funnel is additive to the regex pipeline."""
from __future__ import annotations

import os
from dataclasses import dataclass

from rdflib import Graph

from .readers import read_document
from .extract_baml import extract_offer
from .to_rdf import to_rdf, ExtractionGraph
from .validate import validate, ValidationResult
from .decision import evaluate_m4, build_decision_holon, M4Context, DecisionResult

_HERE = os.path.dirname(os.path.abspath(__file__))
_TXD = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "examples", "transplant")


@dataclass
class M4Result:
    extraction_graph: ExtractionGraph
    validation: ValidationResult
    decision: DecisionResult
    decision_graph: Graph


from rdflib import Namespace as _Namespace

_HOL = _Namespace("https://w3id.org/etkl/hol#")
_ILADUB = _Namespace("https://w3id.org/etkl/iladub#")


def capture_for_milestone(milestone, timeline_graph: Graph, document_text: str,
                          terms: Graph, subject, b=None) -> Graph:
    """Run the milestone's declared (contract-targeted) extractor over a document and
    return the grounded graph on `subject`. The extractor is named by the milestone's
    requiresContext contract via iladub:extractor."""
    from baml_client import sync_client
    from .to_rdf import ground_typed
    b = b if b is not None else sync_client.b
    contract_node = timeline_graph.value(milestone.id, _HOL.requiresContext)
    fn_name = str(timeline_graph.value(contract_node, _ILADUB.extractor))
    typed = getattr(b, fn_name)(document_text)
    return ground_typed(typed, timeline_graph, contract_node, terms, subject).graph


def capture_context(offer_path: str,
                    terms_path: str = os.path.join(_TXD, "transplant-terms.ttl")) -> Graph:
    """Run the SP1 funnel over a document and return the grounded (asserted) graph,
    suitable as a capture_fn body for the timeline loop (loop.advance_with_capture)."""
    text = read_document(offer_path)
    terms = Graph().parse(terms_path, format="turtle")
    return to_rdf(extract_offer(text), terms).graph


def compile_offer(doc_path: str,
                  terms_path: str = os.path.join(_TXD, "transplant-terms.ttl"),
                  shapes_path: str = os.path.join(_TXD, "offer-shapes.ttl"),
                  ontology_path: str = os.path.join(_TXD, "transplant-ontology.ttl"),
                  recipient_abo: str = "O",
                  ischemia_limit_minutes: int = 240) -> M4Result:
    text = read_document(doc_path)
    terms = Graph().parse(terms_path, format="turtle")

    extraction = extract_offer(text)
    eg = to_rdf(extraction, terms)

    shapes = Graph().parse(shapes_path, format="turtle")
    knowledge = Graph().parse(ontology_path, format="turtle")
    result = validate(eg.graph, shapes, knowledge)

    minutes = int(extraction.projected_transport_minutes.value) \
        if extraction.projected_transport_minutes else ischemia_limit_minutes + 1
    donor_abo = extraction.abo_group.value if extraction.abo_group else ""
    decision = evaluate_m4(M4Context(donor_abo=donor_abo, recipient_abo=recipient_abo,
                                     projected_ischemia_minutes=minutes,
                                     ischemia_limit_minutes=ischemia_limit_minutes))
    return M4Result(extraction_graph=eg, validation=result, decision=decision,
                    decision_graph=build_decision_holon(decision))
