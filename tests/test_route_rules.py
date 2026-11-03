"""Written-back rules as hashed cues (document-router plan, Task 4)."""
from rdflib import Graph

from iladub.route.lines import Line
from iladub.route.rules import (
    RULES_PATH,
    rule_boundary,
    rule_doctype,
    write_back_boundary,
    write_back_doctype,
)
from iladub.route.oracle import BoundaryAnswer, DoctypeAnswer


def _ext(texts, page=1):
    return [Line(page, i, t, 10.0 * i, 10.0 * i + 8, 0.0, 100.0) for i, t in enumerate(texts)]


def _rules():
    return Graph().parse(RULES_PATH, format="turtle")


def test_starts_cue_fires():
    rules = _rules()
    page = _ext(["Purchase Agreement", "Sellers: A", "body"])
    write_back_boundary(BoundaryAnswer("STARTS", 0, (0,)), page, rules)
    other = _ext(["body", "Purchase Agreement", "more"], page=2)
    assert rule_boundary(other, rules) == BoundaryAnswer("STARTS", 1, (1,))
    assert rule_boundary(_ext(["nothing", "here"]), rules) is None


def test_two_starts_on_a_page_abstain():
    rules = _rules()
    page = _ext(["Purchase Agreement", "x"])
    write_back_boundary(BoundaryAnswer("STARTS", 0, (0,)), page, rules)
    assert rule_boundary(_ext(["Purchase Agreement", "y", "Purchase Agreement"]), rules) is None


def test_continues_needs_a_cue():
    rules = _rules()
    page = _ext(["Page footer", "x", "Annex"])
    assert rule_boundary(page, rules) is None
    write_back_boundary(BoundaryAnswer("CONTINUES", None, (0, 2)), page, rules)
    assert rule_boundary(page, rules) == BoundaryAnswer("CONTINUES", None, (0, 2))
    # a STARTS match on the same page wins over CONTINUES
    write_back_boundary(BoundaryAnswer("STARTS", 1, (1,)), page, rules)
    assert rule_boundary(page, rules) == BoundaryAnswer("STARTS", 1, (1,))


def test_conflicting_write_back_disables_both():
    rules = _rules()
    page = _ext(["Same line", "x"])
    write_back_boundary(BoundaryAnswer("STARTS", 0, (0,)), page, rules)
    write_back_boundary(BoundaryAnswer("CONTINUES", None, (0,)), page, rules)
    assert rule_boundary(page, rules) is None


def test_doctype_rule_needs_all_cues():
    rules = _rules()
    ext = _ext(["Sellers: A", "Buyers: B", "Sellers shall ship", "Sellers: A"])
    write_back_doctype(DoctypeAnswer("CONTRACT", (0, 1), (2,), (), None, None), ext, rules)
    full = _ext(["noise", "Buyers: B", "Sellers shall ship", "Sellers: A", "Sellers: A"])
    assert rule_doctype(full, rules) == DoctypeAnswer("CONTRACT", (1, 3), (2,), (), None, None)
    assert rule_doctype(_ext(["Buyers: B", "Sellers shall ship"]), rules) is None


def test_doctype_rules_of_different_kinds_abstain():
    rules = _rules()
    ext = _ext(["Sellers: A", "Buyers: B", "Sellers shall ship", "Invoice"])
    write_back_doctype(DoctypeAnswer("CONTRACT", (0, 1), (2,), (), None, None), ext, rules)
    write_back_doctype(DoctypeAnswer("OTHER", (), (), (3,), None, "Invoice"), ext, rules)
    assert rule_doctype(ext, rules) is None
    assert rule_doctype(_ext(["Invoice"]), rules) == DoctypeAnswer("OTHER", (), (), (0,), None, "Invoice")


def test_no_text_in_rules_file():
    rules = _rules()
    page = _ext(["Sellers: ACME", "x"])
    write_back_boundary(BoundaryAnswer("STARTS", 0, (0,)), page, rules)
    write_back_doctype(DoctypeAnswer("CONTRACT", (0,), (1,), (), None, None), page, rules)
    assert "Sellers" not in rules.serialize(format="turtle")
    assert "Sellers" not in RULES_PATH.read_text()
