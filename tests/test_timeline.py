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


from iladub.timeline import Cursor, next_capture_plan


def test_cursor_advances_when_current_ready():
    tl = Timeline.from_graph(_heart_graph())
    cur = Cursor(tl)                       # starts at M4
    assert cur.current.order == 4
    moved = cur.advance(_context(TX.organ, TX.aboGroup), TX["offer"])
    assert moved is True
    assert cur.current.order == 5


def test_cursor_blocks_when_current_not_ready():
    tl = Timeline.from_graph(_heart_graph())
    cur = Cursor(tl)
    moved = cur.advance(_context(TX.organ), TX["offer"])   # abo missing
    assert moved is False
    assert cur.current.order == 4


def test_forward_pass_lists_next_milestone_needs():
    tl = Timeline.from_graph(_heart_graph())
    m4 = next(m for m in tl.ordered() if m.order == 4)
    plan = next_capture_plan(tl, m4, _context(TX.organ, TX.aboGroup), TX["offer"])
    assert plan.milestone_id == next(m.id for m in tl.ordered() if m.order == 5)
    assert TX.recipientReady in plan.needed


from iladub.allen import Interval
from iladub.timeline import feasibility


def test_feasibility_for_clock_milestone_heart():
    tl = Timeline.from_graph(_heart_graph())
    m6 = next(m for m in tl.ordered() if m.order == 6)   # windowLimit 240
    f = feasibility(m6, cross_clamp_minute=0, transport=Interval(0, 95))
    assert f.feasible is True
    assert f.slack_minutes == 145
    assert f.relation in {"starts", "during", "overlaps", "finishes", "equals"}


def test_feasibility_infeasible_when_window_exceeded():
    tl = Timeline.from_graph(_heart_graph())
    m6 = next(m for m in tl.ordered() if m.order == 6)
    f = feasibility(m6, cross_clamp_minute=0, transport=Interval(0, 270))
    assert f.feasible is False
    assert f.slack_minutes == -30


def _kidney_graph():
    return Graph().parse(os.path.join(TXD, "kidney-timeline.ttl"), format="turtle")


def test_same_engine_drives_two_distinct_chains():
    heart = Timeline.from_graph(_heart_graph())
    kidney = Timeline.from_graph(_kidney_graph())
    assert [m.order for m in heart.ordered()] == [4, 5, 6, 7, 8]
    assert [m.order for m in kidney.ordered()] == [1, 2, 3, 4]
    heart_clock = next(m for m in heart.ordered() if m.window_limit_minutes)
    kidney_clock = next(m for m in kidney.ordered() if m.window_limit_minutes)
    assert heart_clock.window_limit_minutes == 240
    assert kidney_clock.window_limit_minutes == 1800
    assert feasibility(kidney_clock, 0, Interval(0, 600)).feasible is True
    assert feasibility(heart_clock, 0, Interval(0, 600)).feasible is False
