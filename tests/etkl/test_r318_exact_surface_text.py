"""R318 — an escalated region's `iladub:surfaceText` is its exact text, never a layout render.

spec docs/superpowers/specs/2026-10-15-escalation-carries-exact-text-design.md § 3.1, § 4.1-4.2.
Every escalation site wrote `render_ascii(band)` (or, for ROUND_TRIP_FAIL, a render of the
refuted reading): an 80-column canvas on which colliding words overwrite each other and long
lines are clipped. The invariant is `bands.band_text` over the escalated region's lines.

THE SEAM, measured 2026-10-15: `compile_tables` takes only a PDF path and reads its bands through
`page_bands`, so a constructed `Band` cannot reach an escalation. Every case below is a reportlab
fixture compiled end to end. Calling `escalate_region` directly would pin nothing.

The comparison is string equality, never a whitespace-split multiset (spec § 4.2): a ruled band's
Word can hold a whole cell, spaces included.
"""
from __future__ import annotations

import pytest

pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from rdflib import RDFS

from iladub.etkl import compile_tables
from iladub.etkl import roundtrip, tiling
from iladub.etkl.bands import band_text
from iladub.etkl.compile import page_bands
from iladub.etkl.holon import ILADUB
from tests.etkl import fixtures

# One fixture per escalation reason it reaches, measured 2026-10-15 by compiling every
# `*_pdf` builder in tests/etkl/fixtures.py. On all 19 that escalate, the shipped
# surfaceText differed from band_text.
_REACHED = [
    ("wide_cell_table_pdf", "KIND_NOT_SUPPORTED"),
    ("currency_sandwich_pdf", "REGION_TILING_FAILED"),
    ("caption_wrap_report_pdf", "MERGE_AMBIGUOUS"),
    ("duplicate_text_header_pdf", "MATRIX_AMBIGUOUS"),
    ("false_transposed_pdf", "TRANSPOSED"),
    ("record_plus_stub_hier_pdf", "MULTI_TABLE_AMBIGUOUS"),
    ("spanner_with_space_ruled_pdf", "RULE_SEPARATED_INK"),
]


def _escalations(pdf: str, reason: str):
    """(region index, surfaceText) for every escalated region of `reason` on page 0.

    The report's index is the band's index (`#region{idx}`, `#…htable{idx}-rt`), so the band is
    read off `page_bands` independently of the compile.
    """
    rep = compile_tables(pdf)
    g = rep.graph
    cands = {str(s): str(g.value(s, ILADUB.surfaceText))
             for s in g.subjects(RDFS.label, None)
             if str(g.value(s, RDFS.label)) == reason}
    hits = [i for i, r in enumerate(rep.regions) if r.verdict == "escalated" and r.reason == reason]
    assert hits and cands, f"fixture drift: {reason} not reached"
    out = []
    for i in hits:
        mine = [t for uri, t in cands.items()
                if uri.endswith(f"#region{i}") or uri.endswith(f"table{i}-rt")]
        assert len(mine) == 1, (i, sorted(cands))
        out.append((i, mine[0]))
    return out


@pytest.mark.parametrize("builder,reason", _REACHED)
def test_escalated_surface_text_is_band_text(tmp_path, builder, reason):
    p = str(tmp_path / f"{builder}.pdf")
    getattr(fixtures, builder)(p)
    bands = page_bands(p, 0)
    for i, text in _escalations(p, reason):
        assert text == band_text(bands[i]), (i, text, band_text(bands[i]))


def test_a_colliding_render_loses_characters_and_the_surface_text_does_not(tmp_path):
    """Spec § 4.1: the case where the renderer does not merely re-space but DROPS ink. Two words
    land on one column of the 80-character canvas and one overwrites the other."""
    p = str(tmp_path / "sandwich.pdf")
    fixtures.currency_sandwich_pdf(p)
    bands = page_bands(p, 0)
    (i, text), = _escalations(p, "REGION_TILING_FAILED")
    squash = lambda s: "".join(s.split())
    # Precondition: the fixture still collides, or this test pins nothing.
    assert squash(roundtrip.render_ascii(bands[i])) != squash(band_text(bands[i]))
    assert squash(text) == squash(band_text(bands[i]))


def test_row_group_ambiguous_carries_band_text(tmp_path, monkeypatch):
    """ROW_GROUP_AMBIGUOUS is reached only when the tiling oracle refuses (as in
    test_tiling_gate.test_gate_reject_escalates_gracefully)."""
    p = str(tmp_path / "rg.pdf")
    fixtures.row_grouped_table_pdf(p)
    bands = page_bands(p, 0)
    monkeypatch.setattr(tiling, "region_tiles", lambda g: False)
    for i, text in _escalations(p, "ROW_GROUP_AMBIGUOUS"):
        assert text == band_text(bands[i])


def test_round_trip_fail_carries_band_text_not_the_refuted_reading(tmp_path, monkeypatch):
    """holon.assert_hier_region's ROUND_TRIP_FAIL wrote `render_region_ascii(region)`, a render of
    the PARSED reading the round trip had just refuted. No fixture fails the round trip on its
    own (measured 2026-10-15), so the refusal is forced; the candidate is merged from the scratch
    graph into the page graph on this fixture."""
    p = str(tmp_path / "subtotal.pdf")
    fixtures.subtotal_hier_table_pdf(p)
    bands = page_bands(p, 0)
    monkeypatch.setattr(roundtrip, "region_round_trips", lambda region, band: False)
    for i, text in _escalations(p, "ROUND_TRIP_FAIL"):
        assert text == band_text(bands[i])
