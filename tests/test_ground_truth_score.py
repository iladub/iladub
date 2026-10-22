from iladub.truth import normalise


def test_normalise_is_exactly_the_three_declared_rules():
    assert normalise("  Week ended\n  Jan 1, 2025 ") == "Week ended Jan 1, 2025"
    assert normalise("-    20,940") == "-20,940"
    assert normalise("+ 62") == "+62"
    assert normalise("a - b") == "a - b"          # a sign is stripped only when leading and before a digit
    assert normalise("Ｒeserve") == "Reserve"      # NFKC
    assert normalise("Reserve") != normalise("reserve")  # no case folding


# ---------------------------------------------------------------- the scorer (Task 2)

from pathlib import Path

from rdflib import BNode, Graph, Literal, RDF, URIRef
from rdflib.namespace import Namespace, XSD

from iladub.feed import table_records
from iladub.truth import TruthRow, load_truth, score_table

TAB = Namespace("https://w3id.org/iladub/tab#")
PROV = Namespace("http://www.w3.org/ns/prov#")
KEYS = {"CORRECT", "WRONG_VALUE", "MISATTACHED", "LOST", "MISSING", "REFUSED", "SPURIOUS",
        "MARKED_LABEL"}


def _table(g, table, page, headers, rows, region_page=None):
    """A local copy of tests/test_feed_chain_walk.py::_table, with ONE change: an entry cell's
    provenance is minted in the compiler's own form, `<doc>#p<page>-<x0>-<top>`
    (src/iladub/etkl/holon.py:126), so that the feed's region (the text after the last '#')
    is `p<page>-<x0>-<top>` as it is in a real compile. The original mints `<table>-src<r>_<c>`,
    which carries no page. Header nodes are single-level."""
    g.add((table, RDF.type, TAB.HierarchicalTable))
    for c, htext in enumerate(headers):
        h = URIRef(f"{table}-h{c}")
        lc = URIRef(f"{table}-hl{c}")
        g.add((h, RDF.type, TAB.HeaderNode))
        g.add((table, TAB.hasHeaderNode, h))
        g.add((h, TAB.coversColumn, URIRef(f"{table}-c{c}")))
        g.add((lc, RDF.type, TAB.LabelCell))
        g.add((lc, TAB.cellText, Literal(htext)))
        g.add((h, TAB.hasLabel, lc))
    for r, cols in rows.items():
        ru = URIRef(f"{table}-r{r}")
        g.add((ru, RDF.type, TAB.LeafRow))
        g.add((table, TAB.hasLeafRow, ru))
        for c, text in cols.items():
            e = URIRef(f"{table}-e{r}_{c}")
            g.add((e, RDF.type, TAB.EntryCell))
            g.add((table, TAB.hasCell, e))
            g.add((e, TAB.atRow, ru))
            g.add((e, TAB.atColumn, URIRef(f"{table}-c{c}")))
            g.add((e, TAB.cellText, Literal(text)))
            g.add((e, TAB.onPage, Literal(page, datatype=XSD.integer)))
            bb = BNode()
            g.add((bb, RDF.type, TAB.BBox))
            g.add((bb, TAB.x0, Literal(50.0 * c, datatype=XSD.decimal)))
            g.add((bb, TAB.y0, Literal(10.0 * r, datatype=XSD.decimal)))
            g.add((e, TAB.hasBBox, bb))
            g.add((e, PROV.wasDerivedFrom, URIRef(f"urn:doc#p{page if region_page is None else region_page}-{50 * c}-{10 * r}")))


P0 = URIRef("urn:doc/p0#h0")
P1 = URIRef("urn:doc/p1#h0")
HEAD = ["Item", "X", "Y", "Z", "Q", "Gamma"]


def _truth(label, col, value, marked=None, occ=0):
    return TruthRow(label, marked or label, occ, col, value)


