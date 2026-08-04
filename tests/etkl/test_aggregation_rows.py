"""Loop H — arithmetic subtotal detection (residue R4, detection half).

A SPARSE row (2 cells vs the modal shape) whose numeric measure equals the token-sum of the
non-aggregation rows above it — back to the previous confirmed aggregation of same-or-outer level
(the label's COLUMN encodes the level) — is an aggregation row, not a data record.

LANGUAGE-INDEPENDENT BY CONSTRUCTION: the label text is never read. A ' Total' suffix test is the
tuned constant of natural language and is expressly forbidden (spec §5).
See docs/superpowers/specs/2026-07-30-subtotal-rows-design.md §2 Findings 4-5.
"""
from iladub.etkl.geometry import Word
from iladub.etkl.grid import LeafGrid
from iladub.etkl.rows import (RowBand, detect_aggregation_rows, is_aggregation_shaped,
                              row_column_count)

GRID = LeafGrid((0.0, 50.0, 100.0, 150.0, 200.0), 4, 50.0, 1.0)
COLS = {0: (5, 45), 1: (55, 95), 2: (105, 145), 3: (155, 195)}


def _row(top, cells):
    """cells: dict of col->text. Builds a RowBand with one cell per named column."""
    out = []
    for col, text in sorted(cells.items()):
        x0, x1 = COLS[col]
        w = Word(text, x0, x1, top, top + 8.0)
        from iladub.etkl.cells import _cell_from
        out.append(_cell_from([w], 0))
    return RowBand(top, top + 8.0, tuple(out))


def _rows(*specs):
    return tuple(_row(10.0 * i, spec) for i, spec in enumerate(specs))


def test_single_level_group_confirms():
    rows = _rows({0: "Jul", 1: "Mackay", 2: "V1", 3: "100"},
                 {1: "Mackay", 2: "V2", 3: "150"},
                 {1: "SUB", 3: "250"})
    agg = detect_aggregation_rows(rows, GRID)
    assert agg == {2: (1, 3, (0, 1))}


def test_label_text_is_never_read():
    # Same structure, label in another language entirely — identical result.
    rows = _rows({0: "Jul", 1: "Mackay", 2: "V1", 3: "100"},
                 {1: "Mackay", 2: "V2", 3: "150"},
                 {1: "Zwischensumme", 3: "250"})
    assert detect_aggregation_rows(rows, GRID) == {2: (1, 3, (0, 1))}


def test_two_level_nesting_by_label_column():
    # Port totals label in c1; the month total labels in c0 (outer level) and sums the DATA
    # rows, with the inner aggregations excluded as members.
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "SUB", 3: "100"},
                 {1: "B", 2: "V2", 3: "200"},
                 {1: "SUB", 3: "200"},
                 {0: "TOT", 3: "300"})
    agg = detect_aggregation_rows(rows, GRID)
    assert agg[1] == (1, 3, (0,))
    assert agg[3] == (1, 3, (2,))
    assert agg[4] == (0, 3, (0, 2))          # data rows only; inner aggs excluded


def test_inner_group_boundary_is_the_previous_same_level_agg():
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "SUB", 3: "100"},
                 {1: "B", 2: "V2", 3: "200"},
                 {1: "SUB", 3: "200"})
    agg = detect_aggregation_rows(rows, GRID)
    assert agg[3] == (1, 3, (2,))            # stops at row 1 (same level), members = row 2 only


def test_blank_member_contributes_nothing():
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "A", 2: "V2", 3: "-"},
                 {1: "SUB", 3: "100"})
    assert detect_aggregation_rows(rows, GRID)[2] == (1, 3, (0, 1))


def test_blank_total_is_never_confirmed():
    # The Port Kembla honesty: a candidate with no numeric measure cannot be verified.
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "-"},
                 {1: "SUB", 3: "-"})
    assert detect_aggregation_rows(rows, GRID) == {}


def test_non_reconciling_sparse_row_is_not_confirmed():
    # A lookup/reference row that happens to be sparse is NOT a subtotal.
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "NOTE", 3: "999"})
    assert detect_aggregation_rows(rows, GRID) == {}


def test_multi_value_cell_sums_its_tokens():
    # The author may box two lines together (no hrule drawn between them — measured on the
    # real report: two TBA bookings in one box, measure cell '20,000 30,000'). The cell's
    # contribution is the sum of its numeric tokens.
    rows = _rows({0: "Jul", 1: "A", 2: "V1 V2", 3: "100 150"},
                 {1: "SUB", 3: "250"})
    assert detect_aggregation_rows(rows, GRID)[1] == (1, 3, (0,))


def test_unconfirmed_sparse_row_is_a_member_of_later_sums():
    # The cascade: a blank-total row stays a row AND contributes its token-sum (0) to the
    # enclosing group — measured on the real report (Portland Total reconciles past the
    # blank Fisherman total above it).
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "BLANKSUB", 3: "-"},
                 {1: "B", 2: "V2", 3: "200"},
                 {0: "TOT", 3: "300"})
    agg = detect_aggregation_rows(rows, GRID)
    assert 1 not in agg
    assert agg[3] == (0, 3, (0, 1, 2))


