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
from rdflib.namespace import SKOS

ETKL = Namespace("https://w3id.org/iladub/etkl#")
SKOSNS = SKOS
ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")
SH = Namespace("http://www.w3.org/ns/shacl#")

_EXACT_RULE = "urn:iladub:suggester/exact-match-rule"
# One rule, two grains: `splitkey` applies it per NAME (a marker SET whole-set-admitted by one
# field), `marker_field` below per VALUE (one marker admitted by one field's scheme). Both mint
# this suggester, so a reader of the graph sees the same accountable rule at either grain.
_UNIQUE_ADMITTING_FIELD_RULE = "urn:iladub:suggester/unique-admitting-field-rule"
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
    # Loop Q §4.2: True for a candidate injected from a section's peeled captions (feed.py's
    # `_inject_section_captions`) — undiscriminated key-or-notice evidence, never set by any
    # other caller. Defaulted so every existing 3-arg call site (positional or keyword) is
    # untouched. Grounding disposal branches on it in exactly one place (R207, 2026-09-10):
    # `ground_concept` asks `marker_field` for the unique scheme that carries the marker's
    # value when `exact_field` cannot name it — a marker's text IS its value, so a field name
    # never matches it, and without that branch every key marker was quarantined.
    is_section_marker: bool = False


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


def marker_field(concept: SurfaceConcept, contract: Contract, terms: Graph) -> ContractField | None:
    """AXIOM (R207) — the ONE scheme-bound contract field whose admissible scheme carries the
    marker's value as a `skos:prefLabel`; `None` when zero or several do.

    A section marker names no column: `feed._inject_section_captions` mints it with text ==
    value, so `exact_field` (which compares TEXT to field NAMES) can never place it, and the
    proposer behind it is asked the wrong question — "which field is called GERALDTON?". The
    right question is the contract's: "which field would ADMIT the value GERALDTON?", and the
    contract answers it decidably, through the same `scheme_member` oracle `_grounds_to` applies
    to every scheme value. Per-value counterpart of `splitkey.resolve_split_key_name`'s arm 2,
    which asks the same question of the whole marker SET to recover the dimension's NAME.

    Ambiguity abstains (§3): two admitting fields is a proposition, not an assertion, and the
    marker stays a quarantined candidate exactly as a marker no scheme carries does. Not called
    for any concept that is not a section marker — a DATA cell whose value happens to be a port
    label sits under a column the contract did not declare, and grounding it by value alone
    would let the value, not the author's structure, decide the field (§0)."""
    if not concept.is_section_marker:
        return None
    admitting = [f for f in contract.fields
                 if f.scheme is not None and scheme_member(concept.value, f.scheme, terms)]
    return admitting[0] if len(admitting) == 1 else None


def _emit_candidate(g, concept, anchor_iri, suggester_iri, confidence):
    cand = BNode()
    g.add((cand, RDF.type, ILADUB.CandidateConcept))
    g.add((cand, RDFS.label, Literal(concept.text)))
    g.add((cand, ILADUB.surfaceText, Literal(concept.value)))
    g.add((cand, ILADUB.suggestedAnchor, URIRef(anchor_iri)))
    from .etkl.membrane import suggester_agent      # R129: refuse a non-IRI suggester HERE
    agent = suggester_agent(suggester_iri)
    g.add((agent, RDF.type, ILADUB.Suggester))
    g.add((cand, ILADUB.suggestedBy, agent))
    g.add((cand, ILADUB.confidence, Literal(Decimal(str(round(confidence, 6))))))
    region = URIRef("urn:iladub:region:" + concept.region)
    g.add((region, RDF.type, ILADUB.SourceRegion))
    g.add((cand, ILADUB.fromRegion, region))
    g.add((cand, ILADUB.status, ILADUB.proposed))
    return cand, agent


def _grounds_to(concept, field, terms, is_exact, contract_shapes, offer_uri, target_class):
    """`(target, admitted_because)` — the grounding TARGET for iladub:groundsTo and the ORACLE
    that admitted it, or `(None, None)` if REJECTED (→ quarantine).

    Scheme-bound field: the SKOS concept whose prefLabel == value (membership is the oracle).
    Non-scheme field that declares a value constraint: the SHACL value membrane is the oracle — the
    value MUST conform, whether the field was identified by exact label match OR by a model proposal
    (legality gates admission uniformly). Non-scheme field WITHOUT a value constraint: an exact label
    match grounds (field-identity is the oracle); a bare proposal has no oracle → None (quarantine).

    WHY THE ORACLE IS RETURNED FROM HERE (spec 2026-08-10 §5.3): `_emit_grounded` records the
    quarantine branch as the option NOT taken, and `dec:rejectedBecause` must name *which* of the
    three refusal paths above would have applied. Deriving that at the call site would duplicate
    this function's branch and let the two drift; the branch that decides is the only place that
    can name its own refusal without re-deciding it."""
    if field.scheme is not None:
        term = scheme_member(concept.value, field.scheme, terms)
        if not term:
            return None, None
        return URIRef(term), (
            f"{concept.value!r} is a member of the admissible scheme {field.scheme}; quarantine "
            f"is the branch for a value no concept in that scheme carries as a prefLabel")
    ps = _property_shape(contract_shapes, field.fills_property)
    if ps is not None and _has_value_constraint(contract_shapes, ps):
        if not _value_conforms(offer_uri, target_class, field.fills_property, concept.value,
                               contract_shapes):
            return None, None
        return URIRef(field.fills_property), (
            f"{concept.value!r} conforms to the contract's SHACL value constraint on "
            f"{field.fills_property}; quarantine is the branch for a value the membrane refuses")
    if not is_exact:
        return None, None
    return URIRef(field.fills_property), (
        f"the concept's label exactly identifies contract field {field.fills_property}, which "
        f"declares no value constraint, so field identity is the oracle; quarantine is the "
        f"branch for a field that was proposed rather than exactly matched")


