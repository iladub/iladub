"""The box-split DECISION (spec 2026-09-28-box-split-design.md § 3.2, ruling R-d).

`iladub.etkl.boxsplit` decides which text bands hold >= 2 of the author's closed ruled boxes
(spec's O1/N1/N2), on top of Task 1's box reader (boxes.py). Bands, exactly as `compile.page_bands`
builds its RAW band list (measured below, R2): `detect_bands(text_lines(extract_words(p)))`.
"""
import os

import pytest
from rdflib import RDF
from rdflib.namespace import XSD

import iladub.etkl.boxsplit as boxsplit_mod
from iladub.etkl.bands import detect_bands
from iladub.etkl.boxes import page_boxes
from iladub.etkl.boxsplit import TAB, _box_owner, bands_to_split, box_evidence
from iladub.etkl.geometry import extract_words, text_lines
from tests.etkl import fixtures as F

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
CBH = os.path.join(CORPUS, "ag-trade", "cbh-stem-2026-08-03.pdf")


def _y_overlap_owner(box, bands):
    """FALSIFICATION MUTANT — NOT SHIPPED. Belongs by bbox y-OVERLAP alone (the first band whose
    [top, bottom] overlaps the box's), dropping I-2a's "every word inside" clause entirely. Used
    only via `monkeypatch.setattr(boxsplit_mod, "_box_owner", _y_overlap_owner)`, which patches
    the MODULE attribute `bands_to_split` resolves at call time — this test module's OWN already
    -imported `_box_owner` name is a separate binding and is never touched, so only the
    decision (`bands_to_split`) is observed under the mutant, exactly as fix round 1 finding 2/3
    requires."""
    for idx, band in enumerate(bands):
        if box.top < band.bottom and box.bottom > band.top:
            return idx
    return None


def _raw_bands(pdf_path: str, page_number: int = 0):
    """R2: the IDENTICAL computation `compile.page_bands` uses to build `raw_bands`
    (`compile.py` — `words = extract_words(pdf_path, page_number)`;
    `raw_bands = detect_bands(text_lines(words))`), so an index this module returns names the
    same band `compile_tables`' `for band in raw_bands:` loop does."""
    return detect_bands(text_lines(extract_words(pdf_path, page_number)))


def corpus_only(fn):
    fn = pytest.mark.skipif(not os.path.exists(CBH), reason="corpus not fetched")(fn)
    return pytest.mark.corpus(fn)


# --- Step 1/2: the decision, on Task 1's fixtures -----------------------------------------------

def test_two_boxes_one_band_selects_the_shared_band_with_both_boxes(tmp_path):
    p = str(tmp_path / "two.pdf")
    F.two_boxes_one_band_pdf(p)
    bands = _raw_bands(p)
    boxes = page_boxes(p, 0)
    result = bands_to_split(bands, boxes)
    assert len(result) == 1
    (idx, selected), = result.items()
    assert len(selected) == 2
    assert {round(b.x0) for b in selected} == {40, 400}
    # every word of the shared band is accounted for by exactly one of the two boxes or by
    # neither (I-2a): both boxes must actually resolve to the SAME band index.
    assert {_box_owner(b, bands) for b in selected} == {idx}


def test_two_boxes_evidence_graph_has_exactly_two_closed_box_nodes(tmp_path):
    """I-2c, positive (fix round 1 finding 4): the two-box fixture's evidence graph carries
    exactly one `tab:ClosedBox` node per box (2 total — never one per word, never one per band),
    each with exactly one canonical `xsd:integer` `tab:boxBandIndex`, both naming the SAME band
    (the fixture's own contract: one shared band)."""
    p = str(tmp_path / "two.pdf")
    F.two_boxes_one_band_pdf(p)
    bands = _raw_bands(p)
    boxes = page_boxes(p, 0)
    g = box_evidence(bands, boxes)
    nodes = list(g.subjects(RDF.type, TAB.ClosedBox))
    assert len(nodes) == 2
    band_indices = set()
    for n in nodes:
        vals = list(g.objects(n, TAB.boxBandIndex))
        assert len(vals) == 1, vals
        lit = vals[0]
        assert lit.datatype == XSD.integer, lit.datatype
        assert str(lit) == str(int(str(lit))), "canonical lexical form, no leading zeros/sign"
        band_indices.add(int(lit))
    assert band_indices == {_box_owner(boxes[0], bands)}


