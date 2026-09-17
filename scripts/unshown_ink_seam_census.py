"""unshown_ink_seam_census — where a per-cell 'unshown ink' fact can actually live.

Measurement only. Reads nothing the pipeline writes, writes nothing, decides nothing. It exists
so that every figure in docs/superpowers/2026-09-17-unshown-ink-spec-review.md can be re-run
rather than re-read, and so that the three seam claims it refutes stay refuted by a command.

  ./.venv/bin/python scripts/unshown_ink_seam_census.py --regions      # region census + reach
  ./.venv/bin/python scripts/unshown_ink_seam_census.py --blank        # the null control's population
  ./.venv/bin/python scripts/unshown_ink_seam_census.py --grain        # cell grain vs ink grain
  ./.venv/bin/python scripts/unshown_ink_seam_census.py --graph <pdf>  # what reaches the OUTPUT graph
  ./.venv/bin/python scripts/unshown_ink_seam_census.py --shape        # can an unshown cell CROSS?
  ./.venv/bin/python scripts/unshown_ink_seam_census.py --address      # do the two address spaces agree?

The four findings, and the mode that measures each:

  RF1  --graph    tab:GridCell is transient: 0 in the compiled graph, where tab:EntryCell is 406
                  and exactly 110 carry tab:cellText "0".
  RF2  --regions  regions.Cell and headers._grid_cells are two different cell notions (10.0% vs
                  95.4% of corpus ink), so "exactly one narrow place to cross" is false.
  RF3  --blank    tab:Blank, the null control's named set, is empty on 118 of 122 gridded regions
                  and on BOTH documents the disposal runs on.
  RF5  --grain    a cell may hold unshown and ordinary ink at once; gcap's 110 do not, cbh's 24 do.

RF4 (the cbh population is white-on-grey at 2.9601, not white-on-pale-blue at 1.6887) is measured
by the sibling instrument, `ink_contrast_probe.py`, whose colour code this module reuses.

Two later modes, added by the RESPEC (spec section 8), measure what the review left assumed:

  RS1  --shape    an EntryCell with an EMPTY tab:cellText is refused TODAY by tab:WrappedCellShape
                  (the drop-continuation guard), so the review's remedy needs that shape widened.
  RS2  --address  the persisted …#htable{b}-e{r}_{c} index space and headers._grid_cells' (r, c)
                  coincide on graincorp-capacity — 406/406 cells, 110/110 zeros, by SET IDENTITY.
                  Empirical, not structural: five EntryCell minting sites, two cell notions.
"""
from __future__ import annotations

import glob
import os
import sys
from collections import Counter

import pdfplumber
from rdflib import RDF, URIRef

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ink_contrast_probe import rgb, ratio, WHITE            # noqa: E402

from iladub.etkl import celltype                            # noqa: E402
from iladub.etkl.compile import page_bands                  # noqa: E402
from iladub.etkl.headers import _grid_cells                 # noqa: E402
from iladub.etkl.regions import classify, column_of         # noqa: E402

TAB = "https://w3id.org/iladub/tab#"
CORPUS = "corpus/*/*.pdf"
GCAP = "corpus/ag-trade/graincorp-capacity-2026-08-04.pdf"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ratio below which a glyph is counted for the grain census, per document. gcap's hidden set sits
# at 1.0856 and cbh's low-contrast control at 1.6887/2.9601; these are CENSUS BRACKETS for a
# measurement, never a decision rule — § 1.1 of the spec refutes the whole class of colour
# thresholds, and nothing in src/ reads this file.
GRAIN_BRACKETS = [("graincorp-capacity", 1.5, "gcap hidden set"),
                  ("cbh-stem", 3.0, "cbh low-contrast control")]


def npages(path):
    with pdfplumber.open(path) as pdf:
        return len(pdf.pages)


def backdrop(ch, rects):
    """The topmost filled rect whose box contains the char's centre; white when there is none."""
    cx, cy = (ch["x0"] + ch["x1"]) / 2, (ch["top"] + ch["bottom"]) / 2
    hit = None
    for r in rects:
        if r["x0"] <= cx <= r["x1"] and r["top"] <= cy <= r["bottom"]:
            hit = r
    return rgb(hit.get("non_stroking_color")) if hit else WHITE


