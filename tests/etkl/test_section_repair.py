"""Loop Q (spec 2026-08-04 §4.0-§4.2): section repair, stitching, key attribution."""
import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import RDF
from rdflib.compare import isomorphic

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


def test_header_box_text_picks_the_header_stack_not_the_notices_strip(tmp_path):
    """Fix round 2 (task review, 2026-08-04): MEASURED on the real CBH specimen —
    real sections draw an ADDITIONAL full-width hrule separating the heading strip
    from the notice strip (three boxes stacked: heading, notices, header), which the
    original `multi_section_ruled_pdf` lacked. `_leading_box_y`'s box-0-only
    selection then picked the NOTICES box (its text differs per section: the
    section's own notice), never the true header box ('Time Nom' / 'ID Accepted
    Client Volume', identical across sections) -> `section_candidates` silently
    returned no group on the real page. `multi_section_ruled_pdf(strip_separators=
    True)` reproduces that extra separator; this pins the FIX directly on
    `tab:headerBoxText`'s content, via the public `section_evidence` graph."""
    from rdflib import Literal
    from iladub.etkl.compile import page_bands
    from iladub.etkl.sectiongraph import section_evidence, TAB
    pdf = tmp_path / "multi_strips.pdf"
    multi_section_ruled_pdf(str(pdf), strip_separators=True)
    bands = page_bands(str(pdf))
    ruled = [(i, b, b.rules) for i, b in enumerate(bands) if b.rules]
    assert len(ruled) == 2, ruled
    g = section_evidence(ruled)
    texts = {str(t) for t in g.objects(None, TAB.headerBoxText)}
    assert texts, "no band emitted a headerBoxText fact at all"
    for t in texts:
        assert "Time Nom" in t and "ID Accepted Client Volume" in t, texts
        assert "BERTH MAY" not in t and "VESSEL DELAYED" not in t, texts