def test_n1_one_box_with_ink_outside_does_not_split(tmp_path):
    p = str(tmp_path / "n1.pdf")
    F.one_box_with_title_pdf(p)
    bands = _raw_bands(p)
    boxes = page_boxes(p, 0)
    assert len(boxes) == 1              # Task 1's own pin; one box only, below the R-d floor
    assert bands_to_split(bands, boxes) == {}


def test_n2_open_lattices_do_not_split(tmp_path):
    p = str(tmp_path / "n2.pdf")
    F.open_lattices_pdf(p)
    bands = _raw_bands(p)
    boxes = page_boxes(p, 0)
    assert boxes == []                  # Task 1's own pin; no closed box at all
    assert bands_to_split(bands, boxes) == {}


# --- the stroked-rect commission negative (Task 1 review) ---------------------------------------

def test_two_wordless_stroked_separators_do_not_split(tmp_path):
    """A band with two closed boxes (Task 1's own commission: a single thin STROKED rect reads
    as a closed box) but NEITHER contains a single word. I-2a's "a box containing no words
    belongs to no band" must exclude both, so the band must not split even though it
    geometrically holds two closed boxes."""
    p = str(tmp_path / "wordless.pdf")
    F.wordless_separator_boxes_pdf(p)
    bands = _raw_bands(p)
    boxes = page_boxes(p, 0)
    assert len(boxes) == 2                                  # the commission itself, confirmed
    assert all(_box_owner(b, bands) is None for b in boxes)  # I-2a's word-count clause
    assert bands_to_split(bands, boxes) == {}


def test_falsification_wordless_separators_split_under_y_overlap_mutant(tmp_path, monkeypatch):
    """DECISION-LEVEL falsification (fix round 1 finding 2/3): both separators sit INSIDE the
    band's own y-range (the fixture's own measured contract), so a y-overlap-only membership
    rule reaches count 2 for band 0 and WRONGLY splits it — proving the shipped `{}` above
    depends on I-2a's word-count clause, not on a geometric accident that keeps the boxes from
    ever overlapping the band in the first place."""
    p = str(tmp_path / "wordless.pdf")
    F.wordless_separator_boxes_pdf(p)
    bands = _raw_bands(p)
    boxes = page_boxes(p, 0)
    monkeypatch.setattr(boxsplit_mod, "_box_owner", _y_overlap_owner)
    mutant = boxsplit_mod.bands_to_split(bands, boxes)
    assert mutant != {}, "the y-overlap mutant must WRONGLY split band 0"
    assert set(mutant) == {0}
    assert len(mutant[0]) == 2


def test_a_wordless_box_emits_no_evidence_node_at_all():
    """I-2c: a box with no owner emits NOTHING into `box_evidence`'s graph — the query cannot
    defend against a node with no `tab:boxBandIndex` fact, so the emitter must never mint one."""
    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Line, Word
    from iladub.etkl.boxes import Box

    band = Band(lines=(Line(words=(Word("x", 500.0, 510.0, 0.0, 9.0),), top=0.0, bottom=9.0),),
                top=0.0, bottom=9.0)
    box = Box(x0=0.0, x1=100.0, top=0.0, bottom=9.0, verticals=(), horizontals=(), title_bar=None)
    g = box_evidence([band], [box])
    assert len(g) == 0


# --- I-2a straddling protection (Step 3 falsification fixture) ----------------------------------

