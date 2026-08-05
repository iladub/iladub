"""R19: the region gate must refuse a PHYSICAL-shape defect, not let it crash compile at
final validation. Measured activation (2026-08-05, loop R41 Task 3): with R41's IndexError
fixed, corpus/financial/apple-fy2026q3-statements.pdf page 1's mtable4 emits matrix cells
carrying a bbox with EMPTY cellText; region_tiles (eleven tiling shapes only) passes the
region, and compile_tables raises AssertionError at final whole-graph validation
(tab:WrappedCellShape, compile.py:624). The gate must include the physical shapes so the
region ESCALATES (fluent-reader invariant: never crash, always at worst escalate)."""
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

TAB = Namespace("https://w3id.org/iladub/tab#")


def _bbox(g, cell, n):
    bb = URIRef(f"urn:r19:bb{n}")
    g.add((bb, RDF.type, TAB.BBox))
    g.add((cell, TAB.hasBBox, bb))


def test_gate_refuses_bbox_cell_with_empty_text():
    # The apple p1#mtable4 defect, minimal: a Cell with a bbox and empty cellText.
    # Pre-fix: region_tiles returns True (the tiling shapes don't see it) — RED.
    from iladub.etkl.tiling import region_tiles
    g = Graph()
    cell = URIRef("urn:r19:cell0")
    g.add((cell, RDF.type, TAB.Cell))
    g.add((cell, TAB.cellText, Literal("")))
    _bbox(g, cell, 0)
    assert not region_tiles(g)


def test_gate_refuses_entrycell_missing_physical_facts():
    # EntryCellPhysicalShape's other half: an asserted EntryCell must carry text,
    # onPage, and bbox. One missing onPage must now refuse at the gate too.
    from iladub.etkl.tiling import region_tiles
    g = Graph()
    cell = URIRef("urn:r19:cell1")
    g.add((cell, RDF.type, TAB.EntryCell))
    g.add((cell, TAB.cellText, Literal("x")))
    _bbox(g, cell, 1)          # bbox + text present, onPage missing
    assert not region_tiles(g)


def test_gate_still_passes_a_well_formed_physical_cell():
    # Guard: a complete cell (text + bbox) must not be refused by the extension.
    from iladub.etkl.tiling import region_tiles
    g = Graph()
    cell = URIRef("urn:r19:cell2")
    g.add((cell, RDF.type, TAB.Cell))
    g.add((cell, TAB.cellText, Literal("Americas")))
    _bbox(g, cell, 2)
    assert region_tiles(g)
