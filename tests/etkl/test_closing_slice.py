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


def test_transposed_now_compiles(tmp_path):
    # Loop 4: the transposed table Loop 3 escalated now COMPILES by axis-flip.
    from tests.etkl.fixtures import transposed_table_pdf
    from iladub.etkl.holon import TAB, ILADUB
    from rdflib import RDF, Literal
    p = tmp_path / "t.pdf"; transposed_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.RecordTable) in report.graph
    t = next(report.graph.subjects(RDF.type, TAB.RecordTable))
    assert (t, TAB.sourceOrientation, Literal("transposed")) in report.graph
    # header recovered from physical column 0: Name, Age, City
    labels = {str(o) for s in report.graph.subjects(RDF.type, TAB.LabelCell)
              for o in report.graph.objects(s, TAB.cellText)}
    assert {"Name", "Age", "City"} <= labels
    # 2 records (Alice, Bob) -> 2 leaf rows; no TRANSPOSED escalation
    assert len(list(report.graph.subjects(RDF.type, TAB.LeafRow))) == 2
    assert (None, None, ILADUB.CandidateConcept) not in report.graph
    assert report.score == 1.0


def test_false_positive_transpose_escalates(tmp_path):
    # a region that trips looks_transposed but is NOT coherent must ESCALATE, not
    # compile an inverted RecordTable (the compile-direction silent-wrong guard).
    from tests.etkl.fixtures import false_transposed_pdf
    from iladub.etkl.holon import TAB, ILADUB, DEC
    from rdflib import RDF
    p = tmp_path / "fp.pdf"; false_transposed_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.RecordTable) not in report.graph
    cand = next(report.graph.subjects(RDF.type, ILADUB.CandidateConcept))
    assert str(next(report.graph.objects(cand, DEC.rationale))) == "TRANSPOSED"


def test_transposed_provenance_survives_flip(tmp_path):
    # Alice's Age value "30" must trace to the PHYSICAL "30" word on the page,
    # proving the flip is a logical relabel, not a coordinate transform.
    from tests.etkl.fixtures import transposed_table_pdf
    from iladub.etkl import extract_words
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "t.pdf"; transposed_table_pdf(str(p))
    word30 = next(w for w in extract_words(str(p)) if w.text == "30")
    report = compile_tables(str(p))
    e = next(s for s in report.graph.subjects(RDF.type, TAB.EntryCell)
             if str(next(report.graph.objects(s, TAB.cellText))) == "30")
    bb = next(report.graph.objects(e, TAB.hasBBox))
    assert abs(float(next(report.graph.objects(bb, TAB.x0))) - word30.x0) < 0.01
    assert int(next(report.graph.objects(e, TAB.onPage))) == 0


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


def test_row_grouped_compiles(tmp_path):
    from tests.etkl.fixtures import row_grouped_table_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "rg.pdf"; row_grouped_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.HierarchicalTable) in report.graph
    tbl = next(report.graph.subjects(RDF.type, TAB.HierarchicalTable))
    assert len(list(report.graph.objects(tbl, TAB.hasLeafColumn))) == 1   # Value (Design A)
    assert len(list(report.graph.objects(tbl, TAB.hasLeafRow))) == 5
    # a row-header tree exists (coversRow), and it's not the flat-record flattening
    assert (None, TAB.coversRow, None) in report.graph
    assert report.score == 1.0


def test_row_grouped_not_a_flat_record(tmp_path):
    # the closing point: it must NOT compile as a flat RecordTable
    from tests.etkl.fixtures import row_grouped_table_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "rg.pdf"; row_grouped_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.RecordTable) not in report.graph


def test_crosstab_compiles(tmp_path):
    from tests.etkl.fixtures import crosstab_table_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "ct.pdf"; crosstab_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.HierarchicalTable) in report.graph
    tbl = next(report.graph.subjects(RDF.type, TAB.HierarchicalTable))
    assert len(list(report.graph.objects(tbl, TAB.hasLeafColumn))) == 6   # data-only
    assert len(list(report.graph.objects(tbl, TAB.hasLeafRow))) == 2
    assert (None, TAB.coversColumn, None) in report.graph                 # column tree
    assert (None, TAB.coversRow, None) in report.graph                    # row tree
    assert report.score == 1.0


