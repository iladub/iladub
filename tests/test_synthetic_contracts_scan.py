"""Synthetic contract set Task 5: simulated handwriting + scan (spec § 4.3).

`affine_box`, `degrade` and `scan_params` tests are CI-runnable. The handwriting tests are local
only: they skip when the templates are absent under synthetic/templates/ or the handwriting TTFs are
absent from /System/Library/Fonts/Supplemental/. Their oracle is the OUTPUT PDF rasterised back by
pypdfium2 (and pdfplumber for the text layer), compared against the degraded UNFILLED page — the
template's own ink (dot leaders sit inside every blank) is subtracted, not counted as the value.
"""
import inspect
from dataclasses import replace
from functools import lru_cache
from io import BytesIO

import numpy as np
import pytest
from pyshacl import validate
from rdflib import Graph

from scripts.synthetic_contracts import manifest as mf
from scripts.synthetic_contracts.fills import FILLS_DIR, Fill, ValueTooLong, load_fill
from scripts.synthetic_contracts.maps import Blank, Box, Part, PartMap, load_map
from scripts.synthetic_contracts.scan import (ScanParams, affine_box, degrade, scan_matrix,
                                              scan_params)

EX = mf.REPO / "examples" / "synthetic-contracts"
FILLS = sorted(p.stem for p in FILLS_DIR.glob("*.ttl"))
DARK = 100        # the brief's "darker than 100"
MIN_NEW_INK = 0.02  # the brief's ">= 2 % pixels"


# Rotations by +-90 deg about (100, 100), written out by hand (y down, OpenCV's sign convention):
# +90: (x, y) -> (y, 200 - x);  -90: (x, y) -> (200 - y, x).
R90 = np.array([[0.0, 1.0, 0.0], [-1.0, 0.0, 200.0]])
R270 = np.array([[0.0, -1.0, 200.0], [1.0, 0.0, 0.0]])


def test_affine_identity():
    m = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    b = Box(3, 10.5, 20.25, 110.0, 30.0)
    assert affine_box(b, m, (595.0, 842.0)) == b


def test_affine_rotation_known():
    # 90 deg about (100, 100) in y-down coordinates (OpenCV's convention, the one degrade uses):
    # (x, y) -> (y, 200 - x). The box x 110..130, y 90..95 has corners mapping to
    # x in {90, 95}, y in {90, 70}: the box (90, 70, 95, 90).
    b = affine_box(Box(1, 110.0, 90.0, 130.0, 95.0), R90, (400.0, 400.0))
    assert b.page == 1
    assert [round(v, 9) for v in (b.x0, b.top, b.x1, b.bottom)] == [90.0, 70.0, 95.0, 90.0]
    # clipped to the page: -90 deg about (100, 100) is (x, y) -> (200 - y, x), so y 190..260 lands
    # on x -60..10 and is cut at the left edge; x 0..50 lands on y 0..50.
    c = affine_box(Box(1, 0.0, 190.0, 50.0, 260.0), R270, (400.0, 400.0))
    assert [round(v, 9) for v in (c.x0, c.top, c.x1, c.bottom)] == [0.0, 0.0, 10.0, 50.0]


def test_scan_matrix_is_known_rotation():
    assert np.allclose(scan_matrix(90.0, (200.0, 200.0)), R90, atol=1e-12)
    assert np.allclose(scan_matrix(-90.0, (200.0, 200.0)), R270, atol=1e-12)


def test_scan_matrix_is_opencvs():
    # degrade hands this matrix (in pixels) to cv2.warpAffine: it must be OpenCV's own convention.
    cv2 = pytest.importorskip("cv2")
    for ang in (-1.5, -0.3, 0.0, 0.7, 1.5, 90.0):
        assert np.allclose(scan_matrix(ang, (595.32, 841.92)),
                           cv2.getRotationMatrix2D((297.66, 420.96), ang, 1.0), atol=1e-9)


