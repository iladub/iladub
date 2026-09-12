"""Grid donation — the derivation half. The query ENUMERATES; donation.offer disposes.

Spec § 3 (the clauses), § 4 (the R203 licence as decision 4).
Plan: docs/superpowers/plans/2026-09-11-grid-donation.md, Task 2
"""
from iladub.etkl.sectiongraph import donor_evidence

from tests.etkl.test_donor_evidence import HEAD, EVERY_MEASURE, _band

RULED = _band((72.0, 200.0, 330.0, 460.0), HEAD)
COARSE = _band((72.0, 265.0, 460.0), (("Subtotal", 80.0, 130.0), ("29.5", 340.0, 370.0)), y=30.0)


def _donors(bands, refusals, idx, ncols):
    from iladub.etkl.donation import donors_for

    return donors_for(donor_evidence(bands, refusals), idx, ncols)


def test_the_relation_fires_on_a_drawn_refused_head_at_the_same_column_count():
    assert _donors([RULED], {0: EVERY_MEASURE}, idx=2, ncols=3) == (0,)


def test_a_later_band_is_never_a_donor():
    """Earlier on the page, by the emitted index — the only ordering the relation uses."""
    assert _donors([RULED], {0: EVERY_MEASURE}, idx=0, ncols=3) == ()


def test_the_wrong_column_count_is_refused_graincorp_p0s_shape():
    """Spec § 3(c): drawn, tiling, and 2 columns against 3. The null control, in CI."""
    assert _donors([RULED, COARSE], {0: EVERY_MEASURE, 1: EVERY_MEASURE}, idx=3, ncols=2) == (1,)
    assert _donors([RULED, COARSE], {0: EVERY_MEASURE, 1: EVERY_MEASURE}, idx=3, ncols=3) == (0,)


def test_an_inferred_interior_boundary_refuses_the_donor():
    """Spec § 3(b), bfs p6 bands 4-9: the vector carries a gutter the compiler inferred.
    Every other clause passes; the drawn clause alone refuses. This is what makes the
    donor unique on bfs p6 rather than merely first."""
    faked = _band((72.0, 200.0, 460.0), HEAD, column_xs=(72.0, 200.0, 291.5, 460.0))
    assert _donors([faked], {0: EVERY_MEASURE}, idx=1, ncols=3) == ()


def test_a_head_the_datagrid_did_not_refuse_is_not_a_donor():
    """Decision 4 / R203: the donor's header is DERIVED. A body-row verdict, any other
    refusal, or no fact at all refuses the donation — the reading must not carry a
    header nobody derived (evidence doc § 2)."""
    assert _donors([RULED], {}, idx=2, ncols=3) == ()
    assert _donors([RULED], {0: "HeterogeneousColumn/col1"}, idx=2, ncols=3) == ()
    assert _donors([RULED], {0: "RowAddressability/no-key"}, idx=2, ncols=3) == ()


def test_two_qualifying_donors_are_both_returned_the_reader_orders_nothing():
    """DECISION E lives in donation.offer, not here: the derivation reports every
    donor and adds no ordinal rule (spec § 3(b) refused one)."""
    twice = _band((72.0, 200.0, 330.0, 460.0), HEAD, y=30.0)
    assert _donors([RULED, twice], {0: EVERY_MEASURE, 1: EVERY_MEASURE}, idx=2, ncols=3) == (0, 1)
