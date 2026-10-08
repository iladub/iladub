"""R301 Task 1 — an appended (fallback data-grid) region carries its lines and its text.

spec 2026-10-08-r301-producer-guard-design.md § 2.4 (text, ruling d). The producer guard
(Task 3) escalates a table whose cell an author's rule separates; its subject is an
APPENDED region (`compile.py:1900`'s datagrid fallback), and the guard needs that region's
`ascii` as the text to escalate and its `line_indices` to join it (Task 2's `build_ledger`)
to the page lines it actually read. Neither existed before this task: the fallback report
was built with `ascii=""` (`compile.py:1922`, pre-change) and `RegionReport` carried no
`line_indices` field at all.

Fixture: `isolated_rows_grid_pdf` (`tests/etkl/fixtures.py:2251`) — [[R228]]'s synthetic page
that reaches `compile.py:1900`'s "NOTHING AT ALL" gate with no corpus dependency. MEASURED
2026-09-14 in that fixture's own docstring: 9 bands (10 lines + 8x1 line), all ignored, so
`asserted_total == 0 and escalated_total == 0`; `derive_data_grid` -> `rows=8 cols=2
universe=UniformGrid`; `datagrid_fallback=True` -> 10 regions = 9 bands + 1 appended
`RECORD_TABLE asserted cells=16` region naming a `table_uri`. Re-confirmed below by the
`off`/`on` asserted-count assertions already proven in
`test_datagrid.py::test_fallback_supplies_the_reading_the_bands_did_not` (same fixture).
"""
from __future__ import annotations

from iladub.etkl import roundtrip
from iladub.etkl.bands import Band
from iladub.etkl.compile import compile_tables
from iladub.etkl.datagrid import derive_data_grids
from iladub.etkl.geometry import extract_words, text_lines
from tests.etkl.fixtures import isolated_rows_grid_pdf


def _appended_and_band_reports(p):
    """Compile the fixture with the fallback on; split its regions into the ONE appended
    (fallback) report (identified by `table_uri is not None` — only the fallback/adoption
    branches ever set it, and this fixture's bands are all `ignored` so adoption never
    triggers: escalated_total stays 0) and the rest (the page's bands)."""
    on = compile_tables(str(p), 0, validate_shapes=False, datagrid_fallback=True)
    appended = [r for r in on.regions if r.table_uri is not None]
    bands = [r for r in on.regions if r.table_uri is None]
    assert len(appended) == 1, (
        "fixture drift: expected exactly one appended fallback region, got %d"
        % len(appended))
    return appended[0], bands, on


def test_appended_region_carries_its_lines_and_its_text(tmp_path):
    p = tmp_path / "isolated_rows.pdf"
    isolated_rows_grid_pdf(str(p))

    off = compile_tables(str(p), 0, validate_shapes=False, datagrid_fallback=False)
    assert off.asserted == 0 and off.escalated == 0, (
        "fixture drift: the gate is NOTHING-AT-ALL; got %d asserted / %d escalated"
        % (off.asserted, off.escalated))

    appended, band_reports, on = _appended_and_band_reports(p)
    assert sum(r.cells for r in on.regions) == 16, (
        "fixture drift: expected 16 cells on the fallback reading, got %d"
        % sum(r.cells for r in on.regions))

    lines = [ln for ln in text_lines(extract_words(str(p), 0)) if ln.words]
    lines.sort(key=lambda ln: ln.top)

    grids = derive_data_grids(str(p), 0)
    assert len(grids) == 1, "fixture drift: expected exactly one derived grid, got %d" % len(grids)
    grid = grids[0]

    # The appended report's line_indices IS the derived grid's row indices into the page's
    # _lines — the join Task 2's build_ledger needs.
    assert appended.line_indices == grid.rows

    # Its ascii is render_ascii over exactly those lines (render_ascii reads only
    # band.lines — roundtrip.py:137-150 — so top/bottom are immaterial to this comparison).
    expected_ascii = roundtrip.render_ascii(
        Band(lines=tuple(lines[i] for i in grid.rows), top=0.0, bottom=0.0))
    assert appended.ascii != ""
    assert appended.ascii == expected_ascii

    # Every band report (never an appended one) carries the untouched default.
    for r in band_reports:
        assert r.line_indices == ()
