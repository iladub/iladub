"""Grid donation — the reading and the disposal. The derivation proposed; this refuses or accepts.

Plan: docs/superpowers/plans/2026-09-11-grid-donation.md, Task 3 (DECISIONS A, D, E)
"""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from reportlab.lib.pagesizes import letter  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

from iladub.etkl.compile import page_bands  # noqa: E402
from iladub.etkl.regions import RegionKind, classify  # noqa: E402
from iladub.etkl.sectiongraph import donor_evidence  # noqa: E402

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
BFS = os.path.join(CORPUS, "gov-stats", "bfs-population-bilan-2023.pdf")
corpus_only = pytest.mark.skipif(not os.path.exists(BFS), reason="corpus not fetched")

EVERY_MEASURE = "HeterogeneousColumn/every-measure"
PAGE_H = letter[1]
RULES = (72.0, 200.0, 330.0, 460.0)
HEAD = (("Region", 80.0), ("Total", 210.0), ("Share", 340.0))
ROWS = (("Vaud", "845870", "18.4"), ("Valais", "365844", "70.5"),
        ("Geneve", "524410", "11.0"), ("Berne", "1063533", "20.3"))


def _page(path, data_cols, head_twice=False):
    """test_grid_donation_relation's page: a ruled 3-column head band, a gap, four unruled
    data rows on `data_cols`. `head_twice` draws the head band a second time — two wholly
    drawn donors at the same column count, the page DECISION E refuses."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 9)
    y = PAGE_H - 90.0
    for _ in range(2 if head_twice else 1):
        for x in RULES:
            c.line(x, y - 4.0, x, y + 14.0)
        for (t, x) in HEAD:
            c.drawString(x, y, t)
        y -= 150.0
    for i, row in enumerate(ROWS):
        for x, cell in zip(data_cols, row):
            c.drawString(x, y - i * 14.0, cell)
    c.save()
    return page_bands(str(path), 0)


def _record_band(bands):
    idx = [i for i, b in enumerate(bands) if classify(b).kind is RegionKind.RECORD_TABLE]
    assert idx, "fixture drew no record-table band"
    return idx[-1]


def _head_bands(bands):
    """Every band the head was drawn into — the donors a refusal map must name."""
    return [i for i, b in enumerate(bands)
            if [w.text for w in b.lines[0].words] == ["Region", "Total", "Share"]]


def test_the_donated_region_takes_the_donors_grid_and_labels_and_shifts_the_rows(tmp_path):
    """DECISION D, on the page: the continuation keeps its band, takes the donor's grid,
    reads the donor's line 0 as its row 0, and its own line 0 becomes row 1."""
    from iladub.etkl.donation import donated_region
    from iladub.etkl.grid import infer_leaf_grid

    bands = _page(tmp_path / "donated.pdf", (80.0, 210.0, 340.0))
    i, d = _record_band(bands), _head_bands(bands)[0]
    reg = donated_region(bands, d, i)
    assert reg.band is bands[i]
    assert reg.grid == infer_leaf_grid(bands[d])
    assert reg.grid.boundaries == RULES
    assert [c.text for c in sorted(reg.cells, key=lambda c: c.col) if c.row == 0] == ["Region", "Total", "Share"]
    assert [c.text for c in sorted(reg.cells, key=lambda c: c.col) if c.row == 1] == list(ROWS[0])
    assert max(c.row for c in reg.cells) == len(ROWS)
    assert reg.reason == "donated"


def test_a_straddling_page_is_refused_at_the_disposal_not_at_the_derivation(tmp_path):
    """DECISION A. The same page with one value shifted across a drawn rule: the
    derivation still names the donor (drawn, refused head, same count — every fact it
    reads is present), and the disposal refuses, because the straddling word's cell does
    not round-trip. The tiling clause lives HERE now, in the shipped per-cell form."""
    from iladub.etkl.donation import donated_region, donation_admissible, donors_for

    bands = _page(tmp_path / "straddling.pdf", (80.0, 190.0, 340.0))
    i, d = _record_band(bands), _head_bands(bands)[0]
    ev = donor_evidence(bands, {d: EVERY_MEASURE})
    assert donors_for(ev, i, classify(bands[i]).grid.ncols) == (d,)
    assert donation_admissible(donated_region(bands, d, i), 0) is False


def test_offer_accepts_a_unique_donor_and_refuses_two(tmp_path):
    """DECISION E: two wholly drawn donors at the same column count is a page this
    relation cannot read. No ordinal rule; the band compiles as it does today."""
    from iladub.etkl.donation import offer

    one = _page(tmp_path / "one.pdf", (80.0, 210.0, 340.0))
    i = _record_band(one)
    d = _head_bands(one)
    assert len(d) == 1
    got = offer(one, i, classify(one[i]), donor_evidence(one, {d[0]: EVERY_MEASURE}), 0)
    assert got is not None and got.donor_index == d[0]

    two = _page(tmp_path / "two.pdf", (80.0, 210.0, 340.0), head_twice=True)
    j = _record_band(two)
    dd = _head_bands(two)
    assert len(dd) == 2, f"fixture must draw two donor bands, got {dd}"
    assert offer(two, j, classify(two[j]), donor_evidence(two, {k: EVERY_MEASURE for k in dd}), 0) is None


@corpus_only
def test_bfs_p6_the_refusal_map_names_band_2_and_no_other_band_every_measure():
    """Evidence doc § 1 row 5, through the shipped function: band 2's line 0 is the one
    head the page datagrid refuses every-measure."""
    from iladub.etkl.donation import head_line_refusals

    bands = page_bands(BFS, 6)
    got = head_line_refusals(BFS, 6, bands)
    assert got.get(2) == EVERY_MEASURE, got
    assert [k for k, v in got.items() if v == EVERY_MEASURE] == [2], got


@corpus_only
def test_bfs_p6_the_five_donations_are_admissible_with_the_spikes_entry_counts():
    """The oracle numbers of handoff 2026-09-10-the-donated-reading-tiles § 2, through the
    plan's construction rather than the spike's (DECISION D)."""
    from iladub.etkl.donation import donated_region, donation_admissible

    bands = page_bands(BFS, 6)
    for i, n in {4: 36, 5: 54, 6: 36, 8: 72, 9: 63}.items():
        reg = donated_region(bands, 2, i)
        assert donation_admissible(reg, 6), i
        assert len([c for c in reg.cells if c.row > 0]) == n, i
