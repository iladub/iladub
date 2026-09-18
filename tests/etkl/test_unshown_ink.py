"""R213 — ink the page does not show, at both crossings.

The phenomenon (spec 2026-09-17): graincorp-capacity p0 holds 110 glyphs the text layer
transcribes as "0" and the page does not show a reader. Before this loop they typed
tab:Numeric, voted in every homogeneity judgement, and were grounded as tonnages of zero —
a § 7 false assertion, because no reader of that page can see them.

There are TWO crossings and they live in different graphs (§ 8.1):

  crossing A, transient  — celltype.grid_evidence's tab:GridCell, where homogeneity is
                           computed. The cell types tab:UnshownInk, which ABSTAINS.
  crossing B, persisted  — the tab:EntryCell the contract actually reads. It mints an EMPTY
                           tab:cellText and carries its transcription in tab:unshownText.

The vocabulary half (the terms, tab:WrappedCellShape's widened disjunct, tab:UnshownInkCellShape)
is pinned in tests/test_tab.py; this file pins the carriage.
"""
import os

from iladub.etkl import celltype
from iladub.etkl.bands import Band

QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")
HB = os.path.join(QDIR, "header-body-split.rq")

# A two-column table whose column 1 is homogeneously numeric from row 1 down: the
# header/body split is 1. Row 2's "0" is the cell the page will be said not to show.
GRID = [[(0, "Port"), (1, "Capacity")],
        [(0, "Geelong"), (1, "10")],
        [(0, "Portland"), (1, "0")],
        [(0, "Newcastle"), (1, "20")]]


def _cells(grid):
    return [(r, c, t) for r, row in enumerate(grid) for (c, t) in row]


# ---------------------------------------------------------------------------
# crossing A — the abstention
# ---------------------------------------------------------------------------

def test_the_null_no_unshown_facts_types_exactly_as_before():
    """The oracle § 3.1 states for this task: with nothing supplied, nothing moves.
    Both the DEFAULTED call and the explicitly-empty one must equal the pre-R213 graph."""
    base = celltype.grid_evidence(_cells(GRID), 2)
    assert set(base) == set(celltype.grid_evidence(_cells(GRID), 2, unshown=()))
    assert set(base) == set(celltype.grid_evidence(_cells(GRID), 2, unshown=None))


def test_an_unshown_cell_types_unshown_ink_and_reads_as_empty():
    from rdflib import Literal, Namespace, URIRef
    TAB = Namespace("https://w3id.org/iladub/tab#")
    g = celltype.grid_evidence(_cells(GRID), 2, unshown={(2, 1)})

    def _cell_at(r, c):
        for u in g.subjects(TAB.atGridRow, Literal(r)):
            if (u, TAB.atGridColumn, Literal(c)) in g:
                return u
        raise AssertionError("no cell at (%d, %d)" % (r, c))

    hidden, shown = _cell_at(2, 1), _cell_at(1, 1)
    assert g.value(hidden, TAB.cellDatatype) == URIRef(TAB.UnshownInk)
    # gridText is what the REGION reads, and the region reads nothing there (§ 2.3).
    assert str(g.value(hidden, TAB.gridText)) == ""
    # Its neighbour is untouched: the abstention is per-cell, not per-column.
    assert g.value(shown, TAB.cellDatatype) == URIRef(TAB.Numeric)
    assert str(g.value(shown, TAB.gridText)) == "10"


def test_the_abstention_is_read_from_the_ontology_not_restated_in_python():
    """tab:UnshownInk abstains because vocab/ontology/tab.ttl says so, and celltype mirrors
    the ontology's tab:datatypeAbstains triples rather than hand-listing them. Adding a future
    abstaining datatype must stay a triple, not a second edit here (the R167 lesson)."""
    from rdflib import Namespace
    TAB = Namespace("https://w3id.org/iladub/tab#")
    assert (TAB.UnshownInk, TAB.datatypeAbstains, None) in [
        (s, p, None) for s, p, o in celltype._DATATYPE_DECLARATIONS]
    # And it is in NO family: unshown ink is not a kind of quantity, whatever it transcribes.
    assert (TAB.UnshownInk, TAB.inDatatypeFamily, None) not in [
        (s, p, None) for s, p, o in celltype._DATATYPE_DECLARATIONS]


