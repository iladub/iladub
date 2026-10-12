"""The worked example of a role contract: `examples/finance/statement-{contract,terms,shapes}.ttl`.

Spec: docs/superpowers/specs/2026-10-12-a-matrix-cell-is-an-observation-design.md §§ 4, 5, 9.2.
Three fields, one per structural role: `fin:lineItem` (row key, scheme-bound), `fin:period`
(column key, `sh:pattern`), `fin:value` (cell value, `sh:pattern`). A contract that declares a
cell-value field is what makes `feed.ground_document` read one record per cell.

THIS IS THE CI ARM (spec § 5, last paragraph): the corpus never reaches CI, so the matrix below
is built here. The corpus arm is `tests/test_corpus_apple_contract.py`.

The pattern strings below have the shapes a statement prints, written as the feed delivers
them: a key is its header path's labels joined by one space, a figure is the cell's text.
"""
from dataclasses import replace

import pytest
from rdflib import Graph, Literal, Namespace, RDF, URIRef

from iladub import ground
from iladub.feed import FeedResult, ground_document
from iladub.ground import (ROLE_CELL_VALUE, ROLE_COLUMN_KEY, ROLE_ROW_KEY, _value_conforms,
                           load_contract)
from iladub.propose_ground import FakeGroundingProposer, GroundingProposal
from iladub.validate import validate
from tests.test_feed_matrix_cell import M0, _matrix

FIN = Namespace("https://example.org/finance#")
ILA = Namespace("https://w3id.org/iladub#")
CONTRACT = "examples/finance/statement-contract.ttl"
TERMS = "examples/finance/statement-terms.ttl"
SHAPES = "examples/finance/statement-shapes.ttl"
OFFER = URIRef("urn:iladub:record:scratch")

ABSTAIN = FakeGroundingProposer(
    GroundingProposal(None, str(FIN) + "x", 0.1, "n/a", "urn:iladub:suggester/fake"))
# Spec § 9.2's proposer: it names the row-key field for whatever it is asked about.
NAMES_LINE_ITEM = FakeGroundingProposer(
    GroundingProposal(str(FIN["f-line-item"]), str(FIN) + "x", 0.9, "names the line item",
                      "urn:iladub:suggester/fake"))


class _Raises:
    """A proposer that must not be asked."""

    def propose_grounding(self, concept, fields, page_context=None):
        raise AssertionError(f"the proposer was asked about {concept!r}")


def _terms():
    return Graph().parse(TERMS, format="turtle")


def _shapes():
    return Graph().parse(SHAPES, format="turtle")


# --- the contract ------------------------------------------------------------------------

def test_the_contract_declares_one_field_per_role():
    c = load_contract(CONTRACT)
    assert c.target_class == str(FIN.StatementFigure)
    assert {f.fills_property: (f.role, f.scheme) for f in c.fields} == {
        str(FIN.lineItem): (ROLE_ROW_KEY, str(FIN["scheme-line-item"])),
        str(FIN.period): (ROLE_COLUMN_KEY, None),
        str(FIN.value): (ROLE_CELL_VALUE, None),
    }


def test_the_contract_conforms_to_the_role_shapes():
    """Run directly, not only through `load_contract`'s raise: the worked example is the
    conforming example `etkl:ContractRoleShape` ships with (spec § 3.1)."""
    verdict = validate(Graph().parse(CONTRACT, format="turtle"), ground._etkl_shapes(), Graph(),
                       use_shapes=list(ground._ROLE_SHAPES))
    assert verdict.conforms, verdict.report_text


def test_every_field_has_an_oracle_of_its_own():
    """A role field with neither a scheme nor a value constraint grounds every concept of its
    role by field identity. The example must not be that contract."""
    shapes = _shapes()
    for f in load_contract(CONTRACT).fields:
        ps = ground._property_shape(shapes, f.fills_property)
        constrained = ps is not None and ground._has_value_constraint(shapes, ps)
        assert (f.scheme is not None) != constrained, f


def test_the_scheme_carries_a_label_a_statement_may_repeat():
    """Without it the refusal by rule has nothing to refuse: a shared label no scheme admits
    quarantines with or without the rule."""
    assert ground.scheme_member("Total net sales", str(FIN["scheme-line-item"]), _terms())


# --- the two patterns --------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "June 27, 2026",
    "September 27, 2025",
    "Three Months Ended June 27, 2026",
    "Three Months Ended June 28, 2025",
    "Nine Months Ended June 27, 2026",
    "Nine Months Ended June 28, 2025",
    "December 1, 2024",
])
def test_the_period_pattern_admits_a_printed_period(text):
    assert _value_conforms(OFFER, str(FIN.StatementFigure), str(FIN.period), text, _shapes())


@pytest.mark.parametrize("text", [
    "Gross margin",                       # a line-item label read into the wrong position
    "Total net sales",
    "Three Months Ended",                 # the spanner alone, with no leaf under it
    "Three Months Ended > June 27, 2026",  # the feed's ` > ` id separator, never a key's text
    "2026",
    "June 2026",
    "",
])
def test_the_period_pattern_refuses_what_is_not_a_period(text):
    assert not _value_conforms(OFFER, str(FIN.StatementFigure), str(FIN.period), text, _shapes())


