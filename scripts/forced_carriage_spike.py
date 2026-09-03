"""The R165 forced-carriage spike — RUN, and refuted (2026-09-03).

The R161 handoff (part 5, graded PROPOSED) predicted that handing apple p0 band 3 the header
reading band 2 asserted, through loop M's page-to-page seam
(`compile_tables(..., carried_header_roles={3: <band 2's reading>})`), would make band 3 pass
`CoverageShape` and assert. This script is the instrument that ran the prediction. Per page it
prints:

  1. the band census — verdict, cell count, table URI, whether the band produced a
     `CarriedHeaderReading` at all (`header_reading`), and for every asserted table what its
     FIRST column header's label text is (the `-lc0` node), which is how a data row asserted as
     a header row is caught;
  2. for every escalated band, the header rows `headers.header_rows_of` finds — what the band
     itself offers as a header;
  3. the forced compile — the reading band 2 produced, or when it produced none (it does, on
     apple: band 2 asserts through the MATRIX branch, which mints no `CarriedHeaderReading`), a
     reading HAND-BUILT from band 2's first header lines over band 3's leaf grid, forced onto
     band 3; and the verdict band 3 then gets.

Every number in `docs/superpowers/2026-09-03-r165-forced-carriage-spike.md` is this script's
output, pasted. Run it from the repo root:

    PYTHONPATH=. .venv/bin/python scripts/forced_carriage_spike.py corpus/financial/apple-fy2026q3-statements.pdf [page] [src band] [dst band]

PROCEDURAL by CLAUDE.md §8: this is an instrument that READS compile results and forces one
input; it decides nothing about any document, carries no tuned constant, and the reading it
hand-builds is deliberately the one the prediction named, not a proposal.
"""
from __future__ import annotations

import sys

from rdflib import URIRef

TAB = "https://w3id.org/iladub/tab#"


def synthetic_reading(lines, boundaries, table_uri: str, page: int):
    """A `CarriedHeaderReading` built from `lines` (top to bottom, the LAST is the leaf) with
    each word keyed by `regions.column_of` over `boundaries` — the same signature notion
    `ruledroles._row_signature` uses, so the block is exactly what the seam would have received
    had loop L confirmed these lines. Non-leaf rows are given the role `continuation`, the only
    non-`level` role a carried vector may carry (a carried vector cannot contain `level`:
    `resolve_ruled_header_rows` refuses it), so the block is the most permissive one the seam
    accepts. Source URIs are placeholders: nothing downstream dereferences them in a spike."""
    from iladub.etkl.regions import column_of
    from iladub.etkl.ruledroles import CarriedHeaderReading, CarriedHeaderRow
    rows = []
    last = len(lines) - 1
    for k, ln in enumerate(lines):
        sig = tuple((column_of((w.x0 + w.x1) / 2.0, boundaries), w.text) for w in ln.words)
        rows.append(CarriedHeaderRow(sig, None if k == last else "continuation",
                                     (URIRef(f"{table_uri}-hsc{k}"),), page))
    return CarriedHeaderReading(tuple(rows))


def census(pdf: str, page: int, graph, regions, bands) -> list[str]:
    from iladub.etkl.headers import header_rows_of
    from iladub.etkl.hierarchical import classify_hierarchical
    out = []
    for i, r in enumerate(regions):
        uri = str(r.table_uri).split("#")[-1] if r.table_uri else None
        line = (f"band {i}: {r.verdict:9} cells={r.cells:3} table={uri} "
                f"header_reading={'yes' if r.header_reading else 'None'}")
        if r.table_uri is not None:
            lc0 = [str(o) for o in graph.objects(URIRef(f"{r.table_uri}-lc0"), URIRef(TAB + "cellText"))]
            line += f" lc0={lc0}"
        if r.verdict == "escalated":
            h = classify_hierarchical(bands[i])
            if h is None:
                line += " hreg=None"
            else:
                hr = header_rows_of(bands[i], h.grid, h.body_line)
                line += f" header_rows={[[c.text for c in row] for row in hr]}"
        line += " | " + (r.ascii.splitlines()[0][:50] if r.ascii else "")
        out.append(line)
    return out


def main(argv):
    from iladub.etkl.compile import compile_tables, page_bands
    from iladub.etkl.headers import header_rows_of
    from iladub.etkl.hierarchical import classify_hierarchical
    from iladub.etkl.ruledroles import carried_roles_for
    pdf = argv[1]
    page = int(argv[2]) if len(argv) > 2 else 0
    src = int(argv[3]) if len(argv) > 3 else 2
    dst = int(argv[4]) if len(argv) > 4 else 3
    base = compile_tables(pdf, page_number=page)
    bands = page_bands(pdf, page)
    print(f"=== {pdf} page {page}: baseline census")
    for line in census(pdf, page, base.graph, base.regions, bands):
        print("  " + line)
    reading = base.regions[src].header_reading
    print(f"=== band {src} header_reading: {reading}")
    if reading is None:
        h = classify_hierarchical(bands[dst])
        if h is None:
            print(f"=== band {dst} has no hierarchical region: nothing to force a reading onto")
            return 0
        b = h.grid.boundaries
        print(f"=== band {dst} leaf grid boundaries: {[round(x, 1) for x in b]}")
        hr = header_rows_of(bands[dst], h.grid, h.body_line)
        print(f"=== band {dst} header_rows_of: {[[c.text for c in row] for row in hr]}")
        n_hdr = max(1, len(hr))
        reading = synthetic_reading(bands[src].lines[:3], b, f"https://example.org/etkl/doc#mtable{src}", page)
        for row in reading.rows:
            print(f"    synthetic row role={row.role!r} signature={row.signature}")
        print(f"=== carried_roles_for(synthetic, band {dst} header rows, band {dst} grid) -> "
              f"{carried_roles_for(reading, hr, h.grid)}")
    forced = compile_tables(pdf, page_number=page, carried_header_roles={dst: reading})
    r = forced.regions[dst]
    print(f"=== forced compile: band {dst} verdict={r.verdict} cells={r.cells} reason={r.reason}")
    print(f"=== asserted tokens: baseline={base.asserted} forced={forced.asserted}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
