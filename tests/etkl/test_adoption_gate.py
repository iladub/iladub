"""The adoption GATE is an AXIOM (spec §5.2): holon-scoped to one page, no numeric literal.

A page is a candidate iff its holon carries an escalation — its reading is INCOMPLETE.

RE-BASELINED 2026-09-14 (R225 arm B, D2 — spec `2026-09-14-the-gate-not-the-predicate-design.md`
§ 1c, § 2). The gate used to ask whether the page was a TOTAL reading failure, by requiring that
no `tab:EntryCell` existed anywhere on it. That is the clause this loop removes, and the reason
is measured rather than preferred: a page may hold a PARTIAL band reading and a COMPLETE grid
reading at the same time, and the partial one then excludes the complete one merely by existing
(ons p7: 94 asserted cells blocking a 276-cell reading of the same lines).

WHAT REPLACES THE ABSENCE TEST IS NOT IN THIS QUERY. This gate runs on the pass-1 graph, before
any grid exists, so it cannot compare the two readings at all — it is a cheap PRE-FILTER over a
costly branch. The adjudication is an ordinal comparison of UNREAD INK in `compile.py`'s adoption
branch, and its contract is pinned in `test_adoption_ledger.py` / `test_datagrid.py`, not here.
"""
from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD

from iladub.etkl.adoption import is_adoption_candidate
from iladub.etkl.holon import TAB

ILADUB = Namespace("https://w3id.org/iladub#")
PROV = Namespace("http://www.w3.org/ns/prov#")
DOC = URIRef("https://example.org/etkl/doc/p1")


def _escalation(g, doc=DOC, page=1):
    """Mint what the PRODUCTION emitter mints — `holon.escalate_region`, in full.

    The helper used to add only the type and `prov:wasDerivedFrom`, a shape no code path in this
    repo produces: every escalation minter in `etkl` (`holon.py:84`, `:462`, `:517` — enumerated
    2026-09-14) emits `iladub:fromRegion` and a `SourceRegion` carrying `iladub:onPage`. The gate
    now reads that page, so a helper minting a partial candidate would be testing a graph the
    compiler cannot build.
    """
    c = URIRef(f"{doc}#region2")
    region = URIRef(f"{c}-source")
    g.add((c, RDF.type, ILADUB.CandidateConcept))
    g.add((c, PROV.wasDerivedFrom, doc))
    g.add((c, ILADUB.fromRegion, region))
    g.add((region, RDF.type, ILADUB.SourceRegion))
    g.add((region, ILADUB.onPage, Literal(int(page), datatype=XSD.integer)))


def _cell(g, page):
    c = URIRef(f"{DOC}#cell0")
    g.add((c, RDF.type, TAB.EntryCell))
    g.add((c, TAB.onPage, Literal(page, datatype=XSD.integer)))


def test_an_escalation_makes_the_page_a_candidate():
    g = Graph()
    _escalation(g)
    assert is_adoption_candidate(g, 1, DOC) is True


def test_a_page_that_asserted_a_cell_is_STILL_a_candidate():
    """THE CLAUSE THIS LOOP DELETED, pinned in its new direction.

    This assertion was `is False` until 2026-09-14 and it is inverted deliberately: one asserted
    cell no longer disqualifies a page. It is not a relaxation of the reader's standards — the
    page still has to prove, further down, that the grid leaves strictly LESS ink unread than the
    bands did. What it stops doing is answering that question with the wrong one.
    """
    g = Graph()
    _escalation(g)
    _cell(g, 1)
    assert is_adoption_candidate(g, 1, DOC) is True


def test_a_page_with_nothing_at_all_is_not_a_candidate():
    """No escalation means nothing to supersede — a page of prose is not a failure.

    This is the invariant the widening does NOT touch, and it is the one that keeps a complete
    reading from being re-read: a page that escalated nothing never reaches the branch at all.
    """
    assert is_adoption_candidate(Graph(), 1, DOC) is False


def test_the_gate_is_page_scoped_not_document_scoped():
    """Another page's escalation must not make this one a candidate.

    STRONGER THAN THE TEST IT REPLACES. The old one showed that another page's CELL did not
    disqualify this page — an assertion about the clause that no longer exists. This one shows
    the surviving page leg is load-bearing: page 0's escalation, under the same document, leaves
    page 1 alone.
    """
    g = Graph()
    _escalation(g, page=0)
    assert is_adoption_candidate(g, 0, DOC) is True
    assert is_adoption_candidate(g, 1, DOC) is False


def test_a_candidate_that_names_no_source_region_is_not_a_candidate():
    """THE PAGE LEG, falsified. A candidate with no `iladub:fromRegion` carries no page, so the
    gate cannot address it to a holon and does not admit it.

    This shape is not one the compiler produces (see `_escalation`'s docstring); the test exists
    because the gate's page-scoping now RESTS on the region, where before it rested on the
    `tab:EntryCell` clause, and a silent regression to doc-scoping would otherwise be invisible.
    """
    g = Graph()
    c = URIRef(f"{DOC}#region2")
    g.add((c, RDF.type, ILADUB.CandidateConcept))
    g.add((c, PROV.wasDerivedFrom, DOC))
    assert is_adoption_candidate(g, 1, DOC) is False


def test_the_query_carries_no_numeric_literal():
    import re
    from pathlib import Path
    # anchored to THIS file, not to the cwd (final review m3): a cwd-relative path makes the
    # test pass or fail depending on where pytest was invoked from. The house idiom, and the
    # same root `adoption.ADOPTION_CANDIDATE_RQ` resolves from `__file__`.
    q = (Path(__file__).resolve().parents[2]
         / "vocab" / "queries" / "adoption-candidate.rq").read_text()
    body = re.sub(r"#.*", "", q)                       # comments may mention numbers
    assert not re.search(r"\b\d+(\.\d+)?\b", body), body
