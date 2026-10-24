"""R334+R336 at the adoption site (spec 2026-10-24 §3.4, §3.3 "Carriage").

Order at `compile_tables`' adoption block: read the boxhead (spanners disposed), then ask the caption
worker, then a grid's read lines are its rows + `carried_lines` (leaves and surviving spanners) + its
disposed caption page lines. The ledger books that union; the rebuild emits `tab:RegionCaption`s
beside the boxhead.

Synthetic, no corpus: the escalating currency-marker table of `tests/etkl/fixtures.py`, drawn with a
title, a unit line and one spanner above its column-label line. NO LIVE CALL — both readers are
fakes installed over the modules' `default_reader`, which the adoption site resolves at call time.
"""
from __future__ import annotations

import pytest
from rdflib import Literal, RDF

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from iladub.etkl import boxhead, caption  # noqa: E402
from iladub.etkl.boxhead import BoxheadReading, FakeBoxheadReader  # noqa: E402
from iladub.etkl.caption import CaptionReading, FakeCaptionReader  # noqa: E402
from iladub.etkl.compile import compile_tables  # noqa: E402
from iladub.etkl.holon import TAB  # noqa: E402

TITLE = "Condensed Revenue Summary"
UNIT = "(in thousands of dollars)"


def _titled_pdf(path: str) -> None:
    """`currency_marker_escalating_pdf`'s rows and x-positions verbatim, with a title, a unit line
    and a spanner `Fiscal year` over the two amount columns, at the table's own 14pt pitch."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from tests.etkl.fixtures import PAGE_H
    c = canvas.Canvas(path, pagesize=letter)
    c.setFont("Courier", 9)
    rows = [
        ("Item",     "",  "Amount",  "",  "Amount"),
        ("Products", "$", "78,678",  "$", "272,629"),
        ("Services", "",  "30,739",  "",  "91,728"),
        ("Other",    "",  "11,729",  "",  "34,035"),
        ("Overall",  "$", "121,146", "$", "398,392"),
    ]
    xs = [72.0, 220.0, 260.0, 380.0, 420.0]
    y0 = PAGE_H - 100.0
    c.drawString(72.0, y0 + 42.0, TITLE)
    c.drawString(72.0, y0 + 28.0, UNIT)
    c.drawString(300.0, y0 + 14.0, "Fiscal year")
    for i, row in enumerate(rows):
        for x, t in zip(xs, row):
            if t:
                c.drawString(x, y0 - i * 14.0, t)
    c.save()


# Block positions: 0 title (3 words), 1 unit (4 words), 2 spanner (2 words), 3 leaves (3 words).
BOXHEAD = BoxheadReading(
    leaf_labels=((0, ((3, 0),)), (1, ((3, 1),)), (2, ((3, 2),))),
    spanning_labels=((1, 2, ((2, 0), (2, 1))),),
    other_words=((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (1, 3)),
    cols_seen=3)


@pytest.fixture
def pdf(tmp_path):
    p = tmp_path / "titled.pdf"
    _titled_pdf(str(p))
    return str(p)


def _compile(pdf, monkeypatch, caption_reading):
    monkeypatch.delenv("BAML_LIVE", raising=False)
    monkeypatch.setattr(boxhead, "default_reader", lambda: FakeBoxheadReader(BOXHEAD))
    monkeypatch.setattr(caption, "default_reader", lambda: FakeCaptionReader(caption_reading))
    monkeypatch.setattr(caption, "_render_crop", lambda pdf_path, page, region: b"png")
    monkeypatch.setattr("iladub.etkl.unshownink.render_region",
                        lambda pdf_path, page, region: b"png")
    return compile_tables(pdf, 0, validate_shapes=True, datagrid_adopt=True)


def _captions(g):
    return {str(t) for cap in g.subjects(RDF.type, TAB.RegionCaption)
            for t in g.objects(cap, TAB.captionText)}


def test_disposed_captions_are_carried_under_the_grid_and_booked_by_the_ledger(pdf, monkeypatch):
    rep = _compile(pdf, monkeypatch, CaptionReading(caption_lines=(0, 1)))
    assert rep.adoption == "adopted"
    g = rep.graph
    grids = set(g.subjects(TAB.hasCaption, None))
    assert len(grids) == 1
    (grid,) = grids
    assert {str(t) for cap in g.objects(grid, TAB.hasCaption)
            for t in g.objects(cap, TAB.captionText)} == {TITLE, UNIT}
    assert not any(g.subjects(RDF.type, TAB.SectionCaption))
    # The ledger books the caption lines: every header word is read, so nothing on the page is
    # left escalated — the title's 3 and the unit's 4 tokens are asserted, not residue.
    assert rep.escalated == 0
    # The spanner is carried at the site too (R334): one more HeaderNode than the three leaves.
    assert len(set(g.subjects(RDF.type, TAB.HeaderNode))) == 4


def test_no_claim_is_the_identity_for_captions(pdf, monkeypatch):
    """A refusing caption reader is NO CLAIM: no caption node, and the title and unit lines stay
    escalated (3 + 4 tokens) — the page a compile with no caption recording produces."""
    rep = _compile(pdf, monkeypatch, CaptionReading(refuses=True))
    assert rep.adoption == "adopted"
    assert not _captions(rep.graph)
    assert rep.escalated == 7


def test_with_no_caption_recording_the_default_reader_misses_and_carries_nothing(
        pdf, monkeypatch, tmp_path):
    """The shipped reader, unpatched, over an EMPTY `readings/caption/`: a miss is NO CLAIM, so a
    compile with no caption recording is the identity for captions."""
    monkeypatch.delenv("BAML_LIVE", raising=False)
    monkeypatch.setattr(caption, "READINGS_DIR", tmp_path / "caption-empty")
    monkeypatch.setattr(boxhead, "default_reader", lambda: FakeBoxheadReader(BOXHEAD))
    rep = compile_tables(pdf, 0, validate_shapes=True, datagrid_adopt=True)
    assert rep.adoption == "adopted"
    assert not _captions(rep.graph)
    assert rep.escalated == 7
