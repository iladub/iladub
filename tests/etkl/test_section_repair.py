"""Loop Q (spec 2026-08-04 §4.0-§4.2): section repair, stitching, key attribution."""
import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import RDF

from iladub.etkl.compile import compile_tables
from iladub.etkl.document import compile_document
from iladub.etkl.holon import TAB
from tests.etkl.fixtures import (multi_section_ruled_pdf, sectioned_ruled_table_pdf,
                                 stem_shaped_ruled_table_pdf)


def test_sections_repair_and_stitch(tmp_path):
    """RED until Tasks 2-4: both sections escalate at band level (loop P machinery is
    inert by default), the driver's section repair re-reads them, the membrane admits
    the readings, and the chain links them into ONE logical table."""
    pdf = tmp_path / "multi.pdf"
    truth = multi_section_ruled_pdf(str(pdf))
    rep = compile_document(str(pdf))
    page = rep.pages[0]
    asserted = [r for r in page.regions if r.verdict == "asserted"]
    assert len(asserted) >= 2, [(r.kind.name, r.verdict, r.reason) for r in page.regions]
    assert any(len(c) == 2 for c in rep.chains), rep.chains   # the two sections chained
    caps = {str(t) for c in rep.graph.subjects(RDF.type, TAB.RegionCaption)
            for t in rep.graph.objects(c, TAB.captionText)}
    for s in truth["sections"]:
        assert any(s["key"] in c for c in caps), (s["key"], caps)


def test_repair_is_monotone_on_stem_shape(tmp_path):
    """The stem-shaped page must traverse the driver with ZERO repair activity:
    same regions, verdicts, reasons, and graph as a driver without the repair.
    Pins spec §4.0's ordering guarantee structurally.

    `getattr(rep, "repaired_bands", ())` is deliberately tolerant of the attribute not
    existing yet: this pin's job is guarding the FUTURE repair (added in Task 4), not
    requiring it to exist today — until then the getattr default makes the assertion
    trivially true, which is acceptable *for this line*. The asserted-region check below
    is what keeps the pin from being vacuous in the meantime: it fails now if the
    fixture ever stopped compiling (e.g. a coordinate regression), so the pin is never
    "green because nothing ran."""
    pdf = tmp_path / "stemlike.pdf"
    stem_shaped_ruled_table_pdf(str(pdf))
    rep = compile_document(str(pdf))
    page = rep.pages[0]
    asserted = [r for r in page.regions if r.verdict == "asserted"]
    assert len(asserted) >= 1, [(r.kind.name, r.verdict, r.reason) for r in page.regions]
    # the stem-shaped single-section page has no intra-page repetition: the repair
    # must not fire — pin via the driver's own record (Task 4 exposes it):
    assert getattr(rep, "repaired_bands", ()) == ()


# --- Task 2: intra-page section recognition AXIOM (spec §4.0 point 3, corrected) ---
# Recognition is VERDICT-INDEPENDENT: section_candidates takes ALL ruled bands of a
# page (escalated and already-asserting alike) and groups those whose header-box
# text and rule-x signature repeat verbatim. Filtering which members get RE-READ is
# Task 4's job (the membrane's), not this AXIOM's.


