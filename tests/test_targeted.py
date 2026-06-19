import os
import pytest
from rdflib import Graph, Namespace, Literal
from baml_client import sync_client
from baml_client.types import RecipientContext, CodedConcept
from iladub.timeline import Timeline, Cursor
from iladub.loop import advance_with_capture
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


def test_targeted_capture_advances_m5_to_m6(monkeypatch):
    # The non-targeted agents must NOT be called — make them explode if they are.
    def _boom(doc):
        raise AssertionError("a non-targeted extractor was called")
    for name in ("ExtractDonorClinical", "ExtractImmunology", "ExtractLogistics"):
        monkeypatch.setattr(sync_client.b, name, _boom, raising=True)
    monkeypatch.setattr(sync_client.b, "ExtractRecipientContext",
        lambda doc: RecipientContext(
            recipientReady=CodedConcept(value="READY", source_quote="readiness: READY", confidence=0.9)),
        raising=True)

    g = _heart_graph()
    tl = Timeline.from_graph(g)
    ctx = Graph()
    ctx.add((TX["offer"], TX.organ, Literal("Heart")))      # M4 already satisfied
    ctx.add((TX["offer"], TX.aboGroup, Literal("O")))
    cursor = Cursor(tl)
    assert cursor.advance(ctx, TX["offer"]) is True          # M4 -> M5
    assert cursor.current.order == 5

    step = advance_with_capture(
        tl, cursor, ctx,
        lambda: capture_for_milestone(cursor.current, g, "recipient text", _terms(), TX["offer"]),
        TX["offer"])
    assert step.advanced is True
    assert cursor.current.order == 6
    assert (TX["offer"], TX.recipientReady, Literal("READY")) in ctx


@pytest.mark.skipif(os.environ.get("BAML_LIVE") != "1",
                    reason="set BAML_LIVE=1 to call the real API")
def test_targeted_capture_live():
    g = _heart_graph()
    tl = Timeline.from_graph(g)
    m5 = next(m for m in tl.ordered() if m.order == 5)
    doc = open(os.path.join(TXD, "recipient-status.txt"), encoding="utf-8").read()
    captured = capture_for_milestone(m5, g, doc, _terms(), TX["offer"])
    assert (TX["offer"], TX.recipientReady, None) in captured