def test_a_box_straddling_two_bands_belongs_to_neither(tmp_path):
    """The fixture Step 3's falsification requires: a box whose frame covers two bands that
    `detect_bands` itself splits (an internal text-row gap past `gap_factor`). I-2a's exact
    rule must refuse it. A SECOND, genuine closed box (fix round 1 finding 3) sits in band 0
    alone, so band 0's true count under I-2a is ONE (the straddler contributes nothing) —
    `bands_to_split` must still return `{}`, not merely refuse the straddler in isolation."""
    p = str(tmp_path / "straddle.pdf")
    F.straddling_box_pdf(p)
    bands = _raw_bands(p)
    assert len(bands) == 2, "the fixture's own contract: the internal gap must split the page"
    boxes = page_boxes(p, 0)
    assert len(boxes) == 2, "the straddler plus the genuine box beside it"
    straddler = max(boxes, key=lambda b: b.bottom - b.top)   # spans both bands; the other does not
    genuine = next(b for b in boxes if b is not straddler)
    assert _box_owner(straddler, bands) is None
    assert _box_owner(genuine, bands) == 0
    assert bands_to_split(bands, boxes) == {}


def test_falsification_straddle_splits_under_y_overlap_mutant(tmp_path, monkeypatch):
    """DECISION-LEVEL falsification (fix round 1 finding 2/3): under the y-overlap-only mutant
    the straddler resolves to band 0 too (the first band its bbox overlaps), joining the
    genuine box there and pushing band 0's count to two — WRONGLY splitting it. Proves the
    shipped `{}` above depends on I-2a's exact rule, not on the straddler being invisible to
    band 0 under any rule."""
    p = str(tmp_path / "straddle.pdf")
    F.straddling_box_pdf(p)
    bands = _raw_bands(p)
    boxes = page_boxes(p, 0)
    monkeypatch.setattr(boxsplit_mod, "_box_owner", _y_overlap_owner)
    mutant = boxsplit_mod.bands_to_split(bands, boxes)
    assert mutant != {}, "the y-overlap mutant must WRONGLY split band 0"
    assert set(mutant) == {0}
    assert len(mutant[0]) == 2


# --- Step 4: the corpus preview (a preview of Task 4's C1) --------------------------------------

@corpus_only
def test_cbh_p0_selects_exactly_band_9_with_two_boxes():
    """MEASURED 2026-09-28: raw band 9 is y 683.5-761.5 (10 lines) — the exact band spec § 1
    names. `page_boxes` finds 6 closed boxes on the page (4 rosters, T1, T2); only band 9's T1/T2
    pair meets the R-d floor."""
    bands = _raw_bands(CBH, 0)
    assert (round(bands[9].top, 1), round(bands[9].bottom, 1)) == (683.5, 761.5)
    boxes = page_boxes(CBH, 0)
    result = bands_to_split(bands, boxes)
    assert set(result) == {9}
    assert len(result[9]) == 2
    assert {round(b.x0) for b in result[9]} == {38, 543}


# --- Task 3: the split, wired into `page_bands` (spec § 3.3-3.6) ---------------------------------

from collections import Counter

import iladub.etkl.compile as compile_mod
from iladub.etkl.compile import page_bands
from iladub.etkl.grid import _rule_boundaries


def _text(lines) -> str:
    return " ".join(w.text for ln in lines for w in ln.words)


def _glyphs(bands) -> Counter:
    """Every non-space glyph an output band carries, in its lines AND its captions. The
    character grain, because a ruled build re-buckets words from chars (`rule_aware_lines`), so
    word boundaries move while the ink does not."""
    return Counter(ch for b in bands for ln in (tuple(b.captions) + tuple(b.lines))
                   for w in ln.words for ch in w.text if not ch.isspace())


def _page_glyphs(p) -> Counter:
    return Counter(ch for w in extract_words(p, 0) for ch in w.text if not ch.isspace())


