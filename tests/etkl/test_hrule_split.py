import os, tempfile
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from iladub.etkl.geometry import extract_hrules, extract_words, text_lines, HRule, Word, Line
from iladub.etkl.bands import detect_bands, Band
from iladub.etkl.grid import infer_leaf_grid
from iladub.etkl.headers import header_body_split
from iladub.etkl import compile_tables
from dataclasses import replace
from tests.etkl import fixtures as F


def _pdf(fn):
    p = os.path.join(tempfile.mkdtemp(), fn.__name__ + ".pdf")
    return p, fn(p)


def _table_band(pdf_path):
    return max(detect_bands(text_lines(extract_words(pdf_path))), key=lambda b: len(b.lines))


# ---- Task 1: extraction ----

def test_extract_hrules_finds_the_under_header_rule():
    p, _ = _pdf(F.all_text_hier_ruled_pdf)
    hr = extract_hrules(p)
    assert len(hr) >= 1
    assert any(90 < h.y < 130 for h in hr), [round(h.y, 1) for h in hr]


def test_extract_hrules_empty_on_borderless():
    p, _ = _pdf(F.all_text_hier_borderless_pdf)
    assert extract_hrules(p) == []


# ---- Task 2: rule-derived split fallback ----

def test_hrule_split_used_when_type_split_none():
    p, _ = _pdf(F.all_text_hier_ruled_pdf)
    band = _table_band(p)
    grid = infer_leaf_grid(band)
    assert header_body_split(band, grid) is None                    # all-text -> type split None
    hr = tuple(h for h in extract_hrules(p) if band.top <= h.y <= band.bottom)
    ruled = replace(band, hrules=hr)
    split = header_body_split(ruled, grid)
    assert split is not None and 1 <= split < len(band.lines)


def test_type_split_wins_when_present_even_with_hrule():
    def w(t, x0, x1, top): return Word(t, x0, x1, top, top + 8)
    lines = [Line((w("Name", 60, 90, 0), w("Score", 160, 195, 0)), 0, 8),
             Line((w("Alice", 60, 90, 20), w("10", 160, 175, 20)), 20, 28),
             Line((w("Bob", 60, 85, 40), w("20", 160, 175, 40)), 40, 48)]
    band = Band(tuple(lines), 0, 48)
    grid = infer_leaf_grid(band)
    base = header_body_split(band, grid)
    assert base is not None                                          # numeric col -> type split
    ruled = replace(band, hrules=(HRule(y=14.0, x0=55, x1=200),))
    assert header_body_split(ruled, grid) == base                   # UNCHANGED — type split wins


# ---- Task 3: end-to-end ----

def test_all_text_hier_ruled_is_captured_not_escalated():
    p, _ = _pdf(F.all_text_hier_ruled_pdf)
    rep = compile_tables(p)
    verdicts = [r.verdict for r in rep.regions]
    assert "asserted" in verdicts, [(str(r.kind).split(".")[-1], r.verdict, r.reason) for r in rep.regions]
    assert rep.score > 0.0, "the all-text hierarchical table should now capture data (was 0.00)"


def test_all_text_hier_borderless_still_escalates():
    p, _ = _pdf(F.all_text_hier_borderless_pdf)
    rep = compile_tables(p)
    assert rep.score == 0.0, "borderless all-text hierarchical has no header/body signal -> escalates"


# ---- Task 4: additive guarantee ----

def test_shipped_fixtures_have_no_hrules():
    for name in ["simple_table_pdf", "pivoted_table_pdf", "crosstab_table_pdf",
                 "row_grouped_table_pdf", "region_pivot_pdf", "partial_merge_report_pdf"]:
        p = os.path.join(tempfile.mkdtemp(), name + ".pdf")
        getattr(F, name)(p)
        assert extract_hrules(p) == [], f"{name} unexpectedly has horizontal rules"
