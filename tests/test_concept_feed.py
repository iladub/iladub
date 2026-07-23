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
