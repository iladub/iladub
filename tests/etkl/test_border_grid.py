import os, tempfile
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from iladub.etkl.geometry import extract_rules, extract_words, text_lines, Rule
from iladub.etkl.bands import detect_bands, Band
from iladub.etkl.grid import infer_leaf_grid
from dataclasses import replace
from tests.etkl import fixtures as F


def _pdf(fn):
    p = os.path.join(tempfile.mkdtemp(), fn.__name__ + ".pdf")
    meta = fn(p)
    return p, meta


def test_extract_rules_recovers_vertical_separators():
    p, meta = _pdf(F.ruled_tight_table_pdf)
    rules = extract_rules(p)
    xs = sorted({round(r.x, 0) for r in rules})
    # the 6 vertical separators (5 columns) — allow rounding to the nearest point
    assert xs == sorted({round(x, 0) for x in meta["rule_xs"]}), f"got {xs}"


def test_extract_rules_empty_on_borderless():
    p, _ = _pdf(F.borderless_tight_table_pdf)
    assert extract_rules(p) == []


def _table_band_with_rules(pdf_path):
    ws = extract_words(pdf_path); bands = detect_bands(text_lines(ws))
    band = max(bands, key=lambda b: len(b.lines))           # the table band
    rules = [r for r in extract_rules(pdf_path) if r.top <= band.bottom and r.bottom >= band.top]
    return band, tuple(rules)


def test_rule_grid_recovers_five_columns():
    p, meta = _pdf(F.ruled_tight_table_pdf)
    band, rules = _table_band_with_rules(p)
    ruled = replace(band, rules=rules)
    g = infer_leaf_grid(ruled)
    assert g.ncols == 5, f"rule grid ncols={g.ncols} (whitespace gave 4)"
    assert g.confidence == 1.0


def test_no_rules_is_byte_identical_to_whitespace():
    p, _ = _pdf(F.borderless_tight_table_pdf)
    band, _ = _table_band_with_rules(p)             # borderless -> rules empty
    assert band.rules == ()
    assert infer_leaf_grid(band) == infer_leaf_grid(replace(band, rules=()))   # additive guarantee


def test_straddling_rules_fall_back_to_whitespace():
    # a lone bogus rule through the middle of a word -> words don't tile -> whitespace path
    p, _ = _pdf(F.borderless_tight_table_pdf)
    band, _ = _table_band_with_rules(p)
    bogus = (Rule(x=100.0, top=band.top, bottom=band.bottom),)
    assert infer_leaf_grid(replace(band, rules=bogus)) == infer_leaf_grid(band)
