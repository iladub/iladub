import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from rdflib import Graph
from tests.etkl.fixtures import simple_table_pdf, pivoted_table_pdf
from iladub.etkl import compile_tables, RegionKind
from iladub.etkl.holon import TAB


def test_record_table_closes_score_one(tmp_path):
    p = tmp_path / "cbc.pdf"; simple_table_pdf(str(p))
    report = compile_tables(str(p))
    assert report.score == 1.0
    assert any(r.kind is RegionKind.RECORD_TABLE and r.verdict == "asserted"
               for r in report.regions)
    # the holon conforms (compile_tables ran SHACL internally when validate_shapes=True)
    assert (None, None, TAB.RecordTable) in report.graph


def test_pivot_now_compiles_hierarchically(tmp_path):
    """After Task 7 the pivot is asserted as tab:HierarchicalTable, not escalated.

    This supersedes the pre-Task-7 test_pivot_escalates_in_band.  The core guard is
    unchanged: the pivot must NEVER be asserted as a RecordTable (that would be a
    structural lie); it is now correctly typed as HierarchicalTable.
    """
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.HierarchicalTable) in report.graph, "pivot must compile to HierarchicalTable"
    assert report.score > 0.0, "must assert at least some body tokens"
    assert report.score < 1.0, (
        "pivot score must be < 1.0: header words (Current Visit, Prior Visit, sub-labels, (SI))"
        " inflate the denominator so the ratio of asserted body tokens is strictly less than 1"
    )
    # safety guard: never a wrong record assertion
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


def test_mixed_document_score_is_token_coherent(tmp_path):
    """A document with a record table + a pivot table exercises both compilation paths.

    After Task 7: the pivot compiles as HierarchicalTable (not escalated), so the
    score is the ratio of asserted body-words / total band words.  Header words in
    the pivot band (Current Visit, Prior Visit, sub-labels) are not body cells and
    count toward the denominator but not the numerator, so 0 < score < 1.
    """
    from iladub.etkl.holon import TAB
    p = tmp_path / "mixed.pdf"
    from tests.etkl.fixtures import record_and_pivot_pdf
    record_and_pivot_pdf(str(p))
    report = compile_tables(str(p))
    # record table branch
    assert any(r.kind is RegionKind.RECORD_TABLE and r.verdict == "asserted" for r in report.regions)
    assert (None, None, TAB.RecordTable) in report.graph
    # hierarchical branch (pivot)
    assert (None, None, TAB.HierarchicalTable) in report.graph
    # score is a coherent token ratio strictly inside (0, 1):
    #   numerator  = record body words + pivot body words (both asserted)
    #   denominator = above + pivot header words (not body cells)
    assert 0.0 < report.score < 1.0, report.score


def test_transposed_escalates_not_asserted(tmp_path):
    from tests.etkl.fixtures import transposed_table_pdf
    from iladub.etkl.holon import TAB, ILADUB, DEC
    from rdflib import RDF
    p = tmp_path / "t.pdf"; transposed_table_pdf(str(p))
    report = compile_tables(str(p))
    # the silent-wrong is closed: NO RecordTable asserted; escalated as TRANSPOSED
    assert (None, None, TAB.RecordTable) not in report.graph
    cand = next(report.graph.subjects(RDF.type, ILADUB.CandidateConcept))
    assert str(next(report.graph.objects(cand, DEC.rationale))) == "TRANSPOSED"
    assert report.score == 0.0


def test_normal_table_still_compiles(tmp_path):
    # the critical no-false-positive guard: a normal numeric record table is unaffected
    from tests.etkl.fixtures import simple_table_pdf
    from iladub.etkl.holon import TAB
    p = tmp_path / "cbc.pdf"; simple_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.RecordTable) in report.graph
    assert report.score == 1.0


def test_all_text_record_not_flagged_transposed(tmp_path):
    """An all-text record table (Region/Manager/Backup) must still compile as a
    RecordTable and must NOT be escalated as TRANSPOSED.

    Guards the conservative 'text is symmetric, never flagged' property: since no
    body row has all-numeric cells in non-label columns, looks_transposed returns
    False and the existing assert path runs unchanged.
    """
    from tests.etkl.fixtures import all_text_table_pdf
    from iladub.etkl.holon import TAB, ILADUB, DEC
    from rdflib import RDF
    p = tmp_path / "text.pdf"; all_text_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.RecordTable) in report.graph, "all-text table must still be a RecordTable"
    # No TRANSPOSED escalation
    for cand in report.graph.subjects(RDF.type, ILADUB.CandidateConcept):
        rationale = str(next(report.graph.objects(cand, DEC.rationale), ""))
        assert rationale != "TRANSPOSED", "all-text table must NOT be flagged TRANSPOSED"
