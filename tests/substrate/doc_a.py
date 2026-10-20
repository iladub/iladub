"""doc-a: the shared input of the substrate oracle and its default-suite agreement test.

Plain Python, no marker, no Fluree: the default suite imports it (spec 2026-10-20 § 4.2, § 5.3).
"""
from __future__ import annotations

import os

from rdflib import Graph, RDF, URIRef, Namespace

from iladub.etkl import federate
from iladub.ground import load_contract, SurfaceConcept
from iladub.propose_ground import GroundingProposal, FakeGroundingProposer

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ILADUB = Namespace("https://w3id.org/iladub#")


def compiled_interior() -> Graph:
    """doc-a compiled exactly as tests/test_federation.py:78-84 does (one grounded node)."""
    fed = os.path.join(ROOT, "examples", "federation")
    contract = load_contract(os.path.join(fed, "doc-a-contract.ttl"))
    shapes = Graph().parse(os.path.join(fed, "doc-a-shapes.ttl"), format="turtle")
    terms = Graph().parse(os.path.join(fed, "terms.ttl"), format="turtle")
    concepts = [SurfaceConcept(text="aboGroup", value="O", region="row1:col-aboGroup")]
    proposer = FakeGroundingProposer(
        GroundingProposal(None, "urn:x", 0.1, "n/a", "urn:iladub:suggester/fake"))
    return federate.compile_document(
        concepts, contract, URIRef("urn:doc:a"), proposer, terms, shapes)


def ungoverned(g: Graph) -> Graph:
    """A copy of ``g`` with every iladub:wasPromotedBy removed from its one grounded node."""
    grounded = list(g.subjects(RDF.type, ILADUB.GroundedNode))
    assert len(grounded) == 1, f"doc-a must hold exactly one grounded node, found {len(grounded)}"
    out = Graph()
    for t in g:
        out.add(t)
    out.remove((grounded[0], ILADUB.wasPromotedBy, None))
    return out