def low_contrast_chars(path, page_number, thresh):
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[page_number]
        rects = [r for r in page.rects if r.get("fill")]
        out = []
        for ch in page.chars:
            fg, bg = rgb(ch.get("non_stroking_color")), backdrop(ch, rects)
            if fg is None or bg is None:
                continue
            if ratio(fg, bg) < thresh:
                out.append(ch)
    return out


def mode_regions():
    """RF2: the two cell notions, and the region census the spec deferred to the plan (§ 7.2)."""
    print("== region census, and the reach of each cell notion\n")
    kinds, tot_w, tot_grid, tot_chars, tot_incell = Counter(), 0, 0, 0, 0
    for path in sorted(glob.glob(CORPUS)):
        name = os.path.basename(path)
        d_w = d_grid = d_chars = d_incell = d_regions = 0
        for pn in range(npages(path)):
            with pdfplumber.open(path) as pdf:
                chars = [c for c in pdf.pages[pn].chars if c["text"].strip()]
            boxes = []
            for band in page_bands(path, pn):
                reg = classify(band)
                d_regions += 1
                kinds[reg.kind.value] += 1
                nw = sum(len(ln.words) for ln in band.lines)
                d_w += nw
                if reg.grid is not None:
                    d_grid += nw                    # every word of a gridded band lands in a cell
                boxes += [cell.bbox for cell in reg.cells]
            for c in chars:
                cx, cy = (c["x0"] + c["x1"]) / 2, (c["top"] + c["bottom"]) / 2
                if any(x0 - 1 <= cx <= x1 + 1 and t - 1 <= cy <= b + 1 for x0, t, x1, b in boxes):
                    d_incell += 1
            d_chars += len(chars)
        print(f"{name:42s} regions={d_regions:3d}  "
              f"chars in a regions.Cell {d_incell:6d}/{d_chars:6d} "
              f"{100.0 * d_incell / d_chars if d_chars else 0:5.1f}%  |  "
              f"words in a gridded band {d_grid:5d}/{d_w:5d} "
              f"{100.0 * d_grid / d_w if d_w else 0:5.1f}%")
        tot_w += d_w; tot_grid += d_grid; tot_chars += d_chars; tot_incell += d_incell
    print(f"\n{'CORPUS':42s} regions={sum(kinds.values()):3d}  "
          f"chars in a regions.Cell {tot_incell}/{tot_chars} "
          f"{100.0 * tot_incell / tot_chars:.1f}%  |  "
          f"words in a gridded band {tot_grid}/{tot_w} {100.0 * tot_grid / tot_w:.1f}%")
    print("by region kind:", dict(kinds))
    print("\nRF2: the two notions differ by an order of magnitude. headers._grid_cells re-derives "
          "its\n     own cells from band.lines and never sees a regions.Cell.")


def mode_blank():
    """RF3: the population § 4.3's null control names, per gridded region."""
    print("== tab:Blank, the null control's named set\n")
    g_regions = g_cells = g_blank = g_zero = 0
    for path in sorted(glob.glob(CORPUS)):
        name = os.path.basename(path)
        regions = cells = blank = zero = 0
        for pn in range(npages(path)):
            for band in page_bands(path, pn):
                reg = classify(band)
                if reg.grid is None:
                    continue
                cs = _grid_cells(band, reg.grid)
                nb = sum(1 for _, _, t in cs if celltype.is_blank(t))
                regions += 1; cells += len(cs); blank += nb
                zero += (nb == 0)
        print(f"{name:42s} gridded regions={regions:3d} cells={cells:5d} "
              f"tab:Blank={blank:4d}  regions with ZERO Blank: {zero}")
        g_regions += regions; g_cells += cells; g_blank += blank; g_zero += zero
    print(f"\nCORPUS: {g_regions} gridded regions, {g_cells} cells, {g_blank} tab:Blank cells; "
          f"{g_zero} regions ({100.0 * g_zero / g_regions:.0f}%) have NO tab:Blank cell at all")
    print("\nthe live alternative — UNPOPULATED grid positions, which tab:Blank never covers:")
    for path, idxs in [("corpus/ag-trade/cbh-stem-2026-08-03.pdf", [1]),
                       ("corpus/ag-trade/graincorp-capacity-2026-08-04.pdf", [3])]:
        bands = page_bands(path, 0)
        for i in idxs:
            band, reg = bands[i], classify(bands[i])
            b = reg.grid.boundaries
            occupied = {(r, column_of((w.x0 + w.x1) / 2.0, b))
                        for r, ln in enumerate(band.lines) for w in ln.words}
            allc = {(r, c) for r in range(len(band.lines)) for c in range(reg.grid.ncols)}
            empty = sorted(allc - occupied)
            col0 = sum(1 for _, c in empty if c == 0)
            print(f"  {os.path.basename(path)} band{i} "
                  f"({len(band.lines)}x{reg.grid.ncols}): populated {len(occupied)}/{len(allc)}, "
                  f"EMPTY {len(empty)} ({col0} of them in column 0)")


