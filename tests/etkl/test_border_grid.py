import os, tempfile
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from iladub.etkl.geometry import extract_rules
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
