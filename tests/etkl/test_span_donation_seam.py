"""Span donation — the seam. compile_tables offers the spanning reading at the assert leg;
the membrane disposes; acceptance is recorded; refusal is invisible.

Spec: docs/superpowers/specs/2026-09-11-the-span-the-author-drew-design.md § 3.1
Plan: docs/superpowers/plans/2026-09-13-the-span-the-author-drew.md, Task 3

THE INVARIANT, and the reason the reading tests and the ledger test are separate: span donation
changes WHICH COLUMNS the author's labels head. It moves no ink. `test_graincorp_p0_ledger_is_
unmoved` must stay GREEN when the offer is removed from the seam while the reading tests go RED
— that separation is the proof, and it is what the task's falsification block exercises.

THE CI FIXTURE EARNS ITS OWN LICENCE — nothing is patched. Getting there took four measured
variants and the result is worth stating, because it is not obvious: the page needs BOTH bands
ruled (clause (d) compares two DRAWN sets, so the recipient must own a vector too), and it needs
two text key columns for the datagrid to reach the HeterogeneousColumn test at all — with one
text column or none it stops earlier at RowAddressability/no-key and the donor is never
licensed. It also needs every recipient word to fit inside its own column: the same fixture with
'September' in a 48pt column makes `_rule_boundaries` return None, the recipient classifies
UNSUPPORTED_TABLE, and the donation has nothing to donate to.
"""
import os

import pytest
from rdflib import Namespace, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, RDFS

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from reportlab.lib.pagesizes import letter        # noqa: E402
from reportlab.pdfgen import canvas               # noqa: E402

TAB = Namespace("https://w3id.org/iladub/tab#")
ETKL = Namespace("https://w3id.org/iladub/etkl#")

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
GRAINCORP = os.path.join(CORPUS, "ag-trade", "graincorp-capacity-2026-08-04.pdf")
corpus_only = pytest.mark.skipif(not os.path.exists(GRAINCORP), reason="corpus not fetched")

PAGE_H = letter[1]
D_XS = (72.0, 168.0, 264.0, 360.0)                            # the donor's 3 drawn intervals
R_XS = (72.0, 120.0, 168.0, 216.0, 264.0, 312.0, 360.0)       # the recipient's 6 leaf columns
LABELS = (("Mackay", 100.0), ("Gladstone", 190.0), ("Portland", 290.0))
ROWS = (("2025/26", "Aug", "12500", "10000", "14000", "13000"),
        ("2025/26", "Sep", "11000", "13500", "12000", "11500"),
        ("2026/27", "Oct", "10500", "12000", "11500", "10000"),
        ("2026/27", "Nov", "13000", "11500", "10000", "12500"))


