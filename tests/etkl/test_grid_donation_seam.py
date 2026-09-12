"""Grid donation — the seam. compile_tables offers the donated reading at the assert leg;
the membrane disposes; acceptance is recorded; refusal is invisible.

Plan: docs/superpowers/plans/2026-09-11-grid-donation.md, Task 4
"""
import os

import pytest
from rdflib import Namespace, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import RDF

from tests.etkl.test_grid_donation_disposal import EVERY_MEASURE, _head_bands, _page, _record_band

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
BFS = os.path.join(CORPUS, "gov-stats", "bfs-population-bilan-2023.pdf")
corpus_only = pytest.mark.skipif(not os.path.exists(BFS), reason="corpus not fetched")
TAB = Namespace("https://w3id.org/iladub/tab#")


def _labels(g, table):
    """The table's label texts in column order, via tab:hasHeaderNode -> tab:hasLabel."""
    out = []
    for h in g.objects(table, TAB.hasHeaderNode):
        lc = g.value(h, TAB.hasLabel)
        out.append((str(h), str(g.value(lc, TAB.cellText))))
    return [t for _, t in sorted(out)]


@corpus_only
def test_bfs_p6_reads_267_entries_under_band_2s_labels():
    """The headline (handoff 2026-09-10-the-donated-reading-tiles § 2): 222 -> 267 entries,
    every donated table labelled by the author's own header, and the provenance link set."""
    from iladub.etkl.compile import compile_tables

    rep = compile_tables(BFS, 6, validate_shapes=False)
    assert sum(r.cells for r in rep.regions) == 267
    g = rep.graph
    doc = next(s for s in g.subjects(RDF.type, TAB.RecordTable) if str(s).endswith("#table2"))
    doc = URIRef(str(doc).rsplit("#", 1)[0])
    donor = URIRef(f"{doc}#table2")
    want = _labels(g, donor)
    assert want[0] == "Grandes régions", want
    for idx, cells in {4: 36, 5: 54, 6: 36, 8: 72, 9: 63}.items():
        t = URIRef(f"{doc}#table{idx}")
        assert rep.regions[idx].cells == cells, idx
        assert _labels(g, t) == want, idx
        assert (t, TAB.headerDonatedBy, donor) in g, idx
    assert (donor, TAB.headerDonatedBy, None) not in g


@corpus_only
def test_donation_moves_no_ink_between_the_ledgers():
    """DECISION D's prediction, measured: the donor's label bboxes hold none of the
    continuation's words, the band's own line 0 becomes round-tripping data cells, and
    every token figure on the page is what it was at 808aa7a."""
    from iladub.etkl.compile import compile_tables

    rep = compile_tables(BFS, 6, validate_shapes=False)
    assert (rep.asserted, rep.escalated) == (276, 25)
    assert {i: (r.tokens_asserted, r.tokens_escalated) for i, r in enumerate(rep.regions)
            if i in (2, 4, 5, 6, 8, 9)} == {2: (15, 0), 4: (36, 0), 5: (54, 0), 6: (36, 0),
                                            8: (72, 0), 9: (63, 0)}


@corpus_only
def test_an_accepted_donation_is_a_recorded_decision():
    from iladub.etkl.compile import compile_tables
    from rdflib.namespace import RDFS

    g = compile_tables(BFS, 6, validate_shapes=False).graph
    labels = [str(o) for o in g.objects(None, RDFS.label)]
    assert labels.count("grid_donation") == 5


def test_a_refused_donation_leaves_the_page_isomorphic(tmp_path, monkeypatch):
    """Global Constraint 6, R165's § 3.2 in this loop's clothes. On the straddling page the
    derivation names a donor and the disposal refuses. Compare against the same page with
    the derivation suppressed: isomorphic (the honest form of byte-identical — see
    test_a_refused_run_leaves_the_page_byte_identical for why N-Triples equality is not).

    The plan also patched `head_line_refusals` here. That patch is DELETED: Task 3 measured
    that the real page datagrid refuses this fixture's head line every-measure, so the
    proposal side of this comparison runs entirely through shipped machinery, and only the
    suppression arm is patched."""
    import iladub.etkl.donation as donation
    from iladub.etkl.compile import compile_tables

    path = tmp_path / "straddling.pdf"
    _page(path, (80.0, 190.0, 340.0))
    with_proposal = compile_tables(str(path), 0, validate_shapes=False)
    monkeypatch.setattr(donation, "donors_for", lambda *a, **k: ())
    without = compile_tables(str(path), 0, validate_shapes=False)
    assert isomorphic(with_proposal.graph, without.graph)
    assert [r.verdict for r in with_proposal.regions] == [r.verdict for r in without.regions]


def test_a_headerless_band_reads_under_the_ruled_head_above_it(tmp_path):
    """R166's detector, inverted for the ONE shape this loop repairs: the same four data
    rows, with the head the author ruled above them, read under 'Region Total Share' and
    assert 12 entries. (test_header_row_is_assumed's detector stays RED-by-design for
    the donor-less shape it draws; this is not that fixture.)

    The plan's monkeypatch of `head_line_refusals` is DELETED here, on Task 3's
    measurement: derive_data_grid returns a grid for this page and refuses its head line
    HeterogeneousColumn/every-measure at the line its ink key identifies. The licence is
    therefore carried by the real map, and this test exercises the whole chain."""
    from iladub.etkl.compile import compile_tables

    path = tmp_path / "donated.pdf"
    bands = _page(path, (80.0, 210.0, 340.0))
    i = _record_band(bands)
    assert len(_head_bands(bands)) == 1
    rep = compile_tables(str(path), 0, validate_shapes=False)
    assert rep.regions[i].verdict == "asserted"
    assert rep.regions[i].cells == 12
    t = URIRef(rep.regions[i].table_uri)
    assert _labels(rep.graph, t) == ["Region", "Total", "Share"]
    assert (t, TAB.headerDonatedBy, None) in rep.graph


def test_the_refusal_map_is_unused_when_no_band_owns_a_vector(tmp_path, monkeypatch):
    """M1's laziness, pinned at the seam rather than only in the unit: a page with no
    ruled band must not pay for derive_data_grid at all."""
    import iladub.etkl.datagrid as datagrid
    from iladub.etkl.compile import compile_tables

    calls = []
    real = datagrid.derive_data_grid
    monkeypatch.setattr(datagrid, "derive_data_grid",
                        lambda *a, **k: (calls.append(a), real(*a, **k))[1])
    path = tmp_path / "unruled.pdf"
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 9)
    for i, row in enumerate((("Vaud", "845870"), ("Valais", "365844"))):
        for x, cell in zip((80.0, 210.0), row):
            c.drawString(x, letter[1] - 90.0 - i * 14.0, cell)
    c.save()
    compile_tables(str(path), 0, validate_shapes=False)
    assert calls == [], calls
