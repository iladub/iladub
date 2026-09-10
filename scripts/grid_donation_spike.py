"""SPIKE instrument (R201 handoff § 5b, run 2026-09-10): the DONATED reading of bfs p6 bands
4/5/6/8/9 under band 2's wholly-drawn grid, put past `region_tiles` — plus a CONTROL that
donates band 2's line 1 (a wrapped header continuation) as the header instead.

PROCEDURAL by CLAUDE.md §8: it builds one candidate reading by hand and prints what the
shipped membrane says about it. It decides nothing and ships no behaviour. Results and what
they refute: `docs/superpowers/2026-09-10-the-donated-reading-tiles-handoff.md` § 2.

Run from the repo root (needs the gitignored corpus):

    PYTHONPATH=. .venv/bin/python scripts/grid_donation_spike.py
"""
import sys
from rdflib import Graph, URIRef
from iladub.etkl.compile import page_bands
from iladub.etkl.grid import _rule_boundaries, LeafGrid
from iladub.etkl.regions import classify, assign_cells, ClassifiedRegion, RegionKind
from iladub.etkl.bands import Band
from iladub.etkl.holon import assert_record_region, cell_round_trips
from iladub.etkl.tiling import region_tiles

PDF = "corpus/gov-stats/bfs-population-bilan-2023.pdf"
PAGE = 6
DOC = URIRef("urn:spike:bfs")

def run(region, tag):
    scratch = Graph()
    n = assert_record_region(scratch, region, URIRef(f"{DOC}#{tag}"), DOC, PAGE)
    tiles = region_tiles(scratch) if n else None
    b = region.grid.boundaries
    data = [c for c in region.cells if c.row > 0]
    rt_fail = [c for c in data if not cell_round_trips(c, b)]
    labels = [c.text for c in sorted(region.cells, key=lambda c: c.col) if c.row == 0]
    return n, tiles, len(data), rt_fail, labels

bands = page_bands(PDF, PAGE)
donor = bands[2]
xs = _rule_boundaries(donor)
print(f"donor band2: xs={[round(x,2) for x in xs]} ncols={len(xs)-1} lines={len(donor.lines)}")
print(f"  line0 words: {[w.text for w in sorted(donor.lines[0].words, key=lambda w: w.x0)]}")
for k in (1, 2, 3):
    print(f"  line{k} words: {[w.text for w in sorted(donor.lines[k].words, key=lambda w: w.x0)]}")
grid = LeafGrid(tuple(xs), len(xs) - 1, (xs[-1] - xs[0]) / (len(xs) - 1), 1.0)

for i in (4, 5, 6, 8, 9):
    b = bands[i]
    reg = classify(b)
    n0, t0, d0, f0, l0 = run(reg, f"base{i}") if reg.kind is RegionKind.RECORD_TABLE else (0, None, 0, [], [])
    print(f"\nband{i} lines={len(b.lines)} words={sum(len(l.words) for l in b.lines)} kind={reg.kind.name}")
    print(f"  BASELINE  entries={n0} tiles={t0} datarows={d0} rt_fail={len(f0)} labels={l0}")
    for hdr_line, tag in ((0, "DONATED line0"), (1, "CONTROL line1 (wrapped continuation as header)")):
        hl = donor.lines[hdr_line]
        dband = Band(lines=(hl,) + tuple(b.lines), top=min(hl.top, b.top), bottom=b.bottom,
                     rules=b.rules, hrules=b.hrules, column_xs=tuple(xs))
        cells = assign_cells(dband, grid)
        dreg = ClassifiedRegion(RegionKind.RECORD_TABLE, dband, grid, cells, "donated")
        n1, t1, d1, f1, l1 = run(dreg, f"don{i}_{hdr_line}")
        ink_words = sum(len(l.words) for l in b.lines)
        carried = sum(len(c.words) for c in cells if c.row > 0 and cell_round_trips(c, grid.boundaries))
        print(f"  {tag:48s} entries={n1} tiles={t1} datarows={d1} rt_fail={len(f1)} ink {carried}/{ink_words} labels={l1}")
        if f1:
            print(f"      rt_fail cells: {[(c.row, c.col, c.text) for c in f1][:4]}")