def test_section_candidates_groups_real_cbh_shaped_bands_with_strip_separators(tmp_path):
    """The end-to-end counterpart of the unit above, over the public API: with the
    extra heading/notice separator (the real CBH shape), the two sections still
    repeat the SAME header box and rule-x signature -> ONE group of both band
    indices, exactly as the simpler (pre-fix-round-2) fixture already pinned."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.sectiongraph import section_candidates
    pdf = tmp_path / "multi_strips.pdf"
    multi_section_ruled_pdf(str(pdf), strip_separators=True)
    bands = page_bands(str(pdf))
    ruled = [(i, b, b.rules) for i, b in enumerate(bands) if b.rules]
    assert len(ruled) == 2, ruled
    groups = section_candidates(ruled)
    assert groups == ((0, 1),), groups


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


def _doubled_border_band_and_rules():
    """The doubled-outer-border evidence shared by
    `test_grid_lines_ink_witness_defeats_doubled_border` and
    `test_interior_rule_xs_excludes_doubled_border` (review round 1 minor): one
    band, four visual lines (heading/notice above the grid, two grid rows below),
    six rules — a true outer pair (72.0/300.0), their doubled TWINS
    (71.7/300.3), and the two real interior column separators (150.0/220.0)."""
    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Line, Rule, Word
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
    return band, rules


def test_grid_lines_ink_witness_defeats_doubled_border():
    """Resurrected from reverted b515283 (`test_grid_lines_interior_rule_presence`),
    renamed + flag-scoped to loop Q's repair path: a line is grid iff an INTERIOR
    rule (ink witness: some band word CENTER on BOTH sides, tab:hasInkLeft/
    tab:hasInkRight) crosses it. A double-drawn outer-border twin, positioned
    strictly between the true outer rule and the far border — which widens the
    default min/max-x span so the TRUE outer rule wrongly passes IT as interior —
    has no ink on its own outboard side, so `ink_witness=True` never admits either
    the twin or the true outer rule as interior."""
    from iladub.etkl.gridregion import grid_lines
    band, rules = _doubled_border_band_and_rules()
    assert grid_lines(band, rules, ink_witness=True) == {2, 3}
    # the default (band-level, non-repair) path stays byte-identical to today's
    # shipped inertness: the min/max-x test now admits the TRUE outer rules
    # (72.0/300.0, no longer the extreme min/max once the twins extend it) as
    # "interior" too, whose full 58-145 y-extent crosses every line -- exactly the
    # defeat section-scope repair exists to fix (gridregion.grid_lines's inertness
    # note), pinned here as the contrast, not a bug in this test.
    assert grid_lines(band, rules) == {0, 1, 2, 3}


def test_interior_rule_xs_excludes_doubled_border():
    """Minor (review round 1): `interior_rule_xs`, salvaged alongside `grid_lines`
    but never directly pinned, on the SAME evidence as the test above: only the
    two real interior column separators (150.0, 220.0) have ink on BOTH sides —
    the true outer rules AND their doubled twins (71.7/72.0/300.0/300.3) never
    qualify, however close a twin sits to another rule x (R31: presence, not
    distance)."""
    from iladub.etkl.gridregion import interior_rule_xs
    band, rules = _doubled_border_band_and_rules()
    assert interior_rule_xs(band, rules) == [150.0, 220.0]


def test_grid_region_ink_query_has_no_numeric_literal():
    """§8, same gate as grid-region.rq/section-repeat.rq: every number in the
    ink-witness AXIOM is a FACT emitted by gridregion.py, never a literal."""
    import re
    from pathlib import Path
    text = Path("vocab/queries/grid-region-ink.rq").read_text()
    body = re.sub(r"#[^\n]*", "", text)
    assert not re.search(r"\b\d+\.?\d*\b", body), "numeric literal in the AXIOM"


def _report_signature(rep):
    """Every DETERMINISTIC, non-BNode-bearing field of a CompilationReport, for a
    byte-identity comparison across two separate `compile_tables` calls.
    `r.ascii` is included after verifying empirically (review round 1 F1: not
    assumed) that it renders identically across both calls on all three fixtures
    this pin exercises. `r.table_uri`/`r.header_reading` are deliberately NOT
    listed here: `table_uri` is a plain URIRef (no BNode), so any mismatch there
    would already break `rep.graph`'s isomorphism check below; `header_reading`
    is an opaque object with no `__eq__` worth pinning on its own."""
    return (
        [(r.kind, r.verdict, r.reason, r.cells, r.ascii) for r in rep.regions],
        rep.score, rep.asserted, rep.escalated,
    )


def test_section_repair_bands_none_is_byte_identical(tmp_path):
    """Task 3's cardinal pin: `section_repair_bands=None` (or omitted entirely)
    never changes a single band's read -- the default path stays byte-identical to
    today's shipped behavior, on THREE distinct shapes: the loop-P clean
    single-section fixture, the stem-shaped (unruled-header) fixture, and the
    doubled-edge multi-section fixture this very flag exists to repair (its bands
    must escalate identically with or without the parameter present -- Task 4 is
    what actually repairs them).

    Review round 1 F1: the report-field comparison alone (kind/verdict/reason/
    cells/ascii/score/asserted/escalated) is necessary but not sufficient -- it
    never looks at `rep.graph`, the actual compiled PRODUCT. Strengthened with an
    ISOMORPHISM-aware graph comparison (`rdflib.compare.isomorphic`, NOT turtle-
    string / triple-set equality): `holon.py` mints raw BNodes for cell/row
    structure, so two runs' graphs can be the correct SAME graph without being
    triple-for-triple identical (a BNode's opaque local id is not stable across
    two independent compiles) -- isomorphism is the right notion of graph
    equality here, exactly as `rdflib.compare`'s own docs recommend for BNode-
    bearing graphs."""
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
        assert isomorphic(omitted.graph, explicit_none.graph), name


def test_section_repair_bands_targets_only_the_named_index(tmp_path):
    """F2 (review round 1): the flag's positive reach through the PUBLIC path was
    untested -- every other test in this file either calls `_build_ruled_band`
    directly (bypassing the `idx in section_repair_bands` glue) or passes
    `section_repair_bands=None` (never exercising the `True` branch at all). This
    pins the selection mechanism itself, through `page_bands` -- the same public
    glue `compile_tables` forwards to and Task 4's driver will call.

    Index mapping verified empirically (not assumed) with a probe script on
    `multi_section_ruled_pdf`: `page_bands` returns exactly 2 bands, both ruled,
    in page order -- band 0 = the GERALDTON section (top ~66.7), band 1 = the
    KWINANA section (top ~256.7).

    The honest MINIMAL form (per the review note): full `compile_tables`
    assertion state does not yet change here -- probed separately, the region
    still classifies MATRIX_AMBIGUOUS regardless of whether band 0 peeled,
    because that classification happens upstream of the caption carry
    (`_emit_band_captions` never runs for an escalated region); making the
    peel's effect reach a compiled VERDICT is Task 4's job (recognition +
    pass-2 re-compile + monotone adoption), not this task's. What Task 3 owns,
    and what this test pins directly, is that `section_repair_bands={0}` peels
    ONLY band 0's captions -- band 1, excluded from the set, stays exactly as
    inert as the shipped default."""
    from iladub.etkl.compile import page_bands
    pdf = tmp_path / "multi.pdf"
    truth = multi_section_ruled_pdf(str(pdf))
    bands = page_bands(str(pdf), section_repair_bands=frozenset({0}))
    assert len(bands) == 2, bands
    assert bands[0].captions, bands[0].captions
    texts0 = [" ".join(w.text for w in ln.words) for ln in bands[0].captions]
    assert any(truth["sections"][0]["key"] in t for t in texts0), texts0
    assert bands[1].captions == (), bands[1].captions


# --- Task 4: the driver's section repair — recognition, pass-2 re-compile, monotone
# adoption, intra-page chains, arithmetic totals (spec §4.0/§4.1 as corrected) ---


def test_adoption_withdraws_the_pass1_escalation_record(tmp_path):
    """Adopting a band's pass-2 re-read SUPERSEDES its pass-1 escalation record: the
    `#region{idx}` CandidateConcept triples are withdrawn whole (two parallel truths
    over one band would leave the feed to pick by iteration order — the
    _supersede_page_groups idiom), the adoption is recorded on `repaired_bands`, and
    the page's score is recomputed honestly from the per-band token ledger."""
    from rdflib import URIRef
    from iladub.etkl.document import page_doc_uri
    from iladub.etkl.holon import ILADUB
    pdf = tmp_path / "multi.pdf"
    multi_section_ruled_pdf(str(pdf))
    rep = compile_document(str(pdf))
    assert rep.repaired_bands == ((0, 0), (0, 1)), rep.repaired_bands
    for idx in (0, 1):
        cand = URIRef(f"{page_doc_uri(0)}#region{idx}")
        assert not list(rep.graph.predicate_objects(cand)), cand
    assert not list(rep.graph.subjects(RDF.type, ILADUB.CandidateConcept))
    assert rep.score == 1.0, rep.score
    # the per-band token ledger's invariant: the page totals ARE the bands' sums
    page = rep.pages[0]
    assert sum(r.tokens_asserted for r in page.regions) == page.asserted
    assert sum(r.tokens_escalated for r in page.regions) == page.escalated


