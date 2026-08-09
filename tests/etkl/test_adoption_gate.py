"""The adoption GATE is an AXIOM (spec §5.2): holon-scoped to one page, no numeric literal.

A page is a candidate iff its holon carries an escalation and NO entry cell. The closure is
query-local and page-scoped — the graph as a whole stays open."""
from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD

from iladub.etkl.adoption import is_adoption_candidate
from iladub.etkl.holon import TAB

ILADUB = Namespace("https://w3id.org/iladub#")
PROV = Namespace("http://www.w3.org/ns/prov#")
DOC = URIRef("https://example.org/etkl/doc/p1")


def _escalation(g, doc=DOC):
    c = URIRef(f"{doc}#region2")
    g.add((c, RDF.type, ILADUB.CandidateConcept))
    g.add((c, PROV.wasDerivedFrom, doc))


def _cell(g, page):
    c = URIRef(f"{DOC}#cell0")
    g.add((c, RDF.type, TAB.EntryCell))
    g.add((c, TAB.onPage, Literal(page, datatype=XSD.integer)))


def test_an_escalation_with_no_cell_is_a_candidate():
    g = Graph()
    _escalation(g)
    assert is_adoption_candidate(g, 1, DOC) is True


def test_a_page_that_asserted_a_cell_is_not_a_candidate():
    g = Graph()
    _escalation(g)
    _cell(g, 1)
    assert is_adoption_candidate(g, 1, DOC) is False


def test_a_page_with_nothing_at_all_is_not_a_candidate():
    """No escalation means nothing to supersede — a page of prose is not a failure."""
    assert is_adoption_candidate(Graph(), 1, DOC) is False


def test_the_gate_is_page_scoped_not_document_scoped():
    """Another page's cell must not disqualify this one, and vice versa."""
    g = Graph()
    _escalation(g)
    _cell(g, 0)                      # page 0 read something; page 1 still failed
    assert is_adoption_candidate(g, 1, DOC) is True


def test_the_query_carries_no_numeric_literal():
    from pathlib import Path
    import re
    q = Path("vocab/queries/adoption-candidate.rq").read_text()
    body = re.sub(r"#.*", "", q)                       # comments may mention numbers
    assert not re.search(r"\b\d+(\.\d+)?\b", body), body
