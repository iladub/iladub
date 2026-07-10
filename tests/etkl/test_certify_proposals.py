# tests/etkl/test_certify_proposals.py
import pytest
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from iladub.etkl.propose import Proposal, FakeProposer
from iladub.etkl.reshape import certify_with_proposals
TAB = Namespace("https://w3id.org/iladub/tab#"); EX = Namespace("https://example.org/d#")


def _nameless_pivot(ragged=False):
    """Product stub + nameless Q1..Q4 pivot; 2 rows. ragged=True drops a cell so it can't invert."""
    g = Graph(); t = EX.tbl
    cols = [EX["c%d" % i] for i in range(5)]
    for c in cols:
        g.add((c, RDF.type, TAB.LeafColumn)); g.add((t, TAB.hasLeafColumn, c))

    def hdr(u, lvl, lbl, covers):
        g.add((u, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, u))
        g.add((u, TAB.headerLevel, Literal(lvl)))
        if lbl is not None:
            lc = URIRef(str(u) + "l"); g.add((lc, TAB.cellText, Literal(lbl))); g.add((u, TAB.hasLabel, lc))
        for c in covers:
            g.add((u, TAB.coversColumn, c))
    hdr(EX.hstub, 0, "Product", [cols[0]])
    hdr(EX.hspan, 0, None, cols[1:])                      # nameless spanning parent
    for c, nm in zip(cols[1:], ["Q1", "Q2", "Q3", "Q4"]):
        hdr(URIRef(str(c) + "h"), 1, nm, [c])
    rows = ["A", "B"]; ru = {r: EX["r" + r] for r in rows}
    vals = {"A": ["A", "1", "2", "3", "4"], "B": ["B", "5", "6", "7", "8"]}
    for r in rows:
        g.add((ru[r], RDF.type, TAB.LeafRow)); g.add((t, TAB.hasLeafRow, ru[r]))
        for c, txt in zip(cols, vals[r]):
            if ragged and r == "B" and c == cols[2]:      # drop one measure cell → not invertible
                continue
            e = EX["e_%s_%s" % (r, str(c)[-1])]
            g.add((e, RDF.type, TAB.EntryCell)); g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru[r])); g.add((e, TAB.atColumn, c)); g.add((e, TAB.cellText, Literal(txt)))
    return g, t


def test_happy_path_names_and_inverts():
    g, t = _nameless_pivot()
    out = certify_with_proposals(g, t, FakeProposer(Proposal("Quarter", 0.9, "quarters")))
    assert out.oracle_ok and out.normalized_base is not None
    facts = list(g.objects(out.normalized_base, TAB.hasBaseFact))
    assert len(facts) == 8
    coords = {(str(g.value(co, TAB.dimensionName)), str(g.value(co, TAB.value)))
              for f in facts for co in g.objects(f, TAB.atDimensionValue)}
    assert ("Quarter", "Q1") in coords and ("Product", "A") in coords


def test_declined_proposal_escalates():
    g, t = _nameless_pivot()
    out = certify_with_proposals(g, t, FakeProposer(None))
    assert out.normalized_base is None
    assert (None, RDF.type, TAB.NormalizedBase) not in g


def test_uninvertible_region_is_rejected_even_with_a_name():
    g, t = _nameless_pivot(ragged=True)
    out = certify_with_proposals(g, t, FakeProposer(Proposal("Quarter", 0.9, "quarters")))
    assert not out.oracle_ok and out.normalized_base is None


def test_named_pivot_does_not_call_proposer(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import region_pivot_pdf
    from iladub.etkl import compile_tables

    class _Spy:
        def propose_dimension_name(self, values, context):
            raise AssertionError("proposer must NOT be called when the pivot is already named")
    p = tmp_path / "rp.pdf"; region_pivot_pdf(str(p))
    rep = compile_tables(str(p))
    t = next(rep.graph.subjects(RDF.type, TAB.HierarchicalTable))
    out = certify_with_proposals(rep.graph, t, _Spy())   # Region is named → no proposal
    assert out.normalized_base is None                   # A2 pass finds no nameless pivot; A1 owns named ones
