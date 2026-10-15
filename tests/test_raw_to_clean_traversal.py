"""holon:06 — the raw→clean traversal derived by ground_document (spec 2026-10-15)."""
import pytest
from rdflib import Graph, Namespace, RDF, URIRef

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")
from iladub.feed import Traversal, ground_document
from iladub.propose_ground import FakeGroundingProposer, GroundingProposal, MappingGroundingProposer
from tests.test_concept_feed import TX, _compiled_hier_graph, _compiled_offer_graph, _offer_deps

ETKL = Namespace("https://w3id.org/iladub/etkl#")
PROV = Namespace("http://www.w3.org/ns/prov#")
RAW = URIRef("https://example.org/demo/offer-table")
SEM = URIRef("https://example.org/demo/transplant-terms")
GROUNDED = {URIRef(f"urn:iladub:region:p0-{x}-{y}") for x in (72, 200, 320) for y in (109, 127)}
QUARANTINED = {URIRef(f"urn:iladub:region:p0-440-{y}") for y in (109, 127)}


def _offer(g=None, traversal=Traversal(RAW, (SEM,)), proposer=None):
    c, terms, shapes, p = _offer_deps()
    g = Graph() if g is None else g
    ground_document(_compiled_offer_graph(), c, proposer or p, terms, shapes, g,
                    validate_shapes=True, traversal=traversal)
    return g


def _etkl_triples(g):
    return [t for t in g if any(str(x).startswith(str(ETKL)) for x in t)]


def test_six_grounded_regions_reconciled_quarantine_excluded():
    g = _offer()
    portal, clean = URIRef(str(RAW) + "#grounding-portal"), URIRef(str(RAW) + "#clean")
    assert set(g.objects(portal, ETKL.reconciles)) == GROUNDED
    assert not QUARANTINED & set(g.objects(None, ETKL.reconciles))
    assert (clean, ETKL.throughPortal, portal) in g
    assert (clean, PROV.wasDerivedFrom, RAW) in g
    assert (portal, ETKL.portalSource, RAW) in g
    assert (portal, ETKL.portalTarget, SEM) in g
    assert len(set(g.subjects(RDF.type, ETKL.CleanDocumentHolon))) == 1


def test_nothing_grounded_constructs_nothing():
    abstain = FakeGroundingProposer(GROUNDING_ABSTAINS)
    c, _terms, shapes, _ = _offer_deps()
    g = Graph()
    # SUBSTITUTED (plan rule 5, measured 2026-10-15): with the shipped transplant terms the Organ
    # column grounds by exact field match + scheme membership even under an abstaining proposer
    # (grounded=2, proposed=6). An EMPTY terms graph gives the scheme oracle nothing to admit, so
    # grounded=0 while all eight candidates are still emitted (proposed=8): quarantined evidence
    # is in scope, promoted evidence is not. The assertions below are the plan's, unweakened.
    res = ground_document(_compiled_offer_graph(), c, abstain, Graph(), shapes, g,
                          traversal=Traversal(RAW, (SEM,)))
    assert res.grounded == 0 and res.proposed == 8
    assert _etkl_triples(g) == []


GROUNDING_ABSTAINS = GroundingProposal(
    None, "https://example.org/transplant#x", 0.1, "n/a", "urn:iladub:suggester/fake")


def test_default_constructs_nothing():
    assert _etkl_triples(_offer(traversal=None)) == []


def test_preseeded_graph_regions_not_reconciled():
    # SUBSTITUTED (plan rule 5, measured 2026-10-15): the hier fixture grounds NOTHING under
    # `_offer_deps()`'s proposer (grounded=0, proposed=30), so a pre-seed made that way holds no
    # promotion and could not distinguish "this call's output" from "all of g". The same fixture
    # under its own proposer (`test_concept_feed.py::test_hierarchical_grounds_end_to_end`, same
    # contract/terms/shapes) grounds 4 regions, p0-191-136/154/208 and p0-197-172 — disjoint
    # from GROUNDED. Same force: g holds another document's promotions before the traversal call.
    c, terms, shapes, _ = _offer_deps()
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    hier_proposer = MappingGroundingProposer({
        "Current Visit > Result (SI)": GroundingProposal(ef.iri, str(TX) + "Magnitude", 0.9,
                                                         "result", "urn:iladub:suggester/fake"),
    })
    g = Graph()
    res = ground_document(_compiled_hier_graph(), c, hier_proposer, terms, shapes, g)
    assert res.grounded > 0                                 # the pre-seed holds promotions
    seeded = {o for o in g.objects() if str(o).startswith("urn:iladub:region:")}
    assert seeded and not seeded & GROUNDED                 # a leak would be visible, not masked
    g = _offer(g)
    assert set(g.objects(None, ETKL.reconciles)) == GROUNDED


def test_second_grounding_into_same_graph_still_reconciles():
    # REGRESSION GUARD only: grounding mints fresh blank nodes per call, so this passes under the
    # fresh-local-graph design AND under a set-difference delta — it does not choose between them.
    g = _offer(traversal=None)
    g = _offer(g)
    assert set(g.objects(None, ETKL.reconciles)) == GROUNDED


def test_two_semantic_holons_one_portal():
    sem2 = URIRef("https://example.org/demo/other-terms")
    g = _offer(traversal=Traversal(RAW, (SEM, sem2)))
    portals = set(g.subjects(RDF.type, ETKL.GroundingPortal))
    assert len(portals) == 1
    assert set(g.objects(next(iter(portals)), ETKL.portalTarget)) == {SEM, sem2}


@pytest.mark.parametrize("raw, sem", [(RAW, ()), (URIRef(str(RAW) + "#x"), (SEM,))])
def test_traversal_refuses_unusable_identity(raw, sem):
    with pytest.raises(ValueError):
        Traversal(raw, sem)


def _membrane(g):
    from iladub.feed import _validate_grounding
    return _validate_grounding(g)


def test_leak_fixture_refused_on_both_focus_nodes():
    """spec § 5 item 2: no throughPortal on one Clean holon; a portal whose source is not
    the other Clean holon's wasDerivedFrom. Each violation on its own focus node."""
    import os
    g = Graph().parse(os.path.join(os.path.dirname(__file__),
                                   "raw-to-clean-traversal-leak.ttl"), format="turtle")
    conforms, report = _membrane(g)
    assert not conforms
    assert "https://example.org/leak/no-portal#clean" in report
    assert "https://example.org/leak/wrong-source#clean" in report


def test_grounding_membrane_runs_the_clean_shape():
    """The shape is IN the membrane validate_shapes=True runs (spec § 3.4), not only in a
    file a test loads by hand."""
    g = _offer()
    g.remove((URIRef(str(RAW) + "#clean"), ETKL.throughPortal, None))
    conforms, report = _membrane(g)
    assert not conforms and "CleanDocumentHolon" in report
