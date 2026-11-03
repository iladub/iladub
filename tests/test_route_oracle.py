"""The router's two oracles (document-router plan, Task 3). Tests verbatim from the plan."""
from iladub.route.lines import Line
from iladub.route.oracle import (
    BoundaryAnswer,
    DoctypeAnswer,
    check_boundary_local,
    check_boundary_split,
    check_doctype,
)


def _ext(texts, page=1):
    return [Line(page, i, t, 10.0 * i, 10.0 * i + 8, 0.0, 100.0) for i, t in enumerate(texts)]

def test_contract_needs_two_parties_and_one_commitment():
    ext = _ext(["Sellers: A", "Buyers: B", "Sellers shall ship", "x"])
    ok = DoctypeAnswer("CONTRACT", (0, 1), (2,), (), None, None)
    assert check_doctype(ok, ext, set()).admitted
    one_party = DoctypeAnswer("CONTRACT", (0,), (2,), (), None, None)
    assert not check_doctype(one_party, ext, set()).admitted
    same_line_twice = DoctypeAnswer("CONTRACT", (0, 0), (2,), (), None, None)
    assert not check_doctype(same_line_twice, ext, set()).admitted
    no_commitment = DoctypeAnswer("CONTRACT", (0, 1), (), (), None, None)
    assert not check_doctype(no_commitment, ext, set()).admitted

def test_ids_off_the_extent_are_refused():
    ext = _ext(["a", "b", "c"])
    for bad in [(0, 9), (-1, 1)]:
        assert not check_doctype(DoctypeAnswer("CONTRACT", bad, (2,), (), None, None), ext, set()).admitted

def test_other_needs_positive_evidence():
    ext = _ext(["Rules for sampling", "b"])
    assert check_doctype(DoctypeAnswer("OTHER", (), (), (0,), "Sampling rules", None), ext, set()).admitted
    assert not check_doctype(DoctypeAnswer("OTHER", (), (), (), "Sampling rules", None), ext, set()).admitted

def test_admitted_type_must_be_listed():
    ext = _ext(["Rules for sampling"])
    a = DoctypeAnswer("OTHER", (), (), (0,), None, "SamplingRules")
    assert check_doctype(a, ext, {"SamplingRules"}).admitted
    assert not check_doctype(a, ext, set()).admitted

def test_continues_refused_on_first_page():
    page = _ext(["header"])
    a = BoundaryAnswer("CONTINUES", None, (0,))
    assert not check_boundary_local(a, page, first_page=True).admitted
    assert check_boundary_local(a, page, first_page=False).admitted

def test_starts_must_cite_its_start_line():
    page = _ext(["end of A", "TITLE OF B"])
    assert check_boundary_local(BoundaryAnswer("STARTS", 1, (1,)), page, False).admitted
    assert not check_boundary_local(BoundaryAnswer("STARTS", 1, (0,)), page, False).admitted

def test_split_same_kind_needs_restart_or_disjoint_parties():
    a, b = _ext(["T", "Sellers: A", "Buyers: B", "shall"]), _ext(["T2", "Sellers: A", "Buyers: B", "shall"], page=2)
    ca = cb = DoctypeAnswer("CONTRACT", (1, 2), (3,), (), None, None)
    assert not check_boundary_split(a, ca, b, cb).admitted            # same parties, no restart
    b_restart = _ext(["T", "Sellers: A", "Buyers: B", "shall"], page=2)
    assert check_boundary_split(a, ca, b_restart, cb).admitted          # restart: same title text
    b_other = _ext(["T2", "Owners: C", "Charterers: D", "shall"], page=2)
    assert check_boundary_split(a, ca, b_other, cb).admitted            # different parties

def test_split_refused_when_a_side_is_refused():
    a, b = _ext(["T", "x"]), _ext(["U", "y"], page=2)
    ok = DoctypeAnswer("OTHER", (), (), (0,), "X", None)
    refused = DoctypeAnswer("REFUSES", (), (), (), None, None)
    assert not check_boundary_split(a, ok, b, refused).admitted


# --- beyond the plan's verbatim set: clauses the verbatim tests leave unpinned ---------------

def test_refuses_is_never_admitted():
    ext = _ext(["Sellers: A", "Buyers: B", "shall"])
    assert not check_doctype(DoctypeAnswer("REFUSES", (0, 1), (2,), (0,), None, None), ext, set()).admitted


def test_boundary_ids_in_range_and_not_repeated():
    page = _ext(["a", "b"])
    assert not check_boundary_local(BoundaryAnswer("CONTINUES", None, (5,)), page, False).admitted
    assert not check_boundary_local(BoundaryAnswer("CONTINUES", None, (-1,)), page, False).admitted
    assert not check_boundary_local(BoundaryAnswer("CONTINUES", None, (0, 0)), page, False).admitted
    assert not check_boundary_local(BoundaryAnswer("STARTS", None, (0,)), page, False).admitted
    assert not check_boundary_local(BoundaryAnswer("STARTS", 7, (7,)), page, False).admitted
    assert not check_boundary_local(BoundaryAnswer("REFUSES", None, (0,)), page, False).admitted


def test_split_kinds_differ_is_admitted_and_same_other_is_refused():
    a = _ext(["T", "Sellers: A", "Buyers: B", "shall"])
    b = _ext(["Rules for sampling", "y"], page=2)
    contract = DoctypeAnswer("CONTRACT", (1, 2), (3,), (), None, None)
    other = DoctypeAnswer("OTHER", (), (), (0,), "X", None)
    assert check_boundary_split(a, contract, b, other).admitted
    c = _ext(["Rules for weighing", "z"], page=3)
    assert not check_boundary_split(b, other, c, other).admitted