def test_degrade_adds_no_ink():
    cv2 = pytest.importorskip("cv2")
    img = np.full((200, 200), 255, dtype=np.uint8)
    for seed in range(5):
        p = replace(scan_params(seed), angle_deg=1.5 if seed % 2 else -1.5)
        out = degrade(img, p)
        assert out.shape == img.shape and out.dtype == np.uint8
        assert out.mean() >= 240, (seed, out.mean())
        k = np.ones((5, 5), np.float64) / 25
        win = cv2.filter2D(out.astype(np.float64), -1, k, borderType=cv2.BORDER_REPLICATE)
        assert win.min() >= 128, (seed, win.min())


def test_degrade_takes_no_text():
    assert list(inspect.signature(degrade).parameters) == ["img", "params"]


def test_scan_params_seeded():
    a, b = scan_params(7), scan_params(7)
    assert a == b and isinstance(a, ScanParams) and a.dpi == 200
    angles = [scan_params(s).angle_deg for s in range(200)]
    assert all(-1.5 <= x <= 1.5 for x in angles)
    assert len(set(angles)) > 150, "angle varies with the seed"


# ---------------------------------------------------------------- handwriting (local only)

def _need_fonts():
    pytest.importorskip("cv2")
    from scripts.synthetic_contracts.flavours import handwriting as hw
    missing = [p for p in hw.HAND_FONTS.values() if not p.exists()]
    if missing:
        pytest.skip(f"local only: handwriting fonts absent: {missing}")
    return hw


@lru_cache(maxsize=None)
def _render(fid):
    hw = _need_fonts()
    f = load_fill(fid)
    t = mf.load_manifest()[f.template]
    try:
        mf.verify(t)
    except mf.TemplateMissing:
        pytest.skip(f"local only: {t.id} template absent under synthetic/templates/")
    return t, f, hw.render_handwriting(t, load_map(f.template), f)


def _raster(pdf_bytes, dpi):
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(pdf_bytes)
    return [np.asarray(doc[i].render(scale=dpi / 72, grayscale=True).to_pil().convert("L"))
            for i in range(len(doc))]


@lru_cache(maxsize=None)
def _unfilled(fid):
    """The same template through the same scan AND the same output stage (image-only PDF, rendered
    back) with nothing drawn: the template's own ink, degraded. The output stage matters: the JPEG
    round trip and pdfium's resampling flip ~70,000 template pixels per document across the
    threshold (measured 2026-10-31), so a base taken before it counts template edges as new ink."""
    from scripts.synthetic_contracts.overlay import overlay
    from scripts.synthetic_contracts.scan import image_pdf, scan_pages
    t, f, _ = _render(fid)
    p = scan_params(f.seed)
    doc = overlay(mf.template_path(t), lambda c, n: None)
    return _raster(image_pdf(scan_pages(doc, p), tuple(doc[0].get_size())), p.dpi)


def _new_ink(fid):
    t, f, (pdf, truth) = _render(fid)
    out, base = _raster(pdf, scan_params(f.seed).dpi), _unfilled(fid)
    assert [p.shape for p in out] == [p.shape for p in base]
    return truth, [(o < DARK) & ~(u < DARK) for o, u in zip(out, base)]


def _px(b, s):
    return (slice(int(b.top * s), int(np.ceil(b.bottom * s))),
            slice(int(b.x0 * s), int(np.ceil(b.x1 * s))))


@pytest.mark.parametrize("fid", FILLS)
def test_scan_truth_boxes_contain_ink(fid):
    truth, new = _new_ink(fid)
    s = scan_params(load_fill(fid).seed).dpi / 72
    for v in truth.values:
        d = new[v.box.page - 1][_px(v.box, s)].mean()
        assert d >= MIN_NEW_INK, (v.field, v.value, round(float(d), 4))


