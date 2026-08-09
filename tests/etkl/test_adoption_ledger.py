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


def test_a_band_that_booked_escalated_ink_under_an_asserted_verdict_still_counts():
    """The verdict STRING is not the authority — the booked tokens are (task 3 review).

    `compile.compile_tables` books `escalated_total += max(0, tokens - n)` while hard-coding the
    report verdict to "asserted" on its ruled-reading and row-role paths. An adopting page has
    `asserted_total == 0`, so a band that reached adoption through one of those paths did so with
    `n == 0` and carries real escalated ink under an "asserted" label. Selecting escalated bands
    by the string would drop that ink from the residue term AND from the untouched term at once —
    the page scoring higher than it read."""
    lines = [_line(2, 10.0), _line(3, 90.0), _line(4, 95.0)]
    bands = [_B(0.0, 50.0), _B(80.0, 100.0)]
    # band 1 is TOUCHED (line 1 admitted) and holds one unread line (line 2).
    asserted_label = build_ledger(lines, (0, 1), bands,
                                  [_R("escalated", 2), _R("asserted", 4)])
    escalated_label = build_ledger(lines, (0, 1), bands,
                                   [_R("escalated", 2), _R("escalated", 4)])
    assert asserted_label == escalated_label, "the label must not change the accounting"
    assert asserted_label.touched == frozenset({0, 1})
    assert asserted_label.residue == (2,)      # the unread line of band 1 survives as residue
    assert asserted_label.asserted_tokens == 5
    assert asserted_label.escalated_tokens == 4

    # And untouched: band 1's own booked count carries, exactly as an "escalated" one would.
    untouched = build_ledger(lines[:2], (0,), bands, [_R("escalated", 2), _R("asserted", 7)])
    assert untouched.touched == frozenset({0})
    assert untouched.escalated_tokens == 7


def test_no_line_is_on_both_sides_ever():
    lines = [_line(1, float(10 * i)) for i in range(10)]
    bands = [_B(0.0, 100.0)]
    reports = [_R("escalated", 10)]
    led = build_ledger(lines, (0, 2, 4, 6, 8), bands, reports)
    assert not set(led.admitted) & set(led.residue)
    assert led.asserted_tokens + led.escalated_tokens == 10


def test_an_out_of_range_grid_row_is_dropped_not_aliased():
    """A negative index would alias to the LAST line and count its ink twice; an index
    past the end has no line at all. Neither may enter the ledger."""
    lines = [_line(1, 0.0)]
    bands = [_B(0.0, 10.0)]
    reports = [_R("escalated", 1)]
    led = build_ledger(lines, (-1, 0, 5), bands, reports)
    assert led.admitted == (0,)
    assert led.asserted_tokens == 1
    assert led.escalated_tokens == 0
