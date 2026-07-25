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

from rdflib import Graph, Literal, Namespace, RDF, URIRef

from .. import ground
from . import interpret

ETKL = Namespace("https://w3id.org/iladub/etkl#")
ILADUB = Namespace("https://w3id.org/iladub#")
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
F = Namespace("https://ns.flur.ee/db#")
RECIPE = URIRef("urn:federate:recipe")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
_QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries")
_FLUREE_TEMPLATE = os.path.join(os.path.dirname(__file__), "..", "fluree", "f-policy-template.jsonld")

# The full IRIs a faithful f:query must reference to preserve AI-inherits-user + the tag join.
_F_QUERY_REFS = (
    "?$identity",
    "http://www.w3.org/ns/prov#actedOnBehalfOf",
    "https://w3id.org/iladub/etkl#hasRole",
    "https://w3id.org/iladub/etkl#grantsTag",
    "https://w3id.org/iladub/etkl#sensitivity",
)


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
    """Concepts whose sensitivity tag some role in `roles` is granted read on.
    Mirrors federate-projection-governed.rq's grant pattern EXACTLY: any resource with
    odrl:action odrl:read ; odrl:assignee <role> ; odrl:target <tag> (no odrl:permission
    linkage required), so the oracle and the query always agree."""
    granted_tags = set()
    for perm in policy.subjects(ODRL.action, ODRL.read):
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


def compile_f_policy(odrl_policy: Graph) -> Graph:
    """Compile the ODRL tag-policy to a Fluree f: policy graph: derive the flat
    etkl:grantsTag grants (AXIOM CONSTRUCT) and union them with the static, data-driven
    f:AccessPolicy template. PROCEDURAL glue — no domain decision, no tuned constant."""
    grants = interpret.run(os.path.join(_QUERIES, "compile-f-grants.rq"), odrl_policy)
    template = Graph().parse(_FLUREE_TEMPLATE, format="json-ld")
    return grants + template


@dataclass(frozen=True)
class FlureeVerdict:
    ok: bool
    missing: tuple       # (role, tag) grants the ODRL policy has but the f: policy dropped
    extra: tuple         # (role, tag) grants the f: policy has but the ODRL policy lacks
    identity_ok: bool    # the template f:query preserves AI-inherits-user + the tag join


def _odrl_grants(policy: Graph) -> set:
    """{ (role, tag) } read-granted by the ODRL policy — mirrors the governed grant pattern
    (policy.subjects(odrl:action odrl:read) -> assignee x target)."""
    out = set()
    for perm in policy.subjects(ODRL.action, ODRL.read):
        roles = {str(r) for r in policy.objects(perm, ODRL.assignee)}
        tags = {str(t) for t in policy.objects(perm, ODRL.target)}
        for r in roles:
            for t in tags:
                out.add((r, t))
    return out


def certify_f_faithful(odrl_policy: Graph, f_policy: Graph, roles=None) -> FlureeVerdict:
    """Faithful iff the f: policy grants exactly what the ODRL policy grants (grant-set
    equivalence) AND its f:query preserves AI-inherits-user + the tag join."""
    odrl = _odrl_grants(odrl_policy)
    fgr = {(str(r), str(t)) for r, t in f_policy.subject_objects(ETKL.grantsTag)}
    if roles is not None:
        rs = {str(r) for r in roles}
        odrl = {(r, t) for (r, t) in odrl if r in rs}
        fgr = {(r, t) for (r, t) in fgr if r in rs}
    missing = tuple(sorted(odrl - fgr))
    extra = tuple(sorted(fgr - odrl))
    query_texts = [str(q) for q in f_policy.objects(None, F.query)]
    identity_ok = any(all(ref in q for ref in _F_QUERY_REFS) for q in query_texts)
    ok = (not missing) and (not extra) and identity_ok
    return FlureeVerdict(ok=ok, missing=missing, extra=extra, identity_ok=identity_ok)
