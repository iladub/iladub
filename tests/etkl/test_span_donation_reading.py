"""Span donation — the relation and the reading. The derivation proposed; this disposes.

Spec: docs/superpowers/specs/2026-09-11-the-span-the-author-drew-design.md § 3.1
Plan: docs/superpowers/plans/2026-09-13-the-span-the-author-drew.md, Task 2 (DECISIONS C, D)

THE RELATION (DECISION D): an earlier band donates a SPANNING header to a band the
record-table branch reads iff (a) it is earlier, (b) its leaf-boundary vector is wholly drawn,
(c) the page datagrid refused its line 0 as a header (the R203 licence), (d) its vector is a
STRICT subset of the recipient's, and (e) exactly one donor qualifies.

CLAUSE (d) REPLACES GRID DONATION'S COUNT CLAUSE; IT DOES NOT DELETE IT. Equal-count donation
stays `donation.offer`'s, unchanged and still refusing graincorp -- which it is right to do,
because a 9-column header is not a 16-column one. The two relations are siblings over the SAME
evidence graph: `donor_evidence` already emits a node for every band that owns a vector, so the
recipient's own boundaries are in the graph beside the donor's and (d) is a join, not a new
emitter (MEASURED: graincorp p0 emits band 2 with 10 boundaries and band 3 with 17).

THE READING IS BUILT FROM THE DERIVATION'S ANSWER, NOT FROM `group_wrapped`, and that is a
correction to the plan measured before the call was written (plan rule 3; reported in the task
report). The plan says the donor's header row "comes from group_wrapped(donor_band,
recipient_grid)". MEASURED: `group_wrapped` groups the donor's words by the RECIPIENT's
columns, which splits the single label 'Port Kembla' into two cells at two recipient columns --
and a tree built from that emits two header nodes over one interval, which is exactly the
reading `tests/tab-span-doubled-label-leak.ttl` exists to refuse. The labels are grouped by the
donor's own INTERVALS, i.e. by what span-covers.rq placed where, so the decision stays in the
query and the join stays in Python.
"""
import os

import pytest
from rdflib import Graph, URIRef

from iladub.etkl.bands import Band
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.geometry import Line, Rule, Word
from iladub.etkl.sectiongraph import donor_evidence
from iladub.etkl.tiling import region_tiles

EVERY_MEASURE = "HeterogeneousColumn/every-measure"

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
GRAINCORP = os.path.join(CORPUS, "ag-trade", "graincorp-capacity-2026-08-04.pdf")
BFS = os.path.join(CORPUS, "gov-stats", "bfs-population-bilan-2023.pdf")
corpus_only = pytest.mark.skipif(not os.path.exists(GRAINCORP), reason="corpus not fetched")
bfs_only = pytest.mark.skipif(not os.path.exists(BFS), reason="corpus not fetched")

# MEASURED: the recipient reads 6 leaf columns on these 7 drawn boundaries; the donor's 4 are
# a STRICT subset, and each donor interval contains exactly two whole recipient columns.
R_XS = (72.0, 120.0, 168.0, 216.0, 264.0, 312.0, 360.0)
D_XS = (72.0, 168.0, 264.0, 360.0)


def _band(xs, rows, y0=0.0, pitch=14.0, column_xs=()):
    lines = []
    for r, words in enumerate(rows):
        y = y0 + r * pitch
        ws = tuple(Word(text=t, x0=a, x1=b, top=y, bottom=y + 10.0) for t, a, b in words)
        lines.append(Line(words=ws, top=y, bottom=y + 10.0))
    return Band(lines=tuple(lines), top=lines[0].top, bottom=lines[-1].bottom,
                rules=tuple(Rule(x=x, top=y0, bottom=y0 + pitch * len(rows)) for x in xs),
                column_xs=column_xs)


def _recipient(xs=R_XS):
    return _band(xs, tuple(
        tuple((f"{p}{i}", xs[i] + 4.0, xs[i] + 40.0) for i in range(len(xs) - 1))
        for p in "abc"), y0=100.0)


def _donor(xs=D_XS, words=None):
    return _band(xs, (words or (("Mackay", 100.0, 140.0), ("Gladstone", 190.0, 240.0),
                                ("Portland", 290.0, 334.0)),))


