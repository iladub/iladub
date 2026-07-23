from iladub.ground import SurfaceConcept
from iladub.propose_ground import GroundingProposal, MappingGroundingProposer


def _c(text, value="x"):
    return SurfaceConcept(text, value, "r0")


def test_mapping_proposer_maps_by_header_text():
    prop = GroundingProposal("urn:f-ef", "urn:anchor", 0.9, "ef", "urn:s")
    mp = MappingGroundingProposer({"LVEF": prop})
    assert mp.propose_grounding(_c("LVEF"), ()) is prop


def test_mapping_proposer_unmapped_header_yields_none_field():
    mp = MappingGroundingProposer({})
    out = mp.propose_grounding(_c("Whatever"), ())
    assert out.field_iri is None


# Bridge tests: feed.table_records
import os
import tempfile

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")
from iladub.etkl import compile_tables
from iladub.feed import Record, table_records
from tests.etkl import fixtures as F


def _compiled_offer_graph():
    p = os.path.join(tempfile.mkdtemp(), "offer.pdf")
    F.offer_table_pdf(p)
    return compile_tables(p).graph


def test_table_records_two_records_correct_cells():
    recs = table_records(_compiled_offer_graph())
    assert len(recs) == 2
    by_header = [{c.text: c.value for c in r.concepts} for r in recs]
    # order is row-stable; row1 = Heart, row2 = Liver
    assert by_header[0] == {"Organ": "Heart", "LVEF": "60", "ABO": "O", "COD": "MVA"}
    assert by_header[1] == {"Organ": "Liver", "LVEF": "55", "ABO": "A", "COD": "CVA"}
    assert all(isinstance(r, Record) and len(r.concepts) == 4 for r in recs)


def test_table_records_carry_distinct_provenance():
    recs = table_records(_compiled_offer_graph())
    regions = [c.region for r in recs for c in r.concepts]
    assert all(regions) and len(set(regions)) == len(regions)  # non-empty and distinct per cell


def _hand_authored_table_graph():
    """Two columns x twelve rows, RDF authored directly (no PDF). Row URIs are minted
    …-r1 .. …-r12 (lexicographically wrong past r1: r1,r10,r11,r12,r2,...) but bbox y0
    increases monotonically with the intended row order; column x0 orders c1 < c2 within
    a row. Pins the bbox-geometry sort — must FAIL if table_records ever regresses to
    sorting by str(URIRef) again."""
    from rdflib import BNode, Graph, Literal, RDF, URIRef
    from rdflib.namespace import XSD

    from iladub.feed import TAB

    g = Graph()
    base = "https://w3id.org/iladub/example#t1"
    t = URIRef(base)
    g.add((t, RDF.type, TAB.RecordTable))

    col_uris = {1: URIRef(f"{base}-c1"), 2: URIRef(f"{base}-c2")}

    # Header: c1 -> "A", c2 -> "B".
    for idx, col in col_uris.items():
        h = URIRef(f"{base}-h{idx}")
        lc = BNode()
        g.add((lc, TAB.cellText, Literal("A" if idx == 1 else "B")))
        g.add((h, TAB.hasLabel, lc))
        g.add((h, TAB.coversColumn, col))
        g.add((t, TAB.hasHeaderNode, h))

    def bbox(x0: float, y0: float) -> BNode:
        n = BNode()
        g.add((n, RDF.type, TAB.BBox))
        g.add((n, TAB.x0, Literal(x0, datatype=XSD.decimal)))
        g.add((n, TAB.y0, Literal(y0, datatype=XSD.decimal)))
        return n

    for i in range(1, 13):
        row = URIRef(f"{base}-r{i}")
        y0 = float(i * 10)  # increases with intended row order 1..12
        for idx, col in col_uris.items():
            x0 = float(idx * 10)  # c1 (x0=10) precedes c2 (x0=20) within a row
            e = URIRef(f"{base}-r{i}-c{idx}")
            g.add((e, RDF.type, TAB.EntryCell))
            g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atColumn, col))
            g.add((e, TAB.atRow, row))
            g.add((e, TAB.cellText, Literal(f"row{i}-col{idx}")))
            g.add((e, TAB.hasBBox, bbox(x0, y0)))
    return g


def test_table_records_orders_by_bbox_not_lexicographic_uri():
    recs = table_records(_hand_authored_table_graph())
    assert len(recs) == 12
    # Rows must come out r1..r12 in bbox y0 order, not lexicographic (r1,r10,r11,r12,r2,...).
    assert [r.row_id for r in recs] == [f"t1-r{i}" for i in range(1, 13)]
    # Within each row, cells must come out in x0 order: col1 ("A") before col2 ("B").
    for i, r in enumerate(recs, start=1):
        assert [c.value for c in r.concepts] == [f"row{i}-col1", f"row{i}-col2"]
        assert [c.text for c in r.concepts] == ["A", "B"]
