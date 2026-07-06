import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from collections import Counter

from tests.etkl.fixtures import pivoted_table_pdf, verbose_header_table_pdf
from iladub.etkl import extract_words, text_lines, detect_bands, infer_leaf_grid
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.bands import Band


def _piv_band(tmp_path):
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    return detect_bands(text_lines(extract_words(str(p))))[-1]


def test_naive_grid_collapses(tmp_path):
    band = _piv_band(tmp_path)
    assert infer_leaf_grid(band).ncols < 7   # merged parent collapses it


def test_recovered_grid_is_seven(tmp_path):
    band = _piv_band(tmp_path)
    assert recover_leaf_grid(band).ncols == 7   # true leaf columns


def test_recovers_grid_under_verbose_header(tmp_path):
    """Verbose spanning title has MORE word tokens than data rows.

    The old max-by-tokens code picked the title row as the 'tiling' set
    (token count 6 vs 1-3 for the body rows), producing ncols == 1 instead of 3.
    The suffix-max fix recovers the true 3-column grid.
    """
    p = tmp_path / "verbose.pdf"
    verbose_header_table_pdf(str(p))
    bands = detect_bands(text_lines(extract_words(str(p))))
    # The table may be one band or the title may band away; take the last band
    # that contains the leaf label + data rows (the one with the most lines).
    band = max(bands, key=lambda b: len(b.lines))

    # Demonstrate that the OLD max-by-tokens logic would have returned the wrong count.
    counts = [len(ln.words) for ln in band.lines]
    old_top = max(Counter(counts).items(), key=lambda kv: (kv[0], kv[1]))[0]
    old_tiling = [ln for ln in band.lines if len(ln.words) >= old_top]
    old_sub = Band(tuple(old_tiling), min(l.top for l in old_tiling), max(l.bottom for l in old_tiling))
    old_ncols = infer_leaf_grid(old_sub).ncols
    # The verbose title is the highest-token row, so the old code collapses to 1 col.
    assert old_ncols != 3, (
        f"old code unexpectedly returned 3 — fixture may need a wider title; got {old_ncols}"
    )

    # New suffix-max code must recover the true 3-column leaf grid.
    assert recover_leaf_grid(band).ncols == 3
