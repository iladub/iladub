"""test_grid_donation_relation — R201's cross-band relation, on a synthetic page, in CI.

Spec: docs/superpowers/specs/2026-09-10-the-grid-the-author-drew-design.md § 3. The
relation says a band whose ink tiles the WHOLLY-DRAWN column grid of an earlier band on
the same page, at the same leaf-column count, is a continuation of that band's table.
On the corpus it fires 5 times, all on bfs p6, with a unique donor and no false donor —
but corpus/ is gitignored and those runs are invisible to CI ([[R173]]), so each of the
three clauses is pinned here — two on a page this module draws with a distractor band
that satisfies the other two clauses, and the third on a band whose fields are
constructed, because reportlab could not be made to lay that band out separately.

The first cut of this module had ONE distractor-free fixture, and falsification found
that it pinned only the tiling clause: deleting `same_ncols` and deleting `wholly_drawn`
both left it green (loop record § 3, F1/F3 round 1). The distractors exist because of
that, and deleting any one clause now reddens exactly one test.

Both tests use the shipped derivation `grid._rule_boundaries` and the census's own
helpers, imported rather than copied: a second implementation of the relation would pin
the copy, not the instrument that produced § 3.
"""
import sys
from pathlib import Path

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from reportlab.lib.pagesizes import letter  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

from iladub.etkl.compile import page_bands  # noqa: E402
from iladub.etkl.grid import _rule_boundaries  # noqa: E402
from iladub.etkl.regions import RegionKind, classify  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from grid_agreement_census import straddlers, wholly_drawn  # noqa: E402

PAGE_H = letter[1]
RULES = (72.0, 200.0, 330.0, 460.0)          # the grid the author DRAWS
HEAD = (("Region", 80.0), ("Total", 210.0), ("Share", 340.0))
COARSE = (72.0, 265.0, 460.0)                # drawn, tiles, but TWO columns
ROWS = (("Vaud", "845870", "18.4"), ("Valais", "365844", "70.5"),
        ("Geneve", "524410", "11.0"), ("Berne", "1063533", "20.3"))


def _row_band(c, y, cols, texts, rules=(), height=14.0):
    for x in rules:
        c.line(x, y - 4.0, x, y + height)
    for x, cell in zip(cols, texts):
        c.drawString(x, y, cell)


def _page(path, data_cols, distractor=None):
    """A ruled 3-column header band, an optional distractor band, a gap, then four
    unruled data rows on `data_cols`. Only bands the author ruled carry rules — bfs
    p6's shape, where band 2 is ruled at 9 columns and bands 4-9 are not.

    distractor='coarse'  a WHOLLY DRAWN band that the data tiles, at 2 columns not 3.
    """
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 9)
    y = PAGE_H - 90.0
    _row_band(c, y, [x for _, x in HEAD], [t for t, _ in HEAD], rules=RULES)
    if distractor == "coarse":
        y -= 150.0
        _row_band(c, y, (80.0, 340.0), ("Subtotal", "29.5"), rules=COARSE)
    y -= 150.0                                # a gap wide enough to split the band
    for i, row in enumerate(ROWS):
        for x, cell in zip(data_cols, row):
            c.drawString(x, y - i * 14.0, cell)
    c.save()
    return page_bands(str(path), 0)


def _donor_indices(bands, i):
    """Every earlier band that donates its grid to band i, per spec § 3."""
    reg = classify(bands[i])
    ncols = reg.grid.ncols if reg.grid else None
    out = []
    for j in range(i):
        donor = _rule_boundaries(bands[j])
        if donor is None or len(donor) < 3:
            continue
        if (len(donor) - 1) == ncols and not straddlers(bands[i], donor) \
                and wholly_drawn(bands[j], donor):
            out.append(j)
    return out


def _record_band(bands):
    """The last band the record-table branch reads — the data rows."""
    idx = [i for i, b in enumerate(bands)
           if classify(b).kind is RegionKind.RECORD_TABLE]
    assert idx, "fixture drew no record-table band"
    return idx[-1]


def test_a_headerless_band_takes_the_grid_the_author_drew_above_it(tmp_path):
    """The relation FIRES: the data rows sit inside the header band's drawn columns,
    at the same column count, so the header band is their donor — and it is the only
    one, which is what makes the reading decidable rather than a choice."""
    bands = _page(tmp_path / "donated.pdf", (80.0, 210.0, 340.0))
    i = _record_band(bands)
    donors = _donor_indices(bands, i)
    assert len(donors) == 1, f"expected exactly one donor, got {donors}"
    assert _rule_boundaries(bands[donors[0]]) == list(RULES)


def test_a_band_whose_ink_leaves_the_drawn_columns_gets_no_donor(tmp_path):
    """The relation ABSTAINS rather than guessing. The same page with its data shifted
    so one value crosses a drawn rule: the tiling clause refuses, and no earlier band
    donates. This is the clause that keeps donation evidence-positive — it reads where
    ink IS, never where it is absent."""
    bands = _page(tmp_path / "straddling.pdf", (80.0, 190.0, 340.0))
    i = _record_band(bands)
    assert _donor_indices(bands, i) == []


def test_a_drawn_band_at_the_wrong_column_count_is_not_a_donor(tmp_path):
    """graincorp p0's shape, in CI (spec § 3(c)): a band the author ruled, which the
    data tiles with zero straddlers, and which reads TWO columns where the data reads
    three. Accepting it would carry a 2-column header onto a 3-column table."""
    bands = _page(tmp_path / "coarse.pdf", (80.0, 210.0, 340.0), distractor="coarse")
    i = _record_band(bands)
    donors = _donor_indices(bands, i)
    assert [_rule_boundaries(bands[j]) for j in donors] == [list(RULES)]


def test_a_band_whose_interior_boundaries_are_inferred_is_not_a_donor(tmp_path):
    """bfs p6's bands 4-9, in CI (spec § 3(b)). Those bands carry a `column_xs` whose
    interior boundaries this compiler CONFIRMED out of the whitespace — `198.47` where
    the author drew `187.29` — and `_rule_boundaries` prefers that vector over the marks.
    The state is constructed rather than drawn: reportlab lays a partially-ruled
    multi-row band out in the SAME band as the fully-ruled one (measured while building
    this fixture), so the page cannot express it, and the clause under test is about the
    band's fields, not its ink.

    Every other clause passes here — the vector is returned, the data tiles it, the
    column count matches — and only `wholly_drawn` refuses. That is what makes the donor
    unique on bfs p6 rather than merely first."""
    from dataclasses import replace

    bands = _page(tmp_path / "donated.pdf", (80.0, 210.0, 340.0))
    i = _record_band(bands)
    inferred = (72.0, 200.0, 291.5, 460.0)          # 291.5 is a gutter, not a mark
    faked = replace(bands[_donor_indices(bands, i)[0]], column_xs=inferred)

    assert _rule_boundaries(faked) == list(inferred)
    assert not straddlers(bands[i], list(inferred))
    assert len(inferred) - 1 == classify(bands[i]).grid.ncols
    assert _donor_indices([faked, bands[i]], 1) == []