def test_every_truth_cell_gets_exactly_one_outcome_and_the_eight_keys_are_exact():
    g = Graph()
    _table(g, P0, 0, HEAD, {
        0: {0: "Alpha", 1: "1", 2: "2", 3: "3", 4: "42"},
        1: {0: "Beta1", 1: "5", 5: "7"},      # the label carries a footnote mark; 'Gamma' is a header text
    })
    _table(g, P1, 1, HEAD, {0: {0: "Theta", 1: "9"}})   # same label as a truth row, wrong page
    truth = [
        _truth("Alpha", "X", "1"),                       # CORRECT
        _truth("Alpha", "Y", "9"),                       # WRONG_VALUE (compiled Y is 2)
        _truth("Alpha", "W", "3"),                       # MISATTACHED (3 sits under Z)
        _truth("Alpha", "V", "77"),                      # LOST
        _truth("Beta", "X", "5", marked="Beta1"),        # CORRECT, matched only through the marked form
        _truth("Gamma", "X", "1"),                       # MISSING by (i): 'Gamma' is a consumed header
        _truth("Epsilon", "X", "1"),                     # REFUSED
        _truth("Zeta", "X", "1"),                        # MISSING by (iii)
        _truth("Theta", "X", "9"),                       # MISSING: its only record is on page 1
    ]
    refused = ["Gamma and Epsilon\nsit in a band nobody asserted"]
    got = score_table(g, truth, [0], refused)
    assert got == {"CORRECT": 2, "WRONG_VALUE": 1, "MISATTACHED": 1, "LOST": 1, "MISSING": 3,
                   "REFUSED": 1, "SPURIOUS": 2, "MARKED_LABEL": 1}, got
    assert set(got) == KEYS
    assert sum(got[k] for k in KEYS - {"SPURIOUS", "MARKED_LABEL"}) == len(truth)


def test_a_page_one_record_is_not_a_candidate():
    g = Graph()
    _table(g, P1, 1, HEAD, {0: {0: "Theta", 1: "9"}})
    got = score_table(g, [_truth("Theta", "X", "9")], [0], [])
    assert got["MISSING"] == 1 and got["CORRECT"] == 0, got
    got = score_table(g, [_truth("Theta", "X", "9")], [1], [])
    assert got["CORRECT"] == 1, got


def test_a_record_with_two_concepts_equal_to_the_label_matches_nothing():
    g = Graph()
    _table(g, P0, 0, HEAD, {0: {0: "Dup", 1: "Dup", 2: "4"}})
    truth = [_truth("Dup", "Y", "4")]
    got = score_table(g, truth, [0], [])
    assert got == {"CORRECT": 0, "WRONG_VALUE": 0, "MISATTACHED": 0, "LOST": 0, "MISSING": 1,
                   "REFUSED": 0, "SPURIOUS": 0, "MARKED_LABEL": 0}, got


def test_a_repeated_value_pairs_by_path_first_and_claims_each_cell_once():
    g = Graph()
    _table(g, P0, 0, HEAD, {0: {0: "Rho", 1: "5", 2: "5"}})
    # The misattachable cell (W) comes FIRST in truth order, ahead of the equal-path cell (X).
    truth = [_truth("Rho", "W", "5"), _truth("Rho", "X", "5")]
    got = score_table(g, truth, [0], [])
    assert got["CORRECT"] == 1 and got["MISATTACHED"] == 1, got
    assert got["WRONG_VALUE"] == 0 and got["LOST"] == 0 and got["SPURIOUS"] == 0, got


def test_a_repeated_label_matches_by_occurrence_in_output_order():
    g = Graph()
    _table(g, P0, 0, HEAD, {0: {0: "Twin", 1: "1"}, 1: {0: "Twin", 1: "2"}})
    truth = [_truth("Twin", "X", "1", occ=0), _truth("Twin", "X", "2", occ=1)]
    assert score_table(g, truth, [0], [])["CORRECT"] == 2


def test_load_truth_reads_the_committed_csv_and_the_provenance_pages():
    rows, pages = load_truth(Path(__file__).parent / "ground-truth" / "fed-h41-2025-01-02", "table-1")
    assert pages == [0]
    assert len(rows) == 128 and isinstance(rows[0], TruthRow) and isinstance(rows[0].row_occurrence, int)
    assert rows[0].row_label == "Reserve Bank credit"


def test_the_page_comes_from_the_concept_regions_never_from_the_row_id():
    """The row_id loses its `p<page> ` prefix once a row header path covers the row (the R166 fix
    this floor rewards), so the scorer must not read it. Here the cells' `tab:onPage` says page 1 (so the
    row_id starts `p1 `) while their regions say page 0: the regions decide."""
    g = Graph()
    _table(g, P1, 1, HEAD, {0: {0: "Mu", 1: "3"}}, region_page=0)
    assert [r.row_id for r in table_records(g, per_cell=True)] == ["p1 h0-r0"]
    assert score_table(g, [_truth("Mu", "X", "3")], [0], [])["CORRECT"] == 1
    assert score_table(g, [_truth("Mu", "X", "3")], [1], [])["MISSING"] == 1


