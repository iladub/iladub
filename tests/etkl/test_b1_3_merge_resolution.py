import os
from dataclasses import replace
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from rdflib import Graph, RDF, URIRef, Namespace
from iladub.etkl import compile_tables
from iladub.etkl.propose import SpanProposal, FakeSpanProposer
from iladub.etkl.span import build_reading, resolve_ambiguous_merge
from iladub.etkl.headers import HeaderNode
from iladub.etkl.holon import assert_hier_region
from iladub.etkl.tiling import region_tiles
from tests.etkl.test_span_gate import _ambiguous_hier_region
from tests.etkl import fixtures as F

ILADUB = Namespace("https://w3id.org/iladub#")


def _reasons(rep):
    return [r.reason for r in rep.regions]


def test_narrow_orphan_resolves_to_asserted_with_promotion():
    # a proposer picks the standalone reading (a legal tiling) -> MERGE_AMBIGUOUS flips to asserted,
    # carrying a PromotionDecision proposition (§3). Both readings are legal for a genuine tie.
    hreg, band = _ambiguous_hier_region()
    assert any(n.ambiguous_flank is not None for n in hreg.tree), "fixture must produce a narrow-flank tie"
    g = Graph()
    fp = FakeSpanProposer(SpanProposal("standalone", 0.8, "flank reads standalone"))
    out = resolve_ambiguous_merge(g, hreg, band, URIRef("urn:doc#htable0"), URIRef("urn:doc"), 0, fp)
    assert out is not None, "a legal reading must resolve"
    n_asserted, promos = out
    assert n_asserted > 0 and len(promos) >= 1
    assert list(g.subjects(RDF.type, ILADUB.PromotionDecision)), "resolution must record a promotion"


def test_no_proposer_stays_escalated():
    # an abstaining proposer -> no resolution (graph untouched, caller escalates)
    hreg, band = _ambiguous_hier_region()
    out = resolve_ambiguous_merge(Graph(), hreg, band, URIRef("urn:doc#htable0"),
                                  URIRef("urn:doc"), 0, FakeSpanProposer(None))
    assert out is None, "an abstaining proposer must not resolve"


def test_illegal_reading_rejected_by_oracle():
    # the load-bearing guard: a reading whose scratch region violates tiling is refused by
    # region_tiles regardless of confidence -> legality gates admission, not confidence.
    hreg, band = _ambiguous_hier_region()
    amb = next(i for i, n in enumerate(hreg.tree) if n.ambiguous_flank is not None)
    flank = hreg.tree[amb].ambiguous_flank
    # deliberately-illegal: a second level-0 leaf over the flank -> two leaf headers for one column
    bad = list(build_reading(hreg.tree, amb, flank, "standalone"))
    bad.append(HeaderNode(0, (flank,), "DUP", None))
    bad_region = replace(hreg, tree=tuple(bad))
    scratch = Graph()
    assert_hier_region(scratch, bad_region, band, URIRef("urn:doc#bad"), URIRef("urn:doc"), 0)
    assert region_tiles(scratch) is False, "overlapping leaf access must fail the tiling oracle"


def test_offcenter_overlap_never_enters_resolution(tmp_path):
    # a genuine overlap collision (no ambiguous_flank) stays escalated even WITH a proposer present
    p = os.path.join(str(tmp_path), "offcenter.pdf"); F.offcenter_merge_report_pdf(p)
    rep = compile_tables(p, span_proposer=FakeSpanProposer(SpanProposal("absorb", 0.99, "x")))
    assert "MERGE_AMBIGUOUS" in _reasons(rep), _reasons(rep)


def test_compile_tables_accepts_span_proposer_kw(tmp_path):
    # signature smoke: the new optional kw exists and the default path is unchanged
    p = os.path.join(str(tmp_path), "simple.pdf"); F.simple_table_pdf(p)
    rep = compile_tables(p)                       # no kw -> today's behaviour
    assert "asserted" in [r.verdict for r in rep.regions]