def test_adoption_swaps_only_asserting_bands(tmp_path, monkeypatch):
    """A recognized candidate whose pass-2 re-read STILL escalates is left byte-
    untouched — its pass-1 report (verdict, reason) stands, its pass-1 escalation
    record stays in the graph, it never enters `repaired_bands` (only ADOPTED bands
    do), and the refusal is recorded as a report note. Simulated by failing band 1's
    pass-2 read at the driver's own seam (the /r2-scoped compile_tables call)."""
    from dataclasses import replace as dc_replace
    from rdflib import URIRef
    import iladub.etkl.document as docmod
    real = docmod.compile_tables

    def failing_pass2(pdf_path, page_number=0, **kw):
        rep = real(pdf_path, page_number=page_number, **kw)
        doc_uri = kw.get("doc_uri")
        if doc_uri is not None and str(doc_uri).endswith("/r2"):
            regs = list(rep.regions)
            regs[1] = dc_replace(regs[1], verdict="escalated",
                                 reason="SIMULATED_PASS2_FAIL", cells=0, table_uri=None)
            rep = dc_replace(rep, regions=tuple(regs))
        return rep

    monkeypatch.setattr(docmod, "compile_tables", failing_pass2)
    pdf = tmp_path / "multi.pdf"
    multi_section_ruled_pdf(str(pdf))
    rep = docmod.compile_document(str(pdf))
    assert rep.repaired_bands == ((0, 0),), rep.repaired_bands
    page = rep.pages[0]
    assert page.regions[0].verdict == "asserted"
    # band 1's PASS-1 report stands — the simulated pass-2 reason never leaks into it
    assert page.regions[1].verdict == "escalated"
    assert page.regions[1].reason == "MATRIX_AMBIGUOUS", page.regions[1].reason
    assert any("band 1" in n and "still escalated" in n for n in rep.notes), rep.notes
    cand1 = URIRef(f"{docmod.page_doc_uri(0)}#region1")
    assert list(rep.graph.predicate_objects(cand1)), "pass-1 escalation must survive"
    cand0 = URIRef(f"{docmod.page_doc_uri(0)}#region0")
    assert not list(rep.graph.predicate_objects(cand0)), "adopted band's record withdrawn"
    # one section asserting alone cannot chain
    assert not any(len(c) == 2 for c in rep.chains), rep.chains
    assert 0.0 < rep.score < 1.0, rep.score