def _box_band(bands, first_word: str, n_cols: int):
    """The one output band whose FIRST line starts with `first_word` and whose author rules tile
    into `n_cols` columns."""
    hits = [b for b in bands if b.lines and b.lines[0].words[0].text == first_word
            and b.rules and _rule_boundaries(b) is not None
            and len(_rule_boundaries(b)) - 1 == n_cols]
    assert len(hits) == 1, [(_text(b.lines[:1]), len(b.rules)) for b in bands]
    return hits[0]


def _two_box_bands(p, spec):
    bands = page_bands(p, 0)
    left = _box_band(bands, spec["left"]["rows"][0][0], spec["left"]["n_cols"])
    right = _box_band(bands, spec["right"]["rows"][0][0], spec["right"]["n_cols"])
    return bands, left, right


def test_two_box_page_bands_split_into_two_box_bands_and_a_residue(tmp_path):
    """O1 on `page_bands`: the one fused raw band becomes a 3-column box band, a 2-column box
    band, and a residue band holding the note. Each box band's captions are exactly its title
    words (I-3c); each box band's lines hold ONLY that box's cells (I-3b: the right box's first
    line is its own first row, no left-box glyph)."""
    p = str(tmp_path / "two.pdf")
    spec = F.two_boxes_one_band_pdf(p)
    bands, left, right = _two_box_bands(p, spec)
    assert _text(left.captions) == spec["left"]["title"]
    assert _text(right.captions) == spec["right"]["title"]
    assert [w.text for w in right.lines[0].words] == list(spec["right"]["rows"][0])
    assert [w.text for w in left.lines[0].words] == list(spec["left"]["rows"][0])
    assert len(left.lines) == len(spec["left"]["rows"])
    assert len(right.lines) == len(spec["right"]["rows"])
    residue = [b for b in bands if spec["note"] in _text(b.lines)]
    assert len(residue) == 1 and residue[0] is not left and residue[0] is not right
    assert _text(residue[0].lines) == spec["note"]


def test_two_box_split_is_a_partition_of_the_page_ink(tmp_path):
    """I-3a at the page_bands grain: every page glyph lands in exactly one output band (lines or
    captions) — nothing lost, nothing carried twice."""
    p = str(tmp_path / "two.pdf")
    F.two_boxes_one_band_pdf(p)
    assert _glyphs(page_bands(p, 0)) == _page_glyphs(p)


def test_partition_words_is_exact_over_text_x0_top(tmp_path):
    """I-3a at the word grain, on the partition itself (before any build re-buckets words):
    box words + title words + residue words == the band's words, as a multiset of
    (text, x0, top)."""
    from iladub.etkl.boxsplit import partition_words
    p = str(tmp_path / "two.pdf")
    F.two_boxes_one_band_pdf(p)
    raw = _raw_bands(p)
    split = bands_to_split(raw, page_boxes(p, 0))
    (idx, boxes), = split.items()
    box_words, title_words, residue_lines = partition_words(raw[idx], boxes)
    key = lambda w: (w.text, w.x0, w.top)
    got = Counter(key(w) for ws in box_words for w in ws)
    got += Counter(key(w) for ws in title_words for w in ws)
    got += Counter(key(w) for ln in residue_lines for w in ln.words)
    want = Counter(key(w) for ln in raw[idx].lines for w in ln.words)
    assert got == want
    assert sum(got.values()) == sum(want.values())


def test_two_box_page_bands_ordered_by_top_then_x0(tmp_path):
    """I-3e: the output is ordered by (top, x0) of each band."""
    p = str(tmp_path / "two.pdf")
    F.two_boxes_one_band_pdf(p)
    bands = page_bands(p, 0)
    keys = [(b.top, min(w.x0 for ln in b.lines for w in ln.words)) for b in bands]
    assert keys == sorted(keys)


