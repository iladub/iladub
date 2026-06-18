import pytest
from iladub.allen import Interval, relation, feasible


@pytest.mark.parametrize("a,b,expected", [
    (Interval(0, 10), Interval(20, 30), "before"),
    (Interval(20, 30), Interval(0, 10), "after"),
    (Interval(0, 10), Interval(10, 20), "meets"),
    (Interval(0, 15), Interval(10, 20), "overlaps"),
    (Interval(5, 8), Interval(0, 20), "during"),
    (Interval(0, 20), Interval(5, 8), "contains"),
    (Interval(0, 10), Interval(0, 20), "starts"),
    (Interval(10, 20), Interval(0, 20), "finishes"),
    (Interval(0, 20), Interval(0, 20), "equals"),
])
def test_relation_classifies(a, b, expected):
    assert relation(a, b) == expected


def test_feasible_when_transport_ends_within_window():
    window = Interval(0, 240)
    assert feasible(window, Interval(0, 95)) is True


def test_infeasible_when_transport_exceeds_window():
    window = Interval(0, 240)
    assert feasible(window, Interval(0, 270)) is False
