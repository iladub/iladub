"""The scan step of the handwriting flavour (spec 2026-10-31 § 4.3). Licence: Apache-2.0.

A filled document is rasterised (pypdfium2, `render(scale=dpi/72)`), each page degraded like a scan
with OpenCV — rotation about the page centre (`warpAffine`), Gaussian blur, Gaussian noise, contrast
loss — and written back as an image-only PDF at the original page size (Pillow). `degrade` takes an
image and its parameters and NOTHING else: no text, no fill, no truth. It cannot invent a value
(§ 4.3: the scan step only degrades); `tests/test_synthetic_contracts_scan.py` pins that it adds no
ink to a white page.

The truth follows the page: `scan_matrix` is the 2x3 affine map the page underwent, in POINTS,
top-left origin (the truth's convention), and `affine_box` maps a truth box through it. The pixel
matrix handed to `warpAffine` is that same matrix conjugated into pixel coordinates, so the drawn
rotation and the recorded one are one matrix.

Justified PROCEDURAL (CLAUDE.md § 8): this module MAKES a document — rasterisation, image
arithmetic, PDF assembly — and exact affine arithmetic on boxes. The ranges in `scan_params`
(angle, blur, noise, contrast) are generation parameters (how much to degrade), not reading
tolerances; nothing here reads a document's content or answers a span/read/group question. No
reader may call it (A3).
"""
from __future__ import annotations

import random
from dataclasses import dataclass, replace
from io import BytesIO

import numpy as np
import pypdfium2 as pdfium
from PIL import Image

from scripts.synthetic_contracts.maps import Box

DPI = 200
ANGLE_MAX = 1.5            # degrees, generation parameter
BLUR = (0.4, 0.9)          # Gaussian sigma in pixels, generation parameter
NOISE = (3.0, 8.0)         # Gaussian noise sd in grey levels, generation parameter
CONTRAST = (0.85, 1.0)     # fraction of ink depth below paper white kept, generation parameter
JPEG_QUALITY = 85          # generation parameter
SCAN_SALT = 0x5343414E     # "SCAN": separates this stream from the fill's and the glyphs' draws


@dataclass(frozen=True)
class ScanParams:
    angle_deg: float
    blur_sigma: float
    noise_sd: float
    contrast: float
    dpi: int
    seed: int = 0  # the noise stream; per page, `scan_pages` derives seed + page number


def scan_params(seed: int) -> ScanParams:
    rng = random.Random(seed ^ SCAN_SALT)
    return ScanParams(angle_deg=rng.uniform(-ANGLE_MAX, ANGLE_MAX), blur_sigma=rng.uniform(*BLUR),
                      noise_sd=rng.uniform(*NOISE), contrast=rng.uniform(*CONTRAST), dpi=DPI,
                      seed=seed)


def scan_matrix(angle_deg: float, page_size: tuple[float, float]) -> np.ndarray:
    """Rotation by `angle_deg` about the page centre, in points, y down — the matrix
    `cv2.getRotationMatrix2D` builds (pinned equal by a test), written out in numpy so the truth
    arithmetic runs where OpenCV is not installed (CI installs no OpenCV)."""
    w, h = page_size
    cx, cy = w / 2, h / 2
    a, b = np.cos(np.radians(angle_deg)), np.sin(np.radians(angle_deg))
    return np.array([[a, b, (1 - a) * cx - b * cy], [-b, a, b * cx + (1 - a) * cy]])


def page_matrix(params: ScanParams, shape: tuple[int, int]) -> np.ndarray:
    """The points matrix `degrade` applies to an image of `shape` (rows, cols): rotation about the
    centre of the page as rasterised. `render_handwriting` records this one matrix as the truth's
    `transform`, so the drawn rotation and the recorded one cannot drift."""
    s = params.dpi / 72
    return scan_matrix(params.angle_deg, (shape[1] / s, shape[0] / s))


def _to_pixels(m_pt: np.ndarray, scale: float) -> np.ndarray:
    """Conjugate a points matrix into pixel indices: px = scale * pt - 0.5 (pixel i covers
    [i, i+1))."""
    a = np.array([[scale, 0.0, -0.5], [0.0, scale, -0.5], [0.0, 0.0, 1.0]])
    m3 = np.vstack([m_pt, [0.0, 0.0, 1.0]])
    return (a @ m3 @ np.linalg.inv(a))[:2]


def affine_box(box: Box, m: np.ndarray, page_size: tuple[float, float]) -> Box:
    """The bounding box of the four transformed corners, clipped to the page."""
    w, h = page_size
    corners = np.array([[box.x0, box.top, 1.0], [box.x1, box.top, 1.0],
                        [box.x0, box.bottom, 1.0], [box.x1, box.bottom, 1.0]])
    p = corners @ np.asarray(m, dtype=float).T
    xs, ys = np.clip(p[:, 0], 0.0, w), np.clip(p[:, 1], 0.0, h)
    return Box(box.page, float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max()))


def degrade(img: np.ndarray, params: ScanParams) -> np.ndarray:
    """Degrade one greyscale page image (uint8, white paper). Takes no text, no fill, no truth."""
    import cv2  # local: CI installs no OpenCV, and only rendering needs it
    hgt, wid = img.shape
    m = _to_pixels(page_matrix(params, img.shape), params.dpi / 72)
    out = cv2.warpAffine(img, m, (wid, hgt), flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=255)
    out = cv2.GaussianBlur(out, (0, 0), params.blur_sigma).astype(np.float64)
    out += np.random.default_rng(params.seed).normal(0.0, params.noise_sd, out.shape)
    out = 255.0 - params.contrast * (255.0 - out)
    return np.clip(np.rint(out), 0, 255).astype(np.uint8)


def rasterise(doc: pdfium.PdfDocument, dpi: int) -> list[np.ndarray]:
    return [np.asarray(doc[i].render(scale=dpi / 72, grayscale=True).to_pil().convert("L"))
            for i in range(len(doc))]


def scan_pages(doc: pdfium.PdfDocument, params: ScanParams) -> list[np.ndarray]:
    """Every page rasterised and degraded; page n's noise stream is `params.seed + n`."""
    return [degrade(img, replace(params, seed=params.seed + n))
            for n, img in enumerate(rasterise(doc, params.dpi), 1)]


def image_pdf(pages: list[np.ndarray], size: tuple[float, float]) -> bytes:
    """An image-only PDF, every page exactly `size` points (Pillow, per-axis resolution)."""
    w, h = size
    if len({p.shape for p in pages}) != 1:
        raise ValueError("pages of different pixel sizes: one resolution per document only")
    imgs = [Image.fromarray(p, mode="L") for p in pages]
    buf = BytesIO()
    imgs[0].save(buf, "PDF", save_all=True, append_images=imgs[1:],
                 dpi=(imgs[0].width * 72 / w, imgs[0].height * 72 / h), quality=JPEG_QUALITY)
    return buf.getvalue()