def test_section_totals_associate_on_the_fixture(tmp_path):
    """with_totals=True: each section's printed TOTAL row reconciles exactly with its
    own section's Volume-column Decimal sum -> tab:SectionTotal + tab:confirmsSection
    for BOTH sections, and no refusal note."""
    pdf = tmp_path / "multi.pdf"
    multi_section_ruled_pdf(str(pdf))
    rep = compile_document(str(pdf))
    tables = {r.table_uri for r in rep.pages[0].regions if r.verdict == "asserted"}
    confirms = list(rep.graph.subject_objects(TAB.confirmsSection))
    assert {o for _, o in confirms} == tables and len(confirms) == 2, confirms
    assert len(set(rep.graph.subjects(RDF.type, TAB.SectionTotal))) == 2
    assert not rep.notes, rep.notes


def test_section_totals_refuse_tampered_total(tmp_path):
    """bad_total_in=1: KWINANA's printed total is off by one, so the exact-arithmetic
    oracle REFUSES the association — no tab:SectionTotal/tab:confirmsSection for that
    section (absence, never a guess) plus a report note — while GERALDTON's total
    still associates and the intra-page stitch itself is unaffected."""
    pdf = tmp_path / "multi.pdf"
    multi_section_ruled_pdf(str(pdf), bad_total_in=1)
    rep = compile_document(str(pdf))
    confirms = list(rep.graph.subject_objects(TAB.confirmsSection))
    assert len(confirms) == 1, confirms
    (_, table), = confirms
    assert str(table).endswith("table0"), table
    assert any("does not reconcile" in n for n in rep.notes), rep.notes
    assert any(len(c) == 2 for c in rep.chains), rep.chains


def test_without_totals_nothing_associates_and_stitch_only_path_chains(tmp_path):
    """with_totals=False: MEASURED (not assumed) — dropping the total line pulls the
    band's bottom up to the last data row, which drops the grid's closing hrule out of
    the band's hrule set, and BOTH sections then assert at BAND level (the loop-L
    ruled path, htable URIs). That makes this fixture the stitch-only witness for
    spec §4.0's corrected point 1: members that already assert pass through untouched
    (`repaired_bands` stays EMPTY — repair never fires on an asserting band) and §4.1
    stitching runs over them all the same, 'whichever route they took'. And with no
    trailing strip below any closing rule there is no total CANDIDATE at all: the
    oracle emits nothing and notes nothing (a refusal note is for a printed total
    that fails, not for a total that was never drawn)."""
    pdf = tmp_path / "multi.pdf"
    multi_section_ruled_pdf(str(pdf), with_totals=False)
    rep = compile_document(str(pdf))
    page = rep.pages[0]
    assert [r.verdict for r in page.regions] == ["asserted", "asserted"], page.regions
    assert rep.repaired_bands == (), rep.repaired_bands
    assert not list(rep.graph.subjects(RDF.type, TAB.SectionTotal))
    assert not rep.notes, rep.notes
    assert any(len(c) == 2 for c in rep.chains), rep.chains