def test_an_unshown_cell_does_not_vote_in_the_homogeneity_judgement():
    """The whole point of the abstention, stated as a difference the AXIOM can see.

    Column 1 of MIXED is numeric from row 1 down EXCEPT for row 2, which holds the word
    "closed" — so the split cannot be 1 while that cell votes. Declare row 2 unshown and it
    abstains exactly as a tab:Blank does, and the split moves to 1.
    """
    mixed = [[(0, "Port"), (1, "Capacity")],
             [(0, "Geelong"), (1, "10")],
             [(0, "Portland"), (1, "closed")],
             [(0, "Newcastle"), (1, "20")]]
    shown = celltype.run_scalar(HB, celltype.grid_evidence(_cells(mixed), 2))
    hidden = celltype.run_scalar(
        HB, celltype.grid_evidence(_cells(mixed), 2, unshown={(2, 1)}))
    assert shown != 1, "fixture is not discriminating: the split is already 1"
    assert hidden == 1, "an unshown cell still voted (got %r)" % (hidden,)


def test_band_carries_the_unshown_set_and_defaults_empty():
    """The carrier, and the precedent it follows: Band.captions and Band.unit_markers are
    default-empty for exactly this reason — every existing constructor must stand."""
    b = Band(lines=(), top=0.0, bottom=1.0)
    assert b.unshown == ()
    assert Band(lines=(), top=0.0, bottom=1.0, unshown=((2, 1),)).unshown == ((2, 1),)


# ---------------------------------------------------------------------------
# crossing B — the persisted cell, and O7's refusal
# ---------------------------------------------------------------------------

import dataclasses                                                      # noqa: E402
import pytest                                                           # noqa: E402

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import Graph, Literal, Namespace, URIRef                    # noqa: E402

TAB = Namespace("https://w3id.org/iladub/tab#")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ONT = os.path.join(ROOT, "vocab", "ontology", "tab.ttl")
SHDIR = os.path.join(ROOT, "vocab", "shapes")


def _shapes():
    g = Graph()
    g.parse(os.path.join(SHDIR, "tab-shapes.ttl"), format="turtle")
    g.parse(os.path.join(SHDIR, "tab-physical-shapes.ttl"), format="turtle")
    return g


def _region(tmp_path, unshown=()):
    """The shipped 3x3 record fixture, with an unshown set declared on its band."""
    from tests.etkl.fixtures import simple_table_pdf
    from iladub.etkl import extract_words, text_lines, detect_bands
    from iladub.etkl.regions import classify
    p = tmp_path / "x.pdf"
    simple_table_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[1]
    reg = classify(dataclasses.replace(band, unshown=tuple(unshown)))
    return reg


def _cell_at(g, table, row, col):
    return URIRef(f"{table}-e{row}_{col}")


def test_persisted_unshown_cell_empties_celltext_and_carries_the_transcription(tmp_path):
    from iladub.etkl.holon import assert_record_region
    table, doc = URIRef("urn:t"), URIRef("urn:doc")

    plain = Graph()
    assert_record_region(plain, _region(tmp_path), table, doc, page=0)
    victim = _cell_at(plain, table, 1, 1)
    was = str(plain.value(victim, TAB.cellText))
    assert was, "fixture is not discriminating: that cell was already textless"

    g = Graph()
    assert_record_region(g, _region(tmp_path, unshown=[(1, 1)]), table, doc, page=0)
    assert str(g.value(victim, TAB.cellText)) == ""
    assert str(g.value(victim, TAB.unshownText)) == was
    # Nothing else is dropped: bbox, page, row and column all survive (§ 7, provenance-to-page).
    for p in (TAB.onPage, TAB.hasBBox, TAB.atRow, TAB.atColumn):
        assert g.value(victim, p) is not None, p
    # And its neighbours are untouched -- the carriage is per-address, not per-row or per-column.
    assert str(g.value(_cell_at(g, table, 1, 0), TAB.cellText)) == \
        str(plain.value(_cell_at(plain, table, 1, 0), TAB.cellText))