def test_a_residue_beside_the_boxes_does_not_reread_their_ink(tmp_path):
    """The residue's inputs are scoped too (spec § 3.4's principle, applied to I-3d): a residue
    word beside the boxes on the title line stretches the residue's y-range across both boxes.
    Built from page-scoped rules and glyphs, the residue would re-read every box glyph in that
    range (measured on cbh p0: the residue came back as the whole fused band, 26 rules). It
    must hold exactly its own words, and the page's ink must still be partitioned."""
    p = str(tmp_path / "aside.pdf")
    spec = F.two_boxes_one_band_pdf(p, aside="1,951")
    bands, left, right = _two_box_bands(p, spec)
    assert _glyphs(bands) == _page_glyphs(p)
    residue = [b for b in bands if b is not left and b is not right]
    assert len(residue) == 1
    assert [_text([ln]) for ln in residue[0].lines] == [spec["aside"], spec["note"]]
    assert residue[0].rules == () and residue[0].hrules == ()
    # I-3e, where the sort is load-bearing: page_boxes' own order puts the residue (whose top is
    # the aside's, on the title line) LAST, so only split_band's (top, x0) sort puts it first.
    keys = [(round(b.top, 1), round(min(w.x0 for ln in b.lines for w in ln.words)))
            for b in bands]
    assert keys == [(181.7, 40), (195.7, 44), (195.7, 404)]


@pytest.mark.parametrize("make", [F.one_box_with_title_pdf, F.open_lattices_pdf])
def test_unselected_pages_take_the_unchanged_path(tmp_path, monkeypatch, make):
    """I-3f: a page `bands_to_split` selects nothing on (N1, N2) produces exactly the band list it
    produces with the split disabled outright."""
    p = str(tmp_path / "n.pdf")
    make(p)
    shipped = page_bands(p, 0)
    monkeypatch.setattr(boxsplit_mod, "bands_to_split", lambda bands, boxes: {})
    assert page_bands(p, 0) == shipped


def test_two_boxes_without_title_bars_still_split_with_empty_captions(tmp_path):
    """Review Focus 2: the title bar is not what triggers the split — the two closed boxes are."""
    p = str(tmp_path / "notitle.pdf")
    spec = F.two_boxes_one_band_pdf(p, titles=False)
    bands, left, right = _two_box_bands(p, spec)
    assert left.captions == () and right.captions == ()
    assert _glyphs(bands) == _page_glyphs(p)


def test_stacked_boxes_in_one_band_split_upper_first(tmp_path):
    """Review Focus 3: two boxes stacked in one raw band (measured: the fixture is ONE
    `detect_bands` band) split, the upper box's band first."""
    p = str(tmp_path / "stacked.pdf")
    spec = F.two_boxes_stacked_pdf(p)
    assert len(_raw_bands(p)) == 1, "the fixture's own contract: one raw band"
    bands = page_bands(p, 0)
    upper = _box_band(bands, spec["upper"]["rows"][0][0], spec["upper"]["n_cols"])
    lower = _box_band(bands, spec["lower"]["rows"][0][0], spec["lower"]["n_cols"])
    assert bands.index(upper) < bands.index(lower)
    assert _text(upper.captions) == spec["upper"]["title"]
    assert _text(lower.captions) == spec["lower"]["title"]
    assert _glyphs(bands) == _page_glyphs(p)


def test_box_bands_are_never_rebuilt_under_section_repair(tmp_path, monkeypatch):
    """Review Focus 5 / spec § 3.6: a box band's `specs` entry is None, so naming its index in
    `section_repair_bands` rebuilds nothing — a rebuild would read page-scoped chars again."""
    p = str(tmp_path / "two.pdf")
    spec = F.two_boxes_one_band_pdf(p)
    bands, left, right = _two_box_bands(p, spec)
    named = frozenset({bands.index(left), bands.index(right)})
    real = compile_mod._build_ruled_band
    repaired = []

    def spy(*args, **kwargs):
        if kwargs.get("section_repair"):
            repaired.append(args[0])
        return real(*args, **kwargs)

    monkeypatch.setattr(compile_mod, "_build_ruled_band", spy)
    again = page_bands(p, 0, section_repair_bands=named)
    assert repaired == []
    assert again == bands


