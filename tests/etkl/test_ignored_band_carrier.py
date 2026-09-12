"""R212 — the band the reader ignored carries its text.

Plan: docs/superpowers/plans/2026-09-12-the-ignored-band-carries-its-text.md, Tasks 2 and 3.
Spec: docs/superpowers/specs/2026-09-12-the-ignored-band-carries-its-text-design.md.

NOT corpus-gated: the pages are built with reportlab, so these run in CI. The corpus arm
(graincorp's own title and footer) is a separate, local measurement — a green CI is not
evidence for it (spec § 5 arm 5).
"""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from pyshacl import validate  # noqa: E402
from reportlab.lib.pagesizes import letter  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402
from rdflib import Graph, Namespace, URIRef, RDF  # noqa: E402
from rdflib.namespace import SH, XSD  # noqa: E402

from iladub.etkl.bands import band_text  # noqa: E402
from iladub.etkl.compile import compile_tables, page_bands, _DOC  # noqa: E402
from iladub.etkl.regions import RegionKind, classify  # noqa: E402

ETKL = Namespace("https://w3id.org/iladub/etkl#")
ILADUB = Namespace("https://w3id.org/iladub#")
TAB = Namespace("https://w3id.org/iladub/tab#")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHAPE_FILE = os.path.join(ROOT, "vocab", "shapes", "etkl-shapes.ttl")
ONT_FILES = [os.path.join(ROOT, "vocab", "ontology", f) for f in ("etkl.ttl", "iladub.ttl")]

PAGE_H = letter[1]
RULES = (72.0, 200.0, 330.0, 460.0)
HEAD = (("Year", 80.0), ("Period", 210.0), ("Mackay", 340.0))
COLS = (80.0, 210.0, 340.0)
ROWS = (("2026", "Jan-Mar", "845870"), ("2026", "Apr-Jun", "365844"),
        ("2027", "Jul-Sep", "524410"), ("2027", "Oct-Dec", "1063533"))
TITLE = "ELEVATION CAPACITY TABLE"
FOOTER = "GrainCorp advise that the tonnages shown are indicative only."


def _furniture_pdf(path):
    """A one-line title, a ruled 3-column table, a one-line footer.

    MEASURED (plan Task 2, this session, and evidence § 3 independently): this page bands as
    b0 NON_TABLE 'fewer than 2 lines' / b1 RECORD_TABLE / b2 NON_TABLE 'fewer than 2 lines',
    and before the carrier existed its 420 triples contained ZERO occurrences of the title or
    the footer.
    """
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 9)
    c.drawString(72.0, PAGE_H - 60.0, TITLE)
    y = PAGE_H - 200.0
    for x in RULES:
        c.line(x, y - 4.0, x, y + 14.0)
    for (t, x) in HEAD:
        c.drawString(x, y, t)
    for i, row in enumerate(ROWS):
        for x, cell in zip(COLS, row):
            c.drawString(x, y - 20.0 - i * 14.0, cell)
    c.drawString(72.0, PAGE_H - 500.0, FOOTER)
    c.save()
    return str(path)


def _marker_pdf(path):
    """A borderless two-line block whose first column is a currency marker.

    After `absorb_unit_markers` (compile.py:394, which runs BEFORE the band loop) the
    remainder is one column, so the band is BOTH ignored and marker-carrying — the only
    shape of band on which DECISION C's two subjects can collide.
    """
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 9)
    y = PAGE_H - 90.0
    for i, val in enumerate(("845870", "365844")):
        c.drawString(80.0, y - i * 14.0, "$")
        c.drawString(140.0, y - i * 14.0, val)
    c.save()
    return str(path)


@pytest.fixture(scope="module")
def furniture(tmp_path_factory):
    p = _furniture_pdf(tmp_path_factory.mktemp("r212") / "furniture.pdf")
    return p, page_bands(p, 0), compile_tables(p, 0)


@pytest.fixture(scope="module")
def marker(tmp_path_factory):
    p = _marker_pdf(tmp_path_factory.mktemp("r212") / "marker.pdf")
    return p, page_bands(p, 0), compile_tables(p, 0)


def _shape_and_ont():
    sg = Graph()
    sg.parse(SHAPE_FILE, format="turtle")
    og = Graph()
    for o in ONT_FILES:
        og.parse(o, format="turtle")
    return sg, og


def _carried(g):
    """{band index: subject} for every carried ignored band in the graph."""
    return {int(g.value(s, ETKL.bandIndex)): s
            for s in g.subjects(RDF.type, ETKL.IgnoredBand)}


def test_the_fixture_bands_as_measured(furniture):
    """The fixture is the RED state's page. If this fails, adjust the fixture — never the
    assertions below, which are what the loop exists to pin."""
    _, bands, _ = furniture
    kinds = [(classify(b).kind, classify(b).reason) for b in bands]
    assert [k for k, _ in kinds] == [RegionKind.NON_TABLE, RegionKind.RECORD_TABLE,
                                     RegionKind.NON_TABLE], kinds


def test_ignored_bands_carry_their_exact_text(furniture):
    """Assertion 1. Exact string equality with `bands.band_text` for the band itself —
    not a substring match, which would pass on any graph that merely mentioned the words."""
    _, bands, rep = furniture
    carried = _carried(rep.graph)
    assert set(carried) == {0, 2}, carried
    for idx in (0, 2):
        assert str(rep.graph.value(carried[idx], ETKL.bandText)) == band_text(bands[idx])
    assert str(rep.graph.value(carried[0], ETKL.bandText)) == TITLE
    assert str(rep.graph.value(carried[2], ETKL.bandText)) == FOOTER


