"""Loop J — R17: the record and transposed paths get the membrane backstop.

A defective region on these paths used to RAISE at compile_tables' final validation
(AssertionError, tab:CoverageShape — the loop G attempt-1 crash class, demonstrated in the
loop G final review by dropping one tab:coversColumn). With the gate, the region escalates
in-band as REGION_TILING_FAILED and the rest of the document survives (§7).
See docs/superpowers/specs/2026-07-30-r17-direct-assert-gate-design.md.
"""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import Namespace

TAB = Namespace("https://w3id.org/iladub/tab#")


def _corrupting(real):
    """Wrap an assert_* function: call it, then delete ONE coversColumn triple from the
    graph it wrote into — the exact R17 demonstration from the loop G final review."""
    def wrapped(g, *args, **kwargs):
        n = real(g, *args, **kwargs)
        t = next(iter(g.triples((None, TAB.coversColumn, None))))
        g.remove(t)
        return n
    return wrapped


def test_defective_record_region_escalates_instead_of_raising(tmp_path, monkeypatch):
    import iladub.etkl.compile as C
    from tests.etkl import fixtures as F
    monkeypatch.setattr(C, "assert_record_region", _corrupting(C.assert_record_region))
    p = os.path.join(str(tmp_path), "rec.pdf")
    F.simple_table_pdf(p)
    rep = C.compile_tables(p)                      # must NOT raise
    assert any(r.verdict == "escalated" and r.reason == "REGION_TILING_FAILED"
               for r in rep.regions), [(r.verdict, r.reason) for r in rep.regions]
    assert not any(r.verdict == "asserted" for r in rep.regions)


def test_defective_transposed_region_escalates_instead_of_raising(tmp_path, monkeypatch):
    import iladub.etkl.holon as H
    import iladub.etkl.compile as C
    from tests.etkl import fixtures as F
    monkeypatch.setattr(H, "assert_transposed_region",
                        _corrupting(H.assert_transposed_region))
    p = os.path.join(str(tmp_path), "tr.pdf")
    F.transposed_table_pdf(p)
    rep = C.compile_tables(p)                      # must NOT raise
    assert any(r.verdict == "escalated" and r.reason == "REGION_TILING_FAILED"
               for r in rep.regions), [(r.verdict, r.reason) for r in rep.regions]


def test_healthy_record_region_is_untouched(tmp_path):
    from iladub.etkl.compile import compile_tables
    from tests.etkl import fixtures as F
    p = os.path.join(str(tmp_path), "rec.pdf")
    F.simple_table_pdf(p)
    rep = compile_tables(p)
    assert any(r.verdict == "asserted" for r in rep.regions)
    assert not any(r.reason == "REGION_TILING_FAILED" for r in rep.regions)
    assert rep.score == 1.0


def test_healthy_transposed_region_is_untouched(tmp_path):
    from iladub.etkl.compile import compile_tables
    from tests.etkl import fixtures as F
    p = os.path.join(str(tmp_path), "tr.pdf")
    F.transposed_table_pdf(p)
    rep = compile_tables(p)
    assert any(r.verdict == "asserted" for r in rep.regions)
    assert not any(r.reason == "REGION_TILING_FAILED" for r in rep.regions)
