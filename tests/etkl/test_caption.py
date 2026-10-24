"""The caption worker (R336): which candidate lines are this table's own caption.

Plan Task 3. The plan-supplied tests are kept verbatim except `emit_captions`' call, which takes the
header block (see the report: `tab:captionRow` is a block position, and a page-line index alone
cannot yield one)."""
import os
from types import SimpleNamespace

from iladub.etkl.boxhead import BoxheadReading, dispose_boxhead
from iladub.etkl import boxhead
from iladub.etkl.caption import (CaptionReading, FakeCaptionReader, candidate_lines,
                                 dispose_captions, question_key, read_grid_captions)


def _w(text, x0, x1):
    return SimpleNamespace(text=text, x0=x0, x1=x1, top=0.0, bottom=1.0)


def _ln(*ws, top):
    return SimpleNamespace(words=list(ws), top=top, bottom=top + 1)


COLS = tuple(SimpleNamespace(x0=float(a), x1=float(a + 100)) for a in (0, 100, 200))
GRID = SimpleNamespace(rows=(5, 6), columns=COLS,
                       refusals={j: "HeterogeneousColumn/every-measure" for j in range(5)})
LINES = [_ln(_w("Masthead", 0, 290), top=0),                      # block 0: candidate
         _ln(_w("Title", 100, 200), top=2),                       # block 1: candidate
         _ln(_w("Millions", 120, 180), top=4),                    # block 2: candidate
         _ln(_w("Group", 120, 280), top=6),                       # block 3: spanner cols 1-2
         _ln(_w("Id", 10, 40), _w("a", 140, 160), _w("b", 240, 260), top=8),   # block 4: leaves
         _ln(_w("x", 10, 20), _w("1", 140, 150), _w("2", 240, 250), top=10),
         _ln(_w("y", 10, 20), _w("3", 140, 150), _w("4", 240, 250), top=12)]
BLOCK = (0, 1, 2, 3, 4)
READING = BoxheadReading(leaf_labels=((0, ((4, 0),)), (1, ((4, 1),)), (2, ((4, 2),))),
                         spanning_labels=((1, 2, ((3, 0),)),),
                         other_words=((0, 0), (1, 0), (2, 0)))


def _disposed():
    return dispose_boxhead(READING, LINES, BLOCK, GRID)


def test_candidates_are_the_lines_filed_entirely_as_other_words():
    assert candidate_lines(LINES, BLOCK, _disposed()) == (0, 1, 2)


def test_contiguous_captions_ending_above_the_topmost_label_are_disposed():
    c = candidate_lines(LINES, BLOCK, _disposed())
    assert dispose_captions(CaptionReading(caption_lines=(1, 2)), c, BLOCK, LINES, _disposed()) == (1, 2)
    assert dispose_captions(CaptionReading(caption_lines=(0, 1, 2)), c, BLOCK, LINES, _disposed()) == (0, 1, 2)


def test_caption_out_of_range_is_no_claim():
    c = candidate_lines(LINES, BLOCK, _disposed())
    assert dispose_captions(CaptionReading(caption_lines=(2, 3)), c, BLOCK, LINES, _disposed()) == ()


def test_caption_not_contiguous_is_no_claim():
    c = candidate_lines(LINES, BLOCK, _disposed())
    assert dispose_captions(CaptionReading(caption_lines=(0, 2)), c, BLOCK, LINES, _disposed()) == ()


def test_caption_not_adjacent_to_the_topmost_label_is_no_claim():
    c = candidate_lines(LINES, BLOCK, _disposed())
    assert dispose_captions(CaptionReading(caption_lines=(0, 1)), c, BLOCK, LINES, _disposed()) == ()


def test_empty_or_refusing_answer_is_no_claim():
    c = candidate_lines(LINES, BLOCK, _disposed())
    assert dispose_captions(CaptionReading(), c, BLOCK, LINES, _disposed()) == ()
    assert dispose_captions(CaptionReading(caption_lines=(2,), refuses=True), c, BLOCK, LINES,
                            _disposed()) == ()


def test_no_candidate_lines_asks_nothing():
    asked = []

    class Spy:
        def read_caption(self, crop_png, ncols, listing):
            asked.append(listing)
            return CaptionReading(caption_lines=(0,))

    no_other = BoxheadReading(leaf_labels=READING.leaf_labels,
                              spanning_labels=((1, 2, ((0, 0), (1, 0), (2, 0), (3, 0))),))
    d = dispose_boxhead(no_other, LINES, BLOCK, GRID)
    assert read_grid_captions("unused.pdf", 0, LINES, GRID, d, Spy()) == () and asked == []


def test_the_caption_key_differs_from_the_boxhead_key_for_the_same_listing():
    assert question_key(3, "L0: x") != boxhead.question_key(3, "L0: x")


