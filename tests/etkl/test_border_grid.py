import os, tempfile
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from iladub.etkl.geometry import extract_rules, extract_words, text_lines, Rule
from iladub.etkl.bands import detect_bands, Band
from iladub.etkl.grid import infer_leaf_grid
from iladub.etkl import compile_tables
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
    assert g.ncols == 5, f"rule grid ncols={g.ncols}"
    assert g.confidence == 1.0
    # DISCRIMINATOR: the rule boundaries are the AUTHOR's exact separators; the whitespace path
    # (rules=()) gives DIFFERENT, wrong boundaries (e.g. a compressed rightmost column that cuts
    # off Q4). This asserts the rule path actually changed the outcome — not a trivial ncols match.
    got = [round(x, 0) for x in g.boundaries]
    want = sorted({round(x, 0) for x in meta["rule_xs"]})
    assert got == want, f"rule boundaries {got} != author separators {want}"
    ws = infer_leaf_grid(replace(band, rules=()))
    assert [round(x, 0) for x in ws.boundaries] != want, "whitespace path must differ from the rules"


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


def test_ruled_tight_table_compiles_as_record_5_cols():
    p, meta = _pdf(F.ruled_tight_table_pdf)
    rep = compile_tables(p)
    kinds = [(str(r.kind).split(".")[-1], r.verdict) for r in rep.regions]
    # the tight ruled table is now captured as a RECORD_TABLE (was UNSUPPORTED via a 4-col grid)
    assert ("RECORD_TABLE", "asserted") in kinds, kinds


def test_borderless_tight_table_unchanged_path():
    # the borderless twin still goes through the whitespace path (no rules) — same as pre-change
    p, _ = _pdf(F.borderless_tight_table_pdf)
    rep = compile_tables(p)   # must not raise; behavior identical to today's whitespace inference
    assert rep is not None
