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
