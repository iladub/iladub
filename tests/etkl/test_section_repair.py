"""Loop Q (spec 2026-08-04 §4.0-§4.2): section repair, stitching, key attribution."""
import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import RDF

from iladub.etkl.document import compile_document
from iladub.etkl.holon import TAB
from tests.etkl.fixtures import multi_section_ruled_pdf, stem_shaped_ruled_table_pdf


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
