"""R165 — the run is one band. The derivation half.

Spec: docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md
Plan: docs/superpowers/plans/2026-09-04-the-run-is-one-band.md
"""
import dataclasses
import os

import pytest
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


# --- Task 2: the derivation query and the run assembly ---

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
APPLE = os.path.join(CORPUS, "financial", "apple-fy2026q3-statements.pdf")
STEM = os.path.join(CORPUS, "ag-trade", "graincorp-stem-2026-07-31.pdf")
corpus_only = pytest.mark.skipif(not os.path.exists(APPLE), reason="corpus not fetched")


@corpus_only
def test_the_relation_is_subsumption_not_equality_apple_p1():
    """O1, first half. Under set EQUALITY apple p1 stops at (2,3) — 26 entries, not the
    56 measured. Under adjacent subsumption its six ruled bands are ONE run 2..7.
    (spec § 1.2 refutation 1, § 3.3 Q1/Q2.)"""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.sectiongraph import merge_run_candidates

    bands = page_bands(APPLE, 1)
    assert merge_run_candidates(bands) == ((2, 7),)


@corpus_only
def test_the_relation_joins_the_dangerous_case_too_graincorp_stem_p0():
    """O1, SECOND half, and it is the half that matters: a test that only pinned apple
    would pass for a relation that special-cases it.

    graincorp-stem p0 band 1 is a TITLE band ('SHIPPING STEM', 5 rule x's) whose set is a
    strict subset of the table's 20. The relation JOINS them — 586 asserted cells are
    inside that proposed run — and only the oracle keeps them (spec § 3.3, R171)."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.sectiongraph import merge_run_candidates

    bands = page_bands(STEM, 0)
    assert (1, 2) in merge_run_candidates(bands)


@corpus_only
def test_runs_are_disjoint_and_ascending_across_the_whole_corpus():
    """DECISION D: maximal contiguous chains over adjacency on a linear index are
    disjoint BY CONSTRUCTION, which is why § 3.2's 'longest run first, then leftmost'
    tie-break is not implemented. This is the pin that makes that argument checkable
    rather than asserted."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.sectiongraph import merge_run_candidates

    for pdf, page in [(APPLE, 0), (APPLE, 1), (APPLE, 2), (STEM, 0)]:
        runs = merge_run_candidates(page_bands(pdf, page))
        assert list(runs) == sorted(runs), (pdf, page)
        seen = set()
        for first, last in runs:
            assert last > first, (pdf, page, first, last)
            span = set(range(first, last + 1))
            assert not (span & seen), f"overlapping runs on {pdf} p{page}: {runs}"
            seen |= span


# --- Task 3: merge_bands, promoted from the spike ---


def test_merge_bands_covers_every_field_of_band():
    """A ninth Band field would be SILENTLY DEFAULTED by merge_bands, and nothing else
    in the suite would notice. Band has 8 fields (bands.py:16-34). If this fails, a
    field was added: decide how the merge carries it, then move this number."""
    from iladub.etkl.bands import Band

    assert len(dataclasses.fields(Band)) == 8, [f.name for f in dataclasses.fields(Band)]


def test_column_xs_comes_from_the_first_carrier_and_is_never_unioned():
    """The contract's load-bearing clause. column_xs is a BOUNDARY VECTOR: unioning two
    vectors invents boundaries no band derived."""
    from iladub.etkl.compile import merge_bands

    a = dataclasses.replace(_band([10.0]), column_xs=())
    b = dataclasses.replace(_band([10.0], y=20.0), column_xs=(1.0, 2.0))
    c = dataclasses.replace(_band([10.0], y=40.0), column_xs=(7.0, 8.0))
    merged = merge_bands([a, b, c], 0, 2)
    assert merged.column_xs == (1.0, 2.0), "first CARRIER, not first band, and not a union"


def test_merge_bands_takes_the_runs_extent_and_concatenates_the_rest():
    from iladub.etkl.compile import merge_bands

    a, b = _band([10.0], y=0.0), _band([20.0], y=20.0)
    merged = merge_bands([a, b], 0, 1)
    assert merged.top == min(a.top, b.top) and merged.bottom == max(a.bottom, b.bottom)
    assert merged.lines == a.lines + b.lines
    assert len(merged.rules) == len(a.rules) + len(b.rules)