@corpus_only
def test_cbh_p0_band_9_splits_into_its_two_drawn_tables():
    """Spec § 3.4 / § 7.3 on the corpus: with every input box-scoped, T1 reads 7 columns x 5
    lines and T2 2 columns x 4 lines; T2's first line is its own first row."""
    bands = page_bands(CBH, 0)
    t1 = [b for b in bands if b.rules and _rule_boundaries(b) and len(_rule_boundaries(b)) == 8]
    t2 = [b for b in bands if b.rules and _rule_boundaries(b) and len(_rule_boundaries(b)) == 3
          and b.lines[0].words[0].text == "ALB"]
    assert len(t1) == 1 and len(t1[0].lines) == 5
    assert len(t2) == 1 and len(t2[0].lines) == 4
    assert [w.text for w in t2[0].lines[0].words] == ["ALB", "1 - 15 October"]
    # I-3a on the page that motivated the split, residue scope included: every glyph once.
    assert _glyphs(bands) == Counter(ch for w in extract_words(CBH, 0) for ch in w.text
                                     if not ch.isspace())


# --- Task 3c: a box band carries its drawn frame and skips the multi-table gate (spec § 9) -------

import dataclasses

from rdflib import Literal, Namespace, URIRef
from rdflib.namespace import RDFS

from iladub.etkl.bands import Band
from iladub.etkl.compile import compile_tables, merge_bands
from iladub.etkl.segment import is_multi_table_ambiguous

DEC = Namespace("https://w3id.org/iladub/dec#")


def _gate_tripping_page(tmp_path):
    """The two-box page with `F.GATE_TRIPPING_LEFT` as its left box: (path, left box band's
    index in `page_bands`, that band)."""
    p = str(tmp_path / "trip.pdf")
    spec = F.two_boxes_one_band_pdf(p, left=F.GATE_TRIPPING_LEFT)
    bands = page_bands(p, 0)
    left = _box_band(bands, spec["left"]["rows"][0][0], spec["left"]["n_cols"])
    return p, bands.index(left), left


def _multi_table_judgement(graph, idx):
    """(chosen option label, rationale) of band `idx`'s one `multi_table` decision holon."""
    region = URIRef(f"{compile_mod._DOC}#region{idx}")
    ds = [d for d in graph.subjects(DEC.regarding, region)
          if graph.value(d, RDFS.label) == Literal("multi_table")]
    assert len(ds) == 1, ds
    return str(graph.value(graph.value(ds[0], DEC.chosen), RDFS.label)), \
        str(graph.value(ds[0], DEC.rationale))


def test_u6_a_framed_box_band_skips_the_multi_table_gate(tmp_path):
    """U6 (spec § 9.5). PRECONDITION, measured here so the test pins something: the gate returns
    True on this box band's content on today's tree. Past it: the band carries the bbox of the box
    it was cut from, `compile_tables` does not escalate it MULTI_TABLE_AMBIGUOUS, and its
    `multi_table` judgement records `single` with a rationale naming the drawn frame."""
    p, idx, left = _gate_tripping_page(tmp_path)
    assert is_multi_table_ambiguous(left) is True, "precondition: the gate trips on this content"
    box = next(b for b in page_boxes(p, 0) if round(b.x0) == 40)
    assert left.frame == (box.x0, box.x1, box.top, box.bottom)
    report = compile_tables(p, 0)
    assert report.regions[idx].reason != "MULTI_TABLE_AMBIGUOUS", report.regions[idx]
    chosen, why = _multi_table_judgement(report.graph, idx)
    assert chosen == "single"
    assert "frame" in why, why


def test_only_box_bands_carry_a_frame(tmp_path):
    """I-9-2 on `page_bands`: both box bands carry their own box's bbox; the residue carries
    none."""
    p = str(tmp_path / "two.pdf")
    spec = F.two_boxes_one_band_pdf(p)
    bands, left, right = _two_box_bands(p, spec)
    frames = {(b.x0, b.x1, b.top, b.bottom) for b in page_boxes(p, 0)}
    assert left.frame in frames and right.frame in frames and left.frame != right.frame
    assert [b.frame for b in bands if b is not left and b is not right] == [None]


