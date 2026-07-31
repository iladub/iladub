"""Membrane tests (spec §6, closed world): conforming minimal graph + one
negative per shape. AXIOM/SHACL — validation only, never derivation."""
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import XSD

from tests.docgov_extract import DG, doc_iri

REPO = Path(__file__).resolve().parent.parent
SHAPES = Graph().parse(REPO / "vocab" / "shapes" / "doc-governance-shapes.ttl")


def _doc(g, path, cls, in_nav=False, excluded=True):
    d = doc_iri(path)
    g.add((d, RDF.type, DG.Document))
    g.add((d, DG.path, Literal(path)))
    if cls:
        g.add((d, DG.docClass, Literal(cls)))
    g.add((d, DG.inNav, Literal(in_nav)))
    g.add((d, DG.excludedFromSite, Literal(excluded)))
    return d


def _wiki(g, path="docs/wiki/concepts/ok.md"):
    d = _doc(g, path, "wiki")
    g.add((d, DG.title, Literal("Ok")))
    g.add((d, DG.docType, Literal("concept")))
    g.add((d, DG.confidence, Literal("high")))
    g.add((d, DG.updated, Literal("2026-07-30", datatype=XSD.date)))
    s = doc_iri("docs/superpowers/specs/2026-07-01-x-design.md")
    g.add((d, DG.cites, s))
    g.add((s, RDF.type, DG.Source))
    g.add((s, DG.path, Literal("docs/superpowers/specs/2026-07-01-x-design.md")))
    g.add((s, DG.exists, Literal(True)))
    g.add((s, DG.isEvidence, Literal(True)))
    return d


def _conforms(g):
    ok, _, report = validate(g, shacl_graph=SHAPES, inference="rdfs", advanced=True)
    return ok, report


def test_conforming_minimal_graph():
    g = Graph()
    _doc(g, "CLAUDE.md", "contract")
    a = _doc(g, "docs/manifesto.md", "assertion", in_nav=True, excluded=False)
    _doc(g, "docs/superpowers/specs/2026-07-01-old-design.md", "evidence")
    w = _wiki(g)
    g.add((w, DG.promotedTo, a))
    n = doc_iri("nav/docs/manifesto.md")  # same IRI scheme as extract()
    g.add((n, RDF.type, DG.NavEntry))
    g.add((n, DG.navPath, Literal("docs/manifesto.md")))
    g.add((n, DG.resolves, Literal(True)))
    ok, report = _conforms(g)
    assert ok, report


def test_classless_document_fails():
    g = Graph()
    _doc(g, "docs/orphan.md", None)
    ok, report = _conforms(g)
    assert not ok and "exactly one class" in str(report)


def test_tracked_confidential_fails():
    g = Graph()
    _doc(g, "internal/decisions/x.md", "confidential")
    ok, report = _conforms(g)
    assert not ok and "internal/" in str(report)


def test_assertion_not_in_nav_fails():
    g = Graph()
    _doc(g, "docs/stray.md", "assertion", in_nav=False, excluded=False)
    assert not _conforms(g)[0]


def test_unexcluded_wiki_or_evidence_fails():
    g = Graph()
    d = _wiki(g)
    g.set((d, DG.excludedFromSite, Literal(False)))
    assert not _conforms(g)[0]


def test_unresolved_nav_entry_fails():
    g = Graph()
    n = doc_iri("nav/docs/gone.md")
    g.add((n, RDF.type, DG.NavEntry))
    g.add((n, DG.navPath, Literal("docs/gone.md")))
    g.add((n, DG.resolves, Literal(False)))
    assert not _conforms(g)[0]


def test_wiki_missing_frontmatter_fields_fails():
    g = Graph()
    d = _doc(g, "docs/wiki/concepts/bare.md", "wiki")  # no title/updated/… facts
    assert not _conforms(g)[0]


def test_wiki_citing_missing_source_fails():
    g = Graph()
    d = _wiki(g)
    s = doc_iri("docs/superpowers/specs/2026-07-01-x-design.md")
    g.set((s, DG.exists, Literal(False)))
    assert not _conforms(g)[0]


def test_promoted_to_non_assertion_fails():
    g = Graph()
    w = _wiki(g)
    e = doc_iri("docs/superpowers/specs/2026-07-01-old-design.md")
    _doc(g, "docs/superpowers/specs/2026-07-01-old-design.md", "evidence")
    g.add((w, DG.promotedTo, e))
    assert not _conforms(g)[0]


def test_missing_doc_impact_after_cutoff_fails():
    g = Graph()
    d = _doc(g, "docs/superpowers/specs/2026-08-01-new-design.md", "evidence")
    g.add((d, DG.requiresDocImpact, Literal(True)))
    g.add((d, DG.hasDocImpact, Literal(False)))
    assert not _conforms(g)[0]