# ---------------------------------------------------------------- the per-cell shape (R333)
#
# Under `per_cell=True` a row covered by a row header (`tab:coversRow`) mints one record PER
# CELL: a row key, a column key and the cell. Both keys' texts are SPACE-joined, so neither
# the multi-level column path nor the row's leaf label can be read off a concept's text. The
# scorer regroups the row's records and reads both paths off the header nodes the keys' regions
# name. The fixtures are `tests/test_feed_matrix_cell.py`'s, the shape `holon` emits.

import pytest

from tests.test_feed_matrix_cell import _matrix
from iladub.truth import TruthShapeError

AVG = [("Averages", "Week ended"), ("Averages", "Change")]
M = URIRef("urn:doc/p0#m")


def test_a_per_cell_row_is_scored_as_one_row_under_its_multi_level_column_paths():
    g = _matrix(Graph(), M, 0, AVG, [("Reserve credit1", {0: "6,819", 1: "-20"}),
                                     ("Bills", {0: "5", 1: "7"})])
    truth = [_truth("Reserve credit", "Averages › Week ended", "6,819", marked="Reserve credit1"),
             _truth("Reserve credit", "Averages › Change", "-20", marked="Reserve credit1"),
             _truth("Bills", "Averages › Week ended", "5"),
             _truth("Bills", "Averages › Change", "8")]
    got = score_table(g, truth, [0], [])
    assert got == {"CORRECT": 3, "WRONG_VALUE": 1, "MISATTACHED": 0, "LOST": 0, "MISSING": 0,
                   "REFUSED": 0, "SPURIOUS": 0, "MARKED_LABEL": 1}, got


def test_a_per_cell_row_under_a_nested_row_header_matches_by_its_leaf_label():
    g = _matrix(Graph(), M, 0, AVG, [("Bills", {0: "5", 1: "7"})])
    group, glabel = URIRef(f"{M}-rg0"), URIRef(f"{M}-rgl0")
    g.add((group, RDF.type, TAB.HeaderNode))
    g.add((M, TAB.hasHeaderNode, group))
    g.add((group, TAB.headerLevel, Literal(0, datatype=XSD.integer)))
    g.add((group, TAB.coversRow, URIRef(f"{M}-r0")))
    g.add((glabel, RDF.type, TAB.LabelCell))
    g.add((glabel, TAB.cellText, Literal("Securities held outright")))
    g.add((glabel, TAB.onPage, Literal(0, datatype=XSD.integer)))
    g.add((group, TAB.hasLabel, glabel))
    leaf = URIRef(f"{M}-rh0")
    g.set((leaf, TAB.headerLevel, Literal(1, datatype=XSD.integer)))
    g.add((leaf, TAB.parentHeader, group))
    (rk,) = {c.text for r in table_records(g, per_cell=True) for c in r.concepts
             if c.role.endswith("RowKey")}
    assert rk == "Securities held outright Bills"     # the precondition: the text is the path
    truth = [_truth("Bills", "Averages › Week ended", "5"), _truth("Bills", "Averages › Change", "7")]
    assert score_table(g, truth, [0], [])["CORRECT"] == 2


def test_a_multi_level_column_path_joins_with_the_separator_the_scorer_expects():
    # No row header covers the row, so this is the one-record-per-row shape: the label is a cell.
    g = _matrix(Graph(), M, 0, [("Item",)] + AVG, [(None, {0: "Alpha", 1: "5", 2: "6"})])
    truth = [_truth("Alpha", "Averages › Week ended", "5"), _truth("Alpha", "Averages › Change", "6")]
    got = score_table(g, truth, [0], [])
    assert got["CORRECT"] == 2 and got["SPURIOUS"] == 0, got


def test_two_label_cells_naming_one_region_with_different_paths_refuse_loudly():
    # Two tables on one page whose label cells share an IRI fragment: the feed gives the second
    # its whole IRI as a region, and the readable region then names two different paths.
    g = _matrix(Graph(), URIRef("urn:a#m"), 0, AVG, [("Bills", {0: "5"})])
    _matrix(g, URIRef("urn:b#m"), 0, AVG, [("Notes", {0: "6"})])
    with pytest.raises(TruthShapeError):
        score_table(g, [_truth("Bills", "Averages › Week ended", "5")], [0], [])
