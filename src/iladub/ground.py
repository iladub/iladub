"""ground — the ground-or-propose pipeline (knowledge-first grounding).

Every concept is a proposition (iladub:CandidateConcept) first; it crosses into the grounded
graph ONLY via an iladub:PromotionDecision, and only when the contract oracle (SKOS
admissibleScheme membership + the contract SHACL shape) admits it. Confidence never promotes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import SKOS

ETKL = Namespace("https://w3id.org/iladub/etkl#")
SKOSNS = SKOS


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
