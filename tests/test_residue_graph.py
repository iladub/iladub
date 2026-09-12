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
    _rows, status, _label, _parked = residue_graph.read_rows()
    expected = {int(rid[1:]): s for rid, s in index_rows().items()}
    assert status == expected, (
        f"the graph and the integrity test disagree about the index: "
        f"missing {sorted(set(expected) - set(status))}, "
        f"extra {sorted(set(status) - set(expected))}, "
        f"differing {[n for n in status if n in expected and status[n] != expected[n]]}")


def test_the_graph_reports_parked_rows_and_the_structural_candidates():
    """Spec § 3.3: a candidate is open, named by no prog:blockedBy, and has no OPEN neighbour.
    Measured 2026-09-11 with every index row read (task 1): 80 candidates; the spec's 78 was
    counted before R131 and R141 were readable. No row is parked on this tree.
    RE-MEASURED 2026-09-11 (the-negative-half): 80 -> 81 — R209 is open, blocks no criterion
    and links only to the closed R179, so it is a candidate by § 3.3's own rule.
    RE-MEASURED 2026-09-11 (etkl-02-r166-first): 81 -> 82 — R210 is open, blocks no criterion and
    links to no row; R166, now named by etkl:02's prog:blockedBy, was not a candidate before or after.
    RE-MEASURED 2026-09-12 (R201/R203, grid donation): 82 -> 84 — R216 and R217 are open, block no
    criterion, and link only to the now-CLOSED R201/R203 that raised them, so both are candidates by
    § 3.3's own rule, exactly as R209 was against the closed R179. MEASURED that the delta is those
    two and nothing else: 84 candidates total, both present, and 82 excluding them — closing R201
    and R203 changed no other row's candidacy (a closed row was never a candidate, and neither was
    anyone's only open neighbour).
    RE-MEASURED 2026-09-12 (R212, the ignored band's carrier): 84 -> 87 — R218, R219 and R220 are
    open, block no criterion, and each has exactly ONE neighbour, the now-CLOSED R212 (R218 and R219
    were raised by R212's spec; R220 by its carrier, the edge coming from R212's own closure text).
    All three are candidates by § 3.3's own rule, exactly as R216/R217 were against the closed
    R201/R203 and R209 against the closed R179. MEASURED that the delta is those three and nothing
    else, by recomputing `candidates` against the HEAD versions of the three register files and
    against this tree: 84 before, 87 after, ADDED = [218, 219, 220], REMOVED = []."""
    rows, status, _label, parked = residue_graph.read_rows()
    assert parked == set()
    crit = residue_graph.read_criteria()
    front = {r for v in crit.values() for r in v}
    open_ = {n for n, s in status.items() if s == "open"}
    nb = {}
    for a, refs in rows.items():
        for b in refs:
            if b in rows:
                nb.setdefault(a, set()).add(b)
                nb.setdefault(b, set()).add(a)
    expected = sorted(n for n in open_ if n not in front and not (nb.get(n, set()) & open_))
    assert residue_graph.candidates(rows, status, crit) == expected
    assert len(expected) == 87