def test_the_persisted_unshown_cell_crosses_the_membrane(tmp_path):
    """The whole point of T1: before the widened disjunct this graph was REFUSED."""
    from pyshacl import validate
    from iladub.etkl.holon import assert_record_region
    g = Graph()
    assert_record_region(g, _region(tmp_path, unshown=[(1, 1)]),
                         URIRef("urn:t"), URIRef("urn:doc"), page=0)
    conforms, _, text = validate(g, shacl_graph=_shapes(),
                                 ont_graph=Graph().parse(ONT, format="turtle"),
                                 inference="rdfs", advanced=True)
    assert conforms, text


def test_the_null_no_unshown_addresses_leaves_the_graph_identical(tmp_path):
    from rdflib.compare import isomorphic
    from iladub.etkl.holon import assert_record_region
    a, b = Graph(), Graph()
    assert_record_region(a, _region(tmp_path), URIRef("urn:t"), URIRef("urn:doc"), page=0)
    assert_record_region(b, _region(tmp_path, unshown=()), URIRef("urn:t"), URIRef("urn:doc"), page=0)
    # ISOMORPHIC, not set-equal: every bbox is a fresh BNode per emission, so set equality
    # would compare blank-node labels and fail on two runs of identical code.
    assert isomorphic(a, b)
    assert not list(a.subjects(TAB.unshownText, None))


def test_o7_an_address_that_reaches_no_cell_REFUSES(tmp_path):
    """O7 (§ 8.8), in its per-address form. The grid address space and the persisted one
    coincide on ONE region of ONE document, measured and EMPIRICAL (§ 8.4). An address the
    disposal supplied that no minted cell consumed means they disagree here -- and the
    carriage refuses the region rather than write the transcription onto the wrong cell,
    or onto none at all while reporting success."""
    from iladub.etkl.holon import assert_record_region, UnshownCarriageError
    with pytest.raises(UnshownCarriageError) as exc:
        assert_record_region(Graph(), _region(tmp_path, unshown=[(99, 99)]),
                             URIRef("urn:t"), URIRef("urn:doc"), page=0)
    assert "reached no tab:EntryCell" in str(exc.value)
    assert "(99, 99)" in str(exc.value)


def test_o7_refuses_rather_than_silently_half_carrying(tmp_path):
    """The direction that matters: one good address and one bad one is still a refusal.
    A carriage that wrote the good one and dropped the bad one would report success on a
    region whose address spaces provably disagree."""
    from iladub.etkl.holon import assert_record_region, UnshownCarriageError
    with pytest.raises(UnshownCarriageError):
        assert_record_region(Graph(), _region(tmp_path, unshown=[(1, 1), (99, 99)]),
                             URIRef("urn:t"), URIRef("urn:doc"), page=0)


# ---------------------------------------------------------------------------
# T5 — clause 2's honest form: the producer-side guard at the grounding site
# ---------------------------------------------------------------------------

def _tiny_table(cell_text, unshown_text=None):
    """One table, one row, one entry cell, with just enough structure for _read_table."""
    from rdflib import RDF
    g = Graph()
    t, row, col, e = (URIRef("urn:t"), URIRef("urn:t-r0"),
                      URIRef("urn:t-c0"), URIRef("urn:t-e0_0"))
    h, lbl = URIRef("urn:t-h0"), URIRef("urn:t-hl0")
    g.add((t, RDF.type, TAB.RecordTable))
    g.add((t, TAB.hasCell, e))
    g.add((h, TAB.headerLevel, Literal(0)))
    g.add((h, TAB.coversColumn, col))
    g.add((h, TAB.hasLabel, lbl))
    g.add((lbl, TAB.cellText, Literal("Capacity")))
    g.add((e, RDF.type, TAB.EntryCell))
    g.add((e, TAB.atRow, row))
    g.add((e, TAB.atColumn, col))
    g.add((e, TAB.cellText, Literal(cell_text)))
    if unshown_text is not None:
        g.add((e, TAB.unshownText, Literal(unshown_text)))
    bb = URIRef("urn:t-e0_0-bbox")
    g.add((bb, RDF.type, TAB.BBox))
    g.add((bb, TAB.x0, Literal(1.0)))
    g.add((bb, TAB.y0, Literal(1.0)))
    g.add((e, TAB.hasBBox, bb))
    return g, t


