"""`scripts/residue_graph.py` — the register as a graph. It must read every index row the
integrity test reads, or the graph it draws is missing the rows it cannot parse.

Measured 2026-09-11 before this test existed: the script's index regex required the status word
to be followed directly by ` | `, so the two rows whose status carries a parenthetical qualifier
(`R131 | open (half (a) done)`, `R141 | open (code landed)`) were absent from its `status` dict —
196 rows read where the index has 198. A parked qualifier (spec 2026-09-11 § 3.3) would drop every
parked row from the very graph that decides whether a row may be parked.
"""
from scripts import residue_graph
from tests.test_residue_register_integrity import index_rows


def test_the_graph_reads_every_index_row_the_integrity_test_reads():
    _rows, status, _label = residue_graph.read_rows()
    expected = {int(rid[1:]): s for rid, s in index_rows().items()}
    assert status == expected, (
        f"the graph and the integrity test disagree about the index: "
        f"missing {sorted(set(expected) - set(status))}, "
        f"extra {sorted(set(status) - set(expected))}, "
        f"differing {[n for n in status if n in expected and status[n] != expected[n]]}")
