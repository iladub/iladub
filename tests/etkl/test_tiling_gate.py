import pytest
from rdflib import Graph, Namespace, URIRef, Literal, RDF

TAB = Namespace("https://w3id.org/iladub/tab#")
EX = Namespace("https://example.org/d#")


def _region(cover, axis="column"):
    """cover: {header-uri: (level, parent-or-None, [leaves])}. Leaves c1..c3 on `axis`."""
    cp = TAB.coversColumn if axis == "column" else TAB.coversRow
    lp = TAB.hasLeafColumn if axis == "column" else TAB.hasLeafRow
    cls = TAB.LeafColumn if axis == "column" else TAB.LeafRow
    g = Graph(); t = EX.t
    for c in (EX.c1, EX.c2, EX.c3):
        g.add((c, RDF.type, cls)); g.add((t, lp, c))
    for h, (lvl, parent, cols) in cover.items():
        g.add((h, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, h))
        g.add((h, TAB.headerLevel, Literal(lvl)))
        if parent is not None:
            g.add((h, TAB.parentHeader, parent))
        for c in cols:
            g.add((h, cp, c))
    return g


def _battery(axis):
    well = _region({EX.h0: (0, None, [EX.c1, EX.c2, EX.c3]),
                    EX.h1: (1, EX.h0, [EX.c1]), EX.h2: (1, EX.h0, [EX.c2]), EX.h3: (1, EX.h0, [EX.c3])}, axis)
    gap = _region({EX.h0: (0, None, [EX.c1, EX.c2]),
                   EX.h1: (1, EX.h0, [EX.c1]), EX.h2: (1, EX.h0, [EX.c2])}, axis)              # c3 uncovered
    overlap = _region({EX.h0: (0, None, [EX.c1, EX.c2, EX.c3]),
                       EX.h1: (1, EX.h0, [EX.c1]), EX.h2: (1, EX.h0, [EX.c1, EX.c2]),          # h1,h2 share c1 @ lvl1
                       EX.h3: (1, EX.h0, [EX.c3])}, axis)
    refine = _region({EX.h0: (0, None, [EX.c1, EX.c2]),                                       # parent misses c3
                      EX.h1: (1, EX.h0, [EX.c1]), EX.h2: (1, EX.h0, [EX.c2]), EX.h3: (1, EX.h0, [EX.c3])}, axis)
    return {"well": (well, True), "gap": (gap, False), "overlap": (overlap, False), "refine": (refine, False)}


def test_region_tiles_matches_backstop_semantics():
    from iladub.etkl.tiling import region_tiles
    for axis in ("column", "row"):
        for name, (g, expect) in _battery(axis).items():
            assert region_tiles(g) is expect, "%s-%s: got %s expect %s" % (axis, name, region_tiles(g), expect)


def test_gate_reject_escalates_gracefully(tmp_path, monkeypatch):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import row_grouped_table_pdf
    from iladub.etkl import compile_tables
    import iladub.etkl.tiling as tiling
    p = tmp_path / "rg.pdf"; row_grouped_table_pdf(str(p))

    # Positive path: normally this row-grouped region tiles and is asserted.
    rep_ok = compile_tables(str(p))
    assert any(r.verdict == "asserted" for r in rep_ok.regions)

    # Disposition: when the SHACL oracle REJECTS the region, compile must escalate THAT region
    # gracefully (ROW_GROUP_AMBIGUOUS) — NOT raise, NOT crash the whole compile.
    monkeypatch.setattr(tiling, "region_tiles", lambda g: False)
    rep_esc = compile_tables(str(p))                                 # must NOT raise
    assert any(r.verdict == "escalated" and r.reason == "ROW_GROUP_AMBIGUOUS" for r in rep_esc.regions)
