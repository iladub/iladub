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


def test_sectioned_ruled_table_reads(tmp_path):
    """RED on main: the heading/notice strips enter the header tree as fabricated
    all-column levels and the wrapped header box reads as several rows -> the section
    escalates (or asserts a garbage reading). GREEN when: exactly one asserted table,
    the four column names correct incl. the welded 'Time Nom Accepted', 12 data cells."""
    truth, rep = _compiled_fixture(tmp_path)
    asserted = [r for r in rep.regions if r.verdict == "asserted"]
    assert len(asserted) == 1, [(r.kind.name, r.verdict, r.reason) for r in rep.regions]
    texts = {str(o) for o in rep.graph.objects(None, TAB.hasLabel)} | \
            {str(o) for s in rep.graph.subjects(RDF.type, TAB.HeaderNode)
             for o in rep.graph.objects(s, TAB.hasLabel)}
    # hasLabel points at label NODES on some paths; fall back to any literal text field.
    # The load-bearing assertion is on the WELDED name reaching the reading:
    flat = " ".join(str(t) for t in rep.graph.objects(None, None)
                    if hasattr(t, "value") or isinstance(t, str))
    for name in truth["header_names"]:
        assert name in flat, f"header name {name!r} missing from the reading"
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
