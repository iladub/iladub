import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")
HOL = Namespace("https://w3id.org/etkl/hol#")
TX = Namespace("https://example.org/transplant#")


def _heart_graph():
    return Graph().parse(os.path.join(TXD, "heart-timeline.ttl"), format="turtle")


def test_heart_process_has_five_milestones():
    g = _heart_graph()
    ms = list(g.objects(TX["heart-process"], HOL.hasMilestone))
    assert len(ms) == 5


from iladub.timeline import Timeline


def test_timeline_loads_ordered_milestones():
    tl = Timeline.from_graph(_heart_graph())
    orders = [m.order for m in tl.ordered()]
    assert orders == [4, 5, 6, 7, 8]


def test_m6_carries_the_clock_and_window():
    tl = Timeline.from_graph(_heart_graph())
    m6 = next(m for m in tl.ordered() if m.order == 6)
    assert m6.clock_start is True
    assert m6.window_limit_minutes == 240


def test_m4_requires_organ_and_abo():
    tl = Timeline.from_graph(_heart_graph())
    m4 = next(m for m in tl.ordered() if m.order == 4)
    assert set(m4.requires) == {TX.organ, TX.aboGroup}


from iladub.timeline import readiness


def _context(*present_props):
    g = Graph()
    for p in present_props:
        g.add((TX["offer"], p, __import__("rdflib").Literal("x")))
    return g


def test_readiness_reports_missing_required_property():
    tl = Timeline.from_graph(_heart_graph())
    m4 = next(m for m in tl.ordered() if m.order == 4)
    r = readiness(m4, _context(TX.organ), TX["offer"])   # abo missing
    assert TX.aboGroup in r.missing
    assert r.ready is False


def test_readiness_true_when_all_present():
    tl = Timeline.from_graph(_heart_graph())
    m4 = next(m for m in tl.ordered() if m.order == 4)
    r = readiness(m4, _context(TX.organ, TX.aboGroup), TX["offer"])
    assert r.ready is True
    assert r.missing == ()
