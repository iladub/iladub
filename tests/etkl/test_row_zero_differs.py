"""Box-split § 10 (Task 3d.4): U9, the one-way oracle "does row 0 differ from its body".

Split out of `test_boxhead_absence.py` (which carries U10, U11 and U14) because together they passed
the plan's ~600-line mark. Spec `docs/superpowers/specs/2026-09-28-box-split-design.md` § 10.3.2 /
§ 10.5 U9; plan Task 3d.4 as amended by A5.
"""
import os as _os

import pytest
from rdflib import Graph, Namespace, RDF

TAB = Namespace("https://w3id.org/iladub/tab#")

# ------------------------------------------------------------------ U9, the oracle (3d.4)
#
# Spec § 10.3.2 / § 10.5 U9, plan Task 3d.4 as amended by A5. `rowzero.row_zero_differs(region,
# pdf, page)` is `row-zero-differs.rq` asked over the region's typed-cell evidence plus the three
# transient style facts. Every region is the one the RECORD path of `compile_tables` passes to
# `assert_record_region` (a spy on the name `compile` binds), so the oracle reads what 3d.6's ask
# site will read. Each per-feature positive first MEASURES that its fixture differs in that
# feature alone, so deleting the feature's clause is the only way the positive can turn False.

from tests.etkl import fixtures as _F

_TEXT_OVER_NUMBERS = [("Port", "Tonnes"), ("ALB", "10"), ("ESP", "30"), ("GER", "50")]
_ALL_NUMBERS = [("ALB", "10"), ("ESP", "30"), ("GER", "50"), ("KWI", "70")]
_GREY, _WHITE, _RED = (0.8, 0.8, 0.8), (1.0, 1.0, 1.0), (0.8, 0.0, 0.0)

_U9_CASES = {
    # § 10.5's first case: a filled, differently-fonted text header over a numeric body
    "header": dict(rows=_TEXT_OVER_NUMBERS, head_font="Helvetica-Bold", head_fill=_GREY),
    # § 10.5's second case: row 0 typed and styled exactly as its body (cbh T2's shape)
    "plain": dict(rows=_ALL_NUMBERS),
    # one positive per feature: only that feature differs between row 0 and the body
    "dtype": dict(rows=_TEXT_OVER_NUMBERS),
    "font": dict(rows=_ALL_NUMBERS, head_font="Helvetica-Bold"),
    "glyph_fill": dict(rows=_ALL_NUMBERS, head_rgb=_RED),
    "rect_fill": dict(rows=_ALL_NUMBERS, head_fill=_GREY, box_fill=_WHITE),
    # the plan's literal "a filled rect behind row 0 only": the body has NO rect-fill value, so
    # § 10.3.2's condition 2 fails for the feature and the oracle is silent (plan finding, 3d.4)
    "rect_row0_only": dict(rows=_ALL_NUMBERS, head_fill=_GREY),
    # § 7's trap: a bold-headed box beside this plain one, on the same text lines
    "neighbour": dict(rows=_ALL_NUMBERS, neighbour=True),
}


def _u9_record_regions(tmp_path, name):
    """(pdf path, [every region the RECORD path hands to `assert_record_region`, in order])."""
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from iladub.etkl import compile as compile_mod
    kw = dict(_U9_CASES[name])
    p = str(tmp_path / f"{name}.pdf")
    _F.styled_box_pdf(p, kw.pop("rows"), **kw)
    seen, real = [], compile_mod.assert_record_region

    def spy(g, region, *a, **k):
        seen.append(region)
        return real(g, region, *a, **k)

    mp = pytest.MonkeyPatch()
    mp.setattr(compile_mod, "assert_record_region", spy)
    try:
        compile_mod.compile_tables(p, 0)
    finally:
        mp.undo()
    return p, seen


