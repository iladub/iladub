"""R302 — the document driver's `grid_idx` is pinned, and so is the coupling that keeps it safe.

`document.compile_document`'s adoption pass reads the first adopted grid at
`grid_idx = len(pages[p].regions)`, pass 1's REGION count. The refuted form, spec § 2.5's "the
re-compile's band count" (`len(band_lists[p])`), differs only on a page whose pass 1 APPENDED a
`datagrid_fallback` region, and then the band count lands on that region instead of the grid.

WHY NO PAGE ADOPTS OVER A FALLBACK REGION TODAY, measured rather than argued. The fallback opens
only at `escalated_total == 0` and adoption only at `escalated_total > 0` (`compile_tables`), so
within one compile the sole bridge is R301's producer guard escalating the appended region. The
adoption site then runs the SAME select (`ruleguard.rule_separated_cells`, read from
`tab:RuleSeparatedInkShape`, a negation-free BGP) over a graph rebuilt from the SAME grids by the
SAME emitter, so the cell that fired fires again and adoption is `guard_refused`. The handoff's
proposition that a page adopting over a fallback region "can be built with the existing synthetic
helpers" is REFUTED on the one shape that reaches the bridge (`isolated_rows_grid_pdf(ruled_cell=
True)`): test 1.

So `grid_idx`'s two forms are indistinguishable today ONLY BECAUSE of the adoption-site guard.
Test 1 pins that coupling, and test 2 forces the state it prevents (silencing the adoption site's
select ONLY, never the pre-adoption guard) to pin the index itself. Both are synthetic and run in
CI, unlike `tests/test_r301_fed_h41.py`, whose p7 is the same shape on a gitignored document.
"""
import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from iladub.etkl import ruleguard  # noqa: E402
from iladub.etkl.compile import compile_tables  # noqa: E402
from tests.etkl.fixtures import isolated_rows_grid_pdf  # noqa: E402


@pytest.fixture(scope="module")
def ruled_fallback_pdf(tmp_path_factory):
    p = tmp_path_factory.mktemp("r302") / "ruled-fallback.pdf"
    meta = isolated_rows_grid_pdf(str(p), ruled_cell=True)
    return str(p), meta


def test_a_fallback_the_guard_escalated_is_refused_adoption(ruled_fallback_pdf):
    """The bridge exists and the adoption site closes it. Falsified by making the adoption site's
    outcome `"adopted"` unconditionally (`compile.py`, `adoption = "guard_refused" if ... else
    "adopted"`): the page then adopts and this fails on the outcome."""
    pdf, meta = ruled_fallback_pdf
    off = compile_tables(pdf, 0, validate_shapes=False, datagrid_adopt=False)
    fallback = off.regions[meta["n_bands"]]
    # Precondition: pass 1 appended a fallback region and the guard escalated it — without this
    # the test would pass on a page that never reached the bridge.
    assert len(off.regions) == meta["n_bands"] + 1
    assert (fallback.verdict, fallback.reason) == ("escalated", ruleguard._REASON)
    assert (off.asserted, off.escalated) == (0, meta["n_cells"])

    on = compile_tables(pdf, 0, validate_shapes=False, datagrid_adopt=True)
    assert on.adoption == "guard_refused"
    assert len(on.regions) == len(off.regions)


def test_grid_idx_skips_the_appended_fallback_region(ruled_fallback_pdf, monkeypatch):
    """With ONLY the adoption site's select silenced, the page adopts over its fallback region:
    the grid lands at `n_bands + 1` and supersedes the fallback at `n_bands`. Falsified by
    `grid_idx = len(band_lists[p])`: the driver reads the fallback region as the grid, notes
    "adoption refused — no data grid region on the re-compile", and the page scores 0.0
    (measured 2026-10-09)."""
    from iladub.etkl.document import compile_document

    pdf, meta = ruled_fallback_pdf
    real_select, real_guard = ruleguard.rule_separated_cells, ruleguard.guard
    inside_guard = []

    def guard(*a, **k):
        inside_guard.append(True)
        try:
            return real_guard(*a, **k)
        finally:
            inside_guard.pop()

    calls = {"guard": 0, "adoption_site": 0}

    def select(g):
        if inside_guard:
            calls["guard"] += 1
            return real_select(g)
        calls["adoption_site"] += 1
        return frozenset()

    # `compile_tables` imports `guard` function-locally and calls `_rg.rule_separated_cells`
    # through the module, so both patches are seen at every call.
    monkeypatch.setattr(ruleguard, "guard", guard)
    monkeypatch.setattr(ruleguard, "rule_separated_cells", select)
    doc = compile_document(pdf, validate_shapes=False)

    assert calls["guard"] > 0 and calls["adoption_site"] > 0
    page = doc.pages[0]
    n = meta["n_bands"]
    assert not [x for x in doc.notes if x.startswith("page 0: adoption refused")], doc.notes
    assert len(page.regions) == n + 2
    assert (page.regions[n].verdict, page.regions[n].reason) == ("superseded", ruleguard._REASON)
    grid = page.regions[n + 1]
    assert (grid.verdict, grid.cells, grid.supersedes) == ("asserted", meta["n_cells"], (n,))