def mode_grain():
    """RF5: does a cell hold unshown ink ALONE, or beside ordinary ink?"""
    print("== cell grain vs ink grain, at the typing seam\n")
    for frag, thresh, label in GRAIN_BRACKETS:
        path = next(p for p in glob.glob(CORPUS) if frag in p)
        low = low_contrast_chars(path, 0, thresh)

        def n_low_in(w):
            return sum(1 for c in low
                       if w.x0 - 0.5 <= (c["x0"] + c["x1"]) / 2 <= w.x1 + 0.5
                       and w.top - 0.5 <= (c["top"] + c["bottom"]) / 2 <= w.bottom + 0.5)

        pure = mixed = pure_c = mixed_c = accounted = 0
        ex = []
        for idx, band in enumerate(page_bands(path, 0)):
            reg = classify(band)
            if reg.grid is None:
                continue
            b = reg.grid.boundaries
            for r, ln in enumerate(band.lines):
                groups = {}
                for w in ln.words:
                    groups.setdefault(column_of((w.x0 + w.x1) / 2.0, b), []).append(w)
                for c, ws in groups.items():
                    counts = [n_low_in(w) for w in ws]
                    n = sum(counts)
                    if not n:
                        continue
                    accounted += n
                    if any(k == 0 for k in counts):
                        mixed += 1; mixed_c += n
                        if len(ex) < 4:
                            ex.append((idx, r, c, " ".join(w.text for w in ws)[:64]))
                    else:
                        pure += 1; pure_c += n
        print(f"== {label} (ratio<{thresh}): {len(low)} low-contrast chars on the page")
        print(f"   inside a typed cell: {accounted}  (unassigned: {len(low) - accounted})")
        print(f"   PURE  (cell holds ONLY low-contrast ink): {pure} cells, {pure_c} chars")
        print(f"   MIXED (low-contrast AND ordinary ink):    {mixed} cells, {mixed_c} chars")
        for e in ex:
            print(f"       mixed: band{e[0]} r{e[1]} c{e[2]}: {e[3]!r}")
        print()


def mode_graph(path):
    """RF1: which cell class reaches the COMPILED graph."""
    from iladub.etkl.document import compile_document
    g = compile_document(path).graph
    print(f"== {os.path.basename(path)}: {len(g)} triples in the compiled graph\n")
    c = Counter(str(o).split("#")[-1] for s, p, o in g if p == RDF.type)
    for k, v in c.most_common(20):
        print(f"   {k:28s} {v}")
    for cls in ("GridCell", "EntryCell"):
        n = len(list(g.subjects(RDF.type, URIRef(TAB + cls))))
        print(f"\n   tab:{cls} in the compiled graph: {n}")
    zeros = [s for s in g.subjects(RDF.type, URIRef(TAB + "EntryCell"))
             if str(g.value(s, URIRef(TAB + "cellText"))).strip() == "0"]
    print(f"   tab:EntryCell whose tab:cellText is exactly '0': {len(zeros)}")
    print(f"   tab:gridText triples: {len(list(g.triples((None, URIRef(TAB + 'gridText'), None))))}")