def test_u7_the_same_content_without_its_frame_still_escalates(tmp_path, monkeypatch):
    """U7 (spec § 9.5, negative): the band U6 skips, with its frame cleared, meets the gate
    exactly as today — escalated MULTI_TABLE_AMBIGUOUS, `multi_table` chosen `multi`."""
    p, idx, _ = _gate_tripping_page(tmp_path)
    real = compile_mod.page_bands
    monkeypatch.setattr(compile_mod, "page_bands", lambda *a, **k: [
        dataclasses.replace(b, frame=None) for b in real(*a, **k)])
    report = compile_tables(p, 0)
    assert report.regions[idx].verdict == "escalated"
    assert report.regions[idx].reason == "MULTI_TABLE_AMBIGUOUS"
    assert _multi_table_judgement(report.graph, idx)[0] == "multi"


def test_u8_a_merged_run_carries_no_frame():
    """U8 (spec § 9.3, I-9-2): the frame answered for its box, not for a run that swallows it.
    `merge_bands` yields no frame even when every band of the run carries one."""
    from iladub.etkl.geometry import Line, Word

    def band(y, frame):
        ln = Line(words=(Word("x", 10.0, 20.0, y, y + 9.0),), top=y, bottom=y + 9.0)
        return Band(lines=(ln,), top=y, bottom=y + 9.0, frame=frame)

    merged = merge_bands([band(0.0, (0.0, 30.0, 0.0, 9.0)), band(20.0, (0.0, 30.0, 20.0, 29.0))],
                         0, 1)
    assert merged.frame is None


# --- Task 4 fix (controller ruling 1, 2026-09-30): a box's title is not a section key ------------
#
# Spec § 1 carries each title-bar text as a `tab:RegionCaption` of its own table. Before this fix
# the shared caption emitter typed EVERY band caption `tab:SectionCaption` too, and
# `feed._table_captions` reads that type as section-key evidence, so on cbh T1's and T2's rows were
# prefixed by their titles (tests/test_cbh_e2e.py's two section-port tests). The origin is carried
# by `Band.title_captions`, set by `boxsplit._box_band`; nothing infers it.


def _caption_types(graph):
    """{caption text: set of local type names} over every `tab:hasCaption` in the graph."""
    out = {}
    for _t, c in graph.subject_objects(TAB.hasCaption):
        out[str(graph.value(c, TAB.captionText))] = {
            str(ty).split("#")[1] for ty in graph.objects(c, RDF.type)}
    return out


def test_a_box_title_is_a_region_caption_and_never_a_section_caption(tmp_path):
    """Both box tables are asserted and carry their title. Each title is a `tab:RegionCaption`
    and is NOT a `tab:SectionCaption`."""
    p = str(tmp_path / "two.pdf")
    spec = F.two_boxes_one_band_pdf(p)
    report = compile_tables(p, 0)
    asserted = [r for r in report.regions if r.verdict == "asserted"]
    assert len(asserted) == 2, [(r.kind.name, r.verdict, r.reason) for r in report.regions]
    types = _caption_types(report.graph)
    for side in ("left", "right"):
        title = spec[side]["title"]
        assert title in types, (title, types)
        assert types[title] == {"RegionCaption"}, (title, types[title])


def test_control_a_peeled_caption_on_an_ordinary_band_is_still_a_section_caption(tmp_path):
    """THE CONTROL. The sectioned ruled table's peeled strips (no box split on this page) keep
    exactly today's typing, `tab:RegionCaption` AND `tab:SectionCaption`. A fix that dropped
    `tab:SectionCaption` everywhere would pass the test above and fail this one."""
    p = str(tmp_path / "section.pdf")
    truth = F.sectioned_ruled_table_pdf(p)
    report = compile_tables(p, 0)
    types = _caption_types(report.graph)
    assert truth["caption_texts"], "precondition: the fixture draws captions"
    for text in truth["caption_texts"]:
        hits = [ts for t, ts in types.items() if text in t]
        assert hits, (text, types)
        assert all(ts == {"RegionCaption", "SectionCaption"} for ts in hits), (text, hits)