def _hier_region_with_subtotal():
    """A minimal HierRegion whose rows contain one confirmable subtotal (the Task 2 shape)."""
    from iladub.etkl.headers import HeaderNode
    from iladub.etkl.hierarchical import HierRegion
    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Line

    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "A", 2: "V2", 3: "150"},
                 {1: "SUB", 3: "250"})
    hdr_words = [Word("K", 5, 45, -10.0, -2.0), Word("Port", 55, 95, -10.0, -2.0),
                 Word("Ship", 105, 145, -10.0, -2.0), Word("Qty", 155, 195, -10.0, -2.0)]
    lines = [Line(tuple(hdr_words), -10.0, -2.0)]
    for rb in rows:
        ws = tuple(w for c in rb.cells for w in c.words)
        lines.append(Line(ws, rb.top, rb.bottom))
    band = Band(tuple(lines), -10.0, 40.0)
    tree = tuple(HeaderNode(0, (i,), t, None, (COLS[i][0] + COLS[i][1]) / 2.0)
                 for i, t in enumerate(["K", "Port", "Ship", "Qty"]))
    return HierRegion(GRID, tree, rows, 1), band


def test_confirmed_rows_are_typed_with_operands():
    from rdflib import Graph, Namespace, RDF, URIRef
    from iladub.etkl.holon import assert_hier_region
    TAB = Namespace("https://w3id.org/iladub/tab#")
    hreg, band = _hier_region_with_subtotal()
    g = Graph()
    t = URIRef("urn:doc#h0")
    n = assert_hier_region(g, hreg, band, t, URIRef("urn:doc"), 0)
    assert n > 0
    agg_rows = list(g.subjects(RDF.type, TAB.DetectedAggregationRow))
    assert len(agg_rows) == 1
    row = agg_rows[0]
    assert (row, RDF.type, TAB.AggregationRow) in g          # supertype written explicitly
    ops = list(g.objects(row, TAB.aggregates))
    assert len(ops) == 2                                      # both member rows
    funcs = [str(o) for o in g.objects(row, TAB.aggregationFunction)]
    assert funcs == ["sum"]


def test_membrane_refuses_an_unexplained_detected_aggregation():
    from rdflib import Graph, Literal, Namespace, RDF, URIRef
    from iladub.etkl.tiling import region_tiles
    TAB = Namespace("https://w3id.org/iladub/tab#")
    g = Graph()
    r = URIRef("urn:doc#h0-r2")
    g.add((r, RDF.type, TAB.DetectedAggregationRow))          # typed, no operands, no function
    assert region_tiles(g) is False


def test_denormalization_bare_aggregation_rows_still_pass():
    # THE PROBED LANDMINE: denormalization.py types rows bare tab:AggregationRow with no
    # row-level operands. The new shape must NOT fire on the supertype.
    from rdflib import Graph, Namespace, RDF, URIRef
    from iladub.etkl.tiling import region_tiles
    TAB = Namespace("https://w3id.org/iladub/tab#")
    g = Graph()
    g.add((URIRef("urn:doc#agg-r1"), RDF.type, TAB.AggregationRow))
    assert region_tiles(g) is True


def test_feed_skips_aggregation_rows(tmp_path):
    import os
    import pytest
    pytest.importorskip("pdfplumber")
    pytest.importorskip("reportlab")
    from rdflib import Namespace, RDF
    from iladub.etkl.compile import compile_tables
    from iladub.feed import table_records
    from tests.etkl import fixtures as F
    TAB = Namespace("https://w3id.org/iladub/tab#")
    p = os.path.join(str(tmp_path), "sub.pdf")
    F.subtotal_hier_table_pdf(p)
    rep = compile_tables(p)
    assert any(r.verdict == "asserted" for r in rep.regions), [r.reason for r in rep.regions]
    # E2E typing pinned (Task 3 review, Minor 2): exactly ONE detected aggregation row,
    # aggregating exactly the two group members r0/r1.
    det = list(rep.graph.subjects(RDF.type, TAB.DetectedAggregationRow))
    assert len(det) == 1, det
    mems = sorted(str(m).rsplit("-", 1)[-1] for m in rep.graph.objects(det[0], TAB.aggregates))
    assert mems == ["r0", "r1"], mems
    recs = table_records(rep.graph)
    joined = [" ".join(sc.value for sc in r.concepts) for r in recs]
    # the subtotal is no record — and the three DATA rows all still are (not vacuous)
    assert len(recs) == 3, joined
    assert not any("250" in j and "SUB" in j for j in joined), joined