def mode_shape():
    """RS1: can a cell whose tab:cellText is EMPTY cross the shipped physical membrane?"""
    from pyshacl import validate
    from rdflib import Graph

    print("== RS1: an unshown cell (empty cellText + unshownText) against the SHIPPED shapes\n")
    data = Graph().parse(data="""
    @prefix tab: <https://w3id.org/iladub/tab#> .
    <urn:c1> a tab:EntryCell ; tab:cellText "" ; tab:onPage 0 ;
       tab:unshownText "0" ; tab:hasBBox <urn:b1> .
    <urn:b1> a tab:BBox ; tab:x0 1.0 ; tab:x1 2.0 .
    <urn:c2> a tab:EntryCell ; tab:cellText "10,000" ; tab:onPage 0 ; tab:hasBBox <urn:b2> .
    <urn:b2> a tab:BBox ; tab:x0 1.0 ; tab:x1 2.0 .
    """, format="turtle")
    sh = Graph().parse(os.path.join(REPO, "vocab/shapes/tab-physical-shapes.ttl"))
    ont = Graph().parse(os.path.join(REPO, "vocab/ontology/tab.ttl"))
    conforms, _, txt = validate(data + ont, shacl_graph=sh, inference="rdfs", advanced=True)
    print(f"   conforms: {conforms}   (c1 = unshown, c2 = ordinary ink)")
    for ln in txt.splitlines():
        if any(k in ln for k in ("Source Shape:", "Focus Node:", "Message:")):
            print("  " + ln.strip())


def mode_address(path=GCAP):
    """RS2: does the worker's grid address space reach the persisted cell?"""
    import re as _re
    from iladub.etkl.document import compile_document

    print(f"== RS2: grid (r, c) vs persisted EntryCell index, {os.path.basename(path)}\n")
    grid_zero, grid_all = set(), set()
    for idx, band in enumerate(page_bands(path, 0)):
        reg = classify(band)
        if reg.grid is None:
            continue
        cells = _grid_cells(band, reg.grid)
        print(f"   band {idx}: {len(band.lines)} lines x {reg.grid.ncols} cols, "
              f"{len(cells)} populated cells")
        for (r, c, t) in cells:
            grid_all.add((idx, r, c))
            if t.strip() == "0":
                grid_zero.add((idx, r, c))
    print(f"   grid-space cells whose joined text is '0': {len(grid_zero)}")

    g = compile_document(path).graph
    pat = _re.compile(r"#h?table(\d+)-e(\d+)_(\d+)$")
    persisted_zero, persisted_all, unparsed = set(), set(), 0
    for e in g.subjects(RDF.type, URIRef(TAB + "EntryCell")):
        m = pat.search(str(e))
        if not m:
            unparsed += 1
            continue
        key = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        persisted_all.add(key)
        if str(g.value(e, URIRef(TAB + "cellText"))).strip() == "0":
            persisted_zero.add(key)
    print(f"   EntryCells parsed: {len(persisted_all)}  unparsed IRI shape: {unparsed}")
    print(f"   persisted cells whose cellText is '0': {len(persisted_zero)}")

    for tbl in sorted({t for t, _, _ in persisted_zero}):
        P = {(r, c) for t, r, c in persisted_zero if t == tbl}
        for bidx in sorted({b for b, _, _ in grid_zero}):
            G = {(r, c) for b, r, c in grid_zero if b == bidx}
            if not (P and G):
                continue
            print(f"   table {tbl} vs band {bidx}: |P|={len(P)} |G|={len(G)} "
                  f"identical={P == G}  P-only={sorted(P - G)[:4]} G-only={sorted(G - P)[:4]}")
    for tbl in sorted({t for t, _, _ in persisted_all}):
        P = {(r, c) for t, r, c in persisted_all if t == tbl}
        for bidx in sorted({b for b, _, _ in grid_all}):
            G = {(r, c) for b, r, c in grid_all if b == bidx}
            if len(P) == len(G) and P and G:
                print(f"   ALL cells, table {tbl} vs band {bidx}: {len(P)} each, "
                      f"identical={P == G}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--regions" in args:
        mode_regions()
    elif "--blank" in args:
        mode_blank()
    elif "--grain" in args:
        mode_grain()
    elif "--shape" in args:
        mode_shape()
    elif "--address" in args:
        rest = [a for a in args if not a.startswith("--")]
        mode_address(rest[0] if rest else GCAP)
    elif "--graph" in args:
        rest = [a for a in args if not a.startswith("--")]
        mode_graph(rest[0] if rest else GCAP)
    else:
        print(__doc__)