def _page(path, gap=150.0):
    """A coarse ruled donor band above a fine ruled recipient band — graincorp p0's shape."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 9)
    y = PAGE_H - 90.0
    for x in D_XS:
        c.line(x, y - 4.0, x, y + 14.0)
    for t, x in LABELS:
        c.drawString(x, y, t)
    y -= gap
    top = y + 14.0
    for i, row in enumerate(ROWS):
        for j, cell in enumerate(row):
            c.drawString(R_XS[j] + 3.0, y - i * 14.0, cell)
    for x in R_XS:
        c.line(x, y - len(ROWS) * 14.0, x, top)
    c.save()
    return str(path)


def _spanning_labels(g, table):
    """(covered leaf-column indices, label text) per header node, ordered left to right.

    The column index is parsed from the leaf-column URI `…-c{i}` that `assert_hier_region`
    mints, so this reads the compiled graph rather than re-deriving anything."""
    out = []
    for h in g.objects(table, TAB.hasHeaderNode):
        cols = sorted(int(str(c).rsplit("-c", 1)[1])
                      for c in g.objects(h, TAB.coversColumn))
        lc = g.value(h, TAB.hasLabel)
        out.append((tuple(cols), str(g.value(lc, TAB.cellText))))
    return [t for _, t in sorted(out)], [c for c, _ in sorted(out)]


# --- the seam, in CI --------------------------------------------------------------------

def test_the_recipient_reads_under_the_donors_spanning_labels(tmp_path):
    """The headline: four data rows that today read under their own first line now read under
    three labels the author drew on a band of their own, each heading TWO leaf columns."""
    from iladub.etkl.compile import compile_tables

    rep = compile_tables(_page(tmp_path / "span.pdf"), 0, validate_shapes=False)
    assert [r.verdict for r in rep.regions] == ["ignored", "asserted"]

    table = URIRef(rep.regions[1].table_uri)
    assert (table, RDF.type, TAB.HierarchicalTable) in rep.graph
    texts, covers = _spanning_labels(rep.graph, table)
    assert texts == ["Mackay", "Gladstone", "Portland"], texts
    assert covers == [(0, 1), (2, 3), (4, 5)], covers


def test_the_provenance_link_names_the_donor_band_and_is_not_headerDonatedBy(tmp_path):
    """The donor is a band the reader IGNORED, not a table, so the link points at the carried
    ignored-band node. `tab:headerDonatedBy` must NOT be used: its domain and range are both
    tab:RecordTable, and this table is hierarchical while the donor has no table URI at all."""
    from iladub.etkl.compile import compile_tables

    rep = compile_tables(_page(tmp_path / "span.pdf"), 0, validate_shapes=False)
    g = rep.graph
    table = URIRef(rep.regions[1].table_uri)
    donor = next(g.objects(table, TAB.spanHeaderDonatedBy))
    assert str(donor).endswith("#ignored0"), donor
    assert (donor, RDF.type, ETKL.IgnoredBand) in g
    assert (table, TAB.headerDonatedBy, None) not in g


def test_an_accepted_span_donation_is_a_recorded_decision(tmp_path):
    """Only on acceptance, and exactly once."""
    from iladub.etkl.compile import compile_tables

    rep = compile_tables(_page(tmp_path / "span.pdf"), 0, validate_shapes=False)
    labels = [str(o) for o in rep.graph.objects(None, RDFS.label)]
    assert labels.count("span_donation") == 1, labels


def test_a_refused_span_donation_leaves_the_page_isomorphic(tmp_path, monkeypatch):
    """Global Constraint 6: a refused donation is INVISIBLE — no triple, no decision record, no
    report. The page must be isomorphic to one where the derivation never proposed anything."""
    import iladub.etkl.donation as donation
    from iladub.etkl.compile import compile_tables

    path = _page(tmp_path / "span.pdf")
    monkeypatch.setattr(donation, "span_donation_admissible", lambda *a, **k: False)
    refused = compile_tables(path, 0, validate_shapes=False)
    monkeypatch.setattr(donation, "span_donors_for", lambda *a, **k: ())
    never = compile_tables(path, 0, validate_shapes=False)

    assert isomorphic(refused.graph, never.graph)
    assert [r.verdict for r in refused.regions] == [r.verdict for r in never.regions]
    assert (refused.asserted, refused.escalated) == (never.asserted, never.escalated)


# --- the corpus -------------------------------------------------------------------------

@corpus_only
def test_graincorp_p0_reads_nine_spanning_labels():
    """The document this was built for: the nine labels the author printed, over sixteen leaf
    columns, in the measured partition 1,1,2,2,2,2,2,2,2."""
    from iladub.etkl.compile import compile_tables

    rep = compile_tables(GRAINCORP, 0, validate_shapes=False)
    table = URIRef(rep.regions[3].table_uri)
    assert (table, RDF.type, TAB.HierarchicalTable) in rep.graph
    texts, covers = _spanning_labels(rep.graph, table)
    assert texts == ["Year", "Elevation Period", "Mackay", "Gladstone", "Fisherman Islands",
                     "Carrington", "Port Kembla", "Geelong", "Portland"], texts
    assert [len(c) for c in covers] == [1, 1, 2, 2, 2, 2, 2, 2, 2], covers
    assert str(next(rep.graph.objects(table, TAB.spanHeaderDonatedBy))).endswith("#ignored2")


@corpus_only
def test_graincorp_p0_ledger_is_unmoved():
    """THE INVARIANT. 406 is the figure tests/etkl/test_run_merge_seam.py already pins for
    ("graincorp-capacity-2026-08-04", 0), and it is the figure before and after this seam —
    which is what makes this test the control in the task's falsification: remove the offer and
    the reading tests redden while this one does not move at all."""
    from iladub.etkl.compile import compile_tables

    rep = compile_tables(GRAINCORP, 0, validate_shapes=False)
    assert rep.asserted == 406, rep.asserted
    assert rep.escalated == 0, rep.escalated


@corpus_only
def test_graincorp_still_compiles_and_seals_at_document_scope():
    """`test_expected_verdict` requires, for cor:Unadjudicated, that compile RETURN at all. The
    document-scope membrane must therefore still seal.

    MEASURED, and it answers evidence § 4's stated UNVERIFIED rather than leaving it open: this
    document's TAB leg does not run at document scope at all. `_legs_for_document` gates it on
    `recognized or section_facts`, graincorp has one page so the continuation AXIOM recognizes
    nothing, and neither input is a function of how band 3 is read — so a spanning donation
    cannot open that condition, and there is no document-scope TAB verdict here to change."""
    from iladub.etkl.document import _legs_for_document, compile_document

    rep = compile_document(GRAINCORP, validate_shapes=True)
    assert rep.pages, "compile_document returned no pages"
    assert _legs_for_document(bool(rep.recognized), False) == ("dec",)
