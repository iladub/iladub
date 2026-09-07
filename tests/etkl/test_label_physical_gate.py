"""[[R179]]: the membrane must require of a header LabelCell what [[R177]] made the emitter write.

R177 repaired `assert_hier_region`, which for months emitted every header `tab:LabelCell` with
text and no location. Nothing validated it: `tab:EntryCellPhysicalShape` requires geometry of
ENTRIES only, so 79 boxless label cells violated provenance-to-the-page (CLAUDE.md § Core design
principles 6) with the membrane silent. `tab:LabelCellPhysicalShape` is the closed-world half.

The shape's condition is the label's OWN non-empty `tab:cellText`, not "the node it labels carries
geometry" as [[R179]]'s row prescribes — no `tab:HeaderNode` carries geometry in the emitted graph
(spec § 2.2). Over this tree the two predicates partition the same single node:
`span.build_reading`'s flank filler (`src/iladub/etkl/span.py:38`), the one header node built for a
column with no header ink, whose text is `""` and which is honestly boxless.

These tests pin the GATE, not the file. A shape added to `vocab/shapes/tab-physical-shapes.ttl`
and not to `tiling._PHYSICAL_SHAPE_IRIS` reaches `compile`'s final whole-graph validation only —
where a violation CRASHES instead of escalating. That is the loop-G lesson recorded at
`src/iladub/etkl/tiling.py:35-39`, and `test_the_shape_is_in_the_region_gate_not_only_the_file`
is what stops it recurring.
"""
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

TAB = Namespace("https://w3id.org/iladub/tab#")


def _label(g, uri, text, *, box=True, page=True):
    lc = URIRef(uri)
    g.add((lc, RDF.type, TAB.LabelCell))
    g.add((lc, TAB.cellText, Literal(text)))
    if page:
        g.add((lc, TAB.onPage, Literal(0)))
    if box:
        bb = BNode()
        g.add((bb, RDF.type, TAB.BBox))
        g.add((lc, TAB.hasBBox, bb))
    return lc


def test_gate_refuses_a_label_with_text_and_no_box():
    from iladub.etkl.tiling import region_tiles
    g = Graph()
    _label(g, "urn:r179:lc0", "Currency", box=False)
    assert not region_tiles(g)


def test_gate_refuses_a_label_with_text_and_no_page():
    # Separate constraint, separate failure — R177's falsification 2 showed the page half
    # is invisible when it shares a constraint with the box half.
    from iladub.etkl.tiling import region_tiles
    g = Graph()
    _label(g, "urn:r179:lc1", "Unit", page=False)
    assert not region_tiles(g)


def test_gate_admits_a_label_carrying_both():
    from iladub.etkl.tiling import region_tiles
    g = Graph()
    _label(g, "urn:r179:lc2", "Americas")
    assert region_tiles(g)


def test_the_textless_flank_filler_stays_exempt():
    # `span.build_reading` mints HeaderNode(0, (flank,), "", None) for a column with NO header
    # ink. Its label honestly carries no location. A shape that refused it would infer from
    # absence — forbidden by CLAUDE.md § Core design principles 7 — and would escalate a region
    # whose only sin is that one of its columns was never titled.
    from iladub.etkl.tiling import region_tiles
    g = Graph()
    _label(g, "urn:r179:lc3", "", box=False, page=False)
    assert region_tiles(g)


def test_the_shape_is_in_the_region_gate_not_only_the_file():
    from iladub.etkl import tiling
    assert TAB.LabelCellPhysicalShape in tiling._PHYSICAL_SHAPE_IRIS
    # and it really made it into the extracted CBD subset the gate validates against
    assert (TAB.LabelCellPhysicalShape, RDF.type, None) in [
        (s, p, None) for s, p, _ in tiling._TILING_SHAPES.triples(
            (TAB.LabelCellPhysicalShape, RDF.type, None))
    ]


def test_an_entrycell_used_as_a_label_is_still_refused_when_it_has_no_box():
    """The EntryCell exclusion is LOSSLESS, and this is what says so.

    `tab:hasLabel` has `rdfs:range tab:LabelCell`, and `rowgroups.py:93` points it at the SOURCE
    `tab:EntryCell` carrying a derived group's label. Under a closure that materialises range
    typing that entry becomes a `tab:LabelCell`, and `tab:LabelCellPhysicalShape` therefore
    excludes any cell that is also an entry — the R19 accident, measured on
    `test_closure_equiv.py::test_both_closures_agree_on_a_mutated_real_page_graph`.

    Nothing is lost by that exclusion because `tab:EntryCellPhysicalShape` asks strictly MORE of
    an entry: `minCount 1` on `cellText`, `onPage` and `hasBBox`, unconditionally. If that ever
    stopped being true, this test is what fails.
    """
    from iladub.etkl.tiling import region_tiles
    g = Graph()
    lc = _label(g, "urn:r179:lc4", "Total", box=False)
    g.add((lc, RDF.type, TAB.EntryCell))
    assert not region_tiles(g)


def test_an_entrycell_used_as_a_label_with_full_geometry_is_admitted():
    from iladub.etkl.tiling import region_tiles
    g = Graph()
    lc = _label(g, "urn:r179:lc5", "Total")
    g.add((lc, RDF.type, TAB.EntryCell))
    assert region_tiles(g)


def test_the_shape_itself_never_fires_on_an_entry_cell():
    """The exclusion, pinned WITHOUT the corpus.

    `test_closure_equiv.py::test_both_closures_agree_on_a_mutated_real_page_graph` is what
    discovered this (spec § 4.3) and it is corpus-gated, so it SKIPS in CI ([[R173]]). This is the
    same claim on a synthetic graph: validated against `tab:LabelCellPhysicalShape` ALONE, a cell
    that is a label and an entry and carries neither box nor page must raise nothing — the entry
    shape is what governs it, and it asks strictly more.
    """
    import os
    from rdflib import Graph as _G
    from iladub.etkl import membrane
    vocab = os.path.join(os.path.dirname(__file__), "..", "..", "vocab")
    full = _G().parse(os.path.join(vocab, "shapes", "tab-physical-shapes.ttl"), format="turtle")
    only_label = _G()
    only_label += full.cbd(TAB.LabelCellPhysicalShape)
    ont = _G().parse(os.path.join(vocab, "ontology", "tab.ttl"), format="turtle")

    g = Graph()
    lc = _label(g, "urn:r179:lc6", "Total", box=False, page=False)
    g.add((lc, RDF.type, TAB.EntryCell))
    conforms, _ = membrane.validate(g, only_label, ont)
    assert conforms

    # control: drop the tab:EntryCell type and the same shape refuses the same cell.
    g.remove((lc, RDF.type, TAB.EntryCell))
    conforms, _ = membrane.validate(g, only_label, ont)
    assert not conforms