def test_pivot_still_column_hierarchy(tmp_path):
    # regression: Loop 2's pivot is NOT stolen by the matrix gate (stub_data_split None)
    from tests.etkl.fixtures import pivoted_table_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "piv.pdf"; pivoted_table_pdf(str(p))
    report = compile_tables(str(p))
    assert (None, None, TAB.HierarchicalTable) in report.graph
    assert (None, TAB.coversRow, None) not in report.graph                # column-only, no row axis


def test_side_by_side_page_compiles_two_tables(tmp_path):
    from tests.etkl.fixtures import side_by_side_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "sxs.pdf"; side_by_side_pdf(str(p))
    report = compile_tables(str(p))
    assert len(list(report.graph.subjects(RDF.type, TAB.RecordTable))) == 2   # was 1 fused
    assert report.score == 1.0


def test_stacked_repeated_header_compiles_two(tmp_path):
    from tests.etkl.fixtures import stacked_repeated_header_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "stk.pdf"; stacked_repeated_header_pdf(str(p))
    report = compile_tables(str(p))
    assert len(list(report.graph.subjects(RDF.type, TAB.RecordTable))) == 2


def test_multi_table_ambiguous_escalates(tmp_path):
    from tests.etkl.fixtures import record_plus_stub_hier_pdf
    from iladub.etkl.holon import ILADUB, DEC
    from rdflib import RDF
    p = tmp_path / "amb.pdf"; record_plus_stub_hier_pdf(str(p))
    report = compile_tables(str(p))
    rationales = {str(o) for s in report.graph.subjects(RDF.type, ILADUB.CandidateConcept)
                  for o in report.graph.objects(s, DEC.rationale)}
    assert "MULTI_TABLE_AMBIGUOUS" in rationales


def test_crosstab_still_single_table(tmp_path):
    # regression: the cross-tab is neither split nor escalated
    from tests.etkl.fixtures import crosstab_table_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "ct.pdf"; crosstab_table_pdf(str(p))
    report = compile_tables(str(p))
    assert len(list(report.graph.subjects(RDF.type, TAB.HierarchicalTable))) == 1


def test_uniform_4col_compiles_one_table(tmp_path):
    """A 4-column uniform-spacing record table (Name/Age/City/Country) must compile
    to exactly ONE tab:RecordTable — not two (the pre-fix false-positive split).

    Guards the gap-dominance fix end-to-end: before the fix, the widest inter-column
    gutter was certified and the band was torn into two 2-column RecordTables; after
    the fix, the widest-to-second-widest ratio (~1.1–1.3) is below _GUTTER_DOMINANCE
    (2.0) so no cut is made and the whole band compiles as a single RecordTable."""
    from tests.etkl.fixtures import uniform_wide_record_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "u4c.pdf"; uniform_wide_record_pdf(str(p))
    report = compile_tables(str(p))
    rec_tables = list(report.graph.subjects(RDF.type, TAB.RecordTable))
    assert len(rec_tables) == 1, f"expected 1 RecordTable, got {len(rec_tables)}"
    assert report.score == 1.0


def test_row_hierarchy_wide_compiles_one_table(tmp_path):
    """A row-hierarchy table with 2 numeric data columns (Headcount + Budget) must
    compile to exactly ONE tab:HierarchicalTable (with coversRow) and ZERO
    tab:RecordTable instances.

    This is the end-to-end guard for the find_table_gutter false-positive fix: before
    the fix, the stub↔data gutter was certified and the band was torn into two
    RecordTables.  After the fix, has_own_stub(right) == False so the cut is rejected
    and the whole band compiles as a single HierarchicalTable."""
    from tests.etkl.fixtures import row_hierarchy_wide_pdf
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    p = tmp_path / "rhw.pdf"; row_hierarchy_wide_pdf(str(p))
    report = compile_tables(str(p))
    hier_tables = list(report.graph.subjects(RDF.type, TAB.HierarchicalTable))
    rec_tables = list(report.graph.subjects(RDF.type, TAB.RecordTable))
    assert len(hier_tables) == 1, f"expected 1 HierarchicalTable, got {len(hier_tables)}"
    assert len(rec_tables) == 0, f"expected 0 RecordTable, got {len(rec_tables)}"
    assert (None, TAB.coversRow, None) in report.graph, "row-header tree must exist (coversRow)"
