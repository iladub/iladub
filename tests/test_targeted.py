import os
from rdflib import Graph, Namespace, Literal
from baml_client import sync_client
from baml_client.types import RecipientContext, CodedConcept
from iladub.timeline import Timeline
from iladub.m4 import capture_for_milestone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")
TX = Namespace("https://example.org/transplant#")


def _heart_graph():
    return Graph().parse(os.path.join(TXD, "heart-timeline.ttl"), format="turtle")


def _terms():
    return Graph().parse(os.path.join(TXD, "transplant-terms.ttl"), format="turtle")


def test_capture_for_milestone_grounds_recipient_ready(monkeypatch):
    monkeypatch.setattr(sync_client.b, "ExtractRecipientContext",
        lambda doc: RecipientContext(
            recipientReady=CodedConcept(value="READY", source_quote="readiness: READY", confidence=0.9)),
        raising=True)
    g = _heart_graph()
    tl = Timeline.from_graph(g)
    m5 = next(m for m in tl.ordered() if m.order == 5)
    captured = capture_for_milestone(m5, g, "ignored text", _terms(), TX["offer"])
    assert (TX["offer"], TX.recipientReady, Literal("READY")) in captured
