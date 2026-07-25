"""federate — the compile→federate loop (loop F).

A compiled CleanDocumentHolon's projection becomes the provided terminology the next
document grounds against. Projection derivation is AXIOM (federate-projection.rq); this
module is PROCEDURAL engine glue — it drives the grounding portal and the CONSTRUCT and
compares result sets. It carries NO domain decision and NO tuned constant.
See docs/superpowers/specs/2026-07-24-compile-federate-design.md.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from rdflib import Graph, Namespace, RDF, URIRef

from .. import ground
from . import interpret

ETKL = Namespace("https://w3id.org/iladub/etkl#")
ILADUB = Namespace("https://w3id.org/iladub#")
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
PROV = Namespace("http://www.w3.org/ns/prov#")
RECIPE = URIRef("urn:federate:recipe")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
_QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries")


@dataclass(frozen=True)
class FederationVerdict:
    ok: bool
    unsound: tuple      # projection concepts with no promoted grounded node behind them
    leaked: tuple       # interior-class instances found in the projection (opacity breach)
    uncontained: tuple  # concepts B grounded to that A never projected


def compile_document(concepts, contract, doc_uri, proposer, terms, contract_shapes) -> Graph:
    """Run the grounding portal over every surface concept; return the interior graph."""
    g = Graph()
    for c in concepts:
        ground.ground_concept(c, contract, doc_uri, proposer, terms, contract_shapes, g)
    return g


def derive_projection(interior: Graph, terms: Graph) -> Graph:
    """AXIOM: run federate-projection.rq over interior ∪ terms → the DocumentProjection."""
    return interpret.run(os.path.join(_QUERIES, "federate-projection.rq"), interior, terms)


def _projection_concepts(projection: Graph) -> set:
    return {str(s) for s in projection.subjects(RDF.type, SKOS.Concept)}


def _promoted_targets(interior: Graph) -> set:
    return {str(o) for s, o in interior.subject_objects(ILADUB.groundsTo)
            if (s, ILADUB.wasPromotedBy, None) in interior}


def _interior_leaks(projection: Graph) -> set:
    leaks = set()
    for cls in (ILADUB.CandidateConcept, ILADUB.PromotionDecision, ILADUB.SourceRegion):
        leaks |= {str(s) for s in projection.subjects(RDF.type, cls)}
    return leaks


def certify_federation(a_interior: Graph, a_projection: Graph, b_graph: Graph) -> FederationVerdict:
    """Certify: projection ⊆ promoted interior (sound) ∧ projection carries no interior term
    (opaque) ∧ every concept B grounded to is in the projection (contained)."""
    proj_concepts = _projection_concepts(a_projection)
    promoted = _promoted_targets(a_interior)

    unsound = tuple(sorted(proj_concepts - promoted))
    leaked = tuple(sorted(_interior_leaks(a_projection)))

    # Containment: B's ONLY terminology in this loop is A's projection, so every concept
    # B grounded to must be in the projection's concept set.
    b_targets = {str(o) for s, o in b_graph.subject_objects(ILADUB.groundsTo)}
    uncontained = tuple(sorted(b_targets - proj_concepts))

    ok = not (unsound or leaked or uncontained)
    return FederationVerdict(ok=ok, unsound=unsound, leaked=leaked, uncontained=uncontained)


def derive_governed_projection(interior: Graph, terms: Graph, governance: Graph,
                               policy: Graph, viewer) -> Graph:
    """AXIOM: run federate-projection-governed.rq for `viewer`. Materialize a one-triple
    recipe graph (<urn:federate:recipe> etkl:forViewer viewer) and union all graphs."""
    recipe = Graph()
    recipe.add((RECIPE, ETKL.forViewer, URIRef(str(viewer))))
    return interpret.run(os.path.join(_QUERIES, "federate-projection-governed.rq"),
                         interior, terms, governance, policy, recipe)


@dataclass(frozen=True)
class GovernedVerdict:
    ok: bool
    unsound: tuple
    leaked: tuple
    uncontained: tuple
    ungranted: tuple    # concepts in the projection whose tag the viewer's role was not granted


def _roles_of(viewer, *graphs) -> set:
    """Resolve the viewer's role(s) via (prov:actedOnBehalfOf)?/etkl:hasRole over the union."""
    g = Graph()
    for x in graphs:
        g += x
    q = """
        PREFIX etkl: <https://w3id.org/iladub/etkl#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?role WHERE { ?viewer (prov:actedOnBehalfOf)?/etkl:hasRole ?role }
    """
    return {str(r) for (r,) in g.query(q, initBindings={"viewer": URIRef(str(viewer))})}


def _permitted_for_role(governance: Graph, policy: Graph, roles: set) -> set:
    """Concepts whose sensitivity tag some role in `roles` is granted read on."""
    granted_tags = set()
    for perm in policy.objects(None, ODRL.permission):
        if (perm, ODRL.action, ODRL.read) in policy:
            assignees = {str(a) for a in policy.objects(perm, ODRL.assignee)}
            if assignees & roles:
                granted_tags |= {str(t) for t in policy.objects(perm, ODRL.target)}
    permitted = set()
    for concept, tag in governance.subject_objects(ETKL.sensitivity):
        if str(tag) in granted_tags:
            permitted.add(str(concept))
    return permitted


def certify_governed_federation(interior: Graph, governance: Graph, policy: Graph, viewer,
                                projection: Graph, consumer_graph: Graph) -> GovernedVerdict:
    """certify_federation (sound ∧ opaque ∧ contained) PLUS governance-soundness:
    every concept in the projection must be one the viewer's role was granted read on."""
    base = certify_federation(interior, projection, consumer_graph)
    roles = _roles_of(viewer, interior, governance, policy)
    permitted = _permitted_for_role(governance, policy, roles)
    proj_concepts = _projection_concepts(projection)
    ungranted = tuple(sorted(proj_concepts - permitted))
    ok = base.ok and not ungranted
    return GovernedVerdict(ok=ok, unsound=base.unsound, leaked=base.leaked,
                           uncontained=base.uncontained, ungranted=ungranted)