def _u9_region(tmp_path, name, first_word=None):
    """The ONE RECORD region of case `name` (whose row 0 starts with `first_word`, when given)."""
    p, seen = _u9_record_regions(tmp_path, name)
    if first_word is not None:
        seen = [r for r in seen
                if min((c for c in r.cells if c.row == 0), key=lambda c: c.col).text == first_word]
    assert len(seen) == 1, f"{name}: expected one RECORD region, got {len(seen)}"
    return p, seen[0]


def _u9_differs_only_in(p, region):
    """Precondition: which of the three style features differ, as sets, between row 0's cells and
    the body's cells of this region — measured off `cell_styles`, not assumed from the fixture."""
    from iladub.etkl.rowzero import cell_styles
    st = cell_styles(p, 0, region.cells)
    head = [s for (r, _c), s in st.items() if r == 0]
    body = [s for (r, _c), s in st.items() if r > 0]
    return {f for f in ("fonts", "glyph_fills", "rect_fills")
            if set().union(*(getattr(s, f) for s in head))
            != set().union(*(getattr(s, f) for s in body))}


def test_u9_header_filled_fonted_text_over_numbers_is_witnessed(tmp_path):
    from iladub.etkl.rowzero import row_zero_differs
    p, region = _u9_region(tmp_path, "header")
    assert _u9_differs_only_in(p, region) == {"fonts", "rect_fills"}
    assert row_zero_differs(region, p, 0) is True


def test_u9_row_zero_typed_and_styled_as_its_body_is_silent(tmp_path):
    from iladub.etkl.rowzero import row_zero_differs
    p, region = _u9_region(tmp_path, "plain")
    assert _u9_differs_only_in(p, region) == set()
    assert row_zero_differs(region, p, 0) is False


def test_u9_a_one_line_region_is_the_stated_blind_spot(tmp_path):
    """No body row, so condition 2 never holds: False, even on the case every feature witnesses.
    MEASURED: a one-line box on this fixture family classifies NON_TABLE ("fewer than 2 lines")
    and never reaches the RECORD path, so the one-line region is the header case's own region cut
    to row 0 — the oracle reads only `region.cells` and `region.band.unshown`."""
    from dataclasses import replace
    from iladub.etkl.rowzero import row_zero_differs
    p, region = _u9_region(tmp_path, "header")
    one = replace(region, cells=tuple(c for c in region.cells if c.row == 0))
    assert len(one.cells) == 2 and row_zero_differs(region, p, 0) is True
    assert row_zero_differs(one, p, 0) is False


@pytest.mark.parametrize("name, differs", [
    ("dtype", set()),
    ("font", {"fonts"}),
    ("glyph_fill", {"glyph_fills"}),
    ("rect_fill", {"rect_fills"}),
])
def test_u9_each_feature_alone_is_a_witness(tmp_path, name, differs):
    from iladub.etkl.rowzero import row_zero_differs
    p, region = _u9_region(tmp_path, name)
    assert _u9_differs_only_in(p, region) == differs, "precondition: only this feature"
    texts = {c.row: c.text for c in region.cells if c.col == 1}
    body_is_numeric = all(t.isdigit() for r, t in texts.items() if r > 0)
    assert body_is_numeric and (texts[0].isdigit() is (name != "dtype")), (
        "precondition: row 0's datatype differs from the body's in the dtype case only")
    assert row_zero_differs(region, p, 0) is True, f"{name}: the feature's witness was not found"


def test_u9_a_rect_behind_row_zero_only_is_not_a_witness(tmp_path):
    """§ 10.3.2's condition 2: a feature witnesses only where the body has SOME value of it. Here
    the body has no rect at all, so row 0's fill is unopposed and the oracle stays silent."""
    from iladub.etkl.rowzero import row_zero_differs
    p, region = _u9_region(tmp_path, "rect_row0_only")
    assert _u9_differs_only_in(p, region) == {"rect_fills"}
    assert row_zero_differs(region, p, 0) is False


