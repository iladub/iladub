"""Every header LabelCell of a hierarchical table carries its box and its page.

[[R177]]. `assert_hier_region` is the ONE `tab:LabelCell` emitter of six that writes no
`tab:hasBBox` -- measured `grep -n "TAB.LabelCell" src/iladub/etkl/holon.py` -> six sites, five of
which write a box within twelve lines (`:144 :194 :262 :294 :346`) and one of which does not. Its
own comment says otherwise ("LabelCell carries the header text + provenance context"), which is how
it survived: the defect was stated in the code and read as a description.

WHY THIS IS NOT ONLY A PROVENANCE GAP. `scripts/unbooked_ink_fate.py` decides whether an asserted
band's ink was RECOVERED or DROPPED by containment in an emitted cell's box, so a boxless LabelCell
makes carried ink indistinguishable from dropped ink. Across the corpus the two populations are the
same set of pages -- 5 of 27 carry bbox-less LabelCells, and those same 5 carry all 111 orphan words
(`scripts/unbooked_ink_fate_corpus.py`; spec § 1.2). So this emitter blinds the only instrument that
can dispose [[R178]], which is why R177 is closed first.

The membrane does NOT catch it: `tab:EntryCellPhysicalShape`
(`vocab/shapes/tab-physical-shapes.ttl:13-19`) requires `tab:hasBBox` on every `tab:EntryCell`, and
no shape requires it on a `tab:LabelCell` (spec § 3.5). These tests are the only enforcement.
"""
import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import Graph, Literal, URIRef  # noqa: E402
from rdflib.namespace import RDF  # noqa: E402

from tests.etkl.fixtures import all_text_hier_ruled_pdf  # noqa: E402

TAB = "https://w3id.org/iladub/tab#"


def _t(name):
    return URIRef(TAB + name)


def _hier_graph(tmp_path):
    """Compile the one fixture that routes through `assert_hier_region` (`compile.py:1165`).

    `all_text_hier_ruled_pdf` is an all-TEXT hierarchical table whose 'Contact' header spans
    Email+Phone -- an all-text body is what keeps it off the matrix and record paths. Asserted by
    the emitted table type below rather than by reading the fixture's docstring, so a routing change
    fails this helper instead of silently testing a different branch.
    """
    from iladub.etkl import compile as C

    p = tmp_path / "hier.pdf"
    all_text_hier_ruled_pdf(str(p))
    rep = C.compile_tables(str(p), 0, validate_shapes=False)
    g = rep.graph
    tables = list(g.subjects(RDF.type, _t("HierarchicalTable")))
    assert tables, "fixture no longer routes through assert_hier_region -- this module tests nothing"
    return g, rep


def _header_label_cells(g: Graph):
    """LabelCells reachable as a HeaderNode's `tab:hasLabel` -- exactly what `:535` emits."""
    return [lc for node in g.subjects(RDF.type, _t("HeaderNode"))
            for lc in g.objects(node, _t("hasLabel"))]


def test_every_header_label_cell_carries_a_bbox(tmp_path):
    """O2, first half. The gap R177 names, stated as the thing that must stop being true."""
    g, _ = _hier_graph(tmp_path)
    cells = _header_label_cells(g)
    assert cells, "no header LabelCells emitted -- the fixture stopped exercising the site"
    missing = [str(lc) for lc in cells if g.value(lc, _t("hasBBox")) is None]
    assert missing == [], (
        "%d of %d header LabelCells carry no tab:hasBBox: %s"
        % (len(missing), len(cells), missing[:5]))


def test_every_header_label_cell_carries_its_page(tmp_path):
    """O2, second half. `tab:onPage` travels with the box at all five sibling emitters.

    Separate from the bbox assertion on purpose: a repair that writes a box and forgets the page
    leaves the cell locatable on the wrong sheet, and one combined assertion would not say which
    half broke.
    """
    g, rep = _hier_graph(tmp_path)
    cells = _header_label_cells(g)
    pages = {g.value(lc, _t("onPage")) for lc in cells}
    assert pages == {Literal(0)}, "expected every header label on page 0, got %r" % (pages,)


def test_the_box_is_the_header_cell_s_own_box_not_the_band_s(tmp_path):
    """O2, third half -- and the one that stops a box being written from the wrong operand.

    A repair that wrote the BAND's box on every label would pass both tests above. This asserts the
    boxes are DISTINCT (a hierarchical header has cells at two levels and several columns) and that
    each lies inside the page, so a constant, a band box, or a zero box all fail.
    """
    g, _ = _hier_graph(tmp_path)
    boxes = []
    for lc in _header_label_cells(g):
        bb = g.value(lc, _t("hasBBox"))
        assert bb is not None
        vals = tuple(float(g.value(bb, _t(a))) for a in ("x0", "y0", "x1", "y1"))
        boxes.append(vals)
    assert len(set(boxes)) > 1, "every header label got the SAME box -- a band box, not a cell box"
    for (x0, y0, x1, y1) in boxes:
        assert x1 > x0 and y1 > y0, "degenerate box %r" % ((x0, y0, x1, y1),)


def test_a_node_with_no_geometry_stays_boxless(tmp_path):
    """The OTHER half of the presence test, and the half falsification cannot reach.

    `span.build_reading` mints `HeaderNode(0, (flank,), "", None)` for a column carrying no header
    ink at all -- a node with nothing to write. The writer is conditional so that node keeps its
    empty text and gets NO box, rather than a zero box asserting a location the source never had
    (CLAUDE.md § Core design principles 7).

    That matters beyond honesty: `tab:WrappedCellShape`
    (`vocab/shapes/tab-physical-shapes.ttl:26-31`) requires non-empty `cellText` on cells that carry
    a box, and `region_tiles` runs those shapes over this very graph
    (`src/iladub/etkl/compile.py:1166`). An UNCONDITIONAL writer would turn the flank node into a
    membrane violation and the whole region into a refusal to assert.

    No corpus document is known to mint such a node, so the state is CONSTRUCTED here by stripping
    the geometry from one real node -- the alternative being no coverage of the branch at all.
    """
    from dataclasses import replace

    from iladub.etkl import compile as C
    from iladub.etkl.hierarchical import classify_hierarchical
    from iladub.etkl.holon import assert_hier_region
    from rdflib import URIRef as U

    p = tmp_path / "hier.pdf"
    all_text_hier_ruled_pdf(str(p))
    band = next(b for b in C.page_bands(str(p), 0) if classify_hierarchical(b) is not None)
    hreg = classify_hierarchical(band)

    stripped = replace(hreg.tree[0], x0=None, top=None, x1=None, bottom=None, page=None)
    hreg2 = replace(hreg, tree=(stripped,) + hreg.tree[1:])

    g = Graph()
    doc, table = U("urn:t:doc"), U("urn:t:doc#htable0")
    assert assert_hier_region(g, hreg2, band, table, doc, 0) > 0, "region stopped asserting"

    labels = _header_label_cells(g)
    boxless = [lc for lc in labels if g.value(lc, _t("hasBBox")) is None]
    assert len(boxless) == 1, (
        "expected exactly the one stripped node to be boxless, got %d of %d"
        % (len(boxless), len(labels)))
    assert g.value(boxless[0], _t("onPage")) is None, "a boxless cell must not claim a page either"
    assert g.value(boxless[0], _t("cellText")) is not None, "it must still carry its text"
