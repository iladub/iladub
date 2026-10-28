"""R334 carriage on a real page (spec 2026-10-24 §3.2): Fed H.4.1 p0's boxhead, read from its
recorded reading offline, is emitted as a leveled header tree that the scorer walks and the grid's
shapes admit.

Fed p0's reading: 7 columns that tile; leaves on cols 0, 1, 6; spanners (1,5) L7, (2,5) L8,
(2,3) L10 and (4,5) L10 (spec §2). Col 2 has no leaf, so its column identity comes from the
spanners alone — the case R334 exists for.
"""
import os

import pytest
from rdflib import Graph, URIRef

pytestmark = pytest.mark.corpus

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FED = os.path.join(ROOT, "held-out", "fed-h41-2025-01-02.pdf")
VOCAB = os.path.join(ROOT, "vocab")


@pytest.fixture(scope="module")
def fed_p0():
    if not os.path.exists(FED):
        pytest.skip("held-out/fed-h41-2025-01-02.pdf is not present")
    from iladub.etkl.boxhead import default_reader, emit_boxhead, header_block, read_grid_boxhead
    from iladub.etkl.datagrid import derive_data_grids, emit_data_grid
    from iladub.etkl.geometry import extract_words, text_lines
    (grid,) = derive_data_grids(FED, 0)
    lines = sorted([ln for ln in text_lines(extract_words(FED, 0)) if ln.words],
                   key=lambda ln: ln.top)
    block = header_block(lines, grid)
    disposed = read_grid_boxhead(FED, 0, lines, grid, default_reader())
    g = Graph()
    grid_uri = emit_data_grid(g, grid, lines, URIRef("https://example.org/etkl/doc/fed-h41"), 0)
    n = emit_boxhead(g, grid_uri, lines, block, disposed, 0)
    return g, grid_uri, n, disposed


def test_fed_p0_emits_seven_header_nodes(fed_p0):
    from iladub.etkl.holon import TAB
    g, grid_uri, n, d = fed_p0
    assert d.refused is None and d.spanner_refusal is None and d.spanners_dropped == ()
    assert n == 7 and len(list(g.objects(grid_uri, TAB.hasHeaderNode))) == 7


def test_fed_p0_levels_follow_the_tree(fed_p0):
    """L7 = 0, leaf col 0 = 0, leaf col 6 = 0, L8 = 1, leaf col 1 = 1, both L10 spanners = 2."""
    from iladub.etkl.holon import TAB
    g, grid_uri, _, d = fed_p0
    lv = {str(h).rsplit("-", 1)[1]: int(v) for h, v in g.subject_objects(TAB.headerLevel)}
    assert [s[:2] for s in d.spanners] == [(1, 5), (2, 5), (2, 3), (4, 5)]
    assert lv == {"s0": 0, "h0": 0, "h6": 0, "s1": 1, "h1": 1, "s2": 2, "s3": 2}


def test_fed_p0_col_2_has_no_leaf_and_walks_its_spanners(fed_p0):
    """Through the scorer's own walk (`feed._header_parts`), not a re-implementation of it."""
    from iladub import feed
    from iladub.etkl.holon import TAB
    g, grid_uri, _, d = fed_p0
    assert 2 not in d.labels
    labels, _node = feed._header_parts(g, [grid_uri], TAB.coversColumn)[URIRef(f"{grid_uri}-c2")]
    assert labels == ("Averages of daily figures", "Change from week ended", "Dec 25, 2024")


def test_fed_p0_tree_conforms_to_the_tab_shapes(fed_p0):
    from pyshacl import validate
    g, *_ = fed_p0
    shapes = Graph().parse(os.path.join(VOCAB, "shapes", "tab-shapes.ttl"), format="turtle")
    ont = Graph().parse(os.path.join(VOCAB, "ontology", "tab.ttl"), format="turtle")
    conforms, _, text = validate(g, shacl_graph=shapes, ont_graph=ont, inference="rdfs",
                                 advanced=True)
    assert conforms, text