def test_without_hrules_the_subtotal_row_fuses(tmp_path):
    """The hrules in subtotal_hier_table_pdf are LOAD-BEARING (Task 3 review, Important 1):
    the SUB row sits at the absorbable 12pt pitch (< lead 16), so stripping the author's
    hrules re-opens the Task 1 fusion defect — SUB fuses into the record above and nothing
    is detectable. This pins that the E2E genuinely integrates de-fusion with detection."""
    import os
    import pytest
    pytest.importorskip("pdfplumber")
    pytest.importorskip("reportlab")
    from rdflib import Namespace, RDF
    from iladub.etkl.compile import compile_tables
    from tests.etkl import fixtures as F
    TAB = Namespace("https://w3id.org/iladub/tab#")
    p = os.path.join(str(tmp_path), "nosub.pdf")
    F.subtotal_hier_table_pdf(p, hrules=False)
    rep = compile_tables(p)
    texts = {str(o) for o in rep.graph.objects(None, TAB.cellText)}
    assert "Mackay SUB" in texts and "150 250" in texts, sorted(texts)   # the fusion
    assert not list(rep.graph.subjects(RDF.type, TAB.DetectedAggregationRow))


def test_a_label_containing_digits_is_still_a_label():
    """THE COLLAPSE CAUGHT AT TASK-4 VERIFICATION, pinned. 'Jul 26 Total' contains the numeric
    token '26'; lenient (any-numeric-token) classification read it as a SECOND measure, so month
    totals stopped being candidates — and every unconfirmed month total then polluted the member
    sums of everything after it. Measured on the real document: detection collapsed from 17 rows
    to 4 (only the pre-month port totals). Candidate classification must be STRICT (a measure
    cell = every token numeric); member contributions stay lenient (token-sum)."""
    rows = _rows({0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "A", 2: "V2", 3: "150"},
                 {1: "SUB", 3: "250"},
                 {0: "Jul 26 Total", 3: "250"},
                 {0: "Aug", 1: "B", 2: "V3", 3: "300"},
                 {1: "SUB", 3: "300"})
    agg = detect_aggregation_rows(rows, GRID)
    assert agg[3] == (0, 3, (0, 1)), agg      # the digit-bearing month total confirms
    assert agg[5] == (1, 3, (4,)), agg        # and the NEXT group is not polluted by it


def test_feed_skips_denormalization_typed_aggregation_rows():
    """The feed exclusion keys on the SUPERTYPE, so it also covers rows that
    denormalization.annotate_aggregations types bare tab:AggregationRow (no operands,
    no Detected subtype). Intended widening, pinned (Task 3 review, Minor 5): a subtotal
    is not a record on ANY path."""
    from rdflib import Graph, Literal, Namespace, RDF, URIRef
    from iladub.feed import table_records
    TAB = Namespace("https://w3id.org/iladub/tab#")
    g = Graph()
    t = URIRef("urn:doc#t0")
    g.add((t, RDF.type, TAB.RecordTable))
    for i, (txt, agg) in enumerate((("10", False), ("10", True))):
        row = URIRef(f"urn:doc#t0-r{i}")
        if agg:
            g.add((row, RDF.type, TAB.AggregationRow))       # bare supertype, as denorm emits
        e = URIRef(f"urn:doc#t0-r{i}-c0")
        g.add((e, RDF.type, TAB.EntryCell))
        g.add((t, TAB.hasCell, e))
        g.add((e, TAB.atRow, row))
        g.add((e, TAB.cellText, Literal(txt)))
    recs = table_records(g)
    assert len(recs) == 1 and "r0" in recs[0].row_id, recs


def test_a_row_with_no_measure_cell_is_not_an_operand():
    """Final-review M-2: a row with NO cell in the measure column (a section-title line)
    contributes nothing to the sum, so it must not be emitted as a tab:aggregates operand
    either — §7, only emit what the source supports. (Distinct from a blank '-' measure
    CELL, which exists in the source and correctly stays a member.)"""
    rows = _rows({0: "SECTION"},
                 {0: "Jul", 1: "A", 2: "V1", 3: "100"},
                 {1: "A", 2: "V2", 3: "150"},
                 {1: "SUB", 3: "250"})
    agg = detect_aggregation_rows(rows, GRID)
    assert agg == {3: (1, 3, (1, 2))}, agg   # row 0 is not among the operands


def test_two_cells_in_one_column_is_not_aggregation_shaped():
    """Final-review F2: `is_aggregation_shaped` (and `row_column_count`, the counting rule it
    shares with `document._confirm_section_total`) counts DISTINCT OCCUPIED COLUMNS, cells
    bucketed by `column_of` — not raw `len(row.cells)`. A row with two cells split WITHIN the
    same column (e.g. a wrapped/split label with no interior rule) has raw cell count 2 — the
    number the pre-fix `_confirm_section_total` inline check compared against 2 — but only ONE
    distinct column is occupied, so it is NOT aggregation-shaped. This is the divergent case
    the two counting rules disagreed on before they were factored into one function."""
    from iladub.etkl.geometry import Word
    from iladub.etkl.cells import _cell_from
    w1 = Word("SUB", 55, 70, 10.0, 18.0)
    w2 = Word("TOTAL", 75, 95, 10.0, 18.0)
    c1 = _cell_from([w1], 0)
    c2 = _cell_from([w2], 0)
    row = RowBand(10.0, 18.0, (c1, c2))
    assert len(row.cells) == 2                          # raw cell count — the OLD, wrong signal
    assert row_column_count(row, GRID) == 1              # both cells land in column 1
    assert not is_aggregation_shaped(row, 4, GRID)        # correctly refused: only 1 column
