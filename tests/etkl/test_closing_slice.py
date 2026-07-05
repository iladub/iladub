import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from rdflib import Graph
from tests.etkl.fixtures import simple_table_pdf, pivoted_table_pdf
from iladub.etkl import compile_tables, RegionKind
from iladub.etkl.holon import TAB, ILADUB


def test_record_table_closes_score_one(tmp_path):
    p = tmp_path / "cbc.pdf"; simple_table_pdf(str(p))
    report = compile_tables(str(p))
    assert report.score == 1.0
    assert any(r.kind is RegionKind.RECORD_TABLE and r.verdict == "asserted"
               for r in report.regions)
    # the holon conforms (compile_tables ran SHACL internally when validate_shapes=True)
    assert (None, None, TAB.RecordTable) in report.graph


def test_pivot_escalates_in_band(tmp_path):
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    report = compile_tables(str(p))
    assert any(r.verdict == "escalated" and r.reason == "KIND_NOT_SUPPORTED"
               for r in report.regions), report.regions
    assert (None, None, ILADUB.CandidateConcept) in report.graph
    assert report.score < 1.0
    # never a fake assertion of the pivot
    assert not any(r.kind is RegionKind.RECORD_TABLE for r in report.regions)


def test_title_excluded_from_score(tmp_path):
    p = tmp_path / "cbc.pdf"; simple_table_pdf(str(p))
    report = compile_tables(str(p))
    non = [r for r in report.regions if r.kind is RegionKind.NON_TABLE]
    assert non and all(r.cells == 0 for r in non)
    # score is 1.0 despite the title band existing -> prose excluded
    assert report.score == 1.0


def test_report_serializes_and_reparses(tmp_path):
    p = tmp_path / "cbc.pdf"; simple_table_pdf(str(p))
    report = compile_tables(str(p))
    ttl = report.to_turtle()
    assert Graph().parse(data=ttl, format="turtle")
