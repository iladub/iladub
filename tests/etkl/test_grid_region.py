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
    """A line is grid iff an INTERIOR rule (ink witness: some band word CENTER on
    BOTH sides) crosses it. Outer-border segments — including a double-drawn twin
    positioned strictly between the true outer rule and the far border, which would
    wrongly pass an x-distance-tolerance test — never make a line grid, because they
    have no ink on their own outboard side (loop P fixwave A)."""
    from iladub.etkl.gridregion import grid_lines
    heading = Line((Word("HEADING", 80, 136, 60, 70),), 60, 70)
    notice = Line((Word("NOTICE", 80, 128, 75, 85), Word("TEXT", 138, 170, 75, 85)), 75, 85)
    row_a = Line((Word("A", 80, 100, 110, 120), Word("B", 160, 200, 110, 120),
                  Word("C", 240, 280, 110, 120)), 110, 120)
    row_1 = Line((Word("1", 80, 100, 130, 140), Word("2", 160, 200, 130, 140),
                  Word("3", 240, 280, 130, 140)), 130, 140)
    lines = (heading, notice, row_a, row_1)      # heading/notice: above interior rules
    band = Band(lines, 60.0, 140.0)
    rules = [Rule(72.0, 58.0, 145.0),             # outer left (full extent)
             Rule(71.7, 58.0, 145.0),             # outer-left TWIN (doubled border)
             Rule(300.0, 58.0, 145.0),            # outer right
             Rule(300.3, 58.0, 145.0),            # outer-right TWIN (doubled border)
             Rule(150.0, 105.0, 145.0),           # INTERIOR: ink on both sides
             Rule(220.0, 105.0, 145.0)]           # INTERIOR: ink on both sides
    assert grid_lines(band, rules) == {2, 3}


def test_grid_lines_abstains_without_interior_rules():
    """Only the two outer rules -> no interior evidence -> abstain (empty set):
    behavior falls back to main's, byte-identical."""
    from iladub.etkl.gridregion import grid_lines
    lines = (_line(60, 70, "A", "B"), _line(80, 90, "1", "2"))
    band = Band(lines, 60.0, 90.0)
    rules = [Rule(72.0, 55.0, 95.0), Rule(300.0, 55.0, 95.0)]
    assert grid_lines(band, rules) == set()


def test_peel_leading_captions_only():
    """Loop P fix round 2 (regression repair): the peel's scope is a LEADING strip
    only (spec §3) — a TRAILING full-width line (a subtotal/total row below the grid)
    must SURVIVE in the band, never peeled. Peeling every non-grid line (the original
    Task-2 shape) swallowed page-local subtotal rows loop H/N's arithmetic derivations
    must see (test_continuation_licence/test_logical_arithmetic regression)."""
    from iladub.etkl.gridregion import grid_lines, enclosed_lines, interior_rule_xs, \
        straddling_lines, peel_leading_captions
    # HEADING's word straddles x=150 (x0=130 < 150 < x1=170), the fixwave A round 2
    # witness that distinguishes a peelable full-width strip from genuine column
    # content (CBH's "GERALDTON"/notice strips chop mid-word at every interior rule
    # they cross; a real header row's words never do — see straddling_lines).
    heading = Line((Word("HEADING", 130, 170, 60, 70),), 60, 70)  # above interior rules -> LEADING, peeled
    row_a = Line((Word("A", 80, 100, 110, 120), Word("B", 160, 200, 110, 120),
                  Word("C", 240, 280, 110, 120)), 110, 120)        # crossed by interior rules -> grid
    row_1 = Line((Word("1", 80, 100, 130, 140), Word("2", 160, 200, 130, 140),
                  Word("3", 240, 280, 130, 140)), 130, 140)        # crossed by interior rules -> grid
    total = Line((Word("TOTAL", 80, 120, 150, 160),), 150, 160)   # below interior rules -> TRAILING, kept
    lines = (heading, row_a, row_1, total)
    band = Band(lines, 60.0, 160.0)
    rules = [Rule(72.0, 58.0, 145.0),            # outer left (full extent)
             Rule(300.0, 58.0, 145.0),           # outer right
             Rule(150.0, 105.0, 145.0),          # INTERIOR: ink on both sides
             Rule(220.0, 105.0, 145.0)]          # INTERIOR: ink on both sides
    gset = grid_lines(band, rules)
    assert gset == {1, 2}
    enclosed = enclosed_lines(band, rules)       # HEADING (60-70) IS inside the outer rules' 58-145
    ixs = interior_rule_xs(band, rules)
    straddling = straddling_lines(band, ixs)
    assert 0 in straddling, straddling           # HEADING's word crosses x=150
    captions, kept = peel_leading_captions(lines, gset, enclosed, straddling)
    assert captions == (lines[0],)
    assert kept == (lines[1], lines[2], lines[3])   # TOTAL line survives, unpeeled


def test_peel_leading_captions_no_op_without_leading_strip():
    """No leading non-grid line (min(gset) == 0) -> identity, nothing peeled — the
    interior/trailing-only case (e.g. a bare grid with a trailing total and no
    heading) is main's byte-identical behavior."""
    from iladub.etkl.gridregion import peel_leading_captions
    lines = (_line(110, 120, "A", "B"), _line(130, 140, "1", "2"), _line(150, 160, "TOTAL"))
    captions, kept = peel_leading_captions(lines, {0, 1}, {0, 1, 2})
    assert captions == ()
    assert kept == lines


