"""rowzero — does row 0 of a drawn table differ from its body? The one-way oracle of box-split § 10.

Spec `docs/superpowers/specs/2026-09-28-box-split-design.md` § 10.3.2. The DECISION is
`vocab/queries/row-zero-differs.rq`, an ASK over one region's transient evidence graph (AXIOM,
open-world derivation; its one NOT EXISTS closes within that graph). It is one-way: `True`
refutes "row 0 is data", `False` refutes nothing — a region with no body row, or a header typed
and styled exactly as its body, is silent (§ 10.3.2, "what it cannot see").

This module is the PROCEDURAL layer only (§ 10.4's table):

- `cell_styles` — raw extraction of each cell's drawn style from pdfplumber's marks;
- `row_zero_evidence` — puts those facts on the typed-cell evidence graph `grid_evidence` builds;
- `row_zero_differs` — invokes the query.

None of them decides header-vs-data, and none carries a constant or a tolerance (I-10-4).
Nothing calls this module yet: the ask site that consults it is Task 3d.6.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Sequence

from rdflib import Graph, Literal, RDF

from . import celltype
from .celltype import TAB

_Q = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries",
                  "row-zero-differs.rq")


@dataclass(frozen=True)
class CellStyle:
    """One cell's drawn style: the distinct values of each feature, as canonical literals."""
    fonts: frozenset[str]
    glyph_fills: frozenset[str]
    rect_fills: frozenset[str]


def colour_literal(value) -> str | None:
    """The canonical literal of one pdfplumber colour value, or None when there is no value.

    PROCEDURAL raw typing: it spells a source value, and decides nothing.

    MEASURED (MEASURE (iv), 2026-09-30, pdfplumber 0.11.10). On cbh-stem p0 every char's
    `non_stroking_color` is a `tuple[float]` of length 1 — `(0.0,)` 6933 times and `(1.0,)` 1019
    times, `ncs` DeviceGray throughout. The page's 190 rects carry a bare `float` 173 times (gray:
    `0.0` 169, `0.588` 4) and a `tuple` of three floats 17 times (RGB, e.g. `(0.0, 0.0, 0.502)`),
    and rects report no `ncs` at all. A reportlab char in the default fill colour reads `(0,)` —
    a tuple holding an INT. So one gray reaches us as `(0,)`, `(0.0,)` and `0.0`, and this spells
    all three the same: every component as a float, a bare number as one component. No gray on
    cbh-stem p0 is also drawn in RGB: no RGB value there has three equal components.

    A different COMPONENT COUNT is a different colour space, and is NOT converted: rects carry no
    colour space, so a one-component value may be DeviceGray or a spot-colour tint, and merging
    it into RGB would be a guess. The cost is at most a witness between two spellings of one
    colour, which refuses a `0` and so reproduces today's output (§ 10.2: never worse than today).

    No value — `None`, a bool, a pattern name or any non-numeric component, or no components at
    all — gives None, and the caller then emits NO fact. It never gives the string "None", which
    no body cell would share and which would therefore be a false witness (Review Focus 4). This
    is `boxes._fill_is_black`'s reading of the same field, which also refuses non-device values."""
    if value is None or isinstance(value, bool):
        return None
    comps = value if isinstance(value, (tuple, list)) else (value,)
    if not comps or not all(isinstance(c, (int, float)) and not isinstance(c, bool)
                            for c in comps):
        return None
    return ",".join(repr(float(c)) for c in comps)


def _page_objects(pdf_path: str, page_number: int) -> tuple[list[dict], list[dict]]:
    """pdfplumber's chars and rects for one page, as its own dicts. The one place this module
    opens a PDF, so a test can substitute the marks without writing a PDF."""
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        return list(page.chars), list(page.rects)


