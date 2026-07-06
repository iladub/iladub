"""test_hier_escalation — ambiguous-boundary escalation proof.

An all-text table with no numeric column is genuinely ambiguous: there is no
type-homogeneous column to pin the header/body boundary, so classify_hierarchical
returns None and compile_tables escalates the whole region as
iladub:CandidateConcept instead of guessing a structure.

Fixture design rationale
------------------------
Row 0 is a single centered label ("Regions") — one word for three leaf columns.
classify() therefore hits the ``len(header.words) != grid.ncols`` guard and
returns UNSUPPORTED_TABLE (not RECORD_TABLE), ensuring compile_tables enters the
hierarchical branch.  Within that branch, header_body_split finds no column that
is all-numeric, returns None, and classify_hierarchical propagates None.
compile_tables then calls escalate_region, emitting an iladub:CandidateConcept.
"""
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from iladub.etkl import extract_words, text_lines, detect_bands, compile_tables
from iladub.etkl.hierarchical import classify_hierarchical
from iladub.etkl.holon import ILADUB

PAGE_W, PAGE_H = letter


def all_text_ambiguous_pdf(path: str) -> dict:
    """All-text table with no numeric column — boundary is genuinely ambiguous;
    must escalate, not guess.

    Row 0 is a single centered spanning label ("Regions"): word count (1) does
    not equal the leaf-column count (3) that infer_leaf_grid recovers from rows
    1-3, so classify() returns UNSUPPORTED_TABLE.  classify_hierarchical then
    returns None because header_body_split cannot find a column that is
    all-numeric down the remaining lines (every cell is a text label).
    compile_tables therefore escalates the whole region as iladub:CandidateConcept.
    """
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    ys = [PAGE_H - 100, PAGE_H - 118, PAGE_H - 136, PAGE_H - 154]
    # Row 0: one centered word — word count (1) ≠ leaf-column count (3)
    c.drawCentredString((60 + 390) / 2.0, ys[0], "Regions")
    # Rows 1-3: three-column all-text rows (no numeric value anywhere)
    rows = [
        ("Region", "North", "South"),
        ("Area",   "Alpha", "Beta"),
        ("Zone",   "Red",   "Blue"),
    ]
    for y, row in zip(ys[1:], rows):
        for x, cell in zip((60, 220, 360), row):
            c.drawString(x, y, cell)
    c.save()
    return {}


def test_all_text_escalates(tmp_path):
    """All-text table: classify_hierarchical returns None → compile_tables escalates
    as iladub:CandidateConcept, NOT guessed as a record or hierarchical table.

    Two sub-assertions:
      1. classify_hierarchical(band) is None — the hierarchical maker correctly
         refuses to guess a boundary when no numeric column exists.
      2. (None, None, ILADUB.CandidateConcept) in report.graph — compile_tables
         escalates the whole region rather than asserting a wrong structure.
    """
    p = tmp_path / "amb.pdf"
    all_text_ambiguous_pdf(str(p))
    band = detect_bands(text_lines(extract_words(str(p))))[-1]

    # Stage 1: the hierarchical maker must return None (no numeric column)
    assert classify_hierarchical(band) is None, (
        "expected classify_hierarchical to return None for an all-text band "
        "(header_body_split should find no numeric column)"
    )

    # Stage 2: compile_tables must escalate it — never assert a wrong structure
    report = compile_tables(str(p))
    assert (None, None, ILADUB.CandidateConcept) in report.graph, (
        "expected an iladub:CandidateConcept triple in the graph "
        "(all-text table must escalate, not be asserted)"
    )
    # Must NOT assert as a record table or hierarchical table.
    # Use graph.subjects(rdf:type, …) rather than (None, None, T) in graph,
    # because escalate_region adds (cand_uri, iladub:suggestedAnchor, TAB.HierarchicalTable)
    # which would falsely match a plain (None, None, TAB.HierarchicalTable) pattern.
    from rdflib import RDF
    from iladub.etkl.holon import TAB
    assert not any(report.graph.subjects(RDF.type, TAB.RecordTable)), \
        "all-text ambiguous band must never be asserted as a RecordTable"
    assert not any(report.graph.subjects(RDF.type, TAB.HierarchicalTable)), \
        "all-text ambiguous band must never be asserted as a HierarchicalTable"