def test_an_unshown_cell_grounds_nothing():
    """Clause 2 (§ 8.5): no asserted contract value may be sourced from a cell whose ink the
    page does not show. The emptied tab:cellText makes that structural, and the guard makes the
    refusal EXPLICIT and attributable rather than an is_blank coincidence."""
    from iladub.feed import _read_table
    shown, t = _tiny_table("14000")
    ordered, rows, _ = _read_table(shown, t)
    assert rows, "fixture is not discriminating: nothing grounds even when the ink is shown"
    assert any(c.value == "14000" for cells in rows.values() for (_x, _y, c, _col) in cells)

    hidden, t = _tiny_table("", unshown_text="14000")
    _ordered, rows, _ = _read_table(hidden, t)
    assert rows == {}, "a tonnage the page does not show reached the grounding path: %r" % rows


def test_a_cell_that_is_read_and_not_read_REFUSES_at_the_grounding_site():
    """The breach the guard exists to make loud: tab:unshownText present AND a non-empty
    tab:cellText. tab:UnshownInkCellShape refuses this in the DOCUMENT membrane; the grounding
    path never sees that membrane (the grounded graph holds 0 tab: triples), so the guard is the
    only thing standing between a six-site emitting convention and a grounded falsehood."""
    from iladub.feed import _read_table
    g, t = _tiny_table("14000", unshown_text="14000")
    with pytest.raises(AssertionError) as exc:
        _read_table(g, t)
    assert "cannot simultaneously be read and not read" in str(exc.value)
    assert "urn:t-e0_0" in str(exc.value)


# ---------------------------------------------------------------------------
# T6 — the NEURAL worker's disposal, and the three refusals
# ---------------------------------------------------------------------------

def _grid3x3():
    """A 3x3 text layer with one hole at (1, 2): the position the page shows as genuinely empty."""
    return [(r, c, "x") for r in range(3) for c in range(3) if (r, c) != (1, 2)]


def _reading(empty, **kw):
    from iladub.etkl.unshownink import Reading
    return Reading(empty_cells=frozenset(empty), **kw)


def test_the_disagreement_types_only_cells_that_have_a_glyph_and_show_no_mark():
    from iladub.etkl.unshownink import dispose
    # The reader sees nothing at (0,0) -- which HAS a glyph -- and at (1,2), which has none.
    # Only the first is a disagreement; the second is an ordinary tab:Blank.
    got = dispose(_reading({(0, 0), (1, 2)}), _grid3x3(), 3, 3)
    assert got == frozenset({(0, 0)})


def test_refusal_1_an_address_outside_the_grid_refuses_the_whole_region():
    from iladub.etkl.unshownink import dispose
    assert dispose(_reading({(0, 0), (1, 2), (9, 9)}), _grid3x3(), 3, 3) == frozenset()


def test_refusal_2_this_is_not_the_grid_i_see_refuses_the_whole_region():
    from iladub.etkl.unshownink import dispose
    r = _reading({(0, 0), (1, 2)}, refuses_grid=True, rows_seen=13, cols_seen=20)
    assert dispose(r, _grid3x3(), 3, 3) == frozenset()


def test_refusal_3_a_reader_that_misses_a_genuinely_empty_cell_is_refused():
    """The null control, and it FIRES -- a control that cannot fire is not a control. The
    reader answers (0,0) but not (1,2), the one position the text layer already reads as empty,
    so it is not reading the page and the region is refused."""
    from iladub.etkl.unshownink import dispose
    assert dispose(_reading({(0, 0)}), _grid3x3(), 3, 3) == frozenset()


def test_refusal_3_is_scoped_to_positions_outside_a_spanning_cell():
    """The confounder, stated in § 8.7 and honoured here: a reader who reads a spanning cell's
    extent as OCCUPIED is reading correctly and must not be refused for it. 25 of gcap band 3's
    26 text-layer-empty positions are the spanning year label's column."""
    from iladub.etkl.unshownink import dispose
    got = dispose(_reading({(0, 0)}), _grid3x3(), 3, 3, spanned=frozenset({(1, 2)}))
    assert got == frozenset({(0, 0)})


