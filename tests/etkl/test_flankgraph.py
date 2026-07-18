from rdflib import Namespace, RDF, Literal
from rdflib.namespace import XSD

from iladub.etkl.flankgraph import flank_evidence

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