def _emit_grounded(g, concept, offer_uri, target_class, field, grounds_to, cand, agent, confidence, rationale, datatype=None, admitted_because=None):
    pd = BNode()
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, agent))
    g.add((pd, DEC.consideredEvidence, cand))
    g.add((pd, DEC.confidence, Literal(Decimal(str(round(confidence, 6))))))
    g.add((pd, DEC.rationale, Literal(rationale)))
    # THE DELIBERATION (spec 2026-08-10 §5.3). Read off the branch `ground_concept` already
    # takes — it branches on `field is None`, then on `grounds_to is None`, and its two
    # outcomes are "grounded" and "proposed". Naming those two invents nothing; the option
    # space is exact, not thin. §8: PROCEDURAL — it records a decision already made.
    #
    # BOTH OPTIONS ARE BNodes, and that is deliberate. `pd`, `cand` and `gn` are all BNodes
    # here (unlike promote.py, where the decision is a URIRef): the whole grounding record is
    # traversal-addressed from `offer_uri`. A URIRef option would be the ONLY named node in a
    # record whose decision, candidate and grounded node are all anonymous — a name that
    # cannot be dereferenced to its own context — and there is no stable identity to mint it
    # from, since one offer may ground several concepts to one field.
    opt_ground = BNode()
    g.add((opt_ground, RDF.type, DEC.Option))
    g.add((opt_ground, RDFS.label, Literal(f"ground to {grounds_to}")))
    g.add((pd, DEC.optionSpace, opt_ground))
    g.add((pd, DEC.chosen, opt_ground))
    opt_quarantine = BNode()
    g.add((opt_quarantine, RDF.type, DEC.Option))
    g.add((opt_quarantine, RDFS.label, Literal("quarantine as a proposition")))
    g.add((pd, DEC.optionSpace, opt_quarantine))
    if admitted_because:
        g.add((opt_quarantine, DEC.rejectedBecause, Literal(admitted_because)))
    gn = BNode()
    g.add((gn, RDF.type, ILADUB.GroundedNode))
    g.add((gn, ILADUB.wasPromotedBy, pd))
    g.add((gn, ILADUB.groundsTo, grounds_to))
    g.add((gn, ILADUB.status, ILADUB.asserted))
    g.add((pd, DEC.produced, gn))
    # the contract instance: type once + the property value, typed when the shape declares a datatype
    g.add((offer_uri, RDF.type, URIRef(target_class)))
    val = Literal(concept.value, datatype=datatype) if datatype is not None else Literal(concept.value)
    g.add((offer_uri, URIRef(field.fills_property), val))
    return gn


def ground_concept(concept, contract, offer_uri, proposer, terms, contract_shapes, g) -> str:
    field = exact_field(concept, contract)
    if field is not None:
        suggester, confidence, rationale, anchor = _EXACT_RULE, 1.0, "Exact contract-field match.", _GIST_CATEGORY
        is_exact = True
    elif (field := marker_field(concept, contract, terms)) is not None:   # R207: a section marker
        suggester, confidence, anchor = _UNIQUE_ADMITTING_FIELD_RULE, 1.0, _GIST_CATEGORY
        rationale = (f"Section marker: {concept.value!r} is a prefLabel in the admissible scheme of "
                     f"exactly one contract field ({field.fills_property}); unique admission "
                     f"derives the field from the contract, no proposer asked.")
        is_exact = True                                     # the field is derived, not proposed
    else:
        prop = proposer.propose_grounding(concept, contract.fields)
        anchor, confidence, rationale, suggester = prop.anchor_iri, prop.confidence, prop.rationale, prop.suggester_iri
        field = next((f for f in contract.fields if f.iri == prop.field_iri), None) if prop.field_iri else None
        is_exact = False
    cand, agent = _emit_candidate(g, concept, anchor, suggester, confidence)
    if field is None:                                       # novel → quarantined proposition
        return "proposed"
    grounds_to, admitted_because = _grounds_to(concept, field, terms, is_exact, contract_shapes,
                                               offer_uri, contract.target_class)
    if grounds_to is None:                                  # unverifiable / rejected → quarantine
        return "proposed"
    ps = _property_shape(contract_shapes, field.fills_property)
    datatype = contract_shapes.value(ps, SH.datatype) if ps is not None else None
    if field.scheme is None and not is_exact:               # grounded via the value-constraint membrane
        rationale = ("%s [grounded via SHACL value-constraint admissibility, weaker than "
                     "scheme-identity]" % rationale)
    _emit_grounded(g, concept, offer_uri, contract.target_class, field, grounds_to,
                   cand, agent, confidence, rationale, datatype, admitted_because)
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