@pytest.mark.parametrize("fid", FILLS)
def test_scan_new_ink_lies_in_truth_boxes(fid):
    # The converse of the test above, and the stronger of the two under skew: of all the ink the
    # fill added to the scanned document, at least 99 % lies inside the value truth boxes. The
    # remainder is the output stage re-encoding template pixels next to a value by a grey level or
    # two across the threshold — measured 2026-10-31 at most 12 of 56,993 pixels (usda-ffp-cp-2);
    # truth boxes left un-skewed at 1.5 deg leave 21-38 % of it outside (all 12 fills fail).
    truth, new = _new_ink(fid)
    s = scan_params(load_fill(fid).seed).dpi / 72
    inside = [np.zeros(p.shape, bool) for p in new]
    for v in truth.values:
        inside[v.box.page - 1][_px(v.box, s)] = True
    total = sum(int(p.sum()) for p in new)
    kept = sum(int((p & i).sum()) for p, i in zip(new, inside))
    assert total > 0 and kept / total >= 0.99, (kept, total)


@pytest.mark.parametrize("fid", FILLS[:2])
def test_scan_has_no_text_layer(fid):
    import pdfplumber
    t, f, (pdf, truth) = _render(fid)
    with pdfplumber.open(BytesIO(pdf)) as d:
        assert len(d.pages) == t.pages
        assert sum(len(p.chars) for p in d.pages) == 0
        with pdfplumber.open(mf.template_path(t)) as tpl:
            for po, pt in zip(d.pages, tpl.pages):
                assert [round(x, 2) for x in (po.width, po.height)] == \
                    [round(x, 2) for x in (pt.width, pt.height)]


@pytest.mark.parametrize("fid", FILLS[:1])
def test_scan_truth_conforms_with_transform(fid):
    t, f, (pdf, truth) = _render(fid)
    assert truth.flavour == "handwriting-scan" and truth.fills == (f.id,) and truth.seed == f.seed
    assert {v.field: v.value for v in truth.values} == f.values
    assert truth.transform is not None and len(truth.transform) == 6
    g = Graph().parse(data=truth.to_turtle(), format="turtle")
    ok, _, report = validate(g + Graph().parse(EX / "synthetic.ttl"),
                             shacl_graph=Graph().parse(EX / "shapes.ttl"),
                             inference="rdfs", advanced=True)
    assert ok, report


@pytest.mark.parametrize("fid", FILLS[:3])
def test_handwriting_ink_inside_truth(fid):
    # The jittered glyphs, rendered alone and undegraded: every dark pixel lies inside some value's
    # (pre-scan) box. One pixel of slack on each side is the rasteriser's anti-aliasing reach — a
    # property of rendering a vector edge onto a pixel grid, not a tuned reading tolerance.
    hw = _need_fonts()
    f = load_fill(fid)
    m = load_map(f.template)
    t = mf.load_manifest()[f.template]
    try:
        mf.verify(t)
    except mf.TemplateMissing:
        pytest.skip("local only")
    glyphs, values = hw.place_glyphs(m, f)
    pages = hw.ink_only(mf.template_path(t), glyphs)
    s = 200 / 72
    for n, img in enumerate(pages, 1):
        inside = np.zeros(img.shape, bool)
        for v in values:
            if v.box.page == n:
                inside[max(0, int(v.box.top * s) - 1):int(np.ceil(v.box.bottom * s)) + 1,
                       max(0, int(v.box.x0 * s) - 1):int(np.ceil(v.box.x1 * s)) + 1] = True
        stray = (img < 128) & ~inside
        assert not stray.any(), (n, int(stray.sum()))
        if any(v.box.page == n for v in values):
            assert (img < 128).any(), "ink was drawn"


def test_handwriting_refuses_value_wider_than_blank():
    hw = _need_fonts()
    box = Box(1, 100.0, 100.0, 130.0, 110.0)
    m = PartMap("x", (Part("form", "contract-form", (Box(1, 0, 0, 595, 842),), None),),
                (Blank("party.seller", box, "form"),), (), "draft")
    f = Fill("x-1", "x", 1, {"party.seller": "Northwind Grain Trading Ltd"}, "Helvetica", 9.0)
    with pytest.raises(ValueTooLong) as e:
        hw.place_glyphs(m, f)
    assert e.value.field == "party.seller"
    ok = Fill("x-1", "x", 1, {"party.seller": "AB"}, "Helvetica", 9.0)
    _, (v,) = hw.place_glyphs(m, ok)
    assert box.x0 <= v.box.x0 and v.box.x1 <= box.x1