def test_u9_containment_is_on_both_axes_a_neighbour_box_does_not_leak(tmp_path):
    """Spec § 7's trap (I-10-4): the bold `Site | Alpha` header of the box to the LEFT lies on this
    box's row-0 text line. A glyph belongs to a cell only when its centre is inside the cell's bbox
    on both axes, so it does not reach this plain box."""
    from iladub.etkl.rowzero import row_zero_differs
    p, region = _u9_region(tmp_path, "neighbour", first_word="ALB")
    assert row_zero_differs(region, p, 0) is False
    _p, left = _u9_region(tmp_path, "neighbour", first_word="Site")
    assert row_zero_differs(left, p, 0) is True, "control: the neighbour's own header witnesses"


def test_u9_an_unshown_row_zero_cell_contributes_no_datatype(tmp_path):
    """A5: `row_zero_differs` passes `region.band.unshown` to `grid_evidence`, so a hidden row-0
    cell types `tab:UnshownInk`, which abstains and contributes no family. The dtype case with its
    one witnessing address (row 0, the `Tonnes` column) hidden has nothing left to witness."""
    from dataclasses import replace
    from iladub.etkl.rowzero import row_zero_differs
    p, region = _u9_region(tmp_path, "dtype")
    assert row_zero_differs(region, p, 0) is True, "precondition: the address is the witness"
    hidden = replace(region, band=replace(region.band, unshown=((0, 1),)))
    assert row_zero_differs(hidden, p, 0) is False


def test_u9_an_unshown_row_zero_cell_contributes_no_style(tmp_path):
    """The style half of A5's reason: a glyph the page does not show has no font or fill a reader
    sees, for the same reason its `tab:gridText` is empty. The font case, with both row-0
    addresses hidden, has no row-0 value left."""
    from dataclasses import replace
    from iladub.etkl.rowzero import row_zero_differs
    p, region = _u9_region(tmp_path, "font")
    hidden = replace(region, band=replace(region.band, unshown=((0, 0), (0, 1))))
    assert row_zero_differs(hidden, p, 0) is False


def test_u9_a_missing_colour_or_font_gives_no_fact(tmp_path, monkeypatch):
    """Review Focus 4: a glyph or rect with no colour value (`None`), or a glyph with no font name,
    gives NO fact for that feature — never a `"None"` literal, which would be a value no body cell
    has, and so a false witness. The plain case, with every row-0 glyph's font and colour erased
    and a colourless filled rect laid over row 0."""
    from iladub.etkl import rowzero
    p, region = _u9_region(tmp_path, "plain")
    row0_bottom = max(c.bbox[3] for c in region.cells if c.row == 0)
    real = rowzero._page_objects

    def erased(pdf_path, page_number):
        chars, rects = real(pdf_path, page_number)
        chars = [dict(ch, fontname=None, non_stroking_color=None)
                 if (ch["top"] + ch["bottom"]) / 2 <= row0_bottom else ch for ch in chars]
        x0, x1 = min(c.bbox[0] for c in region.cells), max(c.bbox[2] for c in region.cells)
        rects = list(rects) + [{"x0": x0, "x1": x1, "top": 0.0, "bottom": row0_bottom,
                                "fill": True, "non_stroking_color": None}]
        return chars, rects

    monkeypatch.setattr(rowzero, "_page_objects", erased)
    st = rowzero.cell_styles(p, 0, region.cells)
    assert all(st[(0, c)] == rowzero.CellStyle(frozenset(), frozenset(), frozenset())
               for c in (0, 1)), {k: v for k, v in st.items() if k[0] == 0}
    g = rowzero.row_zero_evidence(region, p, 0)
    assert not [o for o in g.objects() if str(o) == "None"], "a 'None' literal was emitted"
    assert rowzero.row_zero_differs(region, p, 0) is False