def _page(donor=None, recipient=None, licensed=True):
    """A two-band page: the donor at index 0, the recipient at index 1."""
    bands = [donor or _donor(), recipient or _recipient()]
    ev = donor_evidence(bands, {0: EVERY_MEASURE} if licensed else {})
    return bands, ev


def _span_donors(bands, ev, idx):
    from iladub.etkl.donation import span_donors_for
    return span_donors_for(ev, idx)


# --- the relation, clause by clause -------------------------------------------------------

def test_the_relation_names_the_spanning_donor_where_grid_donation_names_none():
    """The narrowing, in one assertion: the same page, the same evidence graph, two sibling
    relations. Grid donation refuses -- a 3-column header over 6 columns is not an equal-count
    donation, and it is right to refuse. The span relation admits on clause (d) instead."""
    from iladub.etkl.donation import donors_for

    bands, ev = _page()
    assert _span_donors(bands, ev, 1) == (0,)
    assert donors_for(ev, 1, recover_leaf_grid(bands[1]).ncols) == ()


def test_a_donor_boundary_the_recipient_lacks_is_refused_by_clause_d():
    """S1: a licensed, wholly drawn donor carrying one drawn x (200.0) the recipient has not.
    Its vector is no longer a subset, so it heads nothing. This is the clause with no corpus
    negative, which is why it is drawn here."""
    donor = _donor((72.0, 168.0, 200.0, 264.0, 360.0),
                   (("Mackay", 100.0, 140.0), ("Gl", 172.0, 190.0),
                    ("Gladstone", 212.0, 250.0), ("Portland", 290.0, 334.0)))
    bands, ev = _page(donor=donor)
    assert _span_donors(bands, ev, 1) == ()


def test_an_equal_vector_is_not_this_arms_donation():
    """S2: drawn(D) == drawn(R). NOT a strict subset, so this arm must not claim it -- it
    stays grid donation's, and grid donation still admits it. The subset must be PROPER or the
    two relations would both fire on one page."""
    from iladub.etkl.donation import donors_for

    donor = _donor(R_XS, tuple((f"h{i}", R_XS[i] + 4.0, R_XS[i] + 40.0) for i in range(6)))
    bands, ev = _page(donor=donor)
    assert _span_donors(bands, ev, 1) == ()
    assert donors_for(ev, 1, recover_leaf_grid(bands[1]).ncols) == (0,)


def test_an_unlicensed_donor_is_refused_by_clause_c():
    """R203: the donor's header is DERIVED, never assumed. No refusal record, or any other
    refusal, and the donation is refused -- the clause that keeps bfs p6's seven strict-subset
    pairs out of this relation."""
    bands, ev = _page(licensed=False)
    assert _span_donors(bands, ev, 1) == ()

    _, ev2 = _page()
    bands2 = [_donor(), _recipient()]
    other = donor_evidence(bands2, {0: "RowAddressability/no-key"})
    assert _span_donors(bands2, other, 1) == ()


def test_a_later_band_is_never_a_donor():
    """Clause (a), by the emitted index -- the only ordering this relation uses."""
    bands, ev = _page()
    assert _span_donors(bands, ev, 0) == ()


def test_two_qualifying_donors_are_refused_and_nothing_orders_them():
    """DECISION E, reused verbatim from grid donation: two qualifying donors is a page this
    relation cannot read. No ordinal rule, no 'nearest' -- the band compiles as it does today."""
    from iladub.etkl.donation import span_offer

    bands = [_donor(), _donor(), _recipient()]
    ev = donor_evidence(bands, {0: EVERY_MEASURE, 1: EVERY_MEASURE})
    assert _span_donors(bands, ev, 2) == (0, 1)
    assert span_offer(bands, 2, ev, 0) is None


# --- the reading, and its disposal --------------------------------------------------------

def test_the_reading_is_childless_level_zero_nodes_that_tile():
    """DECISION C: a HierRegion with the donor's tree and the recipient's rows, body_line 0.
    Every node is level 0 with no parent and covers MORE THAN ONE column, and the disposal is
    the shipped membrane -- no new shape."""
    from iladub.etkl.donation import span_offer

    bands, ev = _page()
    got = span_offer(bands, 1, ev, 0)
    assert got is not None and got.donor_index == 0

    tree = got.region.tree
    assert [n.level for n in tree] == [0, 0, 0]
    assert all(n.parent is None for n in tree)
    assert [n.covers for n in tree] == [(0, 1), (2, 3), (4, 5)]
    assert [n.text for n in tree] == ["Mackay", "Gladstone", "Portland"]
    assert got.region.body_line == 0
    assert got.region.grid.ncols == 6


