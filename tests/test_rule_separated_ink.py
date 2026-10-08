"""Spec 2026-10-08-rule-separated-ink-design.md — the membrane refuses a cell whose ink an author's
rule separates. Synthetic only: no corpus document is compiled here (fed-h41 is held out)."""
import os
from decimal import Decimal

import pytest
from rdflib import BNode, Graph, Literal, RDF, URIRef
from rdflib.namespace import XSD

from iladub.etkl import membrane
from iladub.etkl.geometry import Char, Rule
from iladub.etkl.ruleink import carry_rule_ink, glyph_extents

TAB_NS = "https://w3id.org/iladub/tab#"
from rdflib import Namespace
TAB = Namespace(TAB_NS)
VOCAB = os.path.join(os.path.dirname(__file__), "..", "vocab")
DOC = "https://example.org/etkl/doc/p0"


def _shapes_and_ont():
    s = Graph().parse(os.path.join(VOCAB, "shapes", "tab-shapes.ttl"), format="turtle")
    o = Graph().parse(os.path.join(VOCAB, "ontology", "tab.ttl"), format="turtle")
    return s, o


def _dec(x):
    return Literal(Decimal(str(x)))


def _page(first_end, last_start, rule_x=100.0, rule_page=0, rule_top=0.0, rule_bottom=50.0):
    """One table, one cell at y [10, 20] on page 0, one rule. The cell's glyph extents are given
    directly — the shape reads facts, it does not compute them."""
    g = Graph()
    t, c, b, r = URIRef(DOC + "#t"), URIRef(DOC + "#c"), BNode(), URIRef(DOC + "#rule-p0-0")
    g.add((t, RDF.type, TAB.RecordTable))
    g.add((t, TAB.hasCell, c))
    g.add((c, RDF.type, TAB.EntryCell))
    g.add((c, TAB.cellText, Literal("96,127+")))
    g.add((c, TAB.onPage, Literal(0, datatype=XSD.integer)))
    g.add((c, TAB.hasBBox, b))
    g.add((b, RDF.type, TAB.BBox))
    for k, v in (("x0", 80.0), ("x1", 110.0), ("y0", 10.0), ("y1", 20.0)):
        g.add((b, TAB[k], _dec(v)))
    g.add((c, TAB.firstGlyphEnd, _dec(first_end)))
    g.add((c, TAB.lastGlyphStart, _dec(last_start)))
    g.add((r, RDF.type, TAB.RuleSpan))
    g.add((r, TAB.ruleX, _dec(rule_x)))
    g.add((r, TAB.ruleTop, _dec(rule_top)))
    g.add((r, TAB.ruleBottom, _dec(rule_bottom)))
    g.add((r, TAB.onPage, Literal(rule_page, datatype=XSD.integer)))
    return g


MSG = "(rule-separated ink)"


def _refusing_shapes(g, engine):
    """(refused by tab:RuleSeparatedInkShape?, report). The minimal page breaks unrelated tab
    shapes (a lone entry cell has no leaf column), so the verdict read is THIS shape's message,
    not the graph's overall conformance."""
    s, o = _shapes_and_ont()
    _, text = membrane.validate(g, s, o, engine=engine)
    return MSG not in text, text


ENGINES = ["pyshacl"] + (["rudof"] if membrane.rudof_available() else [])


@pytest.mark.parametrize("engine", ENGINES)
def test_a_rule_between_a_cells_glyphs_is_refused(engine):
    # glyph wholly left ends at 98, glyph wholly right starts at 102: the rule at 100 separates.
    conforms, text = _refusing_shapes(_page(98.0, 102.0), engine)
    assert not conforms, text


@pytest.mark.parametrize("engine", ENGINES)
@pytest.mark.parametrize("label,kw", [
    # the overrun: the last glyph straddles the rule, none lies wholly right of it (apple, who-*)
    ("overrun", dict(first_end=98.0, last_start=99.5)),
    # the rule is on another page
    ("other page", dict(first_end=98.0, last_start=102.0, rule_page=1)),
    # the rule ends above the cell (touching at y0 is a zero-length overlap)
    ("vertically disjoint", dict(first_end=98.0, last_start=102.0, rule_top=0.0, rule_bottom=10.0)),
])
def test_controls_conform(engine, label, kw):
    conforms, text = _refusing_shapes(_page(**kw), engine)
    assert conforms, (label, text)


def test_equality_is_inclusive_on_both_sides():
    # a glyph ending exactly on the rule is wholly left; one starting exactly on it, wholly right
    conforms, _ = _refusing_shapes(_page(100.0, 100.0), "pyshacl")
    assert not conforms


def _ch(t, x0, x1, top=11.0, bottom=19.0):
    return Char(t, x0, x1, top, bottom)


def test_glyph_extents_are_min_x1_and_max_x0_of_the_glyphs_centred_in_the_box():
    chars = [_ch("9", 81.0, 86.0), _ch("7", 92.0, 98.0), _ch("+", 102.0, 107.0),
             _ch(" ", 98.0, 102.0),                       # a space is never a glyph
             _ch("x", 200.0, 205.0),                      # outside the box
             _ch("y", 90.0, 95.0, top=30.0, bottom=38.0)]  # outside vertically
    assert glyph_extents(chars, (80.0, 10.0, 110.0, 20.0)) == (86.0, 102.0)
    assert glyph_extents(chars, (300.0, 10.0, 310.0, 20.0)) is None


def test_carry_adds_rules_and_extents_and_nothing_on_an_unruled_page():
    g = _page(0, 0)
    for p in (TAB.firstGlyphEnd, TAB.lastGlyphStart):
        g.remove((None, p, None))
    for r in list(g.subjects(RDF.type, TAB.RuleSpan)):
        g.remove((r, None, None))
    before = len(g)
    chars = [_ch("9", 81.0, 86.0), _ch("+", 102.0, 107.0)]
    assert carry_rule_ink(g, DOC, {0: []}, {0: chars}) == 0
    assert len(g) == before
    added = carry_rule_ink(g, DOC, {0: [Rule(100.004, 0.0, 50.0)]}, {0: chars})
    c = URIRef(DOC + "#c")
    assert g.value(c, TAB.firstGlyphEnd) == _dec("86.0")
    assert g.value(c, TAB.lastGlyphStart) == _dec("102.0")
    rules = list(g.subjects(RDF.type, TAB.RuleSpan))
    assert len(rules) == 1 and g.value(rules[0], TAB.ruleX) == _dec("100.0")
    assert added == len(g) - before
