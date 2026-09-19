"""A lone data row is offered the reading its neighbours already get (2026-09-18).

bfs p6 is one table. `Total`, `Zurich` and `Tessin` are each one row of it, set apart by the
author's section spacing, so `detect_bands` returns each as a one-line band, `classify` answers
NON_TABLE / "fewer than 2 lines", and the row was IGNORED — its ink booked nowhere, so the
document score never saw the dropped entries. Every other band of that table is read by grid
donation. `donation.offer_single_line` gives the lone row the same offer, with the column count
left free (one line cannot resolve a gutter profile: `Total` alone reads 3 columns of 9) and the
shipped membrane as the judge.
"""
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BFS = os.path.join(ROOT, "corpus", "gov-stats", "bfs-population-bilan-2023.pdf")

pytestmark = pytest.mark.skipif(not os.path.exists(BFS), reason="corpus not fetched")


def _first(report):
    lines = (report.ascii or "").strip().splitlines()
    return lines[0].split()[0] if lines else ""


def _p6():
    from iladub.etkl.compile import compile_tables
    return compile_tables(BFS, page_number=6, validate_shapes=True)


def test_the_lone_rows_of_bfs_p6_now_assert_under_the_donors_nine_columns():
    by_label = {_first(r): r for r in _p6().regions}
    for label in ("Total", "Zurich"):
        r = by_label[label]
        assert r.verdict == "asserted", f"{label} is still {r.verdict} ({r.reason})"
        assert r.cells == 9, f"{label} must read one entry per column of the donor's grid"


def test_a_lone_line_of_PROSE_is_still_ignored_above_and_below_the_table():
    """The null control. The masthead sits ABOVE every donor (the derivation's `?a < ?b` finds
    none) and the footer sits below one but does not tile its columns. Neither may be read as a
    row — a guard that admitted them would be reading furniture as data."""
    regions = _p6().regions
    assert regions[0].verdict == "ignored" and _first(regions[0]) == "Communiqué"
    assert regions[-1].verdict == "ignored" and regions[-1].cells == 0


def test_FALSIFICATION_the_membrane_is_the_judge_not_the_offer(monkeypatch):
    """Refuse every donated reading and the lone rows go back to being ignored. If this passed
    with the membrane stubbed out, the offer would be admitting rows on its own say-so."""
    from iladub.etkl import donation
    real = donation.donation_admissible

    def refuse_lone_rows(region, page_number):
        return False if len(region.band.lines) == 1 else real(region, page_number)

    monkeypatch.setattr(donation, "donation_admissible", refuse_lone_rows)
    by_label = {_first(r): r for r in _p6().regions}
    assert by_label["Total"].verdict == "ignored" and by_label["Zurich"].verdict == "ignored"


def test_a_band_of_more_than_one_line_is_never_offered_this_reading():
    from iladub.etkl import donation
    from iladub.etkl.compile import page_bands
    from iladub.etkl.sectiongraph import donor_evidence
    bands = page_bands(BFS, 6)
    ev = donor_evidence(bands, donation.head_line_refusals(BFS, 6, bands))
    multi = [i for i, b in enumerate(bands) if len(b.lines) > 1]
    assert multi and all(donation.offer_single_line(bands, i, ev, 6) is None for i in multi)