def test_section_candidates_groups_two_cbh_shaped_bands(tmp_path):
    """The two doubled-edge CBH sections of `multi_section_ruled_pdf` share the SAME
    author-drawn header box ('Time Nom' / 'ID Accepted Client Volume') and the same
    rule-x set -> section_candidates groups both band indices together."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.sectiongraph import section_candidates
    pdf = tmp_path / "multi.pdf"
    multi_section_ruled_pdf(str(pdf))
    bands = page_bands(str(pdf))
    ruled = [(i, b, b.rules) for i, b in enumerate(bands) if b.rules]
    assert len(ruled) == 2, ruled
    groups = section_candidates(ruled)
    assert groups == ((0, 1),), groups


def test_section_candidates_no_group_for_different_shapes(tmp_path):
    """A stem-shaped band (`stem_shaped_ruled_table_pdf` — different header-box text
    AND a different rule-x set, no doubled edges) never shares a signature with a
    CBH-shaped band -> no group forms, even though both are ruled bands."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.sectiongraph import section_candidates
    stem_pdf = tmp_path / "stem.pdf"
    stem_shaped_ruled_table_pdf(str(stem_pdf))
    stem_bands = [b for b in page_bands(str(stem_pdf)) if b.rules]
    assert len(stem_bands) == 1, stem_bands

    cbh_pdf = tmp_path / "multi.pdf"
    multi_section_ruled_pdf(str(cbh_pdf))
    cbh_bands = [b for b in page_bands(str(cbh_pdf)) if b.rules]
    assert cbh_bands, cbh_bands

    combined = [(0, stem_bands[0], stem_bands[0].rules), (1, cbh_bands[0], cbh_bands[0].rules)]
    assert section_candidates(combined) == ()


def test_section_candidates_single_band_no_group(tmp_path):
    """A single ruled band has nothing to repeat WITH -> no group, ever (a group
    requires >= 2 members by construction)."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.sectiongraph import section_candidates
    pdf = tmp_path / "multi.pdf"
    multi_section_ruled_pdf(str(pdf))
    bands = [b for b in page_bands(str(pdf)) if b.rules]
    assert section_candidates([(0, bands[0], bands[0].rules)]) == ()


def test_section_repeat_query_has_no_numeric_literal():
    """§8: the derivation reads facts only; every number is emitted by the
    PROCEDURAL layer (sectiongraph.py), same gate as loop P's grid-region.rq."""
    import re
    from pathlib import Path
    text = Path("vocab/queries/section-repeat.rq").read_text()
    body = re.sub(r"#[^\n]*", "", text)
    assert not re.search(r"\b\d+\.?\d*\b", body), "numeric literal in the AXIOM"


# --- Task 3: the repair flag — ink-witness peel behind section_repair_bands ---
# (spec §4.0, salvaged from reverted b515283; reachable ONLY via the flag — the
# default band path (section_repair=False / section_repair_bands=None) must stay
# byte-identical to today's shipped behavior).


def _raw_ruled_subs(pdf_path, page_number=0):
    """The pre-`_build_ruled_band` `(sub, sub_rules, sub_hrules, page_chars)` tuples
    for every RULED sub-band of one page — the exact same construction
    `compile.page_bands` performs, stopped one step earlier so a test can call
    `_build_ruled_band` directly on the SAME input with different `section_repair`
    values (mirrors tests/test_corpus_stem.py::_ruled_band_page)."""
    from iladub.etkl.geometry import (extract_words, text_lines, extract_rules,
                                      extract_chars, extract_hrules)
    from iladub.etkl.bands import detect_bands
    from iladub.etkl.segment import segment
    words = extract_words(pdf_path, page_number)
    pr = extract_rules(pdf_path, page_number)
    ph = extract_hrules(pdf_path, page_number)
    pc = extract_chars(pdf_path, page_number) if pr else []
    out = []
    for band in detect_bands(text_lines(words)):
        for sub in segment(band):
            sr = tuple(r for r in pr if r.top <= sub.bottom and r.bottom >= sub.top)
            sh = tuple(h for h in ph if sub.top <= h.y <= sub.bottom)
            if sr:
                out.append((sub, sr, sh, pc))
    return out


