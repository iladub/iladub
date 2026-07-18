from rdflib import Namespace, RDF, Literal
from rdflib.namespace import XSD

from iladub.etkl.flankgraph import flank_evidence, sibling_columns

TAB = Namespace("https://w3id.org/iladub/tab#")

# boundaries for 4 leaf columns: col0=[0,100] col1=[100,200] col2=[200,300] col3=[300,340]
B = (0.0, 100.0, 200.0, 300.0, 340.0)


def test_emitter_strict_in_column_and_level():
    # level-0 spanning cell straddling cols 0-2 (ink 20..280 -> strictly in no single col),
    # level-0 narrow cell strictly inside col 3 (ink 305..335),
    # level-1 leaf cells each strictly inside their column.
    cells = [
        (0, 20.0, 280.0, "Region"),      # straddles -> no strictlyInColumn
        (0, 305.0, 335.0, "Notes"),      # strictly in col 3
        (1, 20.0, 80.0, "A"),            # strictly in col 0
    ]
    g = flank_evidence(cells, B)
    hcs = list(g.subjects(RDF.type, TAB.HeaderCell))
    assert len(hcs) == 3
    # the col-3 level-0 cell carries strictlyInColumn=3, headerLevel=0
    got = {(int(g.value(h, TAB.headerLevel)),
            (int(g.value(h, TAB.strictlyInColumn)) if g.value(h, TAB.strictlyInColumn) is not None else None))
           for h in hcs}
    assert (0, 3) in got        # Notes
    assert (0, None) in got     # Region straddler
    assert (1, 0) in got        # A


def test_sibling_columns_names_own_leaf_headers():
    # col 3 has its OWN header cell at level 0 (strictly in col 3) -> (3,0) a sibling.
    # the level-0 straddler (Region) is NOT strictly in any col -> contributes no sibling.
    cells = [
        (0, 20.0, 280.0, "Region"),   # straddles cols 0-2
        (0, 305.0, 335.0, "Notes"),   # strictly in col 3, level 0
        (1, 20.0, 80.0, "A"),         # strictly in col 0, level 1
    ]
    sibs = sibling_columns(cells, B)
    assert (3, 0) in sibs      # col 3 is a same-level (0) sibling leaf
    assert (0, 1) in sibs      # col 0 has its own level-1 header
    assert (0, 0) not in sibs  # col 0 has NO own strict level-0 header (only the straddler covers it)


def test_sibling_columns_empty_when_header_empty():
    # a flank column (col 3) with NO own header cell at any level -> not a sibling anywhere.
    cells = [(0, 20.0, 280.0, "Region"), (1, 20.0, 80.0, "A")]
    sibs = sibling_columns(cells, B)
    assert not any(col == 3 for (col, _lvl) in sibs)
