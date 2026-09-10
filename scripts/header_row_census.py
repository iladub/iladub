"""The header-row census: what evidence licenses "line 0 is the column header"?

Every band that reaches the flat-record-table branch has its FIRST LINE named
`tab:HeaderWord` in `classifygraph.classify_evidence` (`band.lines[0]`, :53) before
any query runs; `classify-kind.rq` then only checks that those words align 1:1 with
the leaf columns — a test every well-aligned DATA row also passes. This script
measures, over the whole corpus, what that costs: for each asserted table it prints
the label row the graph asserts and the first data row beneath it, so a reader can
see whether the labels are labels.

Per asserted table it prints (all graph-derived, so no band alignment is assumed):

    labels=[...]     the tab:LabelCell texts hanging off the header nodes (-lc*)
    row1=[...]       the first data row's entry-cell texts (-e1_*)

and, where the band can be re-identified positionally (checked, never assumed —
`aligned=no` when the check fails, which it does for a TRANSPOSED reading, whose labels
are grid column 0 rather than line 0), the per-column datatype FAMILY of row 0 against
the modal family of rows >= 1, which is the only type-level evidence a header row
can carry:

    contrast=YES     >=1 column where row 0's family differs from the body's mode
    corner=YES       >=1 column with no row-0 ink over a populated body column

PROCEDURAL by CLAUDE.md §8: an instrument that reads compile results and prints
them. It decides nothing about any document and carries no tuned constant; the
judgement of whether a label row is a header row is left to the reader, in prose.

Run it from the repo root:

    PYTHONPATH=. .venv/bin/python scripts/header_row_census.py [pdf ...]
"""
from __future__ import annotations

import collections
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rdflib import URIRef  # noqa: E402

from iladub.etkl import celltype  # noqa: E402
from iladub.etkl.cells import recover_leaf_grid  # noqa: E402
from iladub.etkl.compile import compile_tables, page_bands  # noqa: E402
from iladub.etkl.document import page_count  # noqa: E402
from iladub.etkl.headers import _grid_cells  # noqa: E402

TAB = "https://w3id.org/iladub/tab#"


def _family(dt):
    """The normalised family for a raw datatype IRI, exactly as header-body-split.rq
    reads it (tab:inDatatypeFamily, falling back to the raw type)."""
    for s, p, o in celltype._DATATYPE_DECLARATIONS:
        if s == dt and str(p).endswith("inDatatypeFamily"):
            return str(o).split("#")[-1]
    return str(dt).split("#")[-1]


def _abstains(dt):
    return any(s == dt and str(p).endswith("datatypeAbstains") and bool(o)
               for s, p, o in celltype._DATATYPE_DECLARATIONS)


def profile(band, grid):
    """(row0 families, body modal families) per leaf column. None = no ink there."""
    by_rc = {(r, c): t for r, c, t in _grid_cells(band, grid)}
    row0, body = [], []
    for c in range(grid.ncols):
        t0 = by_rc.get((0, c))
        d0 = None if t0 is None else celltype._cell_datatype(t0)
        row0.append(None if d0 is None else ("ABSTAIN" if _abstains(d0) else _family(d0)))
        counts = collections.Counter()
        for r in range(1, len(band.lines)):
            t = by_rc.get((r, c))
            if t is None:
                continue
            d = celltype._cell_datatype(t)
            if not _abstains(d):
                counts[_family(d)] += 1
        body.append(counts.most_common(1)[0][0] if counts else None)
    return row0, body


def graph_texts(graph, table_uri, prefix, ncols=24):
    out = []
    for k in range(ncols):
        t = [str(o) for o in graph.objects(URIRef(f"{table_uri}-{prefix}{k}"),
                                           URIRef(TAB + "cellText"))]
        if t:
            out.append(t[0])
    return out


def main(argv):
    pdfs = argv[1:] or sorted(glob.glob("corpus/*/*.pdf"))
    for pdf in pdfs:
        for p in range(page_count(pdf)):
            res = compile_tables(pdf, page_number=p)
            bands = page_bands(pdf, p)
            for i, r in enumerate(res.regions):
                if r.verdict != "asserted" or r.table_uri is None:
                    continue
                labels = graph_texts(res.graph, r.table_uri, "lc")
                if not labels:
                    continue                      # matrix / hierarchical: no flat label row
                row1 = graph_texts(res.graph, r.table_uri, "e1_")
                # Positional band re-identification, CHECKED: the band's first line must
                # carry exactly the words the label row carries.
                band = bands[i] if i < len(bands) else None
                aligned = band is not None and band.lines and (
                    "".join(w.text for w in band.lines[0].words).replace(" ", "")
                    == "".join(labels).replace(" ", ""))
                extra = ""
                if aligned:
                    grid = recover_leaf_grid(band)
                    row0, body = profile(band, grid)
                    contrast = any(f0 is not None and fb is not None
                                   and f0 != "ABSTAIN" and f0 != fb
                                   for f0, fb in zip(row0, body))
                    corner = any(f0 in (None, "ABSTAIN") and fb is not None
                                 for f0, fb in zip(row0, body))
                    extra = (f" lines={len(band.lines)} contrast={'YES' if contrast else 'NO '}"
                             f" corner={'YES' if corner else 'NO '} row0={row0} body={body}")
                print(f"{os.path.basename(pdf)} p{p} band{i} kind={str(r.kind).split('.')[-1]} "
                      f"aligned={'yes' if aligned else 'no'}{extra}\n"
                      f"    labels={labels}\n"
                      f"    row1  ={row1}", flush=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv) or 0)
