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
