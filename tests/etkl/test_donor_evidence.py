"""Grid donation — the evidence half (R201 → R203).

Spec: docs/superpowers/specs/2026-09-10-the-grid-the-author-drew-design.md § 3–4
Plan: docs/superpowers/plans/2026-09-11-grid-donation.md, Task 1
"""
from decimal import Decimal

from rdflib import Literal, Namespace

from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Rule, Word

TAB = Namespace("https://w3id.org/iladub/tab#")
EVERY_MEASURE = "HeterogeneousColumn/every-measure"


def _band(xs, words, y=0.0, column_xs=()):
    """A one-line band ruled at `xs`, its words given as (text, x0, x1). `column_xs`
    is the DERIVED vector `_rule_boundaries` prefers when present (grid.py:73)."""
    ws = tuple(Word(text=t, x0=a, x1=b, top=y, bottom=y + 10.0) for t, a, b in words)
    return Band(lines=(Line(words=ws, top=y, bottom=y + 10.0),), top=y, bottom=y + 10.0,
                rules=tuple(Rule(x=x, top=y, bottom=y + 10.0) for x in xs),
                column_xs=column_xs)


HEAD = (("Region", 80.0, 120.0), ("Total", 210.0, 240.0), ("Share", 340.0, 370.0))
RULED = _band((72.0, 200.0, 330.0, 460.0), HEAD)


def _nodes(g):
    return {int(g.value(u, TAB.bandIndex)): u for u in g.subjects(None, TAB.DonorBand)}


def test_a_band_with_no_vector_emits_no_node_at_all():
    """The honest abstain, for this population: no rules, or a word that straddles
    the band's own rule, means _rule_boundaries returns None and the band is absent —
    never a node with zero boundaries, which the query could not defend against."""
    from iladub.etkl.sectiongraph import donor_evidence

    unruled = _band((), HEAD)
    straddling = _band((72.0, 200.0, 330.0, 460.0),
                       (("Region", 80.0, 120.0), ("Total", 190.0, 240.0), ("Share", 340.0, 370.0)))
    g = donor_evidence([unruled, RULED, straddling], {})
    assert set(_nodes(g)) == {1}


def test_the_vector_and_the_rule_xs_are_decimals_at_the_inherited_2dp():
    """DECISION A/Global Constraint 2: the drawn clause is a TERM match between
    tab:donorBoundaryX and tab:bandRuleX, so both must be minted by the same rounding."""
    from iladub.etkl.sectiongraph import donor_evidence

    g = donor_evidence([_band((72.004, 200.0, 330.0, 460.0), HEAD)], {})
    u = _nodes(g)[0]
    bounds = set(g.objects(u, TAB.donorBoundaryX))
    rules = set(g.objects(u, TAB.bandRuleX))
    assert bounds == {Literal(Decimal(s)) for s in ("72.0", "200.0", "330.0", "460.0")}
    assert bounds == rules
    assert int(g.value(u, TAB.leafColumnCount)) == 3


def test_a_derived_gutter_is_a_boundary_but_not_a_rule_x():
    """bfs p6 bands 4-9's shape: column_xs carries an interior gutter this compiler
    inferred (291.5) where the author drew nothing. It is emitted as a boundary — the
    band DOES own a vector — and the query's drawn clause is what refuses it (Task 2)."""
    from iladub.etkl.sectiongraph import donor_evidence

    faked = _band((72.0, 200.0, 460.0), HEAD, column_xs=(72.0, 200.0, 291.5, 460.0))
    g = donor_evidence([faked], {})
    u = _nodes(g)[0]
    assert Literal(Decimal("291.5")) in set(g.objects(u, TAB.donorBoundaryX))
    assert Literal(Decimal("291.5")) not in set(g.objects(u, TAB.bandRuleX))


def test_the_head_refusal_is_a_fact_only_where_the_caller_mapped_one():
    """DECISION C: the R203 licence is carried verbatim from the datagrid's refusal
    record, and only for the band the caller identified BY INK. Nothing here infers."""
    from iladub.etkl.sectiongraph import donor_evidence

    g = donor_evidence([RULED, _band((72.0, 200.0, 330.0, 460.0), HEAD, y=50.0)],
                       {1: EVERY_MEASURE})
    n = _nodes(g)
    assert g.value(n[0], TAB.headLineRefusal) is None
    assert str(g.value(n[1], TAB.headLineRefusal)) == EVERY_MEASURE


def test_band_index_is_the_position_in_the_passed_list():
    """The single index space page_bands enumerates (compile.py:320 docstring)."""
    from iladub.etkl.sectiongraph import donor_evidence

    g = donor_evidence([_band((), HEAD), RULED, _band((), HEAD)], {})
    assert set(_nodes(g)) == {1}
