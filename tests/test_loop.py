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