def test_a_merged_run_keeps_its_box_titles():
    """`merge_bands` concatenates `title_captions` as it does `captions`, of which it is a
    subset: a title stays a title inside a run (unlike `frame`, which U8 drops)."""
    from iladub.etkl.geometry import Line, Word

    def band(y, title):
        ln = Line(words=(Word("x", 10.0, 20.0, y, y + 9.0),), top=y, bottom=y + 9.0)
        cap = Line(words=(Word(title, 10.0, 20.0, y - 9.0, y),), top=y - 9.0, bottom=y)
        return Band(lines=(ln,), top=y, bottom=y + 9.0, captions=(cap,), title_captions=(cap,))

    a, b = band(0.0, "A"), band(20.0, "B")
    merged = merge_bands([a, b], 0, 1)
    assert merged.title_captions == a.title_captions + b.title_captions
    assert merged.captions == a.captions + b.captions


# --- Final review fix wave (2026-10-01, Important 1): the CARRIED half of ruling 1 ---------------
#
# The two emission tests above cannot tell the carried rule (a caption is a title iff it is in
# `band.title_captions`) from an inferred one read off `band.frame`: the box band has a frame and
# the control band does not. Two behaviours only the carried rule gets right are pinned here,
# PDF-free, on the emitter itself:
#   (A) a caption `_build_ruled_band` peeled INSIDE a box band keeps both types;
#   (B) a merged run keeps `title_captions` but drops `frame` (U8), and its titles stay titles.
# Keyed by caption URI, never by text: `_caption_types` above overwrites repeated texts.


def _emitted_caption_types(band):
    """{caption URI: set of local type names} for one `_emit_band_captions` call on `band`."""
    from rdflib import Graph, URIRef

    from iladub.etkl.compile import _emit_band_captions
    g = Graph()
    table = URIRef("urn:test:table")
    _emit_band_captions(g, table, band)
    return {c: {str(ty).split("#")[1] for ty in g.objects(c, RDF.type)}
            for c in g.objects(table, TAB.hasCaption)}


def _title_and_peeled_band(frame):
    """A band whose captions are (title, peeled): the title came from the box's bar, the peeled
    line from inside the box. Emission order fixes the URIs: `-bandcap0` is the title."""
    from iladub.etkl.geometry import Line, Word

    def line(text, y):
        return Line(words=(Word(text, 10.0, 60.0, y, y + 9.0),), top=y, bottom=y + 9.0)

    title, peeled = line("TITLE", 0.0), line("PEELED", 12.0)
    return Band(lines=(line("x", 30.0),), top=0.0, bottom=39.0, captions=(title, peeled),
                title_captions=(title,), frame=frame)


@pytest.mark.parametrize("frame", [(0.0, 70.0, 0.0, 39.0), None], ids=["box_band", "merged_run"])
def test_a_title_is_typed_by_its_carried_origin_not_by_the_frame(frame):
    """Case A (frame set): the title is `{RegionCaption}` and the peeled line is
    `{RegionCaption, SectionCaption}`. Case B (frame None, a merged run's state after U8): the
    title is STILL `{RegionCaption}`. A rule inferred from the frame fails one case or the other:
    "a framed band's captions are titles" fails A's peeled line, "a frameless band's captions are
    section keys" fails B's title."""
    from rdflib import URIRef
    types = _emitted_caption_types(_title_and_peeled_band(frame))
    title, peeled = URIRef("urn:test:table-bandcap0"), URIRef("urn:test:table-bandcap1")
    assert set(types) == {title, peeled}, types
    assert types[title] == {"RegionCaption"}, types
    assert types[peeled] == {"RegionCaption", "SectionCaption"}, types
