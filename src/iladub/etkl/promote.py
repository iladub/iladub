"""promote — emit the accountable provenance for a GenAI-proposed dimension name (Loop A2).

The proposed name is a PROPOSITION: an iladub:CandidateConcept reviewed by an
iladub:PromotionDecision (a dec:DecisionHolon). The reshape structure is oracle-certified;
the NAME is not — dec:rationale records that split.
"""
from __future__ import annotations

import re
from decimal import Decimal

from rdflib import RDF, RDFS, BNode, Literal, Namespace, URIRef
from rdflib.namespace import XSD

TAB = Namespace("https://w3id.org/iladub/tab#")
ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")
GIST = Namespace("https://w3id.org/semanticarts/ns/ontology/gist/")


def _slug(s):
    """IRI-safe slug — a proposed name may be a multi-word phrase (e.g. 'Fiscal Quarter'),
    which would make an unencoded IRI invalid Turtle. The human-readable name is preserved
    verbatim on the CandidateConcept's rdfs:label; this only sanitizes the promotion IRI."""
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-") or "dim"


def _suggester(g, proposal):
    agent = URIRef(proposal.suggester_iri)
    g.add((agent, RDF.type, ILADUB.Suggester))
    return agent


def emit_promotion(g, t, normalized_base, dimension_name, values, proposal):
    """Write the CandidateConcept + PromotionDecision for a promoted name; link the recipe's
    UnpivotOp via tab:namePromotedBy. Returns the PromotionDecision uri."""
    agent = _suggester(g, proposal)
    _confidence = Literal(Decimal(str(round(proposal.confidence, 6))))

    cand = BNode()
    g.add((cand, RDF.type, ILADUB.CandidateConcept))
    g.add((cand, RDFS.label, Literal(dimension_name)))
    g.add((cand, ILADUB.surfaceText, Literal(" | ".join(values))))
    g.add((cand, ILADUB.suggestedBy, agent))
    g.add((cand, ILADUB.suggestedAnchor, GIST.Category))
    g.add((cand, ILADUB.fromRegion, t))
    g.add((cand, ILADUB.status, ILADUB.proposed))
    g.add((cand, ILADUB.confidence, _confidence))

    pd = URIRef("%s-promotion-%s" % (t, _slug(dimension_name)))
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, agent))
    g.add((pd, DEC.consideredEvidence, t))
    g.add((pd, DEC.consideredEvidence, cand))
    g.add((pd, DEC.confidence, _confidence))
    g.add((pd, DEC.rationale, Literal(
        "Reshape round-trips exactly with dimension=%s; the name is a model proposition, "
        "not oracle-verified. Rationale: %s" % (dimension_name, proposal.rationale))))
    g.add((pd, DEC.produced, normalized_base))

    # link the UnpivotOp carrying this dimension name to its promotion
    for op in g.subjects(RDF.type, TAB.UnpivotOp):
        if str(g.value(op, TAB.opDimension)) == dimension_name:
            g.add((op, TAB.namePromotedBy, pd))
    return pd
