"""The grid-donation DESIGN census (2026-09-11, `main` at 808aa7a) — the three measurements
`docs/superpowers/plans/2026-09-11-grid-donation.md` § Measurement rests on:

  M1  the wall clock of `derive_data_grid` per page against `page_bands`;
  M2  whether every band that owns a `_rule_boundaries` vector has a line 0 that
      re-identifies UNIQUELY among the page's text lines by whitespace-stripped ink
      (never by index — [[R202]]);
  M3  the (donor, continuation) pairs the relation yields WITHOUT its tiling clause —
      earlier on the page, wholly drawn, same leaf-column count — and the verdict of the
      plan's disposal on each: `region_tiles` on a scratch graph AND every data cell
      `cell_round_trips`. The reading is built the plan's way (DECISION D: the donor's own
      `infer_leaf_grid`, the donor's row-0 cells, the continuation's rows shifted by one),
      not the spike's (`scripts/grid_donation_spike.py` prepends the donor's line).

Measured output at 808aa7a: 5 pairs, all bfs p6, all accepted — the census's 5 exactly
(`scripts/grid_agreement_census.py`); datagrid 4.9 s / page_bands 39.0 s over 27 pages;
7 donor-vector bands, line-0 identity unique on 7 of 7.

PROCEDURAL by CLAUDE.md §8: an instrument that reads shipped derivations and prints where
they agree. It decides nothing, ships no behaviour, and carries no constant of its own.

Run from the repo root (needs the gitignored corpus):

    PYTHONPATH=. .venv/bin/python scripts/grid_donation_design_census.py
"""
from __future__ import annotations

import glob
import os
import sys
import time
from dataclasses import replace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rdflib import Graph, URIRef  # noqa: E402

from grid_agreement_census import straddlers, wholly_drawn  # noqa: E402
from iladub.etkl.compile import page_bands  # noqa: E402
from iladub.etkl.datagrid import derive_data_grid  # noqa: E402
from iladub.etkl.document import page_count  # noqa: E402
from iladub.etkl.geometry import extract_words, text_lines  # noqa: E402
from iladub.etkl.grid import _rule_boundaries  # noqa: E402
from iladub.etkl.holon import assert_record_region, cell_round_trips  # noqa: E402
from iladub.etkl.regions import ClassifiedRegion, RegionKind, assign_cells, classify  # noqa: E402
from iladub.etkl.tiling import region_tiles  # noqa: E402


def key(line):
    """Band words are word GROUPS (`1 736 124` is one word); page words are raw. Compare
    the ink with whitespace removed, as scripts/donor_header_criterion.py does."""
    return "".join(w.text for w in sorted(line.words, key=lambda w: w.x0)).replace(" ", "")


def main():
    tot_dg = tot_pb = 0.0
    donors_total = ident_unique = ident_multi = ident_none = 0
    pairs = accepted = 0
    for pdf in sorted(glob.glob("corpus/*/*.pdf")):
        name = os.path.basename(pdf).split("-")[0]
        for p in range(page_count(pdf)):
            t = time.perf_counter()
            bands = page_bands(pdf, p)
            tot_pb += time.perf_counter() - t
            t = time.perf_counter()
            dg = derive_data_grid(pdf, p)
            tot_dg += time.perf_counter() - t
            lines = [l for l in sorted(text_lines(extract_words(pdf, p)), key=lambda l: l.top)
                     if l.words]
            vec = {}
            for j, b in enumerate(bands):
                try:
                    xs = _rule_boundaries(b)
                except Exception:  # noqa: BLE001
                    xs = None
                if xs is None or len(xs) < 3 or not wholly_drawn(b, xs):
                    continue
                vec[j] = xs
                donors_total += 1
                hits = [i for i, l in enumerate(lines) if key(l) == key(b.lines[0])]
                if len(hits) == 1:
                    ident_unique += 1
                elif hits:
                    ident_multi += 1
                else:
                    ident_none += 1
                if len(hits) != 1:
                    print(f"  {name} p{p} band{j}: line0 hits={hits}")
            for i, b in enumerate(bands):
                try:
                    reg = classify(b)
                except Exception:  # noqa: BLE001
                    continue
                if reg.kind is not RegionKind.RECORD_TABLE:
                    continue
                for j, xs in vec.items():
                    if j >= i or len(xs) - 1 != reg.grid.ncols:
                        continue
                    pairs += 1
                    donor = classify(bands[j])
                    head = tuple(c for c in donor.cells if c.row == 0)
                    body = tuple(replace(c, row=c.row + 1) for c in assign_cells(b, donor.grid))
                    dreg = ClassifiedRegion(RegionKind.RECORD_TABLE, b, donor.grid, head + body,
                                            "donated")
                    sc = Graph()
                    n = assert_record_region(sc, dreg, URIRef("urn:x#t"), URIRef("urn:x"), p)
                    tiles = bool(region_tiles(sc)) if n else False
                    rt = all(cell_round_trips(c, donor.grid.boundaries) for c in body)
                    hits = [k for k, l in enumerate(lines) if key(l) == key(bands[j].lines[0])]
                    ref = ("?" if dg is None or len(hits) != 1
                           else ("body" if hits[0] in dg.rows else dg.refusals.get(hits[0])))
                    ok = tiles and rt
                    accepted += ok
                    print(f"{name} p{p} band{i} <- donor band{j}: ncols={reg.grid.ncols} "
                          f"straddlers={len(straddlers(b, xs))} "
                          f"donor.grid==xs:{list(donor.grid.boundaries) == xs} entries={n} "
                          f"tiles={tiles} rt={rt} donor line0 datagrid={ref} -> "
                          f"{'ACCEPT' if ok else 'refuse'}")
    print(f"\npage_bands total {tot_pb:.1f}s; derive_data_grid total {tot_dg:.1f}s over 27 pages")
    print(f"donor-vector bands: {donors_total}; line0 identity unique={ident_unique} "
          f"multi={ident_multi} none={ident_none}")
    print(f"structural pairs (no tiling clause): {pairs}; accepted by disposal: {accepted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