def cell_styles(pdf_path: str, page_number: int,
                cells: Sequence) -> dict[tuple[int, int], CellStyle]:
    """Each cell's drawn style, keyed by its `(row, col)` grid address.

    PROCEDURAL, and irreducible for the reason `extract_words` is: the source is a PDF's marks,
    and turning marks into typed facts is raw extraction. It reads, and decides nothing.

    - **glyphs:** a char belongs to the cell when its centre lies inside the cell's bbox on BOTH
      axes (I-10-4). Filtering by y alone is § 7's trap: on cbh-stem p0 band 9 it leaks the left
      box's glyphs into the right box, because the two boxes share text lines.
    - **fills:** a rect counts when it is filled and contains the cell's bbox centre.

    Every bound is a closed interval over the marks' own coordinates. There is no tolerance: a
    glyph whose centre is outside the bbox by any amount is not the cell's. A mark with no font
    name, or no readable colour (`colour_literal`), contributes no value to that feature.

    `cells` are `regions.Cell`s. Two cells at one address are refused: the facts are joined to the
    evidence graph by address, and a shared address would put one cell's style on another."""
    chars, rects = _page_objects(pdf_path, page_number)
    filled = [r for r in rects if r.get("fill")]
    out: dict[tuple[int, int], CellStyle] = {}
    for cell in cells:
        key = (int(cell.row), int(cell.col))
        if key in out:
            raise ValueError(f"cell_styles: two cells at grid address {key}")
        x0, top, x1, bottom = cell.bbox
        cx, cy = (x0 + x1) / 2.0, (top + bottom) / 2.0
        glyphs = [ch for ch in chars
                  if x0 <= (ch["x0"] + ch["x1"]) / 2.0 <= x1
                  and top <= (ch["top"] + ch["bottom"]) / 2.0 <= bottom]
        out[key] = CellStyle(
            fonts=frozenset(f for f in (ch.get("fontname") for ch in glyphs) if f),
            glyph_fills=frozenset(v for v in (colour_literal(ch.get("non_stroking_color"))
                                              for ch in glyphs) if v is not None),
            rect_fills=frozenset(v for v in (colour_literal(r.get("non_stroking_color"))
                                             for r in filled
                                             if r["x0"] <= cx <= r["x1"]
                                             and r["top"] <= cy <= r["bottom"])
                                 if v is not None),
        )
    return out


def _emit_cell_styles(g: Graph, styles: dict[tuple[int, int], CellStyle]) -> None:
    """Put each cell's style facts on the `tab:GridCell` node `grid_evidence` minted for its
    address, found through `tab:atGridRow` / `tab:atGridColumn` — never through the node's IRI,
    which `grid_evidence` mints from an enumeration index (`celltype.grid_evidence`,
    `_EV["cell-%d" % i]`), not from the address. It mints no node.

    PROCEDURAL plumbing: it moves extracted facts into the graph the query reads. An address that
    no grid cell carries, or that two carry, means the two address spaces disagree on this
    region, and it refuses rather than attach a style to the wrong cell or to none (the
    `holon._UnshownCarriage` precedent)."""
    node_at: dict[tuple[int, int], object] = {}
    for n in g.subjects(RDF.type, TAB.GridCell):
        key = (int(g.value(n, TAB.atGridRow)), int(g.value(n, TAB.atGridColumn)))
        if key in node_at:
            raise ValueError(f"row_zero_evidence: two grid cells at address {key}")
        node_at[key] = n
    for key, st in styles.items():
        if key not in node_at:
            raise ValueError(f"row_zero_evidence: no grid cell at address {key}")
        n = node_at[key]
        for v in st.fonts:
            g.add((n, TAB.cellGlyphFont, Literal(v)))
        for v in st.glyph_fills:
            g.add((n, TAB.cellGlyphFill, Literal(v)))
        for v in st.rect_fills:
            g.add((n, TAB.cellRectFill, Literal(v)))


def row_zero_evidence(region, pdf_path: str, page_number: int) -> Graph:
    """The evidence graph `row-zero-differs.rq` asks: `grid_evidence` over the region's cells,
    plus each shown cell's style facts.

    PROCEDURAL assembly; it decides nothing.

    `grid_evidence` receives what `orientation.looks_transposed` passes it (the region's own
    cells and column count) PLUS `unshown`, as `headers.header_body_split` passes it (plan
    amendment A5): without it a hidden row-0 cell is typed by its hidden text and can differ from
    the body, which is a false witness. `body_starts_at` is left at its default of 1, so row 0 is
    the head and every later row is body — the split the query reads from `tab:bodyStartsAt`.

    An unshown cell also gets NO style facts, for the reason its `tab:gridText` is empty: the page
    does not show that glyph, so no reader sees its font or its fill."""
    from .orientation import _ncols, _region_cells
    unshown = tuple(getattr(region.band, "unshown", ()) or ())
    hidden = {(int(r), int(c)) for r, c in unshown}
    g = celltype.grid_evidence(_region_cells(region), _ncols(region), unshown=unshown)
    shown = [c for c in region.cells if (int(c.row), int(c.col)) not in hidden]
    _emit_cell_styles(g, cell_styles(pdf_path, page_number, shown))
    return g


def row_zero_differs(region, pdf_path: str, page_number: int) -> bool:
    """True iff `row-zero-differs.rq` finds a witness that row 0 differs from the body of its
    column (spec § 10.3.2). One-way: `True` refutes "row 0 is data"; `False` refutes nothing.

    PROCEDURAL invocation only (the celltype precedent): the decision is the query's."""
    return celltype.run_ask(_Q, row_zero_evidence(region, pdf_path, page_number))