def test_u9_colour_literal_is_canonical():
    """MEASURE (iv), pinned: pdfplumber 0.11.10 reports one gray as `(0,)` on a reportlab char,
    `(0.0,)` on a cbh-stem p0 char and `0.0` on a cbh-stem p0 rect. They are one colour and give
    one literal. A different component count is a different colour space and is not converted."""
    from iladub.etkl.rowzero import colour_literal
    assert colour_literal((0,)) == colour_literal((0.0,)) == colour_literal(0.0) == colour_literal(0)
    assert colour_literal([0.0, 0.0, 0.502]) == colour_literal((0.0, 0.0, 0.502))
    assert colour_literal((0.0, 0.0, 0.0)) != colour_literal((0.0,))
    for absent in (None, True, "P0", ("P0",), (), [None]):
        assert colour_literal(absent) is None, absent


def test_u9_style_facts_join_the_grid_cells_by_address(tmp_path):
    """A5's join: the style facts ride on the SAME `tab:GridCell` nodes `grid_evidence` mints, found
    through `tab:atGridRow` / `tab:atGridColumn`. Removing every style triple leaves exactly the
    graph `grid_evidence` builds from what `row_zero_differs` passes it, so no node was added."""
    from rdflib.compare import isomorphic
    from iladub.etkl import celltype, rowzero
    from iladub.etkl.orientation import _ncols, _region_cells
    p, region = _u9_region(tmp_path, "header")
    g = rowzero.row_zero_evidence(region, p, 0)
    style = {TAB.cellGlyphFont, TAB.cellGlyphFill, TAB.cellRectFill}
    styled = {s for s, pr, _o in g if pr in style}
    cells = set(g.subjects(RDF.type, TAB.GridCell))
    assert styled and styled <= cells and len(styled) == len(region.cells) == len(cells)
    bare = Graph()
    for t in g:
        if t[1] not in style:
            bare.add(t)
    assert isomorphic(bare, celltype.grid_evidence(_region_cells(region), _ncols(region),
                                                   unshown=region.band.unshown))


def test_u9_the_query_carries_no_numeric_literal():
    """I-10-4: the `.rq` compares by exact term equality and reads the row split from the evidence
    (`tab:bodyStartsAt`), so no number appears in it outside comments and IRIs."""
    import re
    q = open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "vocab",
                           "queries", "row-zero-differs.rq"), encoding="utf-8").read()
    no_iris = re.sub(r"<[^>\s]*>", "", q)
    body = "\n".join(ln.split("#", 1)[0] for ln in no_iris.splitlines())
    assert "ASK" in body and not re.findall(r"\d", body), re.findall(r".*\d.*", body)


_CBH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "corpus", "ag-trade",
                     "cbh-stem-2026-08-03.pdf")


@pytest.mark.corpus
@pytest.mark.skipif(not _os.path.exists(_CBH), reason="corpus not fetched")
def test_u9_cbh_p0_t1_is_witnessed_and_t2_is_silent():
    """§ 10.2's census on cbh-stem p0, now computed BY THE QUERY rather than by a Python probe:
    T1 (`PORT | WHEAT | …`, 5 x 7) is witnessed; T2 (`ALB | 1 - 15 October`, 4 x 2) is not."""
    from iladub.etkl import compile as compile_mod
    from iladub.etkl.rowzero import row_zero_differs
    seen, real = [], compile_mod.assert_record_region

    def spy(g, region, *a, **k):
        seen.append(region)
        return real(g, region, *a, **k)

    mp = pytest.MonkeyPatch()
    mp.setattr(compile_mod, "assert_record_region", spy)
    try:
        compile_mod.compile_tables(_CBH, 0)
    finally:
        mp.undo()
    got = {min((c for c in r.cells if c.row == 0), key=lambda c: c.col).text:
           (1 + max(c.row for c in r.cells), 1 + max(c.col for c in r.cells),
            row_zero_differs(r, _CBH, 0)) for r in seen}
    assert got == {"PORT": (5, 7, True), "ALB": (4, 2, False)}, got