@pytest.mark.parametrize("text", [
    "12,345",            # 9,9
    "$ 12,345",          # $ 9,9
    "$ 1.23",            # $ 9.9
    "12,345,678",        # 9,9,9
    "(12,345)",          # (9,9)
    "123",               # 9
    "(123)",             # (9)
])
def test_the_numeral_pattern_admits_a_printed_figure(text):
    assert _value_conforms(OFFER, str(FIN.StatementFigure), str(FIN.value), text, _shapes())


@pytest.mark.parametrize("text", [
    "Y",
    "",
    "Available",
    "$",                 # the sign with no figure
    "$12,345",           # not as printed: the page puts a space after the sign
    "12,3456",           # not comma-grouped thousands
    "(12,345",           # an unclosed parenthesis
    "12,345 (1)",        # a figure with a footnote marker is not a figure
])
def test_the_numeral_pattern_refuses_what_is_not_a_figure(text):
    assert not _value_conforms(OFFER, str(FIN.StatementFigure), str(FIN.value), text, _shapes())


# --- the switch --------------------------------------------------------------------------

PERIODS = [("Three Months Ended", "March 31, 2026"), ("Three Months Ended", "March 31, 2025")]
# Four rows by two columns: a 2x2 with one repeated label cannot show a row key GROUNDING,
# because both of its rows share the label. The two extra rows are the unshared label the
# scheme carries and the unshared label it does not.
ROWS = [
    ("Total net sales", {0: "100", 1: "90"}),              # shared, and in the scheme
    ("Total net sales", {0: "60", 1: "55"}),               # shared, and in the scheme
    ("Gross margin", {0: "40", 1: "35"}),                  # unshared, in the scheme
    ("Research and development", {0: "(8)", 1: "n/a"}),    # unshared, not in the scheme
]


def _statement():
    return _matrix(Graph(), M0, 0, PERIODS, ROWS)


def _ground(contract, proposer):
    g = Graph()
    result = ground_document(_statement(), contract, proposer, _terms(), _shapes(), g,
                             validate_shapes=True)
    return result, g


def _subjects_by(g, prop):
    out = {}
    for s, o in g.subject_objects(prop):
        out.setdefault(s, set()).add(str(o))
    return out


def test_a_role_contract_grounds_one_record_per_cell():
    # DERIVED from ROWS, not copied from a run. 4 rows x 2 columns = 8 cells = 8 records of
    # three concepts each, 24 concepts.
    #   row keys:    2 grounded (Gross margin x2). 4 refused by rule (Total net sales, shared)
    #                and 2 quarantined (Research and development, no scheme member).
    #   column keys: 8 grounded (both paths are printed periods).
    #   cell values: 7 grounded; `n/a` is refused by the numeral pattern.
    # grounded = 2 + 8 + 7 = 17; proposed = 4 + 2 + 1 = 7; 17 + 7 = 24.
    # `_Raises`: every concept of a matrix record has a role, so no proposer is ever asked.
    result, g = _ground(load_contract(CONTRACT), _Raises())
    assert result == FeedResult(8, 17, 7)
    line_items = _subjects_by(g, FIN.lineItem)
    periods = _subjects_by(g, FIN.period)
    values = _subjects_by(g, FIN.value)
    assert len(periods) == 8 and all(len(v) == 1 for v in periods.values())
    assert sorted(v for vs in values.values() for v in vs) == sorted(
        ["100", "90", "60", "55", "40", "35", "(8)"])
    assert sorted(v for vs in line_items.values() for v in vs) == ["Gross margin"] * 2
    # the figure is under the period and the line the page printed it under
    read = {(next(iter(line_items[s])), next(iter(periods[s])), next(iter(values[s])))
            for s in line_items}
    assert read == {
        ("Gross margin", "Three Months Ended March 31, 2026", "40"),
        ("Gross margin", "Three Months Ended March 31, 2025", "35"),
    }
    assert len(list(g.subjects(RDF.type, FIN.StatementFigure))) == 8


def test_a_shared_row_label_does_not_ground_when_a_proposer_names_its_field():
    """Spec § 9.2. The abstaining arm proves nothing here: a role-less shared label would be
    quarantined by an abstainer too. Under a proposer that names the row-key field the counts
    are the ones derived above, and no line item is carried twice under one period."""
    result, g = _ground(load_contract(CONTRACT), NAMES_LINE_ITEM)
    assert result == FeedResult(8, 17, 7)
    assert (None, FIN.lineItem, Literal("Total net sales")) not in g
    line_items = _subjects_by(g, FIN.lineItem)
    periods = _subjects_by(g, FIN.period)
    assert all(len(v) == 1 for v in line_items.values())
    keyed = [(next(iter(line_items[s])), next(iter(periods[s]))) for s in line_items]
    assert len(keyed) == len(set(keyed)) == 2


def test_a_roleless_contract_does_not_turn_the_keyword_on():
    """The same graph, the same three fields with no role declared: the row reading, one record
    per row. 4 rows, each with 2 cell concepts whose text is a column path; no field is named by
    one, the abstainer names none, so nothing grounds."""
    roleless = load_contract(CONTRACT)
    roleless = replace(roleless, fields=tuple(replace(f, role=None) for f in roleless.fields))
    result, g = _ground(roleless, ABSTAIN)
    assert result == FeedResult(4, 0, 8)
    assert list(g.subjects(RDF.type, ILA.GroundedNode)) == []
