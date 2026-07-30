"""Loop K — the illustrative shipping-stem contract: the real document's vocabulary,
verified by the SHIPPED ground_concept (zero new grounding logic). Scheme membership
(commodity, port), sh:in (status), sh:pattern (total, month) ground; everything else —
vessels, 'TBA', the literal 'Blank' — quarantines honestly (§7). All offline: property
local names match the normalized header texts, so the exact-match path decides and the
proposer only ever abstains."""
import pytest

from rdflib import Graph, Namespace, RDF, URIRef

from iladub.ground import SurfaceConcept, ground_concept, load_contract
from iladub.propose_ground import GroundingProposal, FakeGroundingProposer

ILADUB = Namespace("https://w3id.org/iladub#")
SHIP = Namespace("https://example.org/shipping#")
C = "examples/shipping/stem-contract.ttl"
TERMS = "examples/shipping/stem-terms.ttl"
SHAPES = "examples/shipping/stem-shapes.ttl"

# The shipped grounding tests build an always-abstain FakeGroundingProposer inline (see
# tests/test_grounding.py::_noop_proposer) — it is a local helper, not a module-level
# constant, so we mirror the same GroundingProposal(field_iri=None, ...) construction here
# rather than importing it. field_iri=None means the proposer never identifies a field, so
# any concept that isn't an exact contract-field match falls straight to quarantine.
ABSTAIN = FakeGroundingProposer(
    GroundingProposal(None, str(SHIP) + "x", 0.1, "n/a", "urn:iladub:suggester/fake"))


def _ground(field_text, value):
    contract = load_contract(C)
    terms = Graph().parse(TERMS, format="turtle")
    shapes = Graph().parse(SHAPES, format="turtle")
    g = Graph()
    verdict = ground_concept(SurfaceConcept(field_text, value, "p0-x-y"), contract,
                             URIRef("urn:slot#s1"), ABSTAIN, terms, shapes, g)
    return verdict, g


def test_contract_loads_five_fields_two_schemes():
    c = load_contract(C)
    assert len(c.fields) == 5
    assert sum(1 for f in c.fields if f.scheme) == 2           # commodity, port


@pytest.mark.parametrize("field,value", [
    ("Commodity", "Sorghum"), ("Port", "Mackay"),
    ("Status", "Accepted"), ("Total", "25,000"), ("Month", "Aug 26")])
def test_verifiable_values_ground(field, value):
    verdict, g = _ground(field, value)
    # ground_concept's actual verdict strings (see src/iladub/ground.py:154/157/165):
    # "grounded" on admission, "proposed" on quarantine. Confirmed by reading the source —
    # not guessed.
    assert verdict == "grounded", (field, value, verdict)
    assert (None, RDF.type, ILADUB.PromotionDecision) in g     # accountable admission


@pytest.mark.parametrize("field,value", [
    ("Commodity", "Vibranium"), ("Status", "Perhaps"),
    ("Total", "TBA"), ("Total", "Blank"), ("Month", "sometime"),
    ("Name Of Ship", "STAR EXPRESS")])                          # no contract field at all
def test_unverifiable_values_quarantine(field, value):
    verdict, g = _ground(field, value)
    assert verdict != "grounded", (field, value, verdict)
    assert (None, RDF.type, ILADUB.CandidateConcept) in g      # never dropped, never faked


def test_e2e_fixture_records_ground_offline(tmp_path):
    import os
    pytest.importorskip("pdfplumber")
    pytest.importorskip("reportlab")
    from iladub.etkl.compile import compile_tables
    from iladub.feed import ground_document
    from tests.etkl import fixtures as F
    p = os.path.join(str(tmp_path), "sub.pdf")
    F.subtotal_hier_table_pdf(p)
    rep = compile_tables(p)
    contract = load_contract(C)
    terms = Graph().parse(TERMS, format="turtle")
    shapes = Graph().parse(SHAPES, format="turtle")
    g = Graph()
    res = ground_document(rep.graph, contract, ABSTAIN, terms, shapes, g)
    assert res.records == 3                                     # the subtotal mints none
    # MEASURED (not guessed — see tests/table_records(rep.graph) walked by hand): the
    # fixture's 5 columns are Mon/Port/Ship/Qty/Berth. Only 'Port' normalizes onto a
    # contract property local name exactly ('port' == 'port'); 'Mon' != 'month',
    # 'Ship'/'Qty'/'Berth' have no contract field at all and sit under the 'Voyage' merged
    # header, so their concept text is the header PATH ('Voyage > Ship' etc.), which
    # doesn't normalize onto any field either. So exact_field matches ONLY the Port column,
    # present in all 3 records; its values ('Mackay', 'Mackay', 'Gladstone') are all
    # skos:prefLabels in scheme-port -> 3 grounded.
    #   Concept COUNT is 14, not 5x3=15: the fixture's suppressed-key row-group ("Mackay",
    # covering rows r0+r1) is keyed on the Port STUB column, which is already non-blank in
    # both rows, so no group-key injection fires for it. The blank Mon cell in the second
    # Mackay row (author wrote 'Jul' once per group, on Mon — not the row-group's own
    # label column) is simply dropped (feed.table_records: is_blank) with nothing to
    # recover it, so that record has 4 concepts (Port/Ship/Qty/Berth), not 5. Every
    # non-Port column (13 concepts total: 5 + 4 + 5, minus the 3 Port cells) falls to the
    # always-abstaining ABSTAIN proposer -> field_iri=None -> quarantined.
    assert res.grounded == 3
    assert res.proposed == 11
    assert (None, RDF.type, ILADUB.PromotionDecision) in g
