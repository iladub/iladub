import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from tests.etkl.fixtures import (side_by_side_pdf, stacked_repeated_header_pdf,
                                 simple_table_pdf, crosstab_table_pdf, pivoted_table_pdf)
from iladub.etkl import extract_words, text_lines, detect_bands
from iladub.etkl.segment import find_repeated_header, find_table_gutter, has_own_stub


def _band(maker, tmp_path):
    p = tmp_path / "x.pdf"; maker(str(p))
    return detect_bands(text_lines(extract_words(str(p))))[-1]


def test_find_repeated_header_fires(tmp_path):
    reps = find_repeated_header(_band(stacked_repeated_header_pdf, tmp_path))
    assert len(reps) == 1 and reps[0] >= 1


def test_find_repeated_header_none_on_singles(tmp_path):
    for maker in (simple_table_pdf, crosstab_table_pdf, pivoted_table_pdf):
        assert find_repeated_header(_band(maker, tmp_path)) == []


def test_find_table_gutter_certifies_side_by_side(tmp_path):
    assert find_table_gutter(_band(side_by_side_pdf, tmp_path)) is not None


def test_find_table_gutter_none_on_singles(tmp_path):
    # the critical no-false-positive guard, incl. the cross-tab (its halves are not both-RECORD)
    for maker in (simple_table_pdf, crosstab_table_pdf, pivoted_table_pdf):
        assert find_table_gutter(_band(maker, tmp_path)) is None


def test_has_own_stub(tmp_path):
    # side-by-side right half has a text stub; a cross-tab right half is data-only
    from iladub.etkl.grid import infer_leaf_grid
    from iladub.etkl.regions import column_of
    from iladub.etkl.segment import _band_from_words

    def right_half(maker):
        p = tmp_path / "r.pdf"; maker(str(p))
        words = extract_words(str(p)); band = detect_bands(text_lines(words))[-1]
        g = infer_leaf_grid(band); b = g.boundaries
        cw = {}
        for w in words:
            cw.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w)
        ext = {c: (min(w.x0 for w in ws), max(w.x1 for w in ws)) for c, ws in cw.items()}
        gaps = [(c, ext[c + 1][0] - ext[c][1]) for c in range(g.ncols - 1) if c in ext and c + 1 in ext]
        wc, _ = max(gaps, key=lambda z: z[1]); cut = (ext[wc][1] + ext[wc + 1][0]) / 2.0
        return _band_from_words([w for w in words if (w.x0 + w.x1) / 2.0 >= cut])

    assert has_own_stub(right_half(side_by_side_pdf)) is True
    assert has_own_stub(right_half(crosstab_table_pdf)) is False


from iladub.etkl.segment import segment, is_multi_table_ambiguous
from tests.etkl.fixtures import (all_text_table_pdf, row_grouped_table_pdf,
                                 transposed_table_pdf, record_plus_stub_hier_pdf)


def test_side_by_side_segments_to_two(tmp_path):
    subs = segment(_band(side_by_side_pdf, tmp_path))
    assert len(subs) == 2
    from iladub.etkl.regions import classify, RegionKind
    assert all(classify(s).kind is RegionKind.RECORD_TABLE for s in subs)


def test_stacked_repeated_segments_to_two(tmp_path):
    subs = segment(_band(stacked_repeated_header_pdf, tmp_path))
    assert len(subs) == 2
    # each stack starts with the header, not a fused body
    assert all(tuple(w.text for w in s.lines[0].words) == ("Analyte", "Value", "Unit") for s in subs)


def test_single_tables_never_split(tmp_path):
    # THE invariant — every existing single table segments to exactly one region
    for maker in (simple_table_pdf, pivoted_table_pdf, all_text_table_pdf,
                  crosstab_table_pdf, row_grouped_table_pdf, transposed_table_pdf):
        assert len(segment(_band(maker, tmp_path))) == 1, maker.__name__


def test_multi_table_ambiguous(tmp_path):
    assert is_multi_table_ambiguous(_band(record_plus_stub_hier_pdf, tmp_path)) is True


def test_crosstab_not_ambiguous(tmp_path):
    assert is_multi_table_ambiguous(_band(crosstab_table_pdf, tmp_path)) is False