def test_two_words_of_one_interval_become_ONE_label():
    """The correction measured in the module docstring. 'Port' and 'Kembla' sit in one drawn
    interval; grouping by the RECIPIENT's columns would put them in two and emit two nodes over
    the same run -- the reading tests/tab-span-doubled-label-leak.ttl refuses. One interval, one
    label, its text joined in x order."""
    from iladub.etkl.donation import span_offer

    donor = _donor(D_XS, (("Mackay", 100.0, 140.0), ("Port", 186.0, 212.0),
                          ("Kembla", 216.0, 248.0), ("Portland", 290.0, 334.0)))
    bands, ev = _page(donor=donor)
    got = span_offer(bands, 1, ev, 0)
    assert got is not None
    assert [n.text for n in got.region.tree] == ["Mackay", "Port Kembla", "Portland"]
    assert [n.covers for n in got.region.tree] == [(0, 1), (2, 3), (4, 5)]


def test_the_reading_passes_the_shipped_membrane_and_mints_no_new_shape():
    """The disposal is `region_tiles`, unchanged (DECISION C). Asserted on the graph the
    reading actually produces, not on a hand-written example."""
    from iladub.etkl.donation import span_offer
    from iladub.etkl.holon import assert_hier_region

    bands, ev = _page()
    got = span_offer(bands, 1, ev, 0)
    g = Graph()
    assert_hier_region(g, got.region, bands[1], URIRef("urn:x#t"), URIRef("urn:x"), 0)
    assert region_tiles(g)


# --- the corpus ---------------------------------------------------------------------------

@corpus_only
def test_graincorp_p0_reads_nine_spanning_labels_over_sixteen_columns():
    """The document this relation was built for. Nine labels, the measured partition
    1,1,2,2,2,2,2,2,2, and the nine the author printed -- the ports among them."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.donation import head_line_refusals, span_offer

    bands = page_bands(GRAINCORP, 0)
    ev = donor_evidence(bands, head_line_refusals(GRAINCORP, 0, bands))
    got = span_offer(bands, 3, ev, 0)
    assert got is not None and got.donor_index == 2

    tree = got.region.tree
    assert [len(n.covers) for n in tree] == [1, 1, 2, 2, 2, 2, 2, 2, 2]
    assert [n.text for n in tree] == [
        "Year", "Elevation Period", "Mackay", "Gladstone", "Fisherman Islands",
        "Carrington", "Port Kembla", "Geelong", "Portland"]
    assert all(n.level == 0 and n.parent is None for n in tree)


@corpus_only
def test_graincorp_p0_moves_no_ink():
    """THE INVARIANT (plan, stated once): span donation changes which columns the author's
    labels head. It moves no ink. 406 is the figure tests/etkl/test_run_merge_seam.py already
    pins for ("graincorp-capacity-2026-08-04", 0)."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.donation import head_line_refusals, span_offer
    from iladub.etkl.holon import assert_hier_region

    bands = page_bands(GRAINCORP, 0)
    ev = donor_evidence(bands, head_line_refusals(GRAINCORP, 0, bands))
    got = span_offer(bands, 3, ev, 0)
    g = Graph()
    asserted = assert_hier_region(g, got.region, bands[3], URIRef("urn:x#t"),
                                  URIRef("urn:x"), 0)
    assert asserted == 406, asserted
    assert region_tiles(g)


@bfs_only
def test_bfs_p6_seven_strict_subset_pairs_stay_refused():
    """THE CORPUS NEGATIVE THAT MUST NOT MOVE. bfs p6 carries seven strict-subset pairs --
    (3,4), (3,5), (3,6), (3,8), (3,9), (7,8), (7,9) -- and every one is refused, because only
    band 2 carries the R203 licence and bands 3 and 7 do not. Clause (c) is what holds them
    out; delete it and this page starts donating."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.donation import head_line_refusals, span_offer

    bands = page_bands(BFS, 6)
    ev = donor_evidence(bands, head_line_refusals(BFS, 6, bands))
    for idx in range(len(bands)):
        assert _span_donors(bands, ev, idx) == (), idx
        assert span_offer(bands, idx, ev, 6) is None, idx
