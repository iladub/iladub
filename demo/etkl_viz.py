"""Visualization helpers for the ETKL increment-1a showcase notebook.

The point of the notebook is the *pipeline* (extract_words -> text_lines ->
detect_bands -> infer_leaf_grid); these helpers just draw its intermediate
state over the rendered page so the geometry is visible. Coordinates are PDF
points; the page is rendered at `dpi`, so pixel = point * (dpi / 72).
pdfplumber `top`/`x0` and the rendered image both use a top-left origin, so no
y-flip is needed.
"""
from __future__ import annotations

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pypdfium2 as pdfium

from iladub.etkl.grid import _column_blank_profile

_BAND_COLORS = ["#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b3", "#937860"]


def render_page(pdf_path: str, dpi: int = 150):
    """Return (rgb_image ndarray, scale) for page 0. scale = dpi / 72."""
    page = pdfium.PdfDocument(pdf_path)[0]
    scale = dpi / 72.0
    img = np.asarray(page.render(scale=scale).to_pil().convert("RGB"))
    return img, scale


def _page_ax(img, title, figsize=(7.5, 9.7)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(img)
    ax.set_title(title, fontsize=13, weight="bold", loc="left")
    ax.set_xticks([])
    ax.set_yticks([])
    return fig, ax


def show_page(img, title="The page — what a human eye reads"):
    fig, _ = _page_ax(img, title)
    return fig


def draw_words(img, scale, words, title="Step 1 · geometry — words measured in points"):
    """Overlay each word's bounding box (the raw measured geometry)."""
    fig, ax = _page_ax(img, title)
    for w in words:
        ax.add_patch(mpatches.Rectangle(
            (w.x0 * scale, w.top * scale),
            (w.x1 - w.x0) * scale, (w.bottom - w.top) * scale,
            fill=False, edgecolor="crimson", linewidth=0.8))
    ax.text(0.01, -0.02, f"{len(words)} words, each with an (x0, x1, top, bottom) box in points",
            transform=ax.transAxes, fontsize=10, color="crimson", va="top")
    return fig


def draw_bands(img, scale, bands, title="Step 2-3 · bands — layout from vertical whitespace"):
    """Shade each detected band across the page + a side profile of ink-by-row."""
    fig, (ax, axp) = plt.subplots(
        1, 2, figsize=(9.5, 9.7), gridspec_kw={"width_ratios": [4, 1]})
    ax.imshow(img)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=13, weight="bold", loc="left")
    W = img.shape[1]
    for i, b in enumerate(bands):
        color = _BAND_COLORS[i % len(_BAND_COLORS)]
        y0, y1 = b.top * scale, b.bottom * scale
        ax.add_patch(mpatches.Rectangle(
            (0, y0), W, (y1 - y0), facecolor=color, alpha=0.20,
            edgecolor=color, linewidth=1.5))
        ax.text(W * 0.985, (y0 + y1) / 2, f"band {i}\n{len(b.lines)} line(s)",
                ha="right", va="center", fontsize=9, color=color, weight="bold")

    # side panel: fraction of page width inked at each y (ink runs = bands)
    H = img.shape[0]
    ink = (img.mean(axis=2) < 200)            # dark pixels = ink
    row_ink = ink.mean(axis=1)                # fraction inked per pixel-row
    axp.plot(row_ink, np.arange(H), color="#333", linewidth=0.8)
    axp.fill_betweenx(np.arange(H), 0, row_ink, color="#333", alpha=0.25)
    axp.set_ylim(H, 0)
    axp.set_xlim(0, max(0.05, row_ink.max() * 1.1))
    axp.set_title("ink per row →\nblank gaps split bands", fontsize=9)
    axp.set_yticks([]); axp.set_xticks([])
    return fig


def draw_grid(img, scale, band, grid,
              title="Step 4 · grid — column gutters from vertical whitespace"):
    """Crop to the table band, overlay the leaf-grid boundaries, and plot the
    column blank-fraction profile with detected gutters underneath."""
    xs0 = min(w.x0 for ln in band.lines for w in ln.words)
    xs1 = max(w.x1 for ln in band.lines for w in ln.words)
    pad = 12.0
    x0px, x1px = int((xs0 - pad) * scale), int((xs1 + pad) * scale)
    y0px, y1px = int((band.top - pad) * scale), int((band.bottom + pad) * scale)
    crop = img[y0px:y1px, x0px:x1px]

    fig, (ax, axp) = plt.subplots(
        2, 1, figsize=(9, 6.4), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    fig.suptitle(title, fontsize=13, weight="bold", x=0.02, ha="left", y=1.0)
    ax.imshow(crop, extent=[xs0 - pad, xs1 + pad, band.bottom + pad, band.top - pad])
    ax.set_title(
        f"ncols = {grid.ncols}    pitch = {grid.pitch:.0f} pt    confidence = {grid.confidence:.2f}",
        fontsize=11, color="#1f9e4d", weight="bold", loc="left", pad=6)
    for b in grid.boundaries:
        ax.axvline(b, color="#1f9e4d", linewidth=1.6, alpha=0.9)
    ax.set_yticks([])

    blank = _column_blank_profile(band, xs0, xs1)   # blank fraction per 1pt x-bin
    xbins = np.arange(len(blank)) + xs0
    axp.fill_between(xbins, 0, blank, color="#888", alpha=0.4, step="mid")
    axp.plot(xbins, blank, color="#444", linewidth=0.8)
    axp.axhline(0.98, color="crimson", linestyle="--", linewidth=1,
                label="gutter threshold (0.98)")
    axp.fill_between(xbins, 0, 1, where=blank >= 0.98, color="#1f9e4d", alpha=0.25,
                    step="mid", label="detected gutter")
    for b in grid.boundaries:
        axp.axvline(b, color="#1f9e4d", linewidth=1.4)
    axp.set_ylim(0, 1.05)
    axp.set_ylabel("blank\nfraction", fontsize=9)
    axp.set_xlabel("x (points)")
    axp.legend(loc="lower right", fontsize=8, framealpha=0.9)
    fig.tight_layout()
    return fig
