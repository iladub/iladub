"""Derivation tests (spec §6, open world): SPARQL CONSTRUCT over facts
PRESENT. Only the promotion queue uses a holon-scoped NOT EXISTS."""
from pathlib import Path

from rdflib import Graph, Literal, RDF
from rdflib.namespace import XSD

from tests.docgov_extract import DG, doc_iri

REPO = Path(__file__).resolve().parent.parent
Q = REPO / "vocab" / "queries"


def _wiki_citing(updated, src_path, src_date, evidence):
    g = Graph()
    d = doc_iri("docs/wiki/concepts/p.md")
    g.add((d, RDF.type, DG.Document))
    g.add((d, DG.docClass, Literal("wiki")))
    g.add((d, DG.docType, Literal("concept")))
    g.add((d, DG.updated, Literal(updated, datatype=XSD.date)))
    s = doc_iri(src_path)
    g.add((d, DG.cites, s))
    g.add((s, RDF.type, DG.Source))
    g.add((s, DG.path, Literal(src_path)))
    if evidence:
        g.add((s, DG.docClass, Literal("evidence")))
    g.add((s, DG.lastCommitDate, Literal(src_date, datatype=XSD.date)))
    return g, d, s


def _construct(g, name):
    out = Graph()
    for t in g.query((Q / name).read_text()):
        out.add(t)
    return out


def test_stale_against_evidence_derived():
    g, d, s = _wiki_citing("2026-07-15", "docs/superpowers/specs/2026-07-30-x.md",
                           "2026-07-30", True)
    rows = _construct(g, "docgov-staleness-evidence.rq")
    assert (d, DG.staleAgainstEvidence, s) in rows


def test_fresh_page_not_stale():
    g, d, s = _wiki_citing("2026-07-30", "docs/superpowers/specs/2026-07-30-x.md",
                           "2026-07-30", True)
    assert len(_construct(g, "docgov-staleness-evidence.rq")) == 0


def test_code_staleness_separate_and_not_evidence():
    g, d, s = _wiki_citing("2026-07-15", "vocab/shapes/promotion-shapes.ttl",
                           "2026-07-30", False)
    assert len(_construct(g, "docgov-staleness-evidence.rq")) == 0
    assert (d, DG.staleAgainstCode, s) in _construct(g, "docgov-staleness-code.rq")


def test_promotion_queue_is_unpromoted_wiki_pages():
    g, d, s = _wiki_citing("2026-07-30", "docs/superpowers/specs/2026-07-30-x.md",
                           "2026-07-30", True)
    assert (d, DG.inPromotionQueue, Literal(True)) in _construct(
        g, "docgov-promotion-queue.rq")
    g.add((d, DG.promotedTo, doc_iri("docs/manifesto.md")))
    assert len(_construct(g, "docgov-promotion-queue.rq")) == 0
