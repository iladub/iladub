"""M4 orchestration: compile a raw organ offer into a validated, decision-ready
context. Reader -> multi-agent BAML extraction -> RDF (assert/propose) -> SHACL
-> deterministic decision. The funnel is additive to the regex pipeline."""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone

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

_DEC = _Namespace("https://w3id.org/iladub/dec#")
_ILADUB = _Namespace("https://w3id.org/iladub#")


def capture_for_milestone(milestone, timeline_graph: Graph, document_text: str,
                          terms: Graph, subject, b=None) -> Graph:
    """Run the milestone's declared (contract-targeted) extractor over a document and
    return the grounded graph on `subject`. The extractor is named by the milestone's
    requiresContext contract via iladub:extractor."""
    from baml_client import sync_client
    from .to_rdf import ground_typed
    b = b if b is not None else sync_client.b
    contract_node = timeline_graph.value(milestone.id, _DEC.requiresContext)
    fn_name = str(timeline_graph.value(contract_node, _ILADUB.extractor))
    typed = getattr(b, fn_name)(document_text)
    return ground_typed(typed, timeline_graph, contract_node, terms, subject).graph


def capture_context(offer_path: str,
                    terms_path: str = os.path.join(_TXD, "transplant-terms.ttl"),
                    shapes_path: str = os.path.join(_TXD, "offer-shapes.ttl")) -> Graph:
    """Run the SP1 funnel over a document and return the grounded (asserted) graph,
    suitable as a capture_fn body for the timeline loop (loop.advance_with_capture)."""
    text = read_document(offer_path)
    terms = Graph().parse(terms_path, format="turtle")
    shapes = Graph().parse(shapes_path, format="turtle")
    return to_rdf(extract_offer(text), terms, shapes).graph


def _compile_text(text: str,
                  terms_path: str = os.path.join(_TXD, "transplant-terms.ttl"),
                  shapes_path: str = os.path.join(_TXD, "offer-shapes.ttl"),
                  ontology_path: str = os.path.join(_TXD, "transplant-ontology.ttl"),
                  recipient_abo: str = "O",
                  ischemia_limit_minutes: int = 240,
                  recipient_lvef_floor: int | None = None,
                  absolute_contraindication: bool = False) -> M4Result:
    terms = Graph().parse(terms_path, format="turtle")
    extraction = extract_offer(text)
    shapes = Graph().parse(shapes_path, format="turtle")
    eg = to_rdf(extraction, terms, shapes)

    knowledge = Graph().parse(ontology_path, format="turtle")
    result = validate(eg.graph, shapes, knowledge)

    minutes = int(extraction.projected_transport_minutes.value) \
        if extraction.projected_transport_minutes else ischemia_limit_minutes + 1
    donor_abo = extraction.abo_group.value if extraction.abo_group else ""
    lvef = int(extraction.ejection_fraction.value) \
        if extraction.ejection_fraction and extraction.ejection_fraction.value.strip().isdigit() else None
    decision = evaluate_m4(M4Context(donor_abo=donor_abo, recipient_abo=recipient_abo,
                                     projected_ischemia_minutes=minutes,
                                     ischemia_limit_minutes=ischemia_limit_minutes,
                                     organ_lvef=lvef,
                                     recipient_lvef_floor=recipient_lvef_floor,
                                     absolute_contraindication=absolute_contraindication))
    return M4Result(extraction_graph=eg, validation=result, decision=decision,
                    decision_graph=build_decision_holon(decision))


def compile_offer(doc_path: str,
                  terms_path: str = os.path.join(_TXD, "transplant-terms.ttl"),
                  shapes_path: str = os.path.join(_TXD, "offer-shapes.ttl"),
                  ontology_path: str = os.path.join(_TXD, "transplant-ontology.ttl"),
                  recipient_abo: str = "O",
                  ischemia_limit_minutes: int = 240,
                  recipient_lvef_floor: int | None = None,
                  absolute_contraindication: bool = False) -> M4Result:
    return _compile_text(read_document(doc_path), terms_path, shapes_path,
                         ontology_path, recipient_abo, ischemia_limit_minutes,
                         recipient_lvef_floor, absolute_contraindication)


def compile_offer_databook(in_path: str, out_path: str,
                           terms_path: str = os.path.join(_TXD, "transplant-terms.ttl"),
                           shapes_path: str = os.path.join(_TXD, "offer-shapes.ttl"),
                           ontology_path: str = os.path.join(_TXD, "transplant-ontology.ttl"),
                           recipient_abo: str = "O",
                           ischemia_limit_minutes: int = 240) -> M4Result:
    """Compile a raw-offer DataBook (RawDocumentHolon) into a CleanDocumentHolon DataBook:
    grounded graph + propositions + M4 decision holon + a process provenance stamp."""
    from .databook import read_databook, write_databook, Block, validate_frontmatter

    raw = read_databook(in_path)
    raw_iri = raw.frontmatter.get("id")
    if not raw_iri:
        raise ValueError(f"{in_path}: raw DataBook has no 'id' frontmatter key")
    res = _compile_text(raw.prose, terms_path, shapes_path, ontology_path,
                        recipient_abo, ischemia_limit_minutes)
    clean_iri = raw_iri + ".clean"
    base = "https://example.org/transplant/knowledge/"

    blocks = [
        Block(lang="turtle", id="asserted", graph_iri=clean_iri + "#asserted",
              content=res.extraction_graph.graph.serialize(format="turtle").strip()),
        Block(lang="turtle", id="propositions", graph_iri=clean_iri + "#propositions",
              content=res.extraction_graph.propositions.serialize(format="turtle").strip()),
        Block(lang="turtle", id="decision", graph_iri=clean_iri + "#decision",
              content=res.decision_graph.serialize(format="turtle").strip()),
    ]
    frontmatter = {
        "id": clean_iri,
        "title": raw.frontmatter.get("title", "offer").replace("(raw)", "(compiled)"),
        "type": "databook",
        "version": "1.0.0",
        "created": datetime.now(timezone.utc).date().isoformat(),
        "process": {
            "transformer": "BAML + Claude",
            "transformer_type": "llm",
            "transformer_iri": "https://api.anthropic.com/v1/models/claude-opus-4-8",
            "inputs": [
                {"iri": raw_iri, "role": "primary"},
                {"iri": base + "offer-contract", "role": "contract"},
                {"iri": base + "transplant-terms", "role": "knowledge"},
                {"iri": base + "offer-shapes", "role": "constraint"},
            ],
            "agent": {"name": "iladub", "role": "orchestrator"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
    prose = (
        "## M4 — Offer acceptance decision\n\n"
        f"Recommendation: **{res.decision.recommendation}**. {res.decision.reason}\n\n"
        "`#asserted` carries the grounded offer; `#propositions` holds what could not be "
        "grounded (quarantined, never asserted); `#decision` is the accountable M4 "
        "`dec:DecisionHolon`."
    )
    problems = validate_frontmatter(frontmatter, require_process=True)
    if problems:
        raise ValueError(f"clean DataBook frontmatter invalid: {problems}")
    write_databook(frontmatter, blocks, prose, out_path)
    return res
