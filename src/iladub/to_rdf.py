"""Deterministic typed-extraction -> RDF mapping.

A value that resolves to a SKOS concept (by prefLabel or notation) is ASSERTED
as a contract-bound literal. A value that does not resolve is QUARANTINED as an
iladub:CandidateConcept (a proposition) with provenance to its source region.
Nothing is dropped; nothing is faked.
"""
from __future__ import annotations

from dataclasses import dataclass, field as dc_field

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SKOS

TX = Namespace("https://example.org/transplant#")
ILADUB = Namespace("https://w3id.org/etkl/iladub#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
ETKL = Namespace("https://w3id.org/etkl#")

OFFER = TX["offer"]

# Which OfferExtraction attribute maps to which contract property, and whether it
# must ground against the terminology (a coded concept) or is a free literal.
# organ, abo_group, cause_of_death are coded -> must_ground=True; an unmapped value
# on a must_ground field is what produces a proposition.
_FIELDS = [
    ("organ", TX.organ, True),
    ("ejection_fraction", TX.ejectionFraction, False),
    ("cause_of_death", TX.causeOfDeath, True),
    ("size_metric", TX.sizeMetric, False),
    ("abo_group", TX.aboGroup, True),
    ("hla_typing", TX.hlaTyping, False),
    ("serology", TX.serology, False),
    ("projected_transport_minutes", TX.projectedTransportMinutes, False),
]


@dataclass
class ExtractionGraph:
    graph: Graph = dc_field(default_factory=Graph)       # asserted, contract-bound
    propositions: Graph = dc_field(default_factory=Graph)  # quarantined candidates


def _resolves(terms: Graph, value: str) -> bool:
    v = value.strip().lower()
    for label in terms.objects(None, SKOS.prefLabel):
        if str(label).strip().lower() == v:
            return True
    for notation in terms.objects(None, SKOS.notation):
        if str(notation).strip().lower() == v:
            return True
    return False


def ground_typed(typed_obj, contract_graph: Graph, contract_node: URIRef,
                 terms: Graph, subject: URIRef) -> ExtractionGraph:
    """Map a typed extraction object to RDF, driven by ONE contract (contract_node):
    each etkl:hasField's fillsProperty local-name is read off typed_obj; a field WITH an
    etkl:admissibleScheme must ground (unresolved -> CandidateConcept), a field WITHOUT one
    is asserted as a free literal on `subject`."""
    eg = ExtractionGraph()
    n = 0
    for field in contract_graph.objects(contract_node, ETKL.hasField):
        prop = contract_graph.value(field, ETKL.fillsProperty)
        if prop is None:
            continue
        cc = getattr(typed_obj, str(prop).rsplit("#", 1)[-1], None)
        if cc is None:
            continue
        must_ground = contract_graph.value(field, ETKL.admissibleScheme) is not None
        if (not must_ground) or _resolves(terms, cc.value):
            eg.graph.add((subject, prop, Literal(cc.value)))
        else:
            n += 1
            cand = ILADUB[f"candidate-{n}"]
            region = BNode()
            eg.propositions.add((cand, RDF.type, ILADUB.CandidateConcept))
            eg.propositions.add((cand, ILADUB.confidence, Literal(cc.confidence, datatype=XSD.decimal)))
            eg.propositions.add((cand, ILADUB.fromRegion, region))
            eg.propositions.add((region, RDF.type, ILADUB.SourceRegion))
            eg.propositions.add((region, ILADUB.surfaceText, Literal(cc.source_quote)))
    return eg


def to_rdf(extraction, terms: Graph) -> ExtractionGraph:
    eg = ExtractionGraph()
    eg.graph.add((OFFER, RDF.type, TX.OrganOffer))
    n = 0
    for attr, prop, must_ground in _FIELDS:
        cc = getattr(extraction, attr, None)
        if cc is None:
            continue
        if (not must_ground) or _resolves(terms, cc.value):
            eg.graph.add((OFFER, prop, Literal(cc.value)))
        else:
            n += 1
            cand = ILADUB[f"candidate-{n}"]
            region = BNode()
            eg.propositions.add((cand, RDF.type, ILADUB.CandidateConcept))
            eg.propositions.add((cand, ILADUB.confidence, Literal(cc.confidence, datatype=XSD.decimal)))
            eg.propositions.add((cand, ILADUB.fromRegion, region))
            eg.propositions.add((region, RDF.type, ILADUB.SourceRegion))
            eg.propositions.add((region, ILADUB.surfaceText, Literal(cc.source_quote)))
    return eg
