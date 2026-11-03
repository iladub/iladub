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
    write_back_doctype(DoctypeAnswer("OTHER", (), (), (0,), None, "Invoice"), _ext(["Invoice"]), rules)
    both = _ext(["Sellers: A", "Buyers: B", "Sellers shall ship", "Invoice"])
    # "Invoice" occurs in the contract extent, so the extent-level conflict silences the OTHER rule
    assert rule_doctype(both, rules).kind == "CONTRACT"
    # force a genuine disagreement: a second OTHER rule on a cue the contract extent never held
    write_back_doctype(DoctypeAnswer("OTHER", (), (), (0,), None, "Memo"), _ext(["Memo"]), rules)
    assert rule_doctype(_ext(["Sellers: A", "Buyers: B", "Sellers shall ship", "Memo"]), rules) is None


def test_no_text_in_rules_file():
    rules = _rules()
    page = _ext(["Sellers: ACME", "x"])
    write_back_boundary(BoundaryAnswer("STARTS", 0, (0,)), page, rules)
    write_back_doctype(DoctypeAnswer("CONTRACT", (0,), (1,), (), None, None), page, rules)
    assert "Sellers" not in rules.serialize(format="turtle")
    assert "Sellers" not in RULES_PATH.read_text()


def test_doctype_conflicting_write_back_disables_both():
    rules = _rules()
    ext = _ext(["Sellers: A", "Buyers: B", "Sellers shall ship"])
    write_back_doctype(DoctypeAnswer("CONTRACT", (0, 1), (2,), (), None, None), ext, rules)
    write_back_doctype(DoctypeAnswer("OTHER", (0, 1), (2,), (), None, None), ext, rules)
    assert rule_doctype(ext, rules) is None


def test_other_cue_seen_in_a_contract_extent_is_conflicted_either_order():
    boiler = "Page 1 of 1"
    contract = _ext(["Sellers: A", "Buyers: B", "Sellers shall ship", boiler])
    letter = _ext(["Dear Sir", boiler])
    shared = DoctypeAnswer("OTHER", (), (), (1,), None, None)
    for order in ("contract-first", "other-first"):
        rules = _rules()
        steps = [lambda: write_back_doctype(DoctypeAnswer("CONTRACT", (0, 1), (2,), (), None, None),
                                            contract, rules),
                 lambda: write_back_doctype(shared, letter, rules)]
        for step in (steps if order == "contract-first" else steps[::-1]):
            step()
        assert rule_doctype(_ext([boiler]), rules) is None, order
        # the contract rule is unaffected by the OTHER extent: its cues are not all in that extent
        assert rule_doctype(contract, rules).kind == "CONTRACT", order


def test_distinctive_other_cue_still_fires_after_a_contract_extent():
    rules = _rules()
    write_back_doctype(DoctypeAnswer("CONTRACT", (0, 1), (2,), (), None, None),
                       _ext(["Sellers: A", "Buyers: B", "Sellers shall ship"]), rules)
    write_back_doctype(DoctypeAnswer("OTHER", (), (), (0,), None, None), _ext(["INVOICE no 7"]), rules)
    assert rule_doctype(_ext(["x", "INVOICE no 7"]), rules) == DoctypeAnswer("OTHER", (), (), (1,), None, None)


def test_conflicted_continues_does_not_block_other_continues_cues():
    rules = _rules()
    page = _ext(["Both", "Footer"])
    write_back_boundary(BoundaryAnswer("STARTS", 0, (0,)), page, rules)
    write_back_boundary(BoundaryAnswer("CONTINUES", None, (0, 1)), page, rules)
    assert rule_boundary(_ext(["Both"]), rules) is None
    assert rule_boundary(page, rules) == BoundaryAnswer("CONTINUES", None, (1,))


def test_write_back_refuses_what_is_not_a_rule():
    import pytest
    page = _ext(["a"])
    with pytest.raises(ValueError):
        write_back_boundary(BoundaryAnswer("REFUSES", None, ()), page, _rules())
    with pytest.raises(ValueError):
        write_back_doctype(DoctypeAnswer("REFUSES", (), (), (), None, None), page, _rules())
    with pytest.raises(ValueError):
        write_back_doctype(DoctypeAnswer("CONTRACT", (), (), (), None, None), page, _rules())


def test_agreeing_rules_merge_cues_and_scale():
    import time
    rules = _rules()
    n = 100
    # rule i has cues (party i, commit i); even i fire, odd i lack their commit cue (never listed)
    for i in range(n):
        ext = _ext([f"party {i}", f"commit {i}"])
        write_back_doctype(DoctypeAnswer("CONTRACT", (0,), (1,), (), None, None), ext, rules)
    extent = _ext([f"party {i}" for i in range(n)] + [f"commit {i}" for i in range(0, n, 2)]
                  + [f"filler {i}" for i in range(n)])
    t0 = time.perf_counter()
    got = rule_doctype(extent, rules)
    print(f"scale: 100 rules / {len(extent)} lines in {time.perf_counter() - t0:.2f}s")
    # every firing rule agrees (CONTRACT); cues merge per role, least position
    assert got.kind == "CONTRACT" and got.party_lines == tuple(range(0, n, 2)) and got.commitment_lines == tuple(range(n, n + 50))
    # a firing OTHER rule alongside makes the answer abstain
    write_back_doctype(DoctypeAnswer("OTHER", (), (), (0,), None, None), _ext(["filler 3"]), rules)
    assert rule_doctype(extent, rules) is None
