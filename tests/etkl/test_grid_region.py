"""Loop P (spec 2026-08-04 §3): grid-region scoping + hrule-box header welding."""
import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import RDF

from iladub.etkl import compile_tables
from iladub.etkl.holon import TAB
from tests.etkl.fixtures import sectioned_ruled_table_pdf


def _compiled_fixture(tmp_path):
    pdf = tmp_path / "section.pdf"
    truth = sectioned_ruled_table_pdf(str(pdf))
    return truth, compile_tables(str(pdf))


def _labels(graph):
    """Every asserted column-header label text (HeaderNode -hasLabel-> LabelCell -cellText),
    the same leaf-label accessor as tests/etkl/test_header_stack.py."""
    return [str(t)
            for h in graph.subjects(RDF.type, TAB.HeaderNode)
            for lc in graph.objects(h, TAB.hasLabel)
            for t in graph.objects(lc, TAB.cellText)]


def test_sectioned_ruled_table_reads(tmp_path):
    """RED on main: the heading/notice strips enter the header tree as fabricated
    all-column levels and the wrapped header box reads as several rows -> the section
    escalates (or asserts a garbage reading). GREEN when: exactly one asserted table,
    the four column names correct incl. the welded 'Time Nom Accepted', 12 data cells."""
    truth, rep = _compiled_fixture(tmp_path)
    asserted = [r for r in rep.regions if r.verdict == "asserted"]
    assert len(asserted) == 1, [(r.kind.name, r.verdict, r.reason) for r in rep.regions]
    # Task 3 tightening: read the leaf header labels precisely (was a liberal whole-graph
    # literal scan at RED time, per the Task-1 implementer note) — the load-bearing
    # assertion is that the WELDED name 'Time Nom Accepted' reaches the leaf labels.
    labels = _labels(rep.graph)
    for name in truth["header_names"]:
        assert name in labels, (name, labels)
    assert rep.score >= 0.9, rep.score


def test_sectioned_captions_carried(tmp_path):
    """§5/§7: the peeled strips are CARRIED as tab:RegionCaption, never dropped."""
    truth, rep = _compiled_fixture(tmp_path)
    caps = {str(t) for c in rep.graph.subjects(RDF.type, TAB.RegionCaption)
            for t in rep.graph.objects(c, TAB.captionText)}
    for text in truth["caption_texts"]:
        assert any(text in c for c in caps), (text, caps)


from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Rule, Word


def _line(top, bottom, *texts):
    x = 80.0
    ws = []
    for t in texts:
        ws.append(Word(t, x, x + 8.0 * len(t), top, bottom))
        x += 8.0 * len(t) + 10
    return Line(tuple(ws), top, bottom)


def test_grid_lines_interior_rule_presence():
    """A line is grid iff an INTERIOR rule (x strictly between the band's outermost
    rule x's) crosses it. Outer-border segments never make a line grid."""
    from iladub.etkl.gridregion import grid_lines
    lines = (_line(60, 70, "HEADING"),          # above interior rules
             _line(75, 85, "NOTICE", "TEXT"),    # above interior rules
             _line(110, 120, "A", "B"),          # crossed by interior rules
             _line(130, 140, "1", "2"))          # crossed by interior rules
    band = Band(lines, 60.0, 140.0)
    rules = [Rule(72.0, 58.0, 145.0),            # outer left (full extent)
             Rule(300.0, 58.0, 145.0),           # outer right
             Rule(150.0, 105.0, 145.0),          # INTERIOR: grid rows only
             Rule(220.0, 105.0, 145.0)]
    assert grid_lines(band, rules) == {2, 3}


def test_grid_lines_abstains_without_interior_rules():
    """Only the two outer rules -> no interior evidence -> abstain (empty set):
    behavior falls back to main's, byte-identical."""
    from iladub.etkl.gridregion import grid_lines
    lines = (_line(60, 70, "A", "B"), _line(80, 90, "1", "2"))
    band = Band(lines, 60.0, 90.0)
    rules = [Rule(72.0, 55.0, 95.0), Rule(300.0, 55.0, 95.0)]
    assert grid_lines(band, rules) == set()


def test_grid_region_query_has_no_numeric_literal():
    """§8: the derivation reads facts only; every number is emitted by the
    PROCEDURAL layer (the header-covers.rq / tab:inkCenterX precedent)."""
    import re
    from pathlib import Path
    text = Path("vocab/queries/grid-region.rq").read_text()
    body = re.sub(r"#[^\n]*", "", text)          # strip comments
    assert not re.search(r"\b\d+\.?\d*\b", body), "numeric literal in the AXIOM"


from iladub.etkl.geometry import HRule


def test_weld_merges_rows_sharing_a_full_width_box():
    """Two re-extracted rows inside ONE author-drawn full-width hrule box weld into
    one row; per-column text joins top-to-bottom ('Time Nom' + 'Accepted')."""
    from iladub.etkl.geometry import weld_hrule_boxes
    r1 = _line(110, 118, "Time", "Nom")           # visual line A (col-1 words)
    r2 = _line(122, 130, "ID", "Accepted")        # visual line B
    # words must sit in rule columns for the column join; rebuild precisely:
    a = Line((Word("Time Nom", 160, 220, 110, 118),), 110, 118)
    b = Line((Word("ID", 80, 100, 122, 130), Word("Accepted", 160, 225, 122, 130)), 122, 130)
    hrules = [HRule(105.0, 72.0, 300.0), HRule(140.0, 72.0, 300.0)]
    out = weld_hrule_boxes([a, b], hrules, [72.0, 150.0, 300.0])
    assert len(out) == 1
    texts = sorted(w.text for w in out[0].words)
    assert texts == ["ID", "Time Nom Accepted"]


def test_weld_never_splits_and_ignores_partial_hrules():
    """One row per box -> unchanged; an hrule NOT spanning the rule x-extent (a cell
    border fragment) delimits nothing."""
    from iladub.etkl.geometry import weld_hrule_boxes
    a = Line((Word("A", 80, 90, 110, 118),), 110, 118)
    b = Line((Word("B", 80, 90, 150, 158),), 150, 158)
    full = [HRule(105.0, 72.0, 300.0), HRule(140.0, 72.0, 300.0), HRule(170.0, 72.0, 300.0)]
    partial = [HRule(130.0, 72.0, 120.0)]          # spans a fraction of the width
    assert weld_hrule_boxes([a, b], full, [72.0, 300.0]) == [a, b]
    assert weld_hrule_boxes([a, b], full + partial, [72.0, 300.0]) == [a, b]


def test_weld_without_hrules_is_identity():
    from iladub.etkl.geometry import weld_hrule_boxes
    a = Line((Word("A", 80, 90, 110, 118),), 110, 118)
    assert weld_hrule_boxes([a], [], [72.0, 300.0]) == [a]
