#!/usr/bin/env python3
"""Spike — do the refused lines directly above a data grid's first row tile its columns?

ons p7/p8 escalate 175 tokens and every one is header metadata: the adopted grid reads entries
(datagrid.py derives no header, by design — R71) and nothing reads its boxhead. Before building a
header attachment, measure the candidate rule on EVERY page of the corpus that derives a grid, not
on the page that suggested it: for each refused line in the contiguous block above the grid's
first admitted row, place each word by its centre against the grid's own column intervals.

    contained  centre in exactly one column AND the word's extent inside that column
    crossing   centre in a column but the extent crosses a boundary (a spanner, or a misfit)
    outside    centre in no column

PROCEDURAL measurement: exact interval containment against boundaries the grid already derived.
No tolerance. It decides nothing and emits nothing.
"""
import sys
import pdfplumber
from iladub.etkl import extract_words, text_lines
from iladub.etkl.datagrid import derive_data_grid

DOCS = ["ag-trade/graincorp-capacity-2026-08-04.pdf", "ag-trade/graincorp-stem-2026-07-31.pdf",
        "ag-trade/cbh-stem-2026-08-03.pdf", "gov-stats/ons-index-of-services-2026-02.pdf",
        "gov-stats/bfs-population-bilan-2023.pdf", "financial/apple-fy2026q3-statements.pdf",
        "health/who-wfa-boys-zscore-0-5.pdf"]


def place(word, cols):
    cx = (word.x0 + word.x1) / 2.0
    for i, c in enumerate(cols):
        if c.x0 <= cx < c.x1:
            return ("contained" if (word.x0 >= c.x0 and word.x1 <= c.x1) else "crossing"), i
    return "outside", None


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    tot = dict(contained=0, crossing=0, outside=0)
    print(f"{'doc':10s} {'pg':>3s} {'cols':>4s} {'first':>5s} {'hdr lines':>9s} "
          f"{'contained':>9s} {'crossing':>8s} {'outside':>7s}  columns labelled")
    for rel in DOCS:
        if only and only not in rel:
            continue
        path = "corpus/" + rel
        with pdfplumber.open(path) as pdf:
            n = len(pdf.pages)
        for p in range(n):
            grid = derive_data_grid(path, p)
            if grid is None or not grid.rows:
                continue
            lines = sorted([ln for ln in text_lines(extract_words(path, p)) if ln.words],
                           key=lambda ln: ln.top)
            first = min(grid.rows)
            block, j = [], first - 1
            while j >= 0 and j in grid.refusals:
                block.append(j)
                j -= 1
            if not block:
                continue
            counts = dict(contained=0, crossing=0, outside=0)
            labelled = set()
            for j in block:
                for w in lines[j].words:
                    kind, ci = place(w, grid.columns)
                    counts[kind] += 1
                    if kind == "contained":
                        labelled.add(ci)
            for k in tot:
                tot[k] += counts[k]
            print(f"{rel.split('/')[1][:10]:10s} {p:3d} {len(grid.columns):4d} {first:5d} "
                  f"{len(block):9d} {counts['contained']:9d} {counts['crossing']:8d} "
                  f"{counts['outside']:7d}  {sorted(labelled)}")
    n = sum(tot.values()) or 1
    print(f"\nTOTAL words in header blocks: {sum(tot.values())}  "
          f"contained {tot['contained']} ({100*tot['contained']/n:.0f}%)  "
          f"crossing {tot['crossing']} ({100*tot['crossing']/n:.0f}%)  "
          f"outside {tot['outside']} ({100*tot['outside']/n:.0f}%)")


if __name__ == "__main__":
    main()
