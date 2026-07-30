"""Loop G attempt 2 — header-confirmed refinement, end to end.

The parity test is the loop's reason to exist: attempt 1 CRASHED compile_tables on this fixture
(AssertionError at final SHACL validation, tab:CoverageShape — a phantom column no header covers).
With header confirmation, every candidate in this document is refused (one-sided ink for ID/Date;
no candidate is even generated in the Tonnes interval, since the header word's own ink keeps that
run's blank fraction below the generation threshold) and the compile must be byte-equal to main's.
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


def test_confirmed_split_reaches_the_grid_end_to_end(tmp_path):
    """THE POSITIVE CASE (E8), committed. The review found the confirmed path had ZERO committed
    coverage — the loop's entire point was verified only against a local, uncommittable PDF.
    Four leaf-header labels (ID/Qty/Unit/Total) and 24 data cells prove the confirmed boundary
    reached the grid; the unrefined grid yields 18."""
    from rdflib import Namespace
    TAB = Namespace("https://w3id.org/iladub/tab#")
    p = os.path.join(str(tmp_path), "confirmed.pdf")
    F.confirmed_split_table_pdf(p)
    rep = compile_tables(p)
    asserted = [(r.verdict, r.cells) for r in rep.regions if r.verdict == "asserted"]
    assert asserted == [("asserted", 24)], asserted
    labels = sorted(str(o) for s, _p2, o in rep.graph.triples((None, TAB.cellText, None))
                    if str(o) in ("ID", "Qty", "Unit", "Total"))
    assert labels == ["ID", "Qty", "Total", "Unit"], labels


def test_build_ruled_band_never_synthesises_a_rule(tmp_path):
    """Attempt 1's C2 redress: the guard calls the PRODUCTION band builder directly — the
    replicated-copy version it replaces was proven tautological (compile.py could synthesise
    Rules and every test stayed green). Walks BOTH the plain ruled fixture and the E8 confirmed-
    split fixture, so this guard actually exercises _build_ruled_band's confirmed-boundary exit
    (the review found the unconfirmed fixture alone generates zero candidates, so mutating
    compile.py to synthesise fake Rules at that exit passed every test unchanged)."""
    from iladub.etkl.bands import detect_bands
    from iladub.etkl.compile import _build_ruled_band
    from iladub.etkl.geometry import extract_chars, extract_rules, extract_words, text_lines
    from iladub.etkl.segment import segment

    checked = 0
    for name, fixture in (("ruled.pdf", F.ruled_tight_table_pdf),
                           ("confirmed.pdf", F.confirmed_split_table_pdf)):
        p = os.path.join(str(tmp_path), name)
        fixture(p)
        page_rules = extract_rules(p, 0)
        page_chars = extract_chars(p, 0)
        authored = {round(r.x, 2) for r in page_rules}
        assert authored, "fixture must be ruled"

        for band in detect_bands(text_lines(extract_words(p, 0))):
            for sub in segment(band):
                sub_rules = tuple(r for r in page_rules
                                  if r.top <= sub.bottom and r.bottom >= sub.top)
                if not sub_rules:
                    continue
                b = _build_ruled_band(sub, sub_rules, (), page_chars)
                for r in b.rules:
                    assert round(r.x, 2) in authored, \
                        "a Rule was synthesised for a derived boundary"
                if b.column_xs:
                    xs_a = {round(r.x, 2) for r in b.rules}
                    assert xs_a <= {round(x, 2) for x in b.column_xs}, \
                        "derived list must preserve every author boundary"
                checked += 1
    assert checked, "no ruled band was exercised"


def test_defective_hierarchical_region_escalates_in_band_not_crash(tmp_path, monkeypatch):
    """THE CRASH CLASS, closed at the membrane. The plain hierarchical branch was the last
    region path writing directly into the graph — which is why attempt 1's phantom column
    CRASHED compile_tables at final SHACL validation instead of escalating.

    Sabotage (probe-verified deterministic): blanking the last leaf node's covers passes
    merge_tiling_ok (True — it checks overlap/centering, not coverage), asserts n=10, and fails
    region_tiles (False, tab:CoverageShape). Before the backstop this test dies with an
    AssertionError from compile_tables; after, it escalates in-band."""
    from dataclasses import replace

    from iladub.etkl import hierarchical as H

    p = os.path.join(str(tmp_path), "pm.pdf")
    F.partial_merge_report_pdf(p)
    real = H.classify_hierarchical

    def sabotaged(band):
        hreg = real(band)
        if hreg is None:
            return None
        max_lvl = max(n.level for n in hreg.tree)
        leafs = [i for i, n in enumerate(hreg.tree) if n.covers and n.level == max_lvl]
        tree = list(hreg.tree)
        tree[leafs[-1]] = replace(tree[leafs[-1]], covers=())
        return replace(hreg, tree=tuple(tree))

    monkeypatch.setattr(H, "classify_hierarchical", sabotaged)
    rep = compile_tables(p)                                    # must NOT raise
    reasons = [r.reason for r in rep.regions]
    assert "REGION_TILING_FAILED" in reasons, reasons