def test_peel_never_swallows_an_unenclosed_header_row():
    """Loop P fix round 2's actual root cause, pinned directly: a LEADING non-grid
    line that is NOT enclosed by any rule's y-extent (a merged parent header row like
    'Voyage', drawn with no rule anywhere near it — page_local_group_two_page_pdf's and
    case3_with_subtotals_pdf's shape, where the interior rules start exactly at the
    leaf header row and exclude the spanning parent above it) is NEVER peeled — the
    'leading-only' guard alone is INSUFFICIENT (it still swallowed this real case,
    since the floating row happens to be the sole leading line); enclosure is the
    second, necessary guard."""
    from iladub.etkl.gridregion import grid_lines, enclosed_lines, interior_rule_xs, \
        straddling_lines, peel_leading_captions
    # "Voyage" floats at 16.9-25.9 with NO rule covering that y-range at all (rules
    # start at y=30) -- mirrors the real fixtures' measured geometry.
    lines = (_line(16.9, 25.9, "Voyage"),
             _line(32.9, 41.9, "Mon", "Port", "Ship", "Qty", "Berth"),
             _line(49.7, 57.7, "Jul", "Mackay", "V3", "100", "B3"))
    band = Band(lines, 16.9, 57.7)
    rules = [Rule(36.0, 30.0, 94.0), Rule(106.0, 30.0, 94.0), Rule(186.0, 30.0, 94.0),
             Rule(246.0, 30.0, 94.0), Rule(316.0, 30.0, 94.0), Rule(364.0, 30.0, 94.0)]
    gset = grid_lines(band, rules)
    assert gset == {1, 2}, gset          # "Voyage" (index 0) is not grid -> leading candidate
    enclosed = enclosed_lines(band, rules)
    assert 0 not in enclosed, enclosed   # "Voyage" is not covered by ANY rule's y-extent
    ixs = interior_rule_xs(band, rules)
    straddling = straddling_lines(band, ixs)
    captions, kept = peel_leading_captions(lines, gset, enclosed, straddling)
    assert captions == ()                # NOT peeled -> region stays HierarchicalTable-eligible
    assert kept == lines


def test_peel_never_swallows_a_rule_aligned_header_stack():
    """Loop P fixwave A round 2 (measured on the real GrainCorp stem): a leading
    line that IS enclosed by the outer rule's y-extent, but whose words sit
    strictly INSIDE one rule column each (no straddling ink across any interior
    rule -- the stem's leaf header / wrap rows, e.g. 'GC Fin Year Month Port',
    one word per column), must NOT be peeled. The stem's interior verticals begin
    BELOW the header stack, so the whole stack is 'above the rules' extent' and
    enclosed by the outer box -- "leading + enclosed" alone wrongly peeled it as a
    full-width strip, flattening a genuine header row into a headerless
    RECORD_TABLE (measured: score 1.0000 vs truth 0.9655, chains [1,1,1] vs one
    chain of 3, grounded 0 vs 585). Straddling ink is the missing witness."""
    from iladub.etkl.gridregion import grid_lines, enclosed_lines, interior_rule_xs, \
        straddling_lines, peel_leading_captions
    header = Line((Word("GC", 80, 95, 60, 70), Word("Fin", 160, 178, 60, 70),
                   Word("Year", 240, 265, 60, 70)), 60, 70)
    row_a = Line((Word("A", 80, 100, 110, 120), Word("B", 160, 200, 110, 120),
                  Word("C", 240, 280, 110, 120)), 110, 120)
    row_1 = Line((Word("1", 80, 100, 130, 140), Word("2", 160, 200, 130, 140),
                  Word("3", 240, 280, 130, 140)), 130, 140)
    lines = (header, row_a, row_1)
    band = Band(lines, 60.0, 140.0)
    rules = [Rule(72.0, 58.0, 145.0), Rule(300.0, 58.0, 145.0),
             Rule(150.0, 105.0, 145.0), Rule(220.0, 105.0, 145.0)]
    gset = grid_lines(band, rules)
    assert gset == {1, 2}
    enclosed = enclosed_lines(band, rules)
    assert 0 in enclosed, enclosed          # the header line IS enclosed by the outer rule
    ixs = interior_rule_xs(band, rules)
    straddling = straddling_lines(band, ixs)
    assert 0 not in straddling, straddling  # ...but none of its words straddle an interior rule
    captions, kept = peel_leading_captions(lines, gset, enclosed, straddling)
    assert captions == ()                   # NOT peeled -> stays a genuine header row
    assert kept == lines


def test_grid_region_query_has_no_numeric_literal():
    """§8: the derivation reads facts only; every number is emitted by the
    PROCEDURAL layer (the header-covers.rq / tab:inkCenterX precedent)."""
    import re
    from pathlib import Path
    text = Path("vocab/queries/grid-region.rq").read_text()
    body = re.sub(r"#[^\n]*", "", text)          # strip comments
    assert not re.search(r"\b\d+\.?\d*\b", body), "numeric literal in the AXIOM"


def test_line_enclosed_query_has_no_numeric_literal():
    """§8, same gate, for the fix round-2 enclosure AXIOM."""
    import re
    from pathlib import Path
    text = Path("vocab/queries/line-enclosed.rq").read_text()
    body = re.sub(r"#[^\n]*", "", text)
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
