"""The donor-header criterion, falsified corpus-wide (R203; handoff
`2026-09-10-the-donated-reading-tiles-handoff.md` § 5c, PROPOSED there on ONE page).

The proposition: *a band's line 0 is its header iff the page datagrid
(`derive_data_grid`) refuses that page line `HeterogeneousColumn/every-measure`.*

Population: the 12 asserted `tab:RecordTable` readings of the R166 census
(`docs/superpowers/specs/2026-09-10-the-header-is-assumed-design.md` § 2), whose
"is it a header?" column is a READING made from the printed rows. For each, this
script re-identifies the band's line 0 among the page's text lines BY WORD TEXT
(never by index — [[R202]]) and prints the datagrid's verdict on it. Then, for the
converse direction, it prints EVERY line the datagrid refuses `every-measure` on that
page, so a reader can see whether each is a header.

PROCEDURAL by CLAUDE.md §8: an instrument that reads two shipped derivations and
prints where they agree. It decides nothing and carries no constant.

Run from the repo root (needs the gitignored corpus):

    PYTHONPATH=. .venv/bin/python scripts/donor_header_criterion.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iladub.etkl.compile import page_bands  # noqa: E402
from iladub.etkl.datagrid import derive_data_grid  # noqa: E402
from iladub.etkl.geometry import extract_words, text_lines  # noqa: E402

# (pdf, page, band, census reading of "is line 0 a header?")
POPULATION = [
    ("corpus/ag-trade/cbh-stem-2026-08-03.pdf", 0, 9, "NO"),
    ("corpus/ag-trade/graincorp-capacity-2026-08-04.pdf", 0, 3, "NO"),
    ("corpus/financial/apple-fy2026q3-statements.pdf", 2, 6, "NO"),
    ("corpus/gov-stats/bfs-population-bilan-2023.pdf", 5, 13, "NO (transposed)"),
    ("corpus/gov-stats/bfs-population-bilan-2023.pdf", 6, 2, "YES"),
    ("corpus/gov-stats/bfs-population-bilan-2023.pdf", 6, 4, "NO"),
    ("corpus/gov-stats/bfs-population-bilan-2023.pdf", 6, 5, "NO"),
    ("corpus/gov-stats/bfs-population-bilan-2023.pdf", 6, 6, "NO"),
    ("corpus/gov-stats/bfs-population-bilan-2023.pdf", 6, 8, "NO"),
    ("corpus/gov-stats/bfs-population-bilan-2023.pdf", 6, 9, "NO"),
    ("corpus/health/who-wfa-boys-zscore-0-5.pdf", 0, 4, "NO"),
    ("corpus/health/who-wfa-boys-zscore-0-5.pdf", 1, 4, "NO"),
]


def texts(line):
    return tuple(w.text for w in sorted(line.words, key=lambda w: w.x0))


def key(line):
    """Band words are word GROUPS (`1 736 124` is one word); page words are raw. Compare
    the ink with whitespace removed, as `header_row_census.py` does."""
    return "".join(texts(line)).replace(" ", "")


def page_lines(pdf, page):
    """Exactly `derive_data_grid`'s line list, so indices agree with `grid.refusals`."""
    return [l for l in sorted(text_lines(extract_words(pdf, page)), key=lambda l: l.top)
            if l.words]


def main():
    seen_pages = set()
    for pdf, page, band_idx, reading in POPULATION:
        bands = page_bands(pdf, page)
        band = bands[band_idx]
        lines = page_lines(pdf, page)
        grid = derive_data_grid(pdf, page)
        t0 = texts(band.lines[0])
        hits = [i for i, l in enumerate(lines) if key(l) == key(band.lines[0])]
        idx = hits[0] if len(hits) == 1 else None
        if grid is None:
            verdict = "NO DATAGRID on this page"
        elif idx is None:
            verdict = f"line 0 not uniquely re-identified (hits={hits})"
        elif idx in grid.rows:
            verdict = "body row"
        else:
            verdict = f"refused {grid.refusals.get(idx, '?')}"
        print(f"{os.path.basename(pdf)} p{page} band{band_idx} header?={reading:16s} "
              f"page-line={idx} datagrid: {verdict}\n    line0={' | '.join(t0)[:110]}")
        if grid is not None and (pdf, page) not in seen_pages:
            seen_pages.add((pdf, page))
            em = sorted(i for i, r in grid.refusals.items() if r.endswith("every-measure"))
            print(f"  == page datagrid: {len(grid.columns)} cols ({grid.universe}), "
                  f"{len(grid.rows)} rows, refusals={len(grid.refusals)}; "
                  f"every-measure refusals: {em}")
            for i in em:
                print(f"     line {i:3d}: {' | '.join(texts(lines[i]))[:110]}")


if __name__ == "__main__":
    main()
