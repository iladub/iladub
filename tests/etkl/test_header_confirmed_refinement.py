"""Loop G attempt 2 — header-confirmed refinement, end to end.

The parity test is the loop's reason to exist: attempt 1 CRASHED compile_tables on this fixture
(AssertionError at final SHACL validation, tab:CoverageShape — a phantom column no header covers).
With header confirmation, every candidate in this document is refused (one-sided ink for ID/Date,
a straddling glyph for Tonnes) and the compile must be byte-equal to main's.
See docs/superpowers/specs/2026-07-30-header-confirmed-refinement-design.md.
"""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from iladub.etkl.compile import compile_tables
from tests.etkl import fixtures as F


def test_aligned_space_counter_example_compiles_as_on_main(tmp_path):
    p = os.path.join(str(tmp_path), "aligned.pdf")
    F.aligned_space_table_pdf(p)
    rep = compile_tables(p)                                    # must NOT raise
    asserted = [(str(r.kind).split(".")[-1], r.verdict, r.cells)
                for r in rep.regions if r.verdict == "asserted"]
    assert asserted == [("RECORD_TABLE", "asserted", 18)], asserted
    assert rep.score == 1.0


def test_build_ruled_band_never_synthesises_a_rule(tmp_path):
    """Attempt 1's C2 redress: the guard calls the PRODUCTION band builder directly — the
    replicated-copy version it replaces was proven tautological (compile.py could synthesise
    Rules and every test stayed green)."""
    from iladub.etkl.bands import detect_bands
    from iladub.etkl.compile import _build_ruled_band
    from iladub.etkl.geometry import extract_chars, extract_rules, extract_words, text_lines
    from iladub.etkl.segment import segment

    p = os.path.join(str(tmp_path), "ruled.pdf")
    F.ruled_tight_table_pdf(p)
    page_rules = extract_rules(p, 0)
    page_chars = extract_chars(p, 0)
    authored = {round(r.x, 2) for r in page_rules}
    assert authored, "fixture must be ruled"

    checked = 0
    for band in detect_bands(text_lines(extract_words(p, 0))):
        for sub in segment(band):
            sub_rules = tuple(r for r in page_rules
                              if r.top <= sub.bottom and r.bottom >= sub.top)
            if not sub_rules:
                continue
            b = _build_ruled_band(sub, sub_rules, (), page_chars)
            for r in b.rules:
                assert round(r.x, 2) in authored, "a Rule was synthesised for a derived boundary"
            checked += 1
    assert checked, "no ruled band was exercised"
