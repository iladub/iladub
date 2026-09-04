"""R165 — the run is one band. The derivation half.

Spec: docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md
Plan: docs/superpowers/plans/2026-09-04-the-run-is-one-band.md
"""
from rdflib import Graph, Namespace

from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Rule, Word

TAB = Namespace("https://w3id.org/iladub/tab#")


def _rule(x, top=0.0, bottom=10.0):
    return Rule(x=x, top=top, bottom=bottom)


def _band(xs, y=0.0):
    """A band whose rules sit at `xs`. Lines are irrelevant to run_evidence and are
    deliberately minimal — the emitter reads geometry, never text."""
    w = Word(text="x", x0=0.0, x1=1.0, top=y, bottom=y + 1.0)
    return Band(lines=(Line(words=(w,), top=y, bottom=y + 1.0),),
                top=y, bottom=y + 1.0,
                rules=tuple(_rule(x) for x in xs))


def test_a_band_with_no_rules_emits_no_node_at_all():
    """THE emitter invariant, and the one thing the .rq cannot defend.

    A node emitted with ZERO tab:bandRuleX facts makes both legs of the subsumption
    vacuously true, so it would join EVERY adjacent band in both directions —
    derived runs [(0,2)] where the relation says [] (three-claims measurement § A.1).
    The protection is entirely the emitter's honest abstain, exactly as
    section_evidence's `continue` already does for its own population."""
    from iladub.etkl.sectiongraph import run_evidence

    g = run_evidence([_band([10.0, 20.0, 30.0]), _band([]), _band([10.0, 20.0])])
    indices = sorted(int(o) for o in g.objects(None, TAB.bandIndex))
    assert indices == [0, 2], "the ruleless band at index 1 must emit nothing"
    assert (None, None, TAB.RuledBand) not in g or len(
        set(g.subjects(None, TAB.RuledBand))) == 2


def test_the_emitter_emits_distinct_rounded_xs_not_one_per_rule():
    """The relation is over the band's SET of distinct rounded x-positions. Two rules
    at the same rounded x are one fact, not two — otherwise the subsumption legs
    compare multisets."""
    from iladub.etkl.sectiongraph import run_evidence

    g = run_evidence([_band([10.001, 10.004, 20.0])])
    xs = sorted(float(o) for o in g.objects(None, TAB.bandRuleX))
    assert xs == [10.0, 20.0]


def test_the_predecessor_index_is_a_fact_and_index_zero_has_none():
    """DECISION C: adjacency is a join on an emitted fact, never arithmetic on a
    numeric literal — so the .rq keeps section-repeat.rq:15's standing property."""
    from iladub.etkl.sectiongraph import run_evidence

    g = run_evidence([_band([10.0]), _band([10.0])])
    prevs = {int(s_i): int(p)
             for s in g.subjects(None, TAB.RuledBand)
             for s_i in [next(g.objects(s, TAB.bandIndex))]
             for p in g.objects(s, TAB.prevBandIndex)}
    assert prevs == {1: 0}, "index 0 has no predecessor fact; index 1 has exactly one"


def test_the_predecessor_fact_is_emitted_even_when_the_predecessor_abstained():
    """DECISION C, second half. Band 1 has no rules and emits nothing; band 2 still
    carries prevBandIndex=1. The join then finds nothing — which is the CORRECT
    behaviour (an unruled band never joins, and it breaks the chain), and it must be
    the emitter that is simple, not the query."""
    from iladub.etkl.sectiongraph import run_evidence

    g = run_evidence([_band([10.0]), _band([]), _band([10.0])])
    node = next(s for s in g.subjects(None, TAB.RuledBand)
                if int(next(g.objects(s, TAB.bandIndex))) == 2)
    assert int(next(g.objects(node, TAB.prevBandIndex))) == 1