def test_refusal_3_accepts_a_position_the_READER_reports_as_covered():
    """The repair of 2026-09-18. The prompt tells the reader that a position covered by a
    spanning cell is not empty; refusal 3 then refused it for obeying, because nothing in the
    pipeline could supply `spanned`. The reader now answers the scope itself: (1,2) is accounted
    for as covered rather than left unmentioned, and the disagreement at (0,0) stands."""
    from iladub.etkl.unshownink import dispose
    got = dispose(_reading({(0, 0)}, covered_cells=frozenset({(1, 2)})), _grid3x3(), 3, 3)
    assert got == frozenset({(0, 0)})


def test_refusal_3_still_fires_when_a_position_is_in_NEITHER_list():
    """The control survives the repair, which is the only thing that makes the repair admissible:
    a reader must account for every text-layer-empty position as empty OR covered. Silence about
    (1,2) is still a refusal, exactly as before."""
    from iladub.etkl.unshownink import dispose
    got = dispose(_reading({(0, 0)}, covered_cells=frozenset({(2, 2)})), _grid3x3(), 3, 3)
    assert got == frozenset()


def test_refusal_4_a_covered_position_that_HAS_a_glyph_refuses_the_region():
    """`covered_cells` is the one field a reader could abuse to make the null control vacuous --
    call everything covered and nothing is ever missed. The claim is therefore itself disposed:
    a place the reader calls covered must be a place the text layer also found empty. (0,1) has
    a glyph, so claiming it is covered by a span contradicts the evidence and refuses."""
    from iladub.etkl.unshownink import dispose
    r = _reading({(0, 0), (1, 2)}, covered_cells=frozenset({(0, 1)}))
    assert dispose(r, _grid3x3(), 3, 3) == frozenset()


def test_a_missing_answer_types_nothing_and_claims_nothing():
    """Open-world and evidence-positive (§ 4.2): a cell types unshown only where BOTH readings
    are PRESENT. No reader means no claim -- never 'therefore the ink is shown'."""
    from iladub.etkl.unshownink import dispose
    assert dispose(None, _grid3x3(), 3, 3) == frozenset()


def test_the_readings_are_never_merged():
    """§ 8.9 item 2, answered by construction: there is no API to merge two runs. A union would
    assert more than the evidence supports, an intersection would infer absence, and a majority
    vote would need a run count that is a tuned constant in all but name."""
    from iladub.etkl import unshownink
    assert not [n for n in dir(unshownink)
                if any(k in n.lower() for k in ("merge", "union", "vote", "consensus"))]


def test_the_worker_shape_cannot_express_a_value_on_the_page():
    """RF8, pinned against the generated client rather than against the .baml text: run 1 of the
    blind disposal returned "14,000" -- a tonnage off the page -- because its shape allowed it.
    The only string field is `note`, and the prompt forbids content there; every other field is
    an int or a bool, so no address-shaped answer can smuggle a value."""
    pytest.importorskip("baml_client")
    from baml_client.types import EmptyCellAddress, UnshownInkReading
    assert set(EmptyCellAddress.model_fields) == {"row", "col"}
    ann = {k: str(v.annotation) for k, v in UnshownInkReading.model_fields.items()}
    assert [k for k, v in ann.items() if "str" in v] == ["note"]


def test_the_live_reader_is_env_gated_and_off_by_default():
    from iladub.etkl.unshownink import baml_reader_available
    assert not baml_reader_available() or os.environ.get("BAML_LIVE") == "1"


# ---------------------------------------------------------------------------
# The wiring — one ask per gridded region, gated off by default
# ---------------------------------------------------------------------------

GCAP = os.path.join(ROOT, "corpus", "ag-trade", "graincorp-capacity-2026-08-04.pdf")


