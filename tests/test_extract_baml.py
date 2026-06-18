from baml_client import sync_client
from baml_client.types import DonorClinical, Immunology, Logistics, CodedConcept
from iladub.extract_baml import extract_offer


def _patch(monkeypatch):
    cc = lambda v, q, c=0.9: CodedConcept(value=v, source_quote=q, confidence=c)
    monkeypatch.setattr(sync_client.b, "ExtractDonorClinical",
        lambda doc: DonorClinical(organ=cc("Heart", "Organ offered: HEART"),
                                  ejectionFraction=cc("60", "LVEF 60%"),
                                  causeOfDeath=cc("anoxic brain injury", "anoxic brain injury"),
                                  sizeMetric=cc("78 kg", "Donor size: 78 kg")), raising=True)
    monkeypatch.setattr(sync_client.b, "ExtractImmunology",
        lambda doc: Immunology(aboGroup=cc("O", "Blood group: O"),
                               hlaTyping=cc("A2, B7, DR15", "HLA: A2, B7, DR15"),
                               serology=cc("HIV negative", "HIV negative")), raising=True)
    monkeypatch.setattr(sync_client.b, "ExtractLogistics",
        lambda doc: Logistics(projectedTransportMinutes=cc("95", "estimated transport 95 minutes")),
        raising=True)


def test_extract_offer_merges_three_agents(monkeypatch):
    _patch(monkeypatch)
    result = extract_offer("ignored — agents are mocked")
    assert result.organ.value == "Heart"
    assert result.abo_group.value == "O"
    assert result.projected_transport_minutes.value == "95"
    assert result.organ.source_quote == "Organ offered: HEART"
