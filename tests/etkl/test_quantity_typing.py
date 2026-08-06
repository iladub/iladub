"""Quantity typing (spec 2026-08-06-quantity-typing-design.md).

Two mechanisms, deliberately different:
  - tab:ParenthesizedNumber ABSTAINS — `(171)` is format-identical to the footnote `(1)`
    (measured on apple: 34 negative-shaped, 3 footnote-shaped, all footnotes `(1)`), so no
    grammar can separate them and the honest reading is to abstain, exactly as tab:Blank does.
  - tab:Currency NORMALISES to tab:Quantity — `$ 45,781` is unambiguously a quantity and the
    `$` is a unit marker, a reading this repo already asserts elsewhere (tab:UnitMarker).
"""
from rdflib import Literal, Namespace
from iladub.etkl import celltype
from iladub.etkl.celltype import _cell_datatype, is_paren_number

TAB = Namespace("https://w3id.org/iladub/tab#")


# ---------- recall: forms that ARE parenthesized numbers (R55's mandated battery) ----------

def test_paren_grammar_recall():
    for s in ["(171)", "(698)", "(2,037)", "(1.5)", "(0)", "(1,234.56)", "( 171 )", "(-5)"]:
        assert is_paren_number(s), s
        assert _cell_datatype(s) == TAB.ParenthesizedNumber, s


def test_footnote_marker_is_the_same_form_and_types_the_same_way():
    """`(1)` is a footnote marker on apple, and format-identical to a one-digit negative.
    It MUST type as ParenthesizedNumber too — abstention is what makes that safe. Typing it
    differently would require a digit-count threshold, which the gate forbids."""
    assert _cell_datatype("(1)") == TAB.ParenthesizedNumber


# ---------- precision: forms that are NOT parenthesized numbers ----------

def test_paren_grammar_precision():
    for s in ["(a)", "(i)", "(see p.250)", "(cont'd)", "()", "(171", "171)", "$(171)", "(171)*"]:
        assert not is_paren_number(s), s
        assert _cell_datatype(s) != TAB.ParenthesizedNumber, s


def test_blank_marker_still_types_blank():
    """`(blank)` is the shipped missing-value marker and must not be captured by the new
    grammar — is_blank runs first in _cell_datatype."""
    assert _cell_datatype("(blank)") == TAB.Blank


def test_plain_and_currency_forms_are_unchanged():
    assert _cell_datatype("45,781") == TAB.Numeric
    assert _cell_datatype("$ 45,781") == TAB.Currency
    assert _cell_datatype("Americas") == TAB.Text
    assert _cell_datatype("2020-01-02") == TAB.Date


# ---------- the declarations reach the evidence graph ----------

def test_evidence_graph_carries_the_datatype_declarations():
    """The queries reason over these triples, and the evidence graph is transient — so
    grid_evidence must emit them or every normalisation silently no-ops."""
    g = celltype.grid_evidence([(0, 0, "x")], 1)
    assert (TAB.Blank, TAB.datatypeAbstains, Literal(True)) in g
    assert (TAB.ParenthesizedNumber, TAB.datatypeAbstains, Literal(True)) in g
    assert (TAB.Numeric, TAB.inDatatypeFamily, TAB.Quantity) in g
    assert (TAB.Currency, TAB.inDatatypeFamily, TAB.Quantity) in g


def test_text_neither_abstains_nor_has_a_family():
    """Text must stay its own thing: it is the signal every homogeneity query keys on."""
    g = celltype.grid_evidence([(0, 0, "x")], 1)
    assert (TAB.Text, TAB.datatypeAbstains, Literal(True)) not in g
    assert list(g.objects(TAB.Text, TAB.inDatatypeFamily)) == []


def test_date_is_not_in_the_quantity_family():
    """Date is deliberately its own family — a date column is not a quantity column."""
    g = celltype.grid_evidence([(0, 0, "x")], 1)
    assert list(g.objects(TAB.Date, TAB.inDatatypeFamily)) == []