def _caption_graph():
    from rdflib import Graph, URIRef
    from iladub.etkl.caption import emit_captions
    g = Graph()
    n = emit_captions(g, URIRef("urn:g"), LINES, (1, 2), 0, BLOCK)
    return g, n


def test_captions_are_region_captions_only_with_text_row_and_page():
    from rdflib.namespace import RDF
    from iladub.etkl.holon import TAB
    g, n = _caption_graph()
    assert n == 2
    caps = set(g.subjects(RDF.type, TAB.RegionCaption))
    assert len(caps) == 2 and not set(g.subjects(RDF.type, TAB.SectionCaption))
    assert not any(True for c in caps for _ in g.objects(c, TAB.hasBBox))
    assert sorted(str(t) for t in g.objects(None, TAB.captionText)) == ["Millions", "Title"]
    assert sorted(int(r) for r in g.objects(None, TAB.captionRow)) == [1, 2]
    assert all(int(p) == 0 for c in caps for p in g.objects(c, TAB.onPage))
    assert len(list(g.objects(None, TAB.onPage))) == 2


# ---------------------------------------------------------------------------------------------
# Block positions, not candidate indices; page lines, not block positions
# ---------------------------------------------------------------------------------------------

# A non-candidate line BETWEEN two candidates: block 1 holds a spanner whose ink overflows its
# group (Masthead 0-290 claimed over cols 1-2 = [100, 300]), so EXTENT drops it and its line is
# neither carried nor a candidate. Block 3's spanner survives (laminar: {1,2} on L1 over {1,2} on L3).
GAP_LINES = [_ln(_w("Title", 100, 200), top=0),                   # block 0: candidate
             _ln(_w("Masthead", 0, 290), top=2),                  # block 1: dropped spanner
             _ln(_w("Millions", 120, 180), top=4),                # block 2: candidate
             *LINES[3:]]
GAP_READING = BoxheadReading(leaf_labels=READING.leaf_labels,
                             spanning_labels=((1, 2, ((1, 0),)), (1, 2, ((3, 0),))),
                             other_words=((0, 0), (2, 0)))


def _gap_disposed():
    d = dispose_boxhead(GAP_READING, GAP_LINES, BLOCK, GRID)
    assert d.spanner_refusal is None and d.spanners_dropped == (0,)
    return d


def test_contiguity_is_in_page_order_not_in_candidate_order():
    """Candidates are block 0 and block 2; indices (0, 1) are consecutive CANDIDATES, but a dropped
    spanner's line sits between them on the page, so the answer is not a contiguous run."""
    d = _gap_disposed()
    c = candidate_lines(GAP_LINES, BLOCK, d)
    assert c == (0, 2)
    assert dispose_captions(CaptionReading(caption_lines=(0, 1)), c, BLOCK, GAP_LINES, d) == ()
    assert dispose_captions(CaptionReading(caption_lines=(1,)), c, BLOCK, GAP_LINES, d) == (2,)


def test_a_line_separated_from_the_topmost_label_by_a_dropped_spanner_is_no_claim():
    """Plan property 3: block 0 is separated from block 3's surviving spanner by block 1's dropped
    spanner (and block 2), so it is not directly above the topmost surviving label."""
    d = _gap_disposed()
    c = candidate_lines(GAP_LINES, BLOCK, d)
    assert dispose_captions(CaptionReading(caption_lines=(0,)), c, BLOCK, GAP_LINES, d) == ()


def test_a_duplicated_index_is_no_claim():
    c = candidate_lines(LINES, BLOCK, _disposed())
    assert dispose_captions(CaptionReading(caption_lines=(2, 2)), c, BLOCK, LINES, _disposed()) == ()


def test_a_refused_boxhead_has_no_candidates():
    d = dispose_boxhead(None, LINES, BLOCK, GRID)
    assert d.refused and candidate_lines(LINES, BLOCK, d) == ()


