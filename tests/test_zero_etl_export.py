"""The zero-ETL showcase mechanics: one PDF (a denormalized report between two prose
sections) -> recovered structure -> self-organizing records (no schema) -> round-trip-
certified 1NF -> pandas/parquet, with zero hand-coded ETL. Real iladub package methods.
Backs demo/etkl_1a_showcase.ipynb (docs/superpowers/specs/2026-07-26-etkl-zero-etl-showcase-design.md)."""
import os
import sys
import tempfile

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")
pd = pytest.importorskip("pandas")
pytest.importorskip("pyarrow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "demo"))
import etkl_demo_data as data  # noqa: E402

from iladub.etkl import compile_tables, classify, RegionKind, detect_bands, text_lines, extract_words  # noqa: E402
from iladub.etkl.denormalization import analyze  # noqa: E402
from iladub.etkl.holon import TAB  # noqa: E402
from iladub.feed import table_records  # noqa: E402


def _fixture():
    p = os.path.join(tempfile.mkdtemp(), "memo.pdf")
    truth = data.report_between_prose_pdf(p)
    return p, truth


def test_report_is_segmented_from_prose():
    p, _ = _fixture()
    bands = detect_bands(text_lines(extract_words(p)))
    kinds = [classify(b).kind for b in bands]
    assert kinds.count(RegionKind.NON_TABLE) >= 2   # the two prose sections
    assert any(k is not RegionKind.NON_TABLE for k in kinds)  # the report band recovered


def test_records_self_organize_with_provenance():
    p, _ = _fixture()
    rep = compile_tables(p)
    recs = table_records(rep.graph)
    assert recs, "expected at least one record from the recovered report"
    # header-path-keyed, no schema supplied
    headers = {c.text for r in recs for c in r.concepts}
    assert "Year" in headers or any("Region" in h for h in headers)
    # every cell carries provenance, all distinct
    regions = [c.region for r in recs for c in r.concepts]
    assert all(regions) and len(set(regions)) == len(regions)


def test_zero_etl_1nf_export_round_trips_to_parquet():
    p, truth = _fixture()
    rep = compile_tables(p)
    dr = analyze(rep)
    assert dr.oracle_ok, "round-trip oracle must certify the 1NF inversion (trust anchor)"

    rows = []
    for f in dr.base_facts:
        row = {str(rep.graph.value(co, TAB.dimensionName)): str(rep.graph.value(co, TAB.value))
               for co in rep.graph.objects(f, TAB.atDimensionValue)}
        row["value"] = float(rep.graph.value(f, TAB.measureValue))
        rows.append(row)

    df = (pd.DataFrame(rows)[["Year", "Region", "value"]]
          .sort_values(["Year", "Region"]).reset_index(drop=True))

    out = os.path.join(tempfile.mkdtemp(), "sales_1nf.parquet")
    df.to_parquet(out)                       # zero user ETL: the export is one line
    back = pd.read_parquet(out).sort_values(["Year", "Region"]).reset_index(drop=True)

    expected = (pd.DataFrame(truth["expected_1nf"])[["Year", "Region", "value"]]
                .sort_values(["Year", "Region"]).reset_index(drop=True))
    pd.testing.assert_frame_equal(back, expected)
