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
