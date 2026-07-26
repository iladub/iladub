"""Loop B foundation: the header-covering evidence graph + center-in-ink SPARQL derivation."""
from types import SimpleNamespace

from iladub.etkl.grid import LeafGrid
from iladub.etkl.headergraph import HEADER_COVERS_RQ, header_evidence, run_covers


def _cell(text, x0, x1):
    return SimpleNamespace(text=text, x0=x0, x1=x1)


def test_header_evidence_emits_columns_and_cells():
    grid = LeafGrid((100.0, 150.0, 200.0, 250.0), 3, 50.0, 1.0)
    rows = [[_cell("A", 110, 140), _cell("Reference", 170, 205), _cell("C", 210, 240)]]
    g = header_evidence(rows, grid)
    from rdflib import Namespace, RDF
    TAB = Namespace("https://w3id.org/iladub/tab#")
    assert len(list(g.subjects(RDF.type, TAB.GridColumn))) == 3
    assert len(list(g.subjects(RDF.type, TAB.HeaderCell))) == 3


def test_wide_label_covers_only_its_own_column():
    # boundaries 100,150,200,250 -> col centers 125,175,225. "Reference" ink [170,205] contains
    # ONLY col1's center (175); cols 0 and 2 sit under A/C -> covers {1}, NOT the symmetrized {0,1,2}.
    grid = LeafGrid((100.0, 150.0, 200.0, 250.0), 3, 50.0, 1.0)
    rows = [[_cell("A", 110, 140), _cell("Reference", 170, 205), _cell("C", 210, 240)]]
    covers = run_covers(HEADER_COVERS_RQ, header_evidence(rows, grid))
    assert covers == {(0, 0): (0,), (0, 1): (1,), (0, 2): (2,)}


def test_only_leaf_row_is_covered():
    # A parent row (row 0) and a leaf row (row 1); the query targets MAX(atHeaderRow) = 1 only.
    grid = LeafGrid((100.0, 150.0, 200.0, 250.0), 3, 50.0, 1.0)
    rows = [[_cell("Parent", 120, 230)],
            [_cell("A", 110, 140), _cell("B", 160, 190), _cell("C", 210, 240)]]
    covers = run_covers(HEADER_COVERS_RQ, header_evidence(rows, grid))
    assert set(k[0] for k in covers) == {1}          # only leaf row 1
    assert covers[(1, 0)] == (0,) and covers[(1, 2)] == (2,)