def test_section_repair_flag_peels_doubled_edge_captions(tmp_path):
    """Step 1 (RED first): a CBH-shaped doubled-edge band (`multi_section_ruled_pdf`)
    defeats the default band-level min/max-x interior test (grid_lines's inertness
    note — a doubled outer-border twin widens the min/max span so the TRUE outer
    rule itself gets wrongly admitted as "interior", its full-height y-extent
    flooding grid_lines and preventing the caption peel), so `_build_ruled_band`'s
    default peel (`section_repair=False`, the shipped inert behavior) peels NOTHING:
    `band.captions == ()`. Under `section_repair=True` the peel calls
    `grid_lines(..., ink_witness=True)` (grid-region-ink.rq): the twins have no ink
    on their own outboard side, so they are never interior, and the heading/notice
    strip peels off as captions — the ink witness defeats the doubled border."""
    from iladub.etkl.compile import _build_ruled_band
    pdf = tmp_path / "multi.pdf"
    multi_section_ruled_pdf(str(pdf))
    subs = _raw_ruled_subs(str(pdf))
    assert subs, "expected at least one ruled sub-band"
    sub, sr, sh, pc = subs[0]

    inert = _build_ruled_band(sub, sr, sh, pc, section_repair=False)
    assert inert.captions == (), inert.captions

    repaired = _build_ruled_band(sub, sr, sh, pc, section_repair=True)
    assert repaired.captions, "ink-witness peel should defeat the doubled border"
    texts = [" ".join(w.text for w in ln.words) for ln in repaired.captions]
    assert any("GERALDTON" in t for t in texts), texts


def test_grid_lines_ink_witness_defeats_doubled_border():
    """Resurrected from reverted b515283 (`test_grid_lines_interior_rule_presence`),
    renamed + flag-scoped to loop Q's repair path: a line is grid iff an INTERIOR
    rule (ink witness: some band word CENTER on BOTH sides, tab:hasInkLeft/
    tab:hasInkRight) crosses it. A double-drawn outer-border twin, positioned
    strictly between the true outer rule and the far border — which widens the
    default min/max-x span so the TRUE outer rule wrongly passes IT as interior —
    has no ink on its own outboard side, so `ink_witness=True` never admits either
    the twin or the true outer rule as interior."""
    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Line, Rule, Word
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
    assert grid_lines(band, rules, ink_witness=True) == {2, 3}
    # the default (band-level, non-repair) path stays byte-identical to today's
    # shipped inertness: the min/max-x test now admits the TRUE outer rules
    # (72.0/300.0, no longer the extreme min/max once the twins extend it) as
    # "interior" too, whose full 58-145 y-extent crosses every line -- exactly the
    # defeat section-scope repair exists to fix (gridregion.grid_lines's inertness
    # note), pinned here as the contrast, not a bug in this test.
    assert grid_lines(band, rules) == {0, 1, 2, 3}


def test_grid_region_ink_query_has_no_numeric_literal():
    """§8, same gate as grid-region.rq/section-repeat.rq: every number in the
    ink-witness AXIOM is a FACT emitted by gridregion.py, never a literal."""
    import re
    from pathlib import Path
    text = Path("vocab/queries/grid-region-ink.rq").read_text()
    body = re.sub(r"#[^\n]*", "", text)
    assert not re.search(r"\b\d+\.?\d*\b", body), "numeric literal in the AXIOM"


def _report_signature(rep):
    return ([(r.kind, r.verdict, r.reason, r.cells) for r in rep.regions], rep.score)


def test_section_repair_bands_none_is_byte_identical(tmp_path):
    """Task 3's cardinal pin: `section_repair_bands=None` (or omitted entirely)
    never changes a single band's read -- the default path stays byte-identical to
    today's shipped behavior, on THREE distinct shapes: the loop-P clean
    single-section fixture, the stem-shaped (unruled-header) fixture, and the
    doubled-edge multi-section fixture this very flag exists to repair (its bands
    must escalate identically with or without the parameter present -- Task 4 is
    what actually repairs them)."""
    for name, builder in (
        ("sectioned", sectioned_ruled_table_pdf),
        ("stem-shaped", stem_shaped_ruled_table_pdf),
        ("multi-section", multi_section_ruled_pdf),
    ):
        pdf = tmp_path / f"{name}.pdf"
        builder(str(pdf))
        omitted = compile_tables(str(pdf))
        explicit_none = compile_tables(str(pdf), section_repair_bands=None)
        assert _report_signature(omitted) == _report_signature(explicit_none), name
