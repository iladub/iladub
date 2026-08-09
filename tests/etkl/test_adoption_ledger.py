"""The line ledger (spec 2026-08-09-adoption-at-document-scope §5.3).

Every line is counted exactly once. The two failure directions this pins are the two the
spec measured: zeroing the escalation (page scores 1.0000 whatever the grid missed) and
band-granular withdrawal (the 0.594 double count)."""
from dataclasses import dataclass

from iladub.etkl.adoption import build_ledger


@dataclass(frozen=True)
class _W:
    text: str


@dataclass(frozen=True)
class _L:
    words: tuple
    top: float
    bottom: float


@dataclass(frozen=True)
class _B:
    top: float
    bottom: float


@dataclass(frozen=True)
class _R:
    verdict: str
    tokens_escalated: int = 0


def _line(n_words, top):
    return _L(tuple(_W(f"w{i}") for i in range(n_words)), top, top + 1.0)


def test_a_line_the_grid_read_is_asserted_and_never_residue():
    lines = [_line(3, 10.0), _line(2, 20.0)]
    bands = [_B(0.0, 30.0)]
    reports = [_R("escalated", 5)]
    led = build_ledger(lines, (0, 1), bands, reports)
    assert led.admitted == (0, 1)
    assert led.residue == ()
    assert led.asserted_tokens == 5
    assert led.escalated_tokens == 0
    assert led.touched == frozenset({0})


def test_an_unread_line_inside_an_escalated_band_stays_escalated():
    """The apple p1 shape: the grid reads the leaf rows and drops the section labels."""
    lines = [_line(2, 10.0), _line(3, 20.0), _line(4, 30.0)]
    bands = [_B(0.0, 40.0)]
    reports = [_R("escalated", 9)]
    led = build_ledger(lines, (1, 2), bands, reports)
    assert led.residue == (0,)
    assert led.asserted_tokens == 7
    assert led.escalated_tokens == 2
    assert led.touched == frozenset({0})


def test_a_band_the_grid_never_touched_keeps_its_own_token_count():
    lines = [_line(2, 10.0), _line(3, 90.0)]
    bands = [_B(0.0, 50.0), _B(80.0, 100.0)]
    reports = [_R("escalated", 2), _R("escalated", 7)]
    led = build_ledger(lines, (0,), bands, reports)
    assert led.touched == frozenset({0})
    assert led.residue == ()
    # band 1 is untouched: its OWN escalated token count carries, not the page-level one
    assert led.escalated_tokens == 7
    assert led.asserted_tokens == 2


def test_an_ignored_band_contributes_nothing_to_either_side():
    """A NON_TABLE band's ink was never in the denominator and does not enter it now."""
    lines = [_line(5, 10.0), _line(3, 60.0)]
    bands = [_B(0.0, 50.0), _B(55.0, 70.0)]
    reports = [_R("ignored", 0), _R("escalated", 3)]
    led = build_ledger(lines, (1,), bands, reports)
    assert led.residue == ()            # line 0 sits in an IGNORED band, not an escalated one
    assert led.escalated_tokens == 0
    assert led.asserted_tokens == 3


def test_no_line_is_on_both_sides_ever():
    lines = [_line(1, float(10 * i)) for i in range(10)]
    bands = [_B(0.0, 100.0)]
    reports = [_R("escalated", 10)]
    led = build_ledger(lines, (0, 2, 4, 6, 8), bands, reports)
    assert not set(led.admitted) & set(led.residue)
    assert led.asserted_tokens + led.escalated_tokens == 10
