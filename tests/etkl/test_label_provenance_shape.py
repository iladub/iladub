"""[[R182]] — tab:LabelCoversProvenanceShape: a label's box must cover the ink it claims.

The membrane half of the [[R181]] repair. R181 made `build_row_reading` union a joined label's
box over every fragment it consumed; NOTHING validated it, so a regression would ship a label
whose `tab:hasBBox` covers one line of the three its `tab:cellText` was joined from — provenance
present and PARTIAL, which CLAUDE.md § 6/§ 7 forbid.

Validated against `tiling._TILING_SHAPES`, not the whole shapes file, deliberately: the gate
validates a CBD subset of the IRIs named in `_TILING_SHAPE_IRIS` + `_PHYSICAL_SHAPE_IRIS`, so a
shape present in `tab-physical-shapes.ttl` alone would let a violating region pass the gate and
CRASH at compile's final validation — the R19 failure the tiling module's own comment records,
and the reason R179's shape is listed in both places.

CI-runnable: the fixture is `caption_and_wrap_band`, synthetic, no corpus ([[R173]]).
"""
from decimal import Decimal
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import PROV

from iladub.etkl import membrane, tiling
from tests.etkl.test_rowrole_resolution import TAB, _resolve


def _emitted():
    g, out = _resolve(("furniture", "continuation"))
    assert out is not None, "the fixture must resolve, or this file tests nothing"
    return g


def _conforms(g):
    ok, report = membrane.validate(g, tiling._TILING_SHAPES, tiling._ONT)
    return ok, report


def test_the_real_emission_conforms():
    ok, report = _conforms(_emitted())
    assert ok, report


def test_a_label_whose_box_misses_its_provenance_is_refused():
    """The falsifying case, at the exact shape of the graincorp-stem defect: shrink the joined
    label's box back to its LEAF LINE alone (top 24 instead of 12) and the shape must refuse.
    This is the pre-R181 emission reproduced in the graph rather than in the code."""
    g = _emitted()
    label = next(s for s, _p, o in g.triples((None, TAB.cellText, None)) if str(o) == "Unit Ref")
    bb = g.value(label, TAB.hasBBox)
    g.remove((bb, TAB.y0, None))
    g.add((bb, TAB.y0, Literal(Decimal("24.00"))))
    ok, _report = _conforms(g)
    assert not ok, "a label box that misses its own provenance must not cross the membrane"


def test_a_label_with_no_provenance_edge_is_unaffected():
    """Vacuity is the CORRECT outcome, not a gap: a label nothing was joined into makes no
    provenance claim, and requiring one would infer from absence (CLAUDE.md § 8, open world).
    Drop the only edge and the same graph — unchanged geometry — conforms."""
    g = _emitted()
    g.remove((None, PROV.wasDerivedFrom, None))
    ok, report = _conforms(g)
    assert ok, report
