"""The R165 one-band matrix spike — the prediction the R165 handoff graded PROPOSED.

PREDICTION (docs/superpowers/2026-09-03-r165-forced-carriage-spike-handoff.md § 5): apple p0
compiles as ONE matrix table — under band 2's `Three Months Ended / Nine Months Ended` column
header, with every section heading (`Operating expenses:` …) read as a row header the way
`mtable2` already reads `Net sales:` as `rh0` — if bands 2..7 are handed to the matrix reader as
ONE band instead of six.

This script is the instrument. It:

  1. prints the per-band census of the page as `compile_tables` reads it today (verdict, cells,
     table URI) beside each band's line count, rule count and derived `column_xs`;
  2. MERGES a contiguous run of bands into one `Band` (lines concatenated in document order,
     top/bottom the run's extent, rules/hrules/captions/unit_markers unioned, `column_xs` taken
     from the run's first band that has any — the run shares one `tab:ruleXsSignature`, which is
     the premise the prediction rests on and which this script CHECKS and prints);
  3. calls `is_matrix_candidate` / `classify_matrix` / `assert_matrix_region` / `region_tiles`
     on the merged band exactly the way `compile.py:819-835` does, and prints what each says.

Run it from the repo root:

    PYTHONPATH=. .venv/bin/python scripts/one_band_matrix_spike.py corpus/financial/apple-fy2026q3-statements.pdf [page] [first] [last]

PROCEDURAL by CLAUDE.md §8: an instrument that READS compile results and constructs one input.
It decides nothing about any document and carries no tuned constant; the merge is exactly the
band run the prediction named, supplied on the command line, never inferred.
"""
from __future__ import annotations

import sys

from rdflib import Graph, URIRef

TAB = "https://w3id.org/iladub/tab#"


# merge_bands was PROMOTED to iladub.etkl.compile (R165 Task 3) and is imported here rather
# than copied: this script is committed evidence and its output must stay reproducible, but a
# second copy of the constructor is the drift `page_bands`' docstring exists to prevent.
from iladub.etkl.compile import merge_bands  # noqa: E402,F401


def main(argv):
    from iladub.etkl.compile import compile_tables, page_bands
    from iladub.etkl.matrix import is_matrix_candidate, classify_matrix
    from iladub.etkl.holon import assert_matrix_region
    from iladub.etkl.tiling import region_tiles

    pdf = argv[1]
    page = int(argv[2]) if len(argv) > 2 else 0
    first = int(argv[3]) if len(argv) > 3 else 2
    last = int(argv[4]) if len(argv) > 4 else 7

    base = compile_tables(pdf, page_number=page)
    bands = page_bands(pdf, page)
    print(f"=== {pdf} page {page}: baseline census ({len(bands)} bands)")
    for i, band in enumerate(bands):
        r = base.regions[i]
        uri = str(r.table_uri).split("#")[-1] if r.table_uri else None
        print(f"  band {i}: {r.verdict:10} cells={r.cells:3} table={uri!s:10} "
              f"lines={len(band.lines):2} rules={len(band.rules):2} "
              f"col_xs={[round(x, 1) for x in band.column_xs]}")
        print(f"           first_line={band.lines[0].words and ' '.join(w.text for w in band.lines[0].words)[:70]!r}")

    print(f"=== merging bands {first}..{last} into one")
    run = bands[first:last + 1]
    sigs = {tuple(round(x, 1) for x in b.column_xs) for b in run}
    print(f"    distinct column_xs vectors in the run: {len(sigs)}")
    for s in sigs:
        print(f"      {list(s)}")
    merged = merge_bands(bands, first, last)
    print(f"    merged band: lines={len(merged.lines)} rules={len(merged.rules)} "
          f"hrules={len(merged.hrules)} col_xs={[round(x, 1) for x in merged.column_xs]}")

    cand = is_matrix_candidate(merged)
    print(f"=== is_matrix_candidate(merged) -> {cand}")
    if not cand:
        return 0
    mreg = classify_matrix(merged)
    print(f"=== classify_matrix(merged) -> {mreg if mreg is None else 'MatrixRegion'}")
    if mreg is None:
        return 0
    print(f"    grid boundaries = {[round(x, 1) for x in mreg.grid.boundaries]}")
    print(f"    data_cols = {mreg.data_cols}  split = {getattr(mreg, 'split', None)}")
    print(f"    leaf_rows = {len(mreg.leaf_rows)}")
    for rb in mreg.leaf_rows[:40]:
        print(f"      row: {' | '.join(c.text for c in rb.cells)[:90]}")
    doc = URIRef("https://example.org/etkl/doc")
    table_uri = URIRef(f"{doc}#mtableMERGED")
    scratch = Graph()
    n = assert_matrix_region(scratch, mreg, merged, table_uri, doc, page)
    print(f"=== assert_matrix_region -> {n} entries, {len(scratch)} triples")
    tiles = region_tiles(scratch)
    print(f"=== region_tiles -> {tiles}")
    print("=== column tree (classify_matrix):")
    for k, n in enumerate(mreg.col_tree):
        print(f"    [{k}] level={n.level} covers={n.covers} parent={n.parent} text={n.text!r}")
    print(f"    body_line={mreg.body_line} stub_cols={mreg.stub_cols}")
    print(f"    row_tree ({len(mreg.row_tree)}): "
          f"{[getattr(r, 'text', r) for r in mreg.row_tree][:12]}")
    labels = sorted(f"{str(s).split('#')[-1]}={o}"
                    for s, o in scratch.subject_objects(URIRef(TAB + "cellText"))
                    if "-lc" in str(s))
    print(f"=== column-header cellTexts ({len(labels)}): {labels}")
    rh = sorted(str(o) for s, o in scratch.subject_objects(URIRef(TAB + "cellText"))
                if "-rh" in str(s))
    print(f"=== row-header cellTexts ({len(rh)}): {rh[:30]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
