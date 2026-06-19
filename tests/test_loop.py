import os
from rdflib import Graph, Namespace, Literal
from iladub.timeline import Timeline, Cursor
from iladub.loop import advance_with_capture

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")
TX = Namespace("https://example.org/transplant#")


def _heart():
    return Timeline.from_graph(Graph().parse(os.path.join(TXD, "heart-timeline.ttl"), format="turtle"))


def _captures(*props):
    def fn():
        g = Graph()
        for p in props:
            g.add((TX["offer"], p, Literal("x")))
        return g
    return fn


def test_capture_readies_current_and_advances():
    tl = _heart()
    cursor = Cursor(tl)
    ctx = Graph()
    step = advance_with_capture(tl, cursor, ctx, _captures(TX.organ, TX.aboGroup), TX["offer"])
    assert step.readiness_before.ready is False
    assert step.readiness_after.ready is True
    assert step.advanced is True
    assert cursor.current.order == 5
    assert step.next_plan is not None
    assert TX.recipientReady in step.next_plan.needed


def test_no_advance_when_capture_insufficient():
    tl = _heart()
    cursor = Cursor(tl)
    ctx = Graph()
    step = advance_with_capture(tl, cursor, ctx, _captures(TX.organ), TX["offer"])
    assert step.advanced is False
    assert cursor.current.order == 4
    assert TX.aboGroup in step.still_missing


from baml_client import sync_client
from baml_client.types import DonorClinical, Immunology, Logistics, CodedConcept
from iladub.m4 import capture_context

OFFER = os.path.join(TXD, "offer.txt")


def _patch_agents(monkeypatch):
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


def test_capture_context_grounds_organ_and_abo(monkeypatch):
    _patch_agents(monkeypatch)
    g = capture_context(OFFER)
    assert (TX["offer"], TX.organ, Literal("Heart")) in g
    assert (TX["offer"], TX.aboGroup, Literal("O")) in g