def test_carried_bands_keep_their_band_index(furniture):
    """Assertion 2. The indices are the positions `page_bands` returned — the title is
    band 0 and the footer band 2, with the record table at 1 between them."""
    _, bands, rep = furniture
    assert sorted(_carried(rep.graph)) == [0, 2]
    assert len(bands) == 3


def test_each_carried_band_reaches_its_page(furniture):
    """Assertion 3. Provenance to the page (CLAUDE.md §6) through the source region,
    typed xsd:integer — the form `iladub:onPage`'s narrowed domain requires."""
    _, _, rep = furniture
    g = rep.graph
    for idx, s in _carried(g).items():
        region = g.value(s, ILADUB.fromRegion)
        assert region is not None, f"band {idx} carries no source region"
        assert (region, RDF.type, ILADUB.SourceRegion) in g
        page = g.value(region, ILADUB.onPage)
        assert page is not None, f"band {idx}'s region carries no page"
        assert page.datatype == XSD.integer, page.datatype
        assert int(page) == 0


def test_the_record_table_band_mints_no_carried_node(furniture):
    """Assertion 4. Carriage is scoped to the IGNORED verdict: the band the reader read
    is asserted as a table and carries no etkl:IgnoredBand of its own.

    The population is pinned non-empty FIRST, deliberately: `1 not in carried` alone passes
    vacuously on a graph with no carried bands at all, so with the emitter deleted it would
    stay green while pinning nothing (CLAUDE.md § Plan authoring, defect 5, in assertion form).
    Measured: without the `len(...) == 2` clause this test survives the Task 2 falsification."""
    _, _, rep = furniture
    carried = _carried(rep.graph)
    assert len(carried) == 2, carried
    assert 1 not in carried
    assert URIRef(f"{_DOC}#ignored1") not in set(rep.graph.subjects())


def test_the_carrier_and_the_unit_marker_hanger_are_disjoint(marker):
    """Assertion 5 — DECISION C. On a band that is BOTH ignored and marker-carrying, the
    carrier's subject and the unit-marker hanger are different IRIs, and neither carries the
    other's vocabulary. Reusing one node would fuse two vocabularies the membrane governs
    separately."""
    _, bands, rep = marker
    g = rep.graph
    assert len(bands) == 1 and bands[0].unit_markers, "fixture built no marker-carrying band"
    assert classify(bands[0]).kind is RegionKind.NON_TABLE

    carrier = URIRef(f"{_DOC}#ignored0")
    hanger = URIRef(f"{_DOC}#region0")
    assert carrier != hanger
    assert (carrier, RDF.type, ETKL.IgnoredBand) in g
    assert (hanger, RDF.type, ETKL.IgnoredBand) not in g
    assert list(g.predicate_objects(hanger)), "fixture minted no unit-marker hanger"
    assert not [p for p in g.predicates(carrier) if str(p).startswith(str(TAB))]
    assert not [p for p in g.predicates(hanger) if str(p).startswith(str(ETKL))]


def test_a_real_compiled_graph_conforms_to_the_whole_etkl_shape_file(furniture):
    """Task 3 / DECISION D — THIS TEST IS THE ENFORCEMENT.

    `etkl:IgnoredBandShape` is deliberately NOT wired into any compile membrane. `_validate`
    runs only when the page graph already holds a `tab:RecordTable` / `tab:HierarchicalTable`
    (compile_tables' `validate_shapes` guard), so a page of pure furniture — precisely the page
    with the MOST ignored bands — never reaches a shape at all; wiring would buy enforcement
    that LOOKS total while being silently absent exactly where the carrier matters most, which
    is failing upward (CLAUDE.md §7). The shape is therefore run here, against a REAL compiled
    page graph and not only against the hand-written example in tests/test_vocab_shapes.py.
    """
    _, _, rep = furniture
    sg, og = _shape_and_ont()
    conforms, _, text = validate(rep.graph, shacl_graph=sg, ont_graph=og,
                                 inference="rdfs", advanced=True)
    assert conforms, text


def test_the_ignored_band_shape_is_the_only_one_that_fires_on_a_page_graph(furniture):
    """DECISION D's seam, MEASURED and pinned rather than assumed.

    Validating a compiled graph against the whole file also loads `DocumentProjectionShape`
    and `MembraneHealthShape`. A compiled PAGE graph is *expected* to contain no
    `etkl:DocumentProjection` and no `etkl:CompiledDocumentHolon` — but expected is not
    measured, and validating against a shape you did not expect to fire is a finding.

    Scoped to PAGE graphs deliberately: at DOCUMENT scope `MembraneHealthShape` would fire too
    (document.py mints an `etkl:MembraneValidation` and manages `etkl:membraneHealth` on the
    document holon), and that is not a defect.
    """
    _, _, rep = furniture
    sg, og = _shape_and_ont()
    merged = rep.graph + og
    counts = {}
    for shape in sg.subjects(RDF.type, SH.NodeShape):
        for tc in sg.objects(shape, SH.targetClass):
            counts[str(shape).split("#")[-1]] = len(set(merged.subjects(RDF.type, tc)))
    assert counts["IgnoredBandShape"] == 2, counts
    assert {k: v for k, v in counts.items() if v} == {"IgnoredBandShape": 2}, counts