@pytest.mark.skipif(not os.path.exists(GCAP), reason="corpus not fetched")
def test_region_unshown_renders_and_disposes_without_a_model():
    """`region_unshown` end-to-end on the real region, with the reader faked: the crop is
    rendered from the page (PROCEDURAL raw extraction) and the disposal runs. Pins the wiring
    that a live run would otherwise be the only exercise of."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.headers import _grid_cells
    from iladub.etkl.regions import classify
    from iladub.etkl.unshownink import FakeRegionReader, Reading, region_unshown

    band = [b for b in page_bands(GCAP, 0) if classify(b).grid is not None][1]
    grid = classify(band).grid
    cells = _grid_cells(band, grid)
    nrows, ncols = len(band.lines), grid.ncols
    zeros = {(r, c) for r, c, t in cells if t.strip() == "0"}
    assert len(zeros) == 110, "fixture moved: gcap band 3 no longer holds the 110"

    # The honest answer a reader gives: the 110 unshown zeros PLUS every text-layer-empty
    # position -- which is what both blind readers returned (spec § 8.8).
    empty = {(r, c) for r in range(nrows) for c in range(ncols)} - {
        (r, c) for r, c, _ in cells}
    got = region_unshown(GCAP, 0, band, grid,
                         FakeRegionReader(Reading(empty_cells=frozenset(zeros | empty))))
    assert got == frozenset(zeros), "set identity, not a matching count (R176/R172)"

    # And no reader at all is NO CLAIM -- never "therefore the ink is shown".
    assert region_unshown(GCAP, 0, band, grid, None) == frozenset()


@pytest.mark.skipif(not os.path.exists(GCAP), reason="corpus not fetched")
def test_the_answer_a_LIVE_reader_actually_gives_now_reaches_the_graph():
    """The 2026-09-18 repair, on the real region and in the real answer shape.

    O2's live run returned the 110 unshown zeros plus (1, 6) -- and NOT the 25 column-0 positions
    the spanning year label covers, because the prompt tells it not to. Against the shipped
    disposal that answer typed ZERO: `spanned` was empty at the only call site
    (`compile.py`), so refusal 3 demanded the 25 back. `compile.py`'s own comment recorded the
    wiring as typing "NOTHING end-to-end until the spanned set exists".

    The reader now reports them as covered, and the same answer types all 110. This is the test
    the previous shape could not pass: the earlier end-to-end pin (above) fakes an answer that
    reports the spanned positions as EMPTY, which is the one thing the live reader will not do."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.headers import _grid_cells
    from iladub.etkl.regions import classify
    from iladub.etkl.unshownink import FakeRegionReader, Reading, region_unshown

    band = [b for b in page_bands(GCAP, 0) if classify(b).grid is not None][1]
    grid = classify(band).grid
    cells = _grid_cells(band, grid)
    nrows, ncols = len(band.lines), grid.ncols
    zeros = {(r, c) for r, c, t in cells if t.strip() == "0"}
    empty_positions = {(r, c) for r in range(nrows) for c in range(ncols)} - {
        (r, c) for r, c, _ in cells}

    covered = {p for p in empty_positions if p[1] == 0}          # the spanning year label
    assert len(covered) == 25, "fixture moved: the spanning column is no longer 25 positions"
    assert empty_positions - covered == {(1, 6)}, \
        "fixture moved: (1,6) is the ONE genuinely-empty position, the control's whole strength"

    live_shaped = Reading(empty_cells=frozenset(zeros | {(1, 6)}),
                          covered_cells=frozenset(covered))
    got = region_unshown(GCAP, 0, band, grid, FakeRegionReader(live_shaped))
    assert got == frozenset(zeros), "set identity, not a matching count (R176/R172)"
    assert len(got) == 110

    # FALSIFICATION, inline: the same answer WITHOUT the covered list is the state this repair
    # found -- 110 correct addresses disposed to nothing.
    mute = Reading(empty_cells=frozenset(zeros | {(1, 6)}))
    assert region_unshown(GCAP, 0, band, grid, FakeRegionReader(mute)) == frozenset()


@pytest.mark.skipif(not os.path.exists(GCAP), reason="corpus not fetched")
def test_the_pipeline_attaches_nothing_with_the_gate_off():
    """O3's null at its source: with BAML_LIVE unset, every band's `unshown` is () and the whole
    carriage is the identity. This is why the six-document null holds BY CONSTRUCTION rather than
    by prediction -- a weaker control than § 5 assumed, and reported as such."""
    from iladub.etkl.compile import page_bands
    assert os.environ.get("BAML_LIVE") != "1", "this test asserts the DEFAULT configuration"
    assert all(b.unshown == () for b in page_bands(GCAP, 0))
