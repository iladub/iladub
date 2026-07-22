"""ground — the ground-or-propose pipeline (knowledge-first grounding).

Every concept is a proposition (iladub:CandidateConcept) first; it crosses into the grounded
graph ONLY via an iladub:PromotionDecision, and only when the contract oracle (SKOS
admissibleScheme membership + the contract SHACL shape) admits it. Confidence never promotes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

from rdflib import RDF, RDFS, BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import SKOS, XSD

ETKL = Namespace("https://w3id.org/iladub/etkl#")
SKOSNS = SKOS
ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")
SH = Namespace("http://www.w3.org/ns/shacl#")

_EXACT_RULE = "urn:iladub:suggester/exact-match-rule"
_GIST_CATEGORY = "https://w3id.org/semanticarts/ns/ontology/gist/Category"

# Value constraints (as opposed to cardinality/path) — presence of any means the contract
# declares something the SHACL membrane can verify a proposed value against.
_VALUE_CONSTRAINTS = (SH.datatype, SH["in"], SH.pattern,
                      SH.minInclusive, SH.maxInclusive, SH.minExclusive, SH.maxExclusive,
                      SH.minLength, SH.maxLength)


@dataclass(frozen=True)
class SurfaceConcept:
    text: str
    value: str
    region: str


@dataclass(frozen=True)
class ContractField:
    iri: str
    fills_property: str
    scheme: str | None


@dataclass(frozen=True)
class Contract:
    target_class: str
    fields: tuple[ContractField, ...]


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def load_contract(contract_path: str) -> Contract:
    g = Graph().parse(contract_path, format="turtle")
    contract = next(g.subjects(ETKL.targetClass, None), None)
    target = g.value(contract, ETKL.targetClass)
    fields = []
    for f in g.objects(contract, ETKL.hasField):
        prop = g.value(f, ETKL.fillsProperty)
        scheme = g.value(f, ETKL.admissibleScheme)
        fields.append(ContractField(str(f), str(prop), str(scheme) if scheme else None))
    return Contract(str(target), tuple(fields))


def exact_field(concept: SurfaceConcept, contract: Contract) -> ContractField | None:
    key = _norm(concept.text)
    for f in contract.fields:
        if _norm(f.fills_property.split("#")[-1].split("/")[-1]) == key:
            return f
    return None


def scheme_member(value: str, scheme_iri: str, terms: Graph) -> str | None:
    for c in terms.subjects(SKOSNS.inScheme, URIRef(scheme_iri)):
        for lbl in terms.objects(c, SKOSNS.prefLabel):
            if str(lbl) == value:
                return str(c)
    return None


def _emit_candidate(g, concept, anchor_iri, suggester_iri, confidence):
    cand = BNode()
    g.add((cand, RDF.type, ILADUB.CandidateConcept))
    g.add((cand, RDFS.label, Literal(concept.text)))
    g.add((cand, ILADUB.surfaceText, Literal(concept.value)))
    g.add((cand, ILADUB.suggestedAnchor, URIRef(anchor_iri)))
    agent = URIRef(suggester_iri)
    g.add((agent, RDF.type, ILADUB.Suggester))
    g.add((cand, ILADUB.suggestedBy, agent))
    g.add((cand, ILADUB.confidence, Literal(Decimal(str(round(confidence, 6))))))
    region = URIRef("urn:iladub:region:" + concept.region)
    g.add((region, RDF.type, ILADUB.SourceRegion))
    g.add((cand, ILADUB.fromRegion, region))
    g.add((cand, ILADUB.status, ILADUB.proposed))
    return cand, agent


def _grounds_to(concept, field, terms, is_exact):
    """The grounding TARGET for iladub:groundsTo, or None if REJECTED (→ quarantine).

    Scheme-bound field: the SKOS concept whose prefLabel == value (membership is the oracle), else
    None. Non-scheme field: admitted ONLY for an EXACT label match (the exact match is the oracle);
    a NEURAL proposal to an unconstrained field has no oracle → None (quarantine). Grounding an
    unverifiable NEURAL guess would be confidence-as-validity (§7)."""
    if field.scheme is not None:
        term = scheme_member(concept.value, field.scheme, terms)
        return URIRef(term) if term else None
    return URIRef(field.fills_property) if is_exact else None


def _emit_grounded(g, concept, offer_uri, target_class, field, grounds_to, cand, agent, confidence, rationale):
    pd = BNode()
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, agent))
    g.add((pd, DEC.consideredEvidence, cand))
    g.add((pd, DEC.confidence, Literal(Decimal(str(round(confidence, 6))))))
    g.add((pd, DEC.rationale, Literal(rationale)))
    gn = BNode()
    g.add((gn, RDF.type, ILADUB.GroundedNode))
    g.add((gn, ILADUB.wasPromotedBy, pd))
    g.add((gn, ILADUB.groundsTo, grounds_to))
    g.add((gn, ILADUB.status, ILADUB.asserted))
    g.add((pd, DEC.produced, gn))
    # the contract instance: type once + the property value as a STRING literal (satisfies the shape)
    g.add((offer_uri, RDF.type, URIRef(target_class)))
    g.add((offer_uri, URIRef(field.fills_property), Literal(concept.value)))
    return gn


def ground_concept(concept, contract, offer_uri, proposer, terms, contract_shapes, g) -> str:
    field = exact_field(concept, contract)
    if field is not None:
        suggester, confidence, rationale, anchor = _EXACT_RULE, 1.0, "Exact contract-field match.", _GIST_CATEGORY
        is_exact = True
    else:
        prop = proposer.propose_grounding(concept, contract.fields)
        anchor, confidence, rationale, suggester = prop.anchor_iri, prop.confidence, prop.rationale, prop.suggester_iri
        field = next((f for f in contract.fields if f.iri == prop.field_iri), None) if prop.field_iri else None
        is_exact = False
    cand, agent = _emit_candidate(g, concept, anchor, suggester, confidence)
    if field is None:                                       # novel → quarantined proposition
        return "proposed"
    grounds_to = _grounds_to(concept, field, terms, is_exact)   # the contract oracle
    if grounds_to is None:                                  # unverifiable / rejected → quarantine
        return "proposed"
    _emit_grounded(g, concept, offer_uri, contract.target_class, field, grounds_to, cand, agent, confidence, rationale)
    return "grounded"


def _property_shape(shapes, property_iri):
    """The sh:property node whose sh:path == property_iri, or None."""
    for ps in shapes.subjects(SH.path, URIRef(property_iri)):
        return ps
    return None


def _has_value_constraint(shapes, ps):
    """True iff the property shape declares any value constraint (not just cardinality/path)."""
    return any((ps, p, None) in shapes for p in _VALUE_CONSTRAINTS)


def _value_conforms(offer_uri, target_class, property_iri, value, shapes):
    """SHACL-membrane oracle (§8, closed-world): does `value` satisfy the field's declared value
    constraints? Validates against a FOCUSED node shape targeting the offer that carries ONLY this
    field's sh:property (never the full node shape, whose other required properties would fail a
    scratch offer). The value is cast to the shape's sh:datatype: an ill-typed lexical form (e.g.
    'high' as xsd:decimal) fails sh:datatype -> correctly non-conformant."""
    from .validate import validate

    ps = _property_shape(shapes, property_iri)
    if ps is None:
        return False
    dt = shapes.value(ps, SH.datatype)

    focused = Graph()
    shape = BNode()
    focused.add((shape, RDF.type, SH.NodeShape))
    focused.add((shape, SH.targetNode, offer_uri))
    focused.add((shape, SH.property, ps))
    focused += shapes.cbd(ps)                       # bring the property shape's own constraints

    data = Graph()
    data.add((offer_uri, RDF.type, URIRef(target_class)))
    val = Literal(value, datatype=dt) if dt is not None else Literal(value)
    data.add((offer_uri, URIRef(property_iri), val))

    return validate(data, focused, Graph()).conforms