def test_read_grid_captions_returns_page_line_indices_when_the_block_is_offset(monkeypatch):
    """Two lines above the block that the grid did NOT refuse, so block position k is page line
    k + 2. The reader answers candidate indices; `read_grid_captions` returns PAGE lines."""
    from iladub.etkl import caption
    lines = [_ln(_w("Running head", 0, 290), top=-6), _ln(_w("Section", 0, 100), top=-4), *LINES]
    grid = SimpleNamespace(rows=(7, 8), columns=COLS,
                           refusals={j: "HeterogeneousColumn/every-measure" for j in range(2, 7)})
    assert boxhead.header_block(lines, grid) == (2, 3, 4, 5, 6)
    d = dispose_boxhead(READING, lines, (2, 3, 4, 5, 6), grid)
    seen = []
    monkeypatch.setattr(caption, "_render_crop",
                        lambda pdf, page, region: seen.append(region) or b"png")
    got = read_grid_captions("unused.pdf", 0, lines, grid, d,
                             FakeCaptionReader(CaptionReading(caption_lines=(1, 2))))
    assert got == (3, 4)
    # the crop is the boxhead's own region: the block plus the first data rows
    assert len(seen) == 1 and [ln.top for ln in seen[0].lines] == [0, 2, 4, 6, 8, 10, 12]
    # and the emitted row is the BLOCK position of those page lines, not the page index
    from rdflib import Graph, URIRef
    from iladub.etkl.caption import emit_captions
    from iladub.etkl.holon import TAB
    g = Graph()
    emit_captions(g, URIRef("urn:g"), lines, got, 0, (2, 3, 4, 5, 6))
    assert sorted(int(r) for r in g.objects(None, TAB.captionRow)) == [1, 2]
    assert sorted(str(t) for t in g.objects(None, TAB.captionText)) == ["Millions", "Title"]


def test_read_grid_captions_lists_only_the_candidates(monkeypatch):
    from iladub.etkl import caption
    asked = []

    class Spy:
        def read_caption(self, crop_png, ncols, listing):
            asked.append((ncols, listing))
            return CaptionReading(caption_lines=(2,))

    monkeypatch.setattr(caption, "_render_crop", lambda pdf, page, region: b"png")
    assert read_grid_captions("unused.pdf", 0, LINES, GRID, _disposed(), Spy()) == (2,)
    assert asked == [(3, "C0: [0]Masthead@0-290\nC1: [0]Title@100-200\nC2: [0]Millions@120-180")]


def test_a_reader_that_raises_is_no_claim(monkeypatch):
    from iladub.etkl import caption

    class Raises:
        def read_caption(self, crop_png, ncols, listing):
            raise RuntimeError("down")

    monkeypatch.setattr(caption, "_render_crop", lambda pdf, page, region: b"png")
    assert read_grid_captions("unused.pdf", 0, LINES, GRID, _disposed(), Raises()) == ()
    assert read_grid_captions("unused.pdf", 0, LINES, GRID, _disposed(), None) == ()


def test_the_recorded_reader_replays_and_misses_to_none(tmp_path, monkeypatch):
    import json
    from iladub.etkl import caption
    from iladub.etkl.caption import RecordedCaptionReader
    listing = "C0: [0]Title@100-200"
    (tmp_path / f"{question_key(3, listing)}.json").write_text(
        json.dumps({"caption_lines": [0], "refuses": False, "note": "n"}), encoding="utf-8")
    monkeypatch.setattr(caption, "READINGS_DIR", tmp_path)        # resolved at CALL time
    r = RecordedCaptionReader()
    assert r.read_caption(b"", 3, listing) == CaptionReading(caption_lines=(0,), note="n")
    assert r.read_caption(b"", 4, listing) is None


# ---------------------------------------------------------------------------------------------
# The membrane (M2): text, row and page conform; a box on a caption is refused
# ---------------------------------------------------------------------------------------------

def _validate(g):
    from pyshacl import validate
    from rdflib import Graph
    vocab = os.path.join(os.path.dirname(__file__), "..", "..", "vocab")
    shapes = Graph()
    for f in ("tab-shapes.ttl", "tab-physical-shapes.ttl"):
        shapes.parse(os.path.join(vocab, "shapes", f), format="turtle")
    ont = Graph().parse(os.path.join(vocab, "ontology", "tab.ttl"), format="turtle")
    conforms, _, text = validate(g, shacl_graph=shapes, ont_graph=ont, inference="rdfs",
                                 advanced=True)
    return conforms, text


def _with_grid():
    from rdflib import URIRef
    g, _ = _caption_graph()
    boxhead.emit_boxhead(g, URIRef("urn:g"), LINES, BLOCK, _disposed(), 0)
    return g


def test_caption_nodes_on_a_grid_conform_to_the_tab_shapes():
    from rdflib import URIRef
    from iladub.etkl.holon import TAB
    g = _with_grid()
    assert set(g.objects(URIRef("urn:g"), TAB.hasHeaderNode))
    conforms, text = _validate(g)
    assert conforms, text


def test_control_a_caption_with_a_bbox_is_refused_by_wrapped_cell_shape():
    """M2, kept as a regression: `tab:hasBBox rdfs:domain tab:Cell` types the caption a cell, and a
    cell with a box and no `cellText` is refused. This is why `emit_captions` writes no box."""
    from rdflib import BNode, URIRef
    from iladub.etkl.holon import TAB
    g = _with_grid()
    g.add((URIRef("urn:g-cap0"), TAB.hasBBox, BNode()))
    conforms, text = _validate(g)
    assert not conforms and "WrappedCellShape" in text
