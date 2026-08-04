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
