"""Loop C oracle 2 — header-region content conservation.

A reading that loses header text is REFUSED by region_tiles. See
docs/superpowers/specs/2026-07-26-header-row-roles-design.md §3.4.
"""
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from iladub.etkl.tiling import region_tiles

TAB = Namespace("https://w3id.org/iladub/tab#")
_T = URIRef("urn:doc#t0")


def _source_cell(g, k, text, row=0):
    """One committed tab:HeaderSourceCell — the conservation oracle's target."""
    sc = URIRef("%s-hsc%d" % (_T, k))
    g.add((sc, RDF.type, TAB.HeaderSourceCell))
    g.add((sc, TAB.sourceText, Literal(text)))
    g.add((sc, TAB.sourceRow, Literal(row, datatype=XSD.integer)))
    g.add((_T, TAB.hasHeaderSourceCell, sc))
    return sc


def _label(g, k, text):
    """One header tab:LabelCell, as `assert_hier_region` writes it.

    The geometry is not what these tests are about, but it is what the emitter emits, and since
    [[R179]] `tab:LabelCellPhysicalShape` requires it of any label carrying text — so a label
    minted here without it would be refused by the gate for a reason that has nothing to do with
    content conservation. Adding it makes the fixture faithful; the assertions below are
    unchanged. Measured 2026-09-07: without these two triples, `test_text_merged_into_a_label_is_conserved`
    and `test_graph_without_source_cells_is_unaffected` fail on the physical shape, not the
    conservation one.
    """
    lc = URIRef("%s-hl%d" % (_T, k))
    g.add((lc, RDF.type, TAB.LabelCell))
    g.add((lc, TAB.cellText, Literal(text)))
    g.add((lc, TAB.onPage, Literal(0, datatype=XSD.integer)))
    bb = URIRef("%s-hl%d-bb" % (_T, k))
    g.add((bb, RDF.type, TAB.BBox))
    g.add((lc, TAB.hasBBox, bb))
    return lc


def _caption(g, k, text, row=0):
    cap = URIRef("%s-cap%d" % (_T, k))
    g.add((cap, RDF.type, TAB.RegionCaption))
    g.add((cap, TAB.captionText, Literal(text)))
    g.add((cap, TAB.captionRow, Literal(row, datatype=XSD.integer)))
    g.add((_T, TAB.hasCaption, cap))
    return cap


def test_lost_header_text_is_refused():
    # "Unit" appears in NO label and NO caption -> the word vanished -> refuse.
    g = Graph()
    _source_cell(g, 0, "Unit")
    _label(g, 0, "Ref")
    assert region_tiles(g) is False


def test_text_merged_into_a_label_is_conserved():
    # the continuation reading: "Unit" merged into the label "Unit Ref" -> conserved.
    g = Graph()
    _source_cell(g, 0, "Unit")
    _label(g, 0, "Unit Ref")
    assert region_tiles(g) is True


def test_text_carried_as_a_caption_is_conserved():
    # the furniture reading: "Monday" carried as a RegionCaption, not dropped -> conserved.
    g = Graph()
    _source_cell(g, 0, "Monday")
    _caption(g, 0, "Monday")
    assert region_tiles(g) is True


def test_graph_without_source_cells_is_unaffected():
    # zero-regression guard: the shape targets tab:HeaderSourceCell, so every existing
    # region (which emits none) is untouched by the new oracle.
    g = Graph()
    _label(g, 0, "Anything")
    assert region_tiles(g) is True
